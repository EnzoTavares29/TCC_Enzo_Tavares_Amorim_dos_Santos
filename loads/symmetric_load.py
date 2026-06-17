from loads.base_load import BaseLoad


class SymmetricLoad(BaseLoad):
    """
    Cisalhamento centrado
    """

    def __init__(self, P: float):
        super().__init__(P)
        self.L = None
        self.a = None
        self.load_type = "symmetric"

    def description(self) -> str:
        return f"Cisalhamento centrado | P = {self.P:.2f} N"
