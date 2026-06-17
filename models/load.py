class Load:
    """
    Representa o carregamento aplicado à junta
    """

    def __init__(self, load_type, P, L=None, a=None):
        self.load_type = load_type  # centered, eccentric_in_plane, out_of_plane
        self.P = float(P)
        self.L = float(L) if L is not None else None
        self.a = float(a) if a is not None else None

    def __repr__(self):
        return f"Load(type={self.load_type}, P={self.P}, L={self.L}, a={self.a})"
