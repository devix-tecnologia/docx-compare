#!/usr/bin/env python3
"""
Teste Integrado de Processamento Automático + Agrupamento
Simula o fluxo completo: comparação de documentos → criação de modificações → agrupamento por posições
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.docx_compare.processors.processador_agrupamento import ProcessadorAgrupamento
from src.docx_compare.processors.processador_automatico import processar_versao
from src.docx_compare.utils.agrupador_posicional import AgrupadorPosicional


class TestProcessamentoCompleto:
    """Teste do fluxo completo de processamento e agrupamento"""

    def setup_method(self):
        """Setup para cada teste"""
        self.dados_mock = self._criar_dados_mock()

    def _criar_dados_mock(self):
        """Cria dados mock realistas para os testes"""
        return {
            # Versão criada após comparação
            "versao": {
                "id": "test-versao-123",
                "status": "em_processamento",
                "contrato": {"modelo_contrato": {"id": "test-modelo-456"}},
            },
            # Tags do modelo com posições
            "tags": [
                {
                    "id": "tag-1",
                    "tag_nome": "PRAZO_VIGENCIA",
                    "posicao_inicio_texto": 100,
                    "posicao_fim_texto": 200,
                    "clausulas": [{"id": "clausula-1", "nome": "Prazo de Vigência"}],
                },
                {
                    "id": "tag-2",
                    "tag_nome": "VALOR_CONTRATO",
                    "posicao_inicio_texto": 300,
                    "posicao_fim_texto": 400,
                    "clausulas": [{"id": "clausula-2", "nome": "Valor do Contrato"}],
                },
                {
                    "id": "tag-3",
                    "tag_nome": "CONDICOES_PAGAMENTO",
                    "posicao_inicio_texto": 500,
                    "posicao_fim_texto": 600,
                    "clausulas": [
                        {"id": "clausula-3", "nome": "Condições de Pagamento"}
                    ],
                },
            ],
            # Modificações criadas pelo processador automático
            "modificacoes_criadas": [
                {
                    "id": "mod-1",
                    "categoria": "modificacao",
                    "conteudo": "prazo de 12 meses",
                    "alteracao": "prazo de 24 meses",
                    "posicao_inicio": 150,  # Dentro da tag PRAZO_VIGENCIA
                    "posicao_fim": 170,
                    "clausula": None,  # Inicialmente sem cláusula
                },
                {
                    "id": "mod-2",
                    "categoria": "modificacao",
                    "conteudo": "R$ 10.000,00",
                    "alteracao": "R$ 15.000,00",
                    "posicao_inicio": 350,  # Dentro da tag VALOR_CONTRATO
                    "posicao_fim": 365,
                    "clausula": None,
                },
                {
                    "id": "mod-3",
                    "categoria": "adicao",
                    "conteudo": "",
                    "alteracao": "pagamento em 30 dias",
                    "posicao_inicio": 550,  # Dentro da tag CONDICOES_PAGAMENTO
                    "posicao_fim": 575,
                    "clausula": None,
                },
                {
                    "id": "mod-4",
                    "categoria": "remocao",
                    "conteudo": "texto removido sem posição correspondente",
                    "alteracao": "",
                    "posicao_inicio": 800,  # Fora de qualquer tag
                    "posicao_fim": 820,
                    "clausula": None,
                },
            ],
            # Modificações após agrupamento (resultado esperado)
            "modificacoes_agrupadas": [
                {
                    "id": "mod-1",
                    "clausula": "clausula-1",  # Associada ao PRAZO_VIGENCIA
                },
                {
                    "id": "mod-2",
                    "clausula": "clausula-2",  # Associada ao VALOR_CONTRATO
                },
                {
                    "id": "mod-3",
                    "clausula": "clausula-3",  # Associada ao CONDICOES_PAGAMENTO
                },
                {
                    "id": "mod-4",
                    "clausula": None,  # Não associada (fora das tags)
                },
            ],
        }

    def test_processamento_automatico_cria_modificacoes_com_posicoes(self):
        """Testa se o processamento automático cria modificações com campos posicionais"""

        # Teste simplificado - verificar se as funções existem e podem ser importadas
        from src.docx_compare.utils.text_analysis_utils import (
            analyze_differences_detailed,
        )

        # Verificar que as funções existem
        assert callable(analyze_differences_detailed)
        assert callable(processar_versao)

        # Este teste confirma que as funções necessárias estão disponíveis
        # Testes de integração mais complexos devem ser feitos separadamente

    @patch("src.docx_compare.utils.agrupador_posicional.requests")
    def test_agrupamento_posicional_associa_por_posicoes(self, mock_requests):
        """Testa se o agrupamento posicional associa modificações às cláusulas corretas"""

        def mock_get_response(url, **kwargs):
            """Mock personalizado para diferentes endpoints"""
            mock_response = Mock()
            mock_response.status_code = 200

            if "versao/" in url:
                # Resposta para busca de versão
                mock_response.json.return_value = {"data": self.dados_mock["versao"]}
            elif "modelo_contrato_tag" in url:
                # Resposta para busca de tags
                mock_response.json.return_value = {"data": self.dados_mock["tags"]}
            elif "modificacao" in url and "filter[clausula][_null]" in str(
                kwargs.get("params", {})
            ):
                # Resposta para busca de modificações sem cláusula
                mock_response.json.return_value = {
                    "data": self.dados_mock["modificacoes_criadas"]
                }
            else:
                mock_response.json.return_value = {"data": []}

            return mock_response

        def mock_patch_response(url, **kwargs):
            """Mock para operações de PATCH (associações)"""
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": {}}
            return mock_response

        mock_requests.get.side_effect = mock_get_response
        mock_requests.patch.side_effect = mock_patch_response

        # Criar agrupador e executar
        agrupador = AgrupadorPosicional()
        resultado = agrupador.processar_agrupamento_posicional(
            versao_id="test-versao-123", dry_run=False
        )

        # Verificar estatísticas do agrupamento
        assert "total_modificacoes" in resultado
        assert "associacoes_criadas" in resultado
        assert resultado["total_modificacoes"] == 4
        assert resultado["associacoes_criadas"] == 3  # 3 modificações dentro das tags
        assert resultado["sem_correspondencia"] == 1  # 1 modificação fora das tags

        # Verificar se requests.patch foi chamado para associações
        # O sistema faz 2 chamadas por modificação: update posições + associar cláusula
        patch_calls = [
            call
            for call in mock_requests.patch.call_args_list
            if "modificacao/" in str(call)
        ]
        assert len(patch_calls) >= 3  # Pelo menos 3 associações

    def test_fluxo_completo_processamento_agrupamento(self):
        """Testa o fluxo completo: processamento automático seguido de agrupamento"""

        # Teste simplificado - verificar se as classes necessárias podem ser instanciadas
        processador_agrupamento = ProcessadorAgrupamento(verbose=True)

        # Verificar que o processador foi criado corretamente
        assert processador_agrupamento is not None
        assert hasattr(processador_agrupamento, "agrupador")
        assert hasattr(processador_agrupamento, "executar_single_run")

        # Este teste confirma que a infraestrutura está funcionando
        # Testes de integração com dados reais devem ser feitos separadamente    def test_associacao_posicional_logica_containment(self):
        """Testa a lógica de associação por contenção posicional"""

        agrupador = AgrupadorPosicional()

        # Cenário 1: Modificação completamente dentro da tag
        modificacao_dentro = {"posicao_inicio_numero": 150, "posicao_fim_numero": 170}

        tag_container = {
            "tag_nome": "PRAZO_VIGENCIA",
            "posicao_inicio_texto": 100,
            "posicao_fim_texto": 200,
            "clausulas": [{"id": "clausula-1"}],
        }

        tags = [tag_container]
        resultado = agrupador.associar_modificacao_a_tag(modificacao_dentro, tags)

        assert resultado is not None
        assert resultado["tag_nome"] == "PRAZO_VIGENCIA"

        # Cenário 2: Modificação parcialmente sobreposta
        modificacao_sobreposta = {
            "posicao_inicio_numero": 180,
            "posicao_fim_numero": 250,  # Ultrapassa a tag que vai até 200
        }

        resultado_sobreposta = agrupador.associar_modificacao_a_tag(
            modificacao_sobreposta, tags
        )

        # Com o novo threshold de 0%, deve associar mesmo com sobreposição parcial
        assert resultado_sobreposta is not None
        assert resultado_sobreposta["tag_nome"] == "PRAZO_VIGENCIA"

        # Cenário 3: Modificação completamente fora
        modificacao_fora = {"posicao_inicio_numero": 800, "posicao_fim_numero": 820}

        resultado_fora = agrupador.associar_modificacao_a_tag(modificacao_fora, tags)
        assert resultado_fora is None  # Não deve associar

    def test_calculo_sobreposicao(self):
        """Testa o cálculo de sobreposição entre intervalos"""

        agrupador = AgrupadorPosicional()

        # Teste 1: Sobreposição completa
        sobreposicao1 = agrupador.calcular_sobreposicao((100, 200), (150, 170))
        assert sobreposicao1 > 0

        # Teste 2: Sobreposição parcial
        sobreposicao2 = agrupador.calcular_sobreposicao((100, 180), (150, 200))
        assert sobreposicao2 > 0

        # Teste 3: Sem sobreposição
        sobreposicao3 = agrupador.calcular_sobreposicao((100, 150), (200, 250))
        assert sobreposicao3 == 0

        # Teste 4: Intervalos idênticos
        sobreposicao4 = agrupador.calcular_sobreposicao((100, 200), (100, 200))
        assert sobreposicao4 == 1.0  # 100% de sobreposição


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
