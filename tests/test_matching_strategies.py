"""
Testes unitários para estratégias de matching.

Valida funcionalidade e qualidade de cada implementação.
"""

import sys
from pathlib import Path

import pytest

# Adiciona o diretório versiona-ai ao path
versiona_ai_path = Path(__file__).parent.parent / "versiona-ai"
sys.path.insert(0, str(versiona_ai_path))

from matching import (  # noqa: E402
    DifflibMatcher,
    MatchingStrategy,
    RapidFuzzMatcher,
)
from matching.rapidfuzz_matcher import RAPIDFUZZ_AVAILABLE  # noqa: E402

from tests.matching_rinha_metrics import InstrumentedMatcher  # noqa: E402


# Fixture com diferentes estratégias
@pytest.fixture(params=["difflib", "rapidfuzz"])
def matcher(request) -> MatchingStrategy:
    """Retorna cada estratégia de matching para testar."""
    if request.param == "difflib":
        return InstrumentedMatcher(DifflibMatcher())
    elif request.param == "rapidfuzz":
        if not RAPIDFUZZ_AVAILABLE:
            pytest.skip("RapidFuzz não está instalado")
        return InstrumentedMatcher(RapidFuzzMatcher())
    raise ValueError(f"Matcher desconhecido: {request.param}")


class TestExactMatch:
    """Testes de matching exato."""

    def test_exact_match_found(self, matcher: MatchingStrategy):
        """Match exato deve encontrar posição correta."""
        needle = "Lorem ipsum"
        haystack = "Texto antes. Lorem ipsum dolor sit amet."

        result = matcher.find_best_match(needle, haystack, threshold=0.85)

        assert result.found is True
        assert result.position == 13  # Posição de "Lorem ipsum"
        assert result.similarity == 1.0
        assert "exact" in result.method

    def test_exact_match_not_found(self, matcher: MatchingStrategy):
        """Texto não presente deve retornar não encontrado."""
        needle = "texto inexistente"
        haystack = "Texto completamente diferente."

        result = matcher.find_best_match(needle, haystack, threshold=0.85)

        assert result.found is False
        assert result.position == -1

    def test_empty_needle(self, matcher: MatchingStrategy):
        """Needle vazio deve retornar não encontrado."""
        result = matcher.find_best_match("", "qualquer texto", threshold=0.85)

        assert result.found is False
        assert result.position == -1

    def test_empty_haystack(self, matcher: MatchingStrategy):
        """Haystack vazio deve retornar não encontrado."""
        result = matcher.find_best_match("texto", "", threshold=0.85)

        assert result.found is False
        assert result.position == -1


class TestFuzzyMatch:
    """Testes de fuzzy matching."""

    def test_fuzzy_match_found(self, matcher: MatchingStrategy):
        """Match parcial deve encontrar texto similar."""
        needle = "contrato de prestação"
        haystack = "Este é um contrato de prestaçao de serviços"  # sem ç

        result = matcher.find_best_match(needle, haystack, threshold=0.85)

        assert result.found is True
        assert result.similarity >= 0.90  # Alta similaridade
        assert "fuzzy" in result.method

    def test_fuzzy_match_threshold(self, matcher: MatchingStrategy):
        """Match abaixo do threshold não deve ser encontrado."""
        needle = "texto completamente diferente"
        haystack = "outro texto sem relação alguma"

        result = matcher.find_best_match(needle, haystack, threshold=0.85)

        assert result.found is False
        assert result.similarity < 0.85

    def test_fuzzy_match_best_position(self, matcher: MatchingStrategy):
        """Deve encontrar a melhor posição quando há múltiplas ocorrências."""
        needle = "contrato"
        haystack = "contato com contrato de prestação"

        result = matcher.find_best_match(needle, haystack, threshold=0.85)

        assert result.found is True
        # Deve encontrar "contrato" (exato) e não "contato" (similar)
        assert haystack[result.position : result.position + len(needle)] == "contrato"


