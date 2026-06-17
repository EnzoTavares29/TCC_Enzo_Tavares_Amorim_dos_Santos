# models/joint_parameters.py

class JointParameters:
    """
    Parâmetros globais da junta parafusada
    """

    def __init__(
        self,
        mu=0.4,     # coeficiente de atrito
        C=0.1,      # constante de rigidez da junta
        K=0.20,     # coeficiente torque-aperto
        n_interfaces=1
    ):
        self.mu = mu
        self.C = C
        self.K = K
        self.n_interfaces = n_interfaces
