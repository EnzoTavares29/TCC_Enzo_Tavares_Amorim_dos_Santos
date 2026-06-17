# models/bolt_group.py

class BoltGroup:
    def __init__(self):
        self.bolts = []
        self.expected_bolts = 0
        self.width = 0.0
        self.height = 0.0

    def configure(self, n_bolts, width, height):
        self.expected_bolts = n_bolts
        self.width = width
        self.height = height

    def add_bolt(self, bolt):
        if len(self.bolts) >= self.expected_bolts:
            raise ValueError("Número máximo de parafusos já atingido")
        self.bolts.append(bolt)

    def remove_last_bolt(self):
        if self.bolts:
            self.bolts.pop()
