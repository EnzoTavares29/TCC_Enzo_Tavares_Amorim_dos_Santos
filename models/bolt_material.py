# models/bolt_material.py

class BoltMaterial:
    """
    Propriedades mecânicas do parafuso
    Valores de Sp conforme Shigley / Norton
    """

    def __init__(self, grade, Sp_MPa):
        self.grade = grade
        self.Sp_MPa = Sp_MPa  # resistência de prova (MPa)


class BoltMaterialTable:
    """
    Tabela de classes de parafuso
    """

    _materials = {
        "5.8":  BoltMaterial("5.8", 380),
        "8.8":  BoltMaterial("8.8", 600),
        "10.9": BoltMaterial("10.9", 830),
        "12.9": BoltMaterial("12.9", 970),
    }

    @classmethod
    def available_grades(cls):
        return list(cls._materials.keys())

    @classmethod
    def get_material(cls, grade):
        return cls._materials[grade]
