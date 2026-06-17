# calculations/bearing_joint.py

import math


class BearingJointCalculator:
    """
    Dimensionamento de junta de apoio
    """

    def __init__(self, joint_params):
        self.params = joint_params

    def evaluate_bolt(self, bolt, Fi, bolt_iso, material):
        """
        Avalia um parafuso individual
        """

        At = bolt_iso.At_mm2 * 1e-6  # mm² → m²
        Sp = material.Sp_MPa * 1e6   # MPa → Pa
        C = self.params.C

        sigma_eq = (1 / At) * math.sqrt(
            (Fi + C * bolt.Pf) ** 2 +
            3 * bolt.Vb ** 2
        )

        Np = Sp / sigma_eq

        # segurança contra separação da junta
        if bolt.Pf > 0:
            Nsj = Fi / ((1 - C) * bolt.Pf)
        else:
            Nsj = float("inf")

        return {
            "sigma_eq": sigma_eq,
            "Np": Np,
            "Nsj": Nsj
        }
