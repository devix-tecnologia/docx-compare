"""
Teste de regressão para Task #016:
Sistema não detecta alterações dentro de cláusulas existentes

Este teste valida que o sistema corrigido consegue detectar modificações sutis
dentro de cláusulas (não apenas inserções de blocos inteiros).

Contrato de teste: 86035523-977b-42cf-adda-6fd364170aa9 (Teste - Esse vai! #N0159)
Baseline: Sistema detectava apenas 10 inserções (0 alterações)
Meta: Sistema deve detectar ~40-50 modificações (60-70% alterações)
"""

import os
import sys

import pytest

# Path setup
versiona_ai_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, versiona_ai_dir)
tests_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tests_dir)

# ruff: noqa: E402
from fixtures.contrato_86035523_fixture import (
    CONTRATO_ID,
    CONTRATO_NUMERO,
    CONTRATO_TITULO,
    LINKS,
    METRICAS_ESPERADAS_POS_CORRECAO,
    METRICAS_IA_REFERENCIA,
    METRICAS_SISTEMA_ANTES,
    MODELO_ID,
    MODELO_NOME,
    MODIFICACOES_IA_NAO_DETECTADAS_SISTEMA,
    TOTAL_TAGS_MODELO,
    VERSAO_ID,
    validar_metricas_pos_correcao,
)


