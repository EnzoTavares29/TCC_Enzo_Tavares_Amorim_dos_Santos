import math
from calculations.preload import PreloadCalculator
from calculations.combined_stress import CombinedStressCalculator
from calculations.joint_friction import JointFrictionCalculator


class ShearCenteredWithTorqueCalculator:
    """
    Cisalhamento centrado COM torque de aperto
    (Shigley completo)

    - Pré-carga via torque
    - Cisalhamento distribuído igualmente
    - Tensão equivalente (von Mises)
    - FS do parafuso
    - FS da junta por atrito
    """

    def __init__(self, bolts, load, bolt_props, torque_Nmm, mu):
        self.bolts = bolts
        self.P = load.P
        self.At = bolt_props.area_tracao
        self.sy = bolt_props.sy
        self.mu = mu
        self.d = bolt_props.nominal_diameter
        self.torque = torque_Nmm

    def calculate(self):
        """
        Calculate safety factors using COEMI methodology
        Fi is computed from torque using the standard Shigley preload relationship.
        """
        n = len(self.bolts)
        Vb = self.P / n  # Shear force per bolt (N)

        # Pré-carga a partir do torque de aperto
        Fi = PreloadCalculator(self.torque, self.d).preload_force()
        if Fi < 0:
            raise ValueError("Torque de aperto inválido; verifique o valor inserido.")

        per_bolt = []
        fs_bolt_min = float("inf")
        preloads_effective = []

        for b in self.bolts:
            # Von Mises equivalent stress
            sigma = Fi / self.At  # Tensile stress from preload (MPa)
            tau = Vb / self.At    # Shear stress (MPa)
            sigma_eq = math.sqrt(sigma**2 + 3 * tau**2)

            fs_bolt = self.sy / sigma_eq if sigma_eq > 0 else float("inf")

            per_bolt.append({
                "label": b.label,
                "Fi_shear": Vb,
                "Fp": Fi,  # N
                "sigma_eq": sigma_eq,
                "fs_bolt": fs_bolt,
                "separated": False
            })

            # Record per-bolt values on the Bolt object for consistency
            try:
                b.set_preload(Fi)
                b.set_shear(Vb)
            except Exception:
                pass

            preloads_effective.append(Fi)

            if fs_bolt < fs_bolt_min:
                fs_bolt_min = fs_bolt

        # FS da junta por atrito (friction joint)
        fs_joint = (self.mu * n * Fi) / self.P if self.P > 0 else 0

        return {
            "per_bolt": per_bolt,
            "critical_bolt": "Todos",
            "fs_bolt_min": fs_bolt_min,
            "fs_joint": fs_joint
        }


def calculate_shear_centered_with_torque(bp, load, torque, mu, interfaces, n_bolts):
    """
    COEMI method for shear centered with torque
    Fi is derived from the input torque using the preload coefficient K.
    """
    Vb = load.P / n_bolts  # Shear force per bolt
    d = bp.nominal_diameter
    At = bp.area_tracao
    Sp = bp.sy * 1e6  # Convert MPa to Pa for calculation
    Np = 1.0  # Standard preload factor
    
    # Pré-carga a partir do torque de aperto
    Fi = PreloadCalculator(torque, d).preload_force()
    if Fi < 0:
        raise ValueError("Torque de aperto inválido; verifique o valor inserido.")
    
    # Bearing joint stress (von Mises)
    sigma = Fi / At  # Tensile stress from preload
    tau = Vb / At    # Shear stress
    sigma_eq = math.sqrt(sigma**2 + 3 * tau**2)
    fs_bolt = bp.sy / sigma_eq
    
    # Friction joint
    fs_joint = (mu * n_bolts * Fi) / load.P if load.P > 0 else float("inf")
    t_opt = (load.P * d) / (0.2 * mu * n_bolts * interfaces)
    
    return {
        "fs_bolt": fs_bolt,
        "fs_joint": fs_joint,
        "t_optimal": t_opt,
        "Fp": Fi,
        "per_bolt": []
    }
