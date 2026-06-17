from loads.base_load import BaseLoad


class EccentricOutOfPlane(BaseLoad):
    """
    Carregamento excêntrico fora do plano
    (cisalhamento + tração)
    """

    def __init__(self, P: float, L: float, a: float):
        super().__init__(P)
        self.L = L          # excentricidade no plano [mm]
        self.a = a          # distância fora do plano [mm]
        self.load_type = "eccentric_out_of_plane"

    def description(self) -> str:
        return (
            f"Excêntrico fora do plano | "
            f"P = {self.P:.2f} N | L = {self.L:.2f} mm | a = {self.a:.2f} mm"
        )
