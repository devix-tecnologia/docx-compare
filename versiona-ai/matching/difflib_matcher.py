"""
Implementação de matching usando difflib (biblioteca padrão Python).

Esta é a implementação atual do sistema.
"""

import difflib

from .base import MatchingStrategy, MatchResult


class DifflibMatcher(MatchingStrategy):
    """
    Matching usando difflib.SequenceMatcher.

    Características:
    - Biblioteca padrão (sem dependências)
    - Algoritmo: Ratcliff-Obershelp
    - Performance: ~O(n*m) onde n=len(haystack), m=len(needle)
    - Qualidade: Boa para textos similares
    """

    @property
    def name(self) -> str:
        return "difflib"

    def find_best_match(
        self,
        needle: str,
        haystack: str,
        threshold: float = 0.85,
    ) -> MatchResult:
        """
        Busca por sliding window, comparando cada posição.

        Complexidade: O(n * m) onde n=len(haystack), m=len(needle)
        """
        if not needle or not haystack:
            return MatchResult(
                found=False,
                position=-1,
                similarity=0.0,
                method="difflib_exact",
            )

        # Tenta match exato primeiro (rápido)
        if needle in haystack:
            pos = haystack.find(needle)
            return MatchResult(
                found=True,
                position=pos,
                similarity=1.0,
                method="difflib_exact",
            )

        # Fuzzy matching por sliding window
        needle_len = len(needle)
        best_ratio = 0.0
        best_pos = -1

        for i in range(len(haystack) - needle_len + 1):
            chunk = haystack[i : i + needle_len]
            ratio = difflib.SequenceMatcher(None, needle, chunk).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_pos = i

                # Early exit se encontrou match perfeito
                if ratio >= 0.99:
                    break

        found = best_ratio >= threshold

        return MatchResult(
            found=found,
            position=best_pos if found else -1,
            similarity=best_ratio,
            method="difflib_fuzzy",
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

        Estratégia:
        1. Procura contexto completo (before + needle + after)
        2. Se não achar, procura só o needle
        """
        # Monta o texto completo com contexto
        full_context = context_before + needle + context_after

        # Tenta encontrar com contexto completo
        if full_context in haystack:
            # Encontrou o contexto completo
            pos = haystack.find(full_context)
            # A posição do needle é offset pelo contexto anterior
            needle_pos = pos + len(context_before)

            return MatchResult(
                found=True,
                position=needle_pos,
                similarity=1.0,
                method="difflib_context_exact",
            )

        # Fallback: procura só o needle
        fallback = self.find_best_match(needle, haystack, threshold)

        if fallback.found and "fuzzy" not in fallback.method:
            return MatchResult(
                found=True,
                position=fallback.position,
                similarity=fallback.similarity,
                method="difflib_fallback_fuzzy",
            )

        return fallback
