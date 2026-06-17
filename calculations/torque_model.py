# calculations/torque_model.py

class TorqueModel:
    """
    Modelo clássico de torque-aperto (Shigley)
    """

    def __init__(self, K=0.20):
        self.K = K

    def preload(self, torque_Nm, diameter_mm):
        """
        torque_Nm : torque aplicado (Nm)
        diameter_mm : diâmetro nominal (mm)
        """
        d_m = diameter_mm / 1000  # mm → m
        return torque_Nm / (self.K * d_m)
