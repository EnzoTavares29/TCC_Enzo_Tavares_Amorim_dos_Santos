from abc import ABC, abstractmethod


class BaseLoad(ABC):
    """
    Classe base abstrata para carregamentos
    """

    def __init__(self, P: float):
        self.P = P  # Força [N]

    @abstractmethod
    def description(self) -> str:
        pass
