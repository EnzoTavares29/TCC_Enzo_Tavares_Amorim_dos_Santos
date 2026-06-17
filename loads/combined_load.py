# loads/combined_load.py

from loads.base_load import BaseLoad

class CombinedLoad(BaseLoad):
    """
    Combina carregamento excêntrico no plano + fora do plano
    """

    def __init__(self, F_shear: float, F_tension: float, L: float, A: float):
        super().__init__(F_shear)  # P is F_shear
        self.F_shear = F_shear
        self.F_tension = F_tension
        self.L = L  # excentricidade no plano [mm]
        self.A = A  # excentricidade fora do plano [mm]
        self.load_type = "combined"

    def description(self) -> str:
        return (
            f"Carregamento combinado | "
            f"F_shear = {self.F_shear:.2f} N | F_tension = {self.F_tension:.2f} N | "
            f"L = {self.L:.2f} mm | A = {self.A:.2f} mm"
        )
