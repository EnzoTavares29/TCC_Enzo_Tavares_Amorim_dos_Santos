from loads.base_load import BaseLoad


class EccentricInPlane(BaseLoad):
    """
    Cisalhamento excêntrico no plano da junta (Shigley)
    """

    def __init__(self, P: float, L: float):
        super().__init__(P)
        self.L = L          # excentricidade no plano [mm]
        self.a = None
        self.load_type = "eccentric_in_plane"

    def description(self) -> str:
        return (
            f"Cisalhamento excêntrico no plano | "
            f"P = {self.P:.2f} N | L = {self.L:.2f} mm"
        )
