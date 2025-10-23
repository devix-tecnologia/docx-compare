"""
Módulo de matching para encontrar tags em documentos.

Fornece diferentes implementações de algoritmos de matching
para comparar performance e qualidade.
"""

from .base import MatchingStrategy, MatchResult
from .difflib_matcher import DifflibMatcher
from .rapidfuzz_matcher import RapidFuzzMatcher

__all__ = [
    "MatchingStrategy",
    "MatchResult",
    "DifflibMatcher",
    "RapidFuzzMatcher",
]
