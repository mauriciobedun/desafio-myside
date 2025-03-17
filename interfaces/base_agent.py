# interfaces/base_agent.py

from abc import ABC, abstractmethod
from typing import Dict

class BaseAgent(ABC):
    @abstractmethod
    def execute(self, nome: str, telefone: str) -> Dict:
        """
        Executa a lógica do agente.
        Retorna as informações coletadas/inferidas em um dicionário.
        """
        pass
