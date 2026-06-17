import math
from calculations.preload import PreloadCalculator
from calculations.combined_stress import CombinedStressCalculator

class EccentricInPlaneCalculator:
    """
    Cisalhamento excêntrico no plano (Shigley)
    Tração axial = apenas pré-carga
    """

    def __init__(self, bolts, load, centroid, bolt_props, torque_Nmm, mu):
        self.bolts = bolts
        self.P = load.P
        self.e = load.L
        self.cx, self.cy = centroid
        self.At = bolt_props.area_tracao
        self.sy = bolt_props.sy
        self.mu = mu
        self.d  = bolt_props.nominal_diameter
        self.torque = torque_Nmm

    def calculate(self):
        """
        Calculate safety factors for eccentric in-plane loading using COEMI methodology
        """
        n = len(self.bolts)
        M = self.P * self.e

        # Radii to centroid
        r_vals = {}
        sum_r2 = 0.0
        for b in self.bolts:
            dx = b.x - self.cx
            dy = b.y - self.cy
            r = math.sqrt(dx*dx + dy*dy)
            r_vals[b.label] = r
            sum_r2 += r*r

        F_direct = self.P / n

        # Pré-carga do torque de aperto
        Fi = PreloadCalculator(self.torque, self.d).preload_force()
        if Fi < 0:
            raise ValueError("Torque de aperto inválido; verifique o valor inserido.")

        per_bolt = []
        fs_bolt_min = float("inf")
        critical = None

        for b in self.bolts:
            Fm = (M * r_vals[b.label]) / sum_r2
            Fs = F_direct + Fm

            # Von Mises stress
            sigma = Fi / self.At
            tau = Fs / self.At
            sigma_eq = math.sqrt(sigma**2 + 3 * tau**2)
            fs_bolt = self.sy / sigma_eq if sigma_eq > 0 else float("inf")

            per_bolt.append({
                "label": b.label,
                "Fi_shear": Fs,
                "Fp": Fi,
                "sigma_eq": sigma_eq,
                "fs_bolt": fs_bolt,
                "separated": False
            })

            # Record per-bolt values on the Bolt object for consistency
            try:
                b.set_preload(Fi)
                b.set_shear(Fs)
            except Exception:
                pass

            if fs_bolt < fs_bolt_min:
                fs_bolt_min = fs_bolt
                critical = b.label

        # Friction joint safety factor
        fs_joint = (self.mu * n * Fi) / self.P if self.P > 0 else float("inf")

        return {
            "per_bolt": per_bolt,
            "critical_bolt": critical,
            "fs_bolt_min": fs_bolt_min,
            "fs_joint": fs_joint
        }


def calculate_eccentric_in_plane(bp, load, bolt_positions):
    # Simplified calculation
    n = len(bolt_positions)
    Fi = load.P / n
    tau = Fi / bp.area_tracao
    fs = bp.tau_adm / tau
    return {
        "fs_bolt": fs,
        "per_bolt": [],
        "critical_bolt": "N/A"
    }
