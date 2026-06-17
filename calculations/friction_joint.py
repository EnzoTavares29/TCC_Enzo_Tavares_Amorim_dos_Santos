# calculations/friction_joint.py

class FrictionJointCalculator:
    """
    Friction-based joint evaluation.

    This helper is tolerant: it accepts either a bolt object with attributes
    (`Pf`, `Vb`) or a per-bolt dictionary produced by other calculators
    (keys: `Fp`, `Fi_shear`). It returns the friction force available on the
    interface (`Fat`) and the safety factor against shear (`Ncis`).
    """

    def __init__(self, joint_params):
        self.params = joint_params

    def evaluate_bolt(self, bolt_or_dict, Fi):
        mu = self.params.mu
        C = self.params.C
        n = self.params.n_interfaces

        # Support both dict produced by calculators and Bolt objects
        if isinstance(bolt_or_dict, dict):
            Pf = bolt_or_dict.get("Fp", 0)
            Vb = bolt_or_dict.get("Fi_shear", 0)
        else:
            Pf = getattr(bolt_or_dict, "Pf", 0)
            Vb = getattr(bolt_or_dict, "Vb", 0)

        Fm = Fi - (1 - C) * Pf
        Fat = mu * Fm * n

        Ncis = Fat / Vb if Vb and Vb > 0 else float("inf")

        return {"Fat": Fat, "Ncis": Ncis}
