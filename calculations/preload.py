class PreloadCalculator:
    """
    Cálculo de pré-carga a partir do torque (Shigley)
    T = K * Fp * d  ->  Fp = T / (K*d)
    """

    def __init__(self, torque_Nmm, diameter_mm, K=0.20):
        self.T = torque_Nmm   # N·mm
        self.d = diameter_mm # mm
        self.K = K

    def preload_force(self):
        return self.T / (self.K * self.d)
