"""
Implementação de matching usando RapidFuzz.

RapidFuzz é uma biblioteca otimizada em C++ que é muito mais rápida
que difflib para operações de fuzzy matching.
"""

from .base import MatchingStrategy, MatchResult

try:
    from rapidfuzz import fuzz

    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


class RapidFuzzMatcher(MatchingStrategy):
    """
    Matching usando RapidFuzz.

    Características:
    - Implementação em C++ (muito mais rápida que difflib)
    - Performance: ~10-100x mais rápido que difflib
    - Algoritmo: Levenshtein otimizado
    - Qualidade: Similar ou melhor que difflib

    Requer: pip install rapidfuzz
    """

    def __init__(self):
        if not RAPIDFUZZ_AVAILABLE:
            raise ImportError(
                "RapidFuzz não está instalado. "
                "Instale com: pip install rapidfuzz"
            )

    @property
    def name(self) -> str:
        return "rapidfuzz"

    def find_best_match(
        self,
        needle: str,
        haystack: str,
        threshold: float = 0.85,
    ) -> MatchResult:
        """
        Busca usando RapidFuzz com sliding window otimizado.

        Performance: ~10-50x mais rápido que difflib.
        """
        if not needle or not haystack:
            return MatchResult(
                found=False,
                position=-1,
                similarity=0.0,
                method="rapidfuzz_exact",
            )

        # Tenta match exato primeiro (rápido)
        if needle in haystack:
            pos = haystack.find(needle)
            return MatchResult(
                found=True,
                position=pos,
                similarity=1.0,
                method="rapidfuzz_exact",
            )

        # Fuzzy matching otimizado
        needle_len = len(needle)
        best_ratio = 0.0
        best_pos = -1

        # RapidFuzz é MUITO mais rápido que difflib aqui
        for i in range(len(haystack) - needle_len + 1):
            chunk = haystack[i : i + needle_len]
            # fuzz.ratio é ~50x mais rápido que SequenceMatcher
            ratio = fuzz.ratio(needle, chunk) / 100.0  # Normaliza para 0-1

            if ratio > best_ratio:
                best_ratio = ratio
                best_pos = i

                # Early exit
                if ratio >= 0.99:
                    break

        found = best_ratio >= threshold

        return MatchResult(
            found=found,
            position=best_pos if found else -1,
            similarity=best_ratio,
            method="rapidfuzz_fuzzy",
        )

    def find_with_context(
        self,
        needle: str,
        context_before: str,
        context_after: str,
        haystack: str,
        threshold: float = 0.85,
    ) -> MatchResult:
        """
        Busca usando contexto anterior e posterior.

        Estratégia idêntica ao DifflibMatcher, mas usando RapidFuzz.
        """
        # Monta o texto completo com contexto
        full_context = context_before + needle + context_after

        # Tenta encontrar com contexto completo
        if full_context in haystack:
            pos = haystack.find(full_context)
            needle_pos = pos + len(context_before)

            return MatchResult(
                found=True,
                position=needle_pos,
                similarity=1.0,
                method="rapidfuzz_context_exact",
            )

        # Fallback: procura só o needle
        return self.find_best_match(needle, haystack, threshold)
