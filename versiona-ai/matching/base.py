"""
Classe base abstrata para estratégias de matching.

Define a interface que todas as implementações devem seguir.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MatchResult:
    """Resultado de uma operação de matching."""

    found: bool
    """Se o texto foi encontrado."""

    position: int
    """Posição onde o texto foi encontrado (ou -1 se não encontrado)."""

    similarity: float
    """Percentual de similaridade (0.0 a 1.0)."""

    method: str
    """Método usado para encontrar (ex: 'exact', 'fuzzy', 'context')."""


class MatchingStrategy(ABC):
    """
    Interface abstrata para estratégias de matching.

    Cada implementação deve fornecer um algoritmo diferente
    para encontrar texto em documentos.
    """

    @abstractmethod
    def find_best_match(
        self,
        needle: str,
        haystack: str,
        threshold: float = 0.85,
    ) -> MatchResult:
        """
        Encontra a melhor correspondência de 'needle' em 'haystack'.

        Args:
            needle: Texto a ser procurado.
            haystack: Texto onde procurar.
            threshold: Limite mínimo de similaridade (0.0 a 1.0).

        Returns:
            MatchResult com informações sobre o matching.
        """
        pass

    @abstractmethod
    def find_with_context(
        self,
        needle: str,
        context_before: str,
        context_after: str,
        haystack: str,
        threshold: float = 0.85,
    ) -> MatchResult:
        """
        Encontra texto usando contexto anterior e posterior.

        Args:
            needle: Texto a ser procurado.
            context_before: Contexto que aparece antes do needle.
            context_after: Contexto que aparece depois do needle.
            haystack: Texto onde procurar.
            threshold: Limite mínimo de similaridade (0.0 a 1.0).

        Returns:
            MatchResult com informações sobre o matching.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome da estratégia de matching."""
        pass
