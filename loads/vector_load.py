import math
from loads.base_load import BaseLoad


class VectorLoad(BaseLoad):
    """Representa um carregamento vetorial aplicado no plano da junta."""

    def __init__(self, Fx, Fy, Fz, x=0.0, y=0.0, z=0.0):
        self.Fx = float(Fx)
        self.Fy = float(Fy)
        self.Fz = float(Fz)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.P = math.hypot(self.Fx, self.Fy)
        self.load_type = "vector"

    def description(self) -> str:
        return (
            f"Vetor de força: Fx={self.Fx:.1f} N, Fy={self.Fy:.1f} N, Fz={self.Fz:.1f} N; "
            f"Ponto de aplicação: ({self.x:.1f}, {self.y:.1f}, {self.z:.1f}) mm"
        )

    @property
    def shear_magnitude(self):
        return math.hypot(self.Fx, self.Fy)

    @property
    def resultant_magnitude(self):
        return math.sqrt(self.Fx ** 2 + self.Fy ** 2 + self.Fz ** 2)
