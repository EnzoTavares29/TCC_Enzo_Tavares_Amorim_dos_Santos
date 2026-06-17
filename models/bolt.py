class Bolt:
    def __init__(self, x, y, label):
        self.x = float(x)
        self.y = float(y)
        self.label = label
        # Preload (Fp) and shear force on bolt (Vb) — set later by calculators
        self.Pf = 0.0
        self.Vb = 0.0

    def set_preload(self, Fp):
        self.Pf = float(Fp)

    def set_shear(self, Vb):
        self.Vb = float(Vb)
