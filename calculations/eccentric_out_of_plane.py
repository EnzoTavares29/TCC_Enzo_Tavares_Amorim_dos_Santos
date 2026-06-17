import math
from calculations.preload import PreloadCalculator
from calculations.combined_stress import CombinedStressCalculator
from calculations.joint_friction import JointFrictionCalculator

class EccentricOutOfPlaneCalculator:
    """
    Excêntrico fora do plano (Shigley COMPLETO):
    - cisalhamento
    - tração axial externa com sinal (+/-)
    - separação da junta
    - FS do parafuso (von Mises)
    - FS da junta por atrito (COEMI)
    """

    def __init__(self, bolts, load, centroid, bolt_props,
                 torque_Nmm, mu, neutral_axis="y", load_factor=0.10, preload_factor=1.30):
        self.bolts = bolts
        self.P = load.P
        self.e = load.L          # braço no plano
        self.a = load.a          # braço fora do plano
        self.cx, self.cy = centroid
        self.At = bolt_props.area_tracao
        self.sy = bolt_props.sy
        self.sp = bolt_props.sp
        self.mu = mu
        self.d  = bolt_props.nominal_diameter
        self.torque = torque_Nmm
        self.neutral_axis = neutral_axis  # 'x' ou 'y'
        self.C = load_factor
        self.Np = preload_factor

    def _bolt_geometry(self):
        n = len(self.bolts)
        M_in = self.P * self.e
        sum_r2 = 0.0
        geometry = []

        for b in self.bolts:
            dx = b.x - self.cx
            dy = b.y - self.cy
            r = math.sqrt(dx*dx + dy*dy)
            sum_r2 += r*r
            geometry.append({
                "label": b.label,
                "dx": dx,
                "dy": dy,
                "r": r,
                "y": abs(b.y)
            })

        if sum_r2 == 0.0:
            raise ValueError("Geometria inválida: somatório r² = 0")

        Vc = self.P / n
        M_out = self.P * self.a
        sum_y2 = sum(item["y"]**2 for item in geometry)
        if sum_y2 == 0.0:
            raise ValueError("Geometria inválida: somatório y² = 0")

        for item in geometry:
            r = item["r"]
            item["Vt"] = (M_in * r) / sum_r2
            item["Vc"] = Vc
            item["cos_theta"] = item["dx"] / r if r != 0.0 else 0.0
            item["Vb"] = math.sqrt(
                Vc**2 + item["Vt"]**2 + 2 * Vc * item["Vt"] * item["cos_theta"]
            )
            item["Pf"] = (M_out * item["y"]) / sum_y2

        return geometry

    def calculate(self):
        geometry = self._bolt_geometry()
        Fp0 = PreloadCalculator(self.torque, self.d).preload_force()

        per_bolt = []
        fs_bolt_min = float("inf")
        critical = None
        preloads_effective = []

        for item in geometry:
            Fs = item["Vb"]
            Pf = item["Pf"]
            Fa = Fp0 - self.C * Pf
            separated = Fa <= 0.0
            Fp_eff = max(Fa, 0.0)

            if not separated:
                sigma = Fp_eff / self.At
                tau = Fs / self.At
                sigma_eq = math.sqrt(sigma**2 + 3 * tau**2)
                fs_bolt = self.sy / sigma_eq if sigma_eq > 0 else float("inf")
                preloads_effective.append(Fp_eff)
            else:
                sigma_eq = 0.0
                fs_bolt = 0.0

            per_bolt.append({
                "label": item["label"],
                "Fi_shear": Fs,
                "Fp": Fp_eff,
                "Vc": item["Vc"],
                "Vt": item["Vt"],
                "Pf": Pf,
                "sigma_eq": sigma_eq,
                "fs_bolt": fs_bolt,
                "separated": separated
            })

            if not separated and fs_bolt < fs_bolt_min:
                fs_bolt_min = fs_bolt
                critical = item["label"]

        fs_joint = JointFrictionCalculator(
            preloads_effective, self.mu, self.P
        ).safety_factor()

        return {
            "per_bolt": per_bolt,
            "critical_bolt": critical,
            "fs_bolt_min": fs_bolt_min,
            "fs_joint": fs_joint,
            "Fp0": Fp0
        }

    def calculate_coemi_required_torque(self):
        geometry = self._bolt_geometry()
        required_torques = []
        per_bolt = []
        fs_bolt_min = float("inf")
        joint_factor_min = float("inf")

        SpN = (self.sp * self.At) / self.Np

        for item in geometry:
            Pf = item["Pf"]
            Fi = SpN - self.C * Pf
            Fi = max(Fi, 0.0)
            torque_Nmm = 0.20 * Fi * self.d

            sigma = Fi / self.At if self.At > 0 else 0.0
            tau = item["Vb"] / self.At if self.At > 0 else 0.0
            sigma_eq = math.sqrt(sigma**2 + 3 * tau**2) if self.At > 0 else 0.0
            fs_bolt = self.sy / sigma_eq if sigma_eq > 0 else float("inf")
            nsj = Fi / ((1.0 - self.C) * Pf) if Pf > 0 else float("inf")

            per_bolt.append({
                "label": item["label"],
                "Vb": item["Vb"],
                "Pf": Pf,
                "Fi_required": Fi,
                "torque_Nmm": torque_Nmm,
                "sigma_eq": sigma_eq,
                "fs_bolt": fs_bolt,
                "nsj": nsj
            })

            required_torques.append(torque_Nmm)
            if fs_bolt < fs_bolt_min:
                fs_bolt_min = fs_bolt
            if nsj < joint_factor_min:
                joint_factor_min = nsj

        required_torque = max(required_torques) if required_torques else 0.0

        return {
            "T_required_Nmm": required_torque,
            "T_required_Nm": required_torque / 1000.0,
            "per_bolt": per_bolt,
            "fs_bolt_min": fs_bolt_min,
            "fs_joint": joint_factor_min,
            "critical_bolt": min(per_bolt, key=lambda x: x["fs_bolt"])["label"] if per_bolt else None
        }


def calculate_eccentric_out_of_plane(bp, load, torque, mu, interfaces, bolt_positions):
    """
    COEMI method for eccentric out-of-plane loading (friction joint)
    Fi = sqrt[(Sp*At/Np)² - 3*Vb²]
    FS_joint = (μ * Σ Fi) / F_applied
    """
    import math
    
    n = len(bolt_positions)
    Vb = load.F_shear / n  # Shear force per bolt
    d = bp.nominal_diameter
    At = bp.area_tracao
    Sp = bp.sy * 1e6  # Convert MPa to Pa
    Np = 1.0
    
    # Pré-carga a partir do torque de aperto
    Fi = PreloadCalculator(torque, d).preload_force()
    if Fi < 0:
        raise ValueError("Torque de aperto inválido; verifique o valor inserido.")
    
    # Bearing joint stress calculation
    sigma = Fi / At  # Tensile stress from preload
    tau = Vb / At    # Shear stress
    sigma_eq = math.sqrt(sigma**2 + 3 * tau**2)
    fs_bolt = bp.sy / sigma_eq if sigma_eq > 0 else float("inf")
    
    # Friction joint
    fs_joint = (mu * n * Fi) / load.F_shear if load.F_shear > 0 else float("inf")
    t_opt = (load.F_shear * d) / (0.2 * mu * n * interfaces)
    
    return {
        "fs_bolt": fs_bolt,
        "fs_joint": fs_joint,
        "t_optimal": t_opt,
        "Fp": Fi * 1000,
        "per_bolt": []
    }
