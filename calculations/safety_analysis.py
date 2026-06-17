# calculations/safety_analysis.py

class SafetyAnalyzer:
    """
    Analisa todos os parafusos e identifica o crítico
    """

    def __init__(self):
        pass

    def critical_by(self, bolts, key):
        """
        Retorna o parafuso mais crítico segundo a chave
        (menor fator de segurança)
        """
        valid = [b for b in bolts if getattr(b, key) is not None]
        return min(valid, key=lambda b: getattr(b, key))
