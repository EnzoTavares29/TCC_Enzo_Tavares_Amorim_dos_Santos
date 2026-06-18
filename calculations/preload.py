class PreloadCalculator:
    """
    Cálculo de pré-carga a partir do torque (Shigley)
    T = K * Fp * d  ->  Fp = T / (K*d)

    Notes:
    - Inputs: `torque_Nmm` in N·mm, `diameter_mm` in mm, `K` dimensionless.
    - Returns: preload force `Fp` in N.
    """

    def __init__(self, torque_Nmm, diameter_mm, K=0.20):
        self.T = torque_Nmm   # N·mm
        self.d = diameter_mm # mm
        self.K = K

    def preload_force(self):
        # Prevent division by zero
        if self.K * self.d == 0:
            return 0.0
        return self.T / (self.K * self.d)  # returns N