class TestContextMatch:
    """Testes de matching com contexto."""

    def test_context_exact_match(self, matcher: MatchingStrategy):
        """Match com contexto exato deve encontrar posição correta."""
        needle = "cláusula 5.1"
        context_before = "Conforme previsto na "
        context_after = " deste contrato"
        haystack = (
            "Texto anterior. Conforme previsto na cláusula 5.1 "
            "deste contrato, as partes."
        )

        result = matcher.find_with_context(
            needle, context_before, context_after, haystack, threshold=0.85
        )

        assert result.found is True
        assert result.similarity == 1.0
        assert "exact" in result.method
        # Verifica que a posição aponta para o início do needle
        assert haystack[result.position : result.position + len(needle)] == needle

    def test_context_fallback_to_fuzzy(self, matcher: MatchingStrategy):
        """Se contexto não for encontrado, deve usar fuzzy."""
        needle = "cláusula 5.1"
        context_before = "contexto que não existe"
        context_after = "outro contexto inexistente"
        haystack = "Texto com cláusula 5.1 sem o contexto esperado."

        result = matcher.find_with_context(
            needle, context_before, context_after, haystack, threshold=0.85
        )

        assert result.found is True
        assert "fuzzy" in result.method


class TestRealWorldScenarios:
    """Testes com cenários reais do sistema."""

    def test_tag_com_acentos(self, matcher: MatchingStrategy):
        """Tags com acentuação devem funcionar."""
        needle = "prestação de serviços"
        haystack = "Contrato de prestação de serviços entre as partes."

        result = matcher.find_best_match(needle, haystack, threshold=0.85)

        assert result.found is True
        assert result.similarity >= 0.95

    def test_tag_com_quebras_linha(self, matcher: MatchingStrategy):
        """Tags com quebras de linha devem ser normalizadas."""
        needle = "cláusula importante do contrato"
        haystack = "Texto com\ncláusula importante\ndo contrato\naqui."

        # Normaliza espaços
        needle_norm = " ".join(needle.split())
        haystack_norm = " ".join(haystack.split())

        result = matcher.find_best_match(needle_norm, haystack_norm, threshold=0.85)

        assert result.found is True

    def test_tag_numeracao(self, matcher: MatchingStrategy):
        """Tags de numeração (ex: 5.1, 5.1.1) devem funcionar."""
        test_cases = [
            ("5.1", "Cláusula 5.1 - Objeto do contrato"),
            ("5.1.1", "Item 5.1.1 especifica que"),
            ("16.8.4", "Conforme 16.8.4 desta seção"),
        ]

        for needle, haystack in test_cases:
            result = matcher.find_best_match(needle, haystack, threshold=0.85)
            assert result.found is True, f"Não encontrou: {needle}"
            assert result.similarity == 1.0


@pytest.mark.skipif(not RAPIDFUZZ_AVAILABLE, reason="RapidFuzz não instalado")
class TestMatcherEquivalence:
    """Testes para garantir que ambas implementações retornam resultados equivalentes."""

    def test_same_results_exact_match(self):
        """Ambas devem retornar mesmos resultados para match exato."""
        difflib_matcher = DifflibMatcher()
        rapidfuzz_matcher = RapidFuzzMatcher()

        needle = "texto de teste"
        haystack = "Este é um texto de teste para validação."

        result_difflib = difflib_matcher.find_best_match(
            needle, haystack, threshold=0.85
        )
        result_rapidfuzz = rapidfuzz_matcher.find_best_match(
            needle, haystack, threshold=0.85
        )

        assert result_difflib.found == result_rapidfuzz.found
        assert result_difflib.position == result_rapidfuzz.position
        assert result_difflib.similarity == result_rapidfuzz.similarity

    def test_similar_results_fuzzy_match(self):
        """Ambas devem retornar resultados similares para fuzzy match."""
        difflib_matcher = DifflibMatcher()
        rapidfuzz_matcher = RapidFuzzMatcher()

        needle = "contrato de prestação"
        haystack = "contrato de prestaçao de serviços"  # Pequena diferença

        result_difflib = difflib_matcher.find_best_match(
            needle, haystack, threshold=0.85
        )
        result_rapidfuzz = rapidfuzz_matcher.find_best_match(
            needle, haystack, threshold=0.85
        )

        assert result_difflib.found == result_rapidfuzz.found
        # Similaridade pode variar ligeiramente, mas deve estar próxima
        assert abs(result_difflib.similarity - result_rapidfuzz.similarity) < 0.05
