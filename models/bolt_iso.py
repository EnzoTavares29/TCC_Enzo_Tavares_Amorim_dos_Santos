"""
Propriedades de parafusos métricos ISO
Baseado em:
- ISO 898-1
- Shigley – Elementos de Máquinas
"""

from models.iso_bolt_table import ISO_BOLT_TABLE


# =========================
# Classes mecânicas ISO 898-1
# =========================
BOLT_CLASSES = {
    "5.8": {
        "Su": 500.0,    # MPa
        "Sy": 400.0
    },
    "8.8": {
        "Su": 800.0,
        "Sy": 640.0
    },
    "10.9": {
        "Su": 1000.0,
        "Sy": 900.0
    },
    "12.9": {
        "Su": 1200.0,
        "Sy": 1080.0
    }
}


class BoltProperties:
    """
    Propriedades geométricas e mecânicas do parafuso
    """

    def __init__(self, diameter: str, series: str, bolt_class: str):
        # ---------- Geometria ----------
        if diameter not in ISO_BOLT_TABLE:
            raise ValueError("Diâmetro não encontrado na tabela ISO")

        if series not in ISO_BOLT_TABLE[diameter]:
            raise ValueError("Série de rosca inválida para este diâmetro")

        self.diameter = diameter
        self.series = series
        self.geometry = ISO_BOLT_TABLE[diameter][series]

        # ---------- Classe mecânica ----------
        if bolt_class not in BOLT_CLASSES:
            raise ValueError("Classe do parafuso inválida")

        self.bolt_class = bolt_class
        self.material = BOLT_CLASSES[bolt_class]

    # =========================
    # Geometria
    # =========================
    @property
    def pitch(self):
        return self.geometry["pitch"]

    @property
    def area_tracao(self):
        """Área resistente à tração At [mm²]"""
        return self.geometry["At"]

    @property
    def area_raiz(self):
        """Área na raiz da rosca Ar [mm²]"""
        return self.geometry["Ar"]

    # =========================
    # Material
    # =========================
    @property
    def Su(self):
        """Resistência última à tração [MPa]"""
        return self.material["Su"]

    @property
    def Sy(self):
        """Limite de escoamento [MPa]"""
        return self.material["Sy"]

    @property
    def tau_adm(self):
        """
        Tensão admissível ao cisalhamento segundo Shigley
        τ = 0,577 · Sy
        """
        return 0.577 * self.Sy
