class JointFrictionCalculator:
    """
    FS da junta por atrito (COEMI)
    FS_junta = (mu * sum(Fp_ativos)) / F_cisalhamento
    """

    def __init__(self, preload_forces, mu, shear_load):
        self.preloads = preload_forces  # lista de Fp efetivos (>=0)
        self.mu = mu
        self.F = shear_load

    def safety_factor(self):
        if self.F <= 0:
            return float("inf")
        return (self.mu * sum(self.preloads)) / self.F