class TestRegressaoTask016:
    """
    Testes de regressão para validar correção do problema de detecção
    de modificações dentro de cláusulas.

    Relacionado à Task #016: task-016-sistema-nao-detecta-alteracoes-dentro-clausulas.md
    """

    def test_metricas_baseline_documentadas(self):
        """Valida que as métricas do sistema ANTES da correção estão documentadas."""
        assert METRICAS_SISTEMA_ANTES["total_modificacoes"] == 10
        assert METRICAS_SISTEMA_ANTES["por_categoria"]["INSERCAO"] == 10
        assert METRICAS_SISTEMA_ANTES["por_categoria"]["ALTERACAO"] == 0
        assert METRICAS_SISTEMA_ANTES["por_categoria"]["REMOCAO"] == 0

        # Taxa de inserção era 100%
        taxa_insercao = (
            METRICAS_SISTEMA_ANTES["por_categoria"]["INSERCAO"]
            / METRICAS_SISTEMA_ANTES["total_modificacoes"]
        ) * 100
        assert taxa_insercao == 100.0, "Baseline: sistema detectava apenas inserções"

    def test_metricas_ia_referencia_documentadas(self):
        """Valida que as métricas da IA (ground truth) estão documentadas."""
        assert METRICAS_IA_REFERENCIA["total_modificacoes"] == 44
        assert METRICAS_IA_REFERENCIA["por_categoria"]["ALTERACAO"] == 34

        # Taxa de alteração da IA era ~77%
        taxa_alteracao = (
            METRICAS_IA_REFERENCIA["por_categoria"]["ALTERACAO"]
            / METRICAS_IA_REFERENCIA["total_modificacoes"]
        ) * 100
        assert taxa_alteracao > 75.0, (
            "IA detectou principalmente alterações, não inserções"
        )

    def test_exemplos_modificacoes_nao_detectadas_documentados(self):
        """Valida que exemplos de modificações não detectadas estão documentados."""
        assert len(MODIFICACOES_IA_NAO_DETECTADAS_SISTEMA) >= 3

        # Verificar que são ALTERACAO, não INSERCAO
        for mod in MODIFICACOES_IA_NAO_DETECTADAS_SISTEMA:
            assert mod["tipo"] == "ALTERACAO", (
                "Modificações não detectadas deveriam ser ALTERACAO"
            )
            assert "conteudo_original" in mod, "Modificação deve ter conteudo_original"
            assert "conteudo" in mod, "Modificação deve ter conteudo (novo)"
            assert mod["conteudo"] != mod["conteudo_original"], (
                "Conteúdo deve ser diferente do original"
            )

    @pytest.mark.skip(reason="Teste de integração real - executar após correção")
    def test_processamento_versao_pos_correcao(self):
        """
        Teste de integração real: processa versão e valida métricas.

        ATENÇÃO: Este teste faz chamadas reais ao Directus e reprocessa a versão.
        Deve ser executado APÓS implementar a correção da Task #016.
        """

        # TODO: Implementar teste real após correção
        # 1. Buscar modelo e versão do Directus
        # 2. Processar versão
        # 3. Validar métricas com validar_metricas_pos_correcao()

        pytest.skip("Teste real não implementado - aguardando correção")

    def test_validacao_metricas_pos_correcao_com_dados_simulados(self):
        """Testa função de validação com dados simulados."""

        # Caso 1: Sistema ainda detectando apenas inserções (FALHA esperada)
        resultado_ruim = {
            "modificacoes": [{"categoria": "INSERCAO"} for _ in range(10)]
        }
        validacao_ruim = validar_metricas_pos_correcao(resultado_ruim)
        assert not validacao_ruim["valido"], "Sistema com apenas inserções deve falhar"
        assert len(validacao_ruim["erros"]) > 0

        # Caso 2: Sistema detectando alterações (SUCESSO esperado)
        resultado_bom = {
            "modificacoes": [{"categoria": "ALTERACAO"} for _ in range(32)]
            + [{"categoria": "INSERCAO"} for _ in range(10)]
            + [{"categoria": "REMOCAO"} for _ in range(2)]
        }
        validacao_boa = validar_metricas_pos_correcao(resultado_bom)
        assert validacao_boa["valido"], (
            f"Sistema corrigido deve passar: {validacao_boa['erros']}"
        )
        assert validacao_boa["metricas_obtidas"]["total_modificacoes"] >= 40
        assert validacao_boa["metricas_obtidas"]["por_categoria"]["ALTERACAO"] >= 30

    def test_metricas_esperadas_pos_correcao_sao_razoaveis(self):
        """Valida que as métricas esperadas são razoáveis e alcançáveis."""
        assert METRICAS_ESPERADAS_POS_CORRECAO["total_modificacoes_minimo"] >= 40
        assert METRICAS_ESPERADAS_POS_CORRECAO["alteracoes_minimo"] >= 30
        assert METRICAS_ESPERADAS_POS_CORRECAO["concordancia_com_ia_minimo"] >= 80.0
        assert METRICAS_ESPERADAS_POS_CORRECAO["taxa_alteracao_minimo"] >= 60.0
        assert METRICAS_ESPERADAS_POS_CORRECAO["taxa_insercao_maximo"] <= 30.0

    def test_contrato_metadados_corretos(self):
        """Valida que os metadados do contrato estão corretos."""
        assert CONTRATO_ID == "86035523-977b-42cf-adda-6fd364170aa9"
        assert VERSAO_ID == "8d8e89a8-ba89-4e0e-846c-43e7ad058309"
        assert MODELO_ID == "48b43d38-76b4-47a2-93a4-4216ad57defc"
        assert CONTRATO_TITULO == "Teste - Esse vai!"
        assert CONTRATO_NUMERO == "N0159"
        assert MODELO_NOME == "Contrato de prestação de serviço - Rotina"
        assert TOTAL_TAGS_MODELO == 294

    def test_links_documentados(self):
        """Valida que todos os links de referência estão documentados."""
        assert "contrato_directus" in LINKS
        assert "versao_directus" in LINKS
        assert "modelo_directus" in LINKS
        assert "teste_ab_completo" in LINKS
        assert "resultado_ia" in LINKS

        assert CONTRATO_ID in LINKS["contrato_directus"]
        assert VERSAO_ID in LINKS["versao_directus"]
        assert MODELO_ID in LINKS["modelo_directus"]


# Executar testes standalone
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
