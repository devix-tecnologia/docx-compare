"""Teste de validação do contrato de vigência."""

import os
import sys

# Path setup
tests_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tests_dir)

# Import fixture
from fixtures.contrato_vigencia_fixture import (
    METRICAS_ESPERADAS,
    MODELO_TEXTO_ORIGINAL,
    TOTAL_MODIFICACOES_ESPERADO,
    VERSAO_TEXTO_MODIFICADO,
)


class TestContratoVigencia:
    """Testes de validação."""

    def test_modelo_contem_clausulas(self):
        """Valida cláusulas do modelo."""
        assert "1.  OBJETO" in MODELO_TEXTO_ORIGINAL
        assert "QUADRO RESUMO" in MODELO_TEXTO_ORIGINAL

    def test_versao_contem_modificacoes(self):
        """Valida modificações."""
        assert "ESCOPO INICIAL PREVISTO" in VERSAO_TEXTO_MODIFICADO
        assert "2.5" in VERSAO_TEXTO_MODIFICADO

    def test_metricas(self):
        """Valida métricas."""
        assert TOTAL_MODIFICACOES_ESPERADO == 7
        assert METRICAS_ESPERADAS["revisao_manual"] == 0
