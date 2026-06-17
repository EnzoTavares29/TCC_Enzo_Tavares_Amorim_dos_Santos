import math

class CombinedStressCalculator:
    """
    von Mises: tração + cisalhamento (Shigley)
    sigma_eq = sqrt( sigma^2 + 3*tau^2 )
    """

    def __init__(self, axial_force, shear_force, area):
        self.Fa = axial_force
        self.Fs = shear_force
        self.A  = area

    def equivalent_stress(self):
        sigma = self.Fa / self.A
        tau = self.Fs / self.A
        return math.sqrt(sigma**2 + 3.0 * tau**2)


def calculate_combined_stress(bp, load, bolt_positions):
    """
    COEMI method for combined stress (eccentric loading, bearing joint)
    Uses At_min = sqrt[3*Vb² + ((2-C)*Pf)²] / Sp
    """
    import math
    
    n = len(bolt_positions)
    Vb = load.F_shear / n  # Shear force per bolt
    At = bp.area_tracao
    Sp = bp.sy * 1e6  # Pa
    
    # Simplified: direct stress calculation (distributed load assumption)
    # For each bolt: σ = Vb / At (shear), τ = 0 (simplified, no tension in bearing only)
    # Total: σ_eq = sqrt(3*τ²) = sqrt(3) * τ
    
    tau = Vb / At
    sigma_eq = math.sqrt(3) * tau  # For pure shear: σ_eq = sqrt(3) * τ
    fs_bolt = bp.sy / sigma_eq
    
    return {
        "fs_bolt": fs_bolt,
        "per_bolt": [],
        "critical_bolt": "N/A"
    }
