class ShearCenteredCalculator:
    """
    Cisalhamento centrado
    Retorno PADRONIZADO
    """

    def __init__(self, bolts, load, bolt_props, tau_adm):
        self.bolts = bolts
        self.P = load.P
        self.At = bolt_props.area_tracao
        self.tau_adm = tau_adm

    def calculate(self):
        n = len(self.bolts)
        Fi = self.P / n
        tau = Fi / self.At
        fs = self.tau_adm / tau

        per_bolt = []
        for b in self.bolts:
            per_bolt.append({
                "label": b.label,
                "Fi_shear": Fi,
                "Fp": 0.0,
                "tau": tau,
                "fs_bolt": fs,
                "separated": False
            })

            # record per-bolt values on the Bolt object for consistency
            try:
                b.set_preload(0.0)
                b.set_shear(Fi)
            except Exception:
                pass

        return {
            "per_bolt": per_bolt,
            "critical_bolt": "Todos",
            "fs_bolt_min": fs
        }


def calculate_shear_centered(bp, load, n_bolts):
    """
    COEMI bearing joint method for shear centered loading
    FS = τ_adm / τ = τ_adm / (Vb / At)
    """
    Vb = load.P / n_bolts
    tau = Vb / bp.area_tracao
    fs = bp.tau_adm / tau
    return {
        "fs_bolt": fs,
        "per_bolt": [],
        "critical_bolt": "N/A"
    }
