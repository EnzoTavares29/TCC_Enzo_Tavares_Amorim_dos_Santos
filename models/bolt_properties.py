from models.iso_bolt_table import ISO_BOLT_TABLE


class BoltProperties:
    """
    Propriedades mecânicas do parafuso
    Baseado no Shigley + ISO
    """

    def __init__(self, diameter: str, series: str, bolt_class: str):
        self.diameter = diameter
        self.series = series
        self.bolt_class = bolt_class

        self.area_tracao = self._get_area_tracao()
        self.sy, self.su, self.sp = self._get_material_properties()
        self.tau_adm = 0.577 * self.sy  # Shigley (von Mises)
        # nominal diameter in mm (e.g. 'M6' -> 6.0)
        try:
            self.nominal_diameter = float(self.diameter.lstrip('M'))
        except Exception:
            self.nominal_diameter = None

    def _get_area_tracao(self):
        try:
            return ISO_BOLT_TABLE[self.diameter][self.series]["At"]
        except KeyError:
            raise ValueError("Diâmetro ou série não encontrados na tabela ISO")

    def _get_material_properties(self):
        classes = {
            "5.8": (400, 500, 380),
            "8.8": (640, 800, 600),
            "10.9": (900, 1000, 900),
            "12.9": (1100, 1200, 1000)
        }

        if self.bolt_class not in classes:
            raise ValueError("Classe de parafuso inválida")

        sy, su, sp = classes[self.bolt_class]
        return sy, su, sp
