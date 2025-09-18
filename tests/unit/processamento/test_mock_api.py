#!/usr/bin/env python3
"""
Teste de Mock e API do Sistema de Agrupamento
Foca especificamente nos mocks das requisições Directus e validação das APIs
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.docx_compare.utils.agrupador_posicional import AgrupadorPosicional


class TestMockAPI:
    """Testa mocks das APIs do Directus para agrupamento"""

    @patch("src.docx_compare.utils.agrupador_posicional.requests")
    def test_mock_buscar_tags_com_posicoes(self, mock_requests):
        """Testa mock da busca de tags com posições válidas"""

        # Dados mock realistas
        mock_response_data = {
            "data": [
                {
                    "id": "tag-1",
                    "tag_nome": "PRAZO_VIGENCIA",
                    "posicao_inicio_texto": 100,
                    "posicao_fim_texto": 200,
                    "clausulas": [{"id": "clausula-1", "nome": "Prazo"}],
                },
                {
                    "id": "tag-2",
                    "tag_nome": "VALOR_CONTRATO",
                    "posicao_inicio_texto": 300,
                    "posicao_fim_texto": 400,
                    "clausulas": [{"id": "clausula-2", "nome": "Valor"}],
                },
            ]
        }

        # Configurar mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_requests.get.return_value = mock_response

        # Executar teste
        agrupador = AgrupadorPosicional()
        resultado = agrupador.buscar_tags_com_posicoes_validas("modelo-test-123")

        # Verificações
        assert len(resultado) == 2
        assert resultado[0]["tag_nome"] == "PRAZO_VIGENCIA"
        assert resultado[1]["tag_nome"] == "VALOR_CONTRATO"

        # Verificar que a requisição foi feita corretamente
        mock_requests.get.assert_called_once()
        call_args = mock_requests.get.call_args
        assert "modelo_contrato_tag" in call_args[0][0]

    @patch("src.docx_compare.utils.agrupador_posicional.requests")
    def test_mock_buscar_modificacoes_sem_clausula(self, mock_requests):
        """Testa mock da busca de modificações sem cláusula"""

        mock_response_data = {
            "data": [
                {
                    "id": "mod-1",
                    "categoria": "modificacao",
                    "conteudo": "texto original",
                    "alteracao": "texto modificado",
                    "posicao_inicio": 150,
                    "posicao_fim": 170,
                },
                {
                    "id": "mod-2",
                    "categoria": "adicao",
                    "conteudo": "",
                    "alteracao": "texto adicionado",
                    "posicao_inicio": 350,
                    "posicao_fim": 375,
                },
            ]
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_requests.get.return_value = mock_response

        agrupador = AgrupadorPosicional()
        resultado = agrupador.buscar_modificacoes_com_posicoes_validas(
            "versao-test-456"
        )

        assert len(resultado) == 2
        assert resultado[0]["categoria"] == "modificacao"
        assert resultado[1]["categoria"] == "adicao"

        # Verificar parâmetros da requisição
        call_args = mock_requests.get.call_args
        params = call_args[1]["params"]
        assert params["filter[clausula][_null]"] == "true"
        assert params["filter[versao][_eq]"] == "versao-test-456"

    @patch("src.docx_compare.utils.agrupador_posicional.requests")
    def test_mock_associacao_modificacao_clausula(self, mock_requests):
        """Testa mock da associação de modificação à cláusula"""

        # Mock para operação de PATCH (associação)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"id": "mod-1", "clausula": "clausula-1"}
        }
        mock_requests.patch.return_value = mock_response

        agrupador = AgrupadorPosicional()
        sucesso = agrupador.associar_modificacao_clausula_api("mod-1", "clausula-1")

        assert sucesso is True

        # Verificar que PATCH foi chamado corretamente
        mock_requests.patch.assert_called_once()
        call_args = mock_requests.patch.call_args

        # Verificar URL
        assert "modificacao/mod-1" in call_args[0][0]

        # Verificar dados enviados
        data_enviada = call_args[1]["json"]
        assert data_enviada["clausula"] == "clausula-1"

    @patch("src.docx_compare.utils.agrupador_posicional.requests")
    def test_mock_erro_api_graceful_handling(self, mock_requests):
        """Testa tratamento gracioso de erros da API"""

        # Simular erro 404
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_requests.get.return_value = mock_response

        agrupador = AgrupadorPosicional()
        resultado = agrupador.buscar_tags_com_posicoes_validas("modelo-inexistente")

        # Deve retornar lista vazia em caso de erro
        assert resultado == []

        # Simular erro de conexão
        mock_requests.get.side_effect = Exception("Connection timeout")

        resultado_erro = agrupador.buscar_modificacoes_com_posicoes_validas(
            "versao-erro"
        )
        assert resultado_erro == []

    def test_dados_estatisticas_agrupamento(self):
        """Testa estrutura das estatísticas retornadas pelo agrupamento"""

        # Simular resultado de agrupamento
        estatisticas_esperadas = {
            "total_modificacoes": 4,
            "associacoes_criadas": 3,
            "associacoes_falharam": 0,
            "sem_correspondencia": 1,
            "detalhes": [
                {
                    "modificacao_id": "mod-1",
                    "tag": "PRAZO_VIGENCIA",
                    "clausula_id": "clausula-1",
                    "status": "sucesso",
                }
            ],
        }

        # Validar estrutura
        assert "total_modificacoes" in estatisticas_esperadas
        assert "associacoes_criadas" in estatisticas_esperadas
        assert "associacoes_falharam" in estatisticas_esperadas
        assert "sem_correspondencia" in estatisticas_esperadas
        assert "detalhes" in estatisticas_esperadas

        # Validar números
        total = estatisticas_esperadas["total_modificacoes"]
        criadas = estatisticas_esperadas["associacoes_criadas"]
        falharam = estatisticas_esperadas["associacoes_falharam"]
        sem_corresp = estatisticas_esperadas["sem_correspondencia"]

        assert total == criadas + falharam + sem_corresp

        # Calcular taxa de sucesso
        taxa_sucesso = (criadas / total * 100) if total > 0 else 0
        assert taxa_sucesso == 75.0  # 3/4 = 75%

    @patch("src.docx_compare.utils.agrupador_posicional.requests")
    def test_mock_fluxo_completo_agrupamento(self, mock_requests):
        """Testa fluxo completo com mocks sequenciais"""

        def mock_get_side_effect(url, **kwargs):
            """Mock que retorna dados diferentes baseado na URL"""
            mock_response = Mock()
            mock_response.status_code = 200

            if "versao/" in url:
                # Mock busca de versão
                mock_response.json.return_value = {
                    "data": {
                        "id": "versao-123",
                        "contrato": {"modelo_contrato": {"id": "modelo-456"}},
                    }
                }
            elif "modelo_contrato_tag" in url:
                # Mock busca de tags
                mock_response.json.return_value = {
                    "data": [
                        {
                            "id": "tag-1",
                            "tag_nome": "PRAZO",
                            "posicao_inicio_texto": 100,
                            "posicao_fim_texto": 200,
                            "clausulas": [{"id": "clausula-1"}],
                        }
                    ]
                }
            elif "modificacao" in url:
                # Mock busca de modificações
                mock_response.json.return_value = {
                    "data": [
                        {
                            "id": "mod-1",
                            "categoria": "modificacao",
                            "conteudo": "texto teste",
                            "alteracao": "texto alterado",
                            "posicao_inicio": 150,
                            "posicao_fim": 170,
                        }
                    ]
                }

            return mock_response

        def mock_patch_side_effect(url, **kwargs):
            """Mock para operações PATCH"""
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": {}}
            return mock_response

        # Configurar mocks
        mock_requests.get.side_effect = mock_get_side_effect
        mock_requests.patch.side_effect = mock_patch_side_effect

        # Executar agrupamento completo
        agrupador = AgrupadorPosicional()
        resultado = agrupador.processar_agrupamento_posicional(
            versao_id="versao-123", dry_run=False
        )

        # Verificar resultado
        assert "total_modificacoes" in resultado
        assert resultado["total_modificacoes"] == 1
        assert resultado["associacoes_criadas"] == 1

        # Verificar que as chamadas corretas foram feitas
        assert mock_requests.get.call_count >= 3  # versão + tags + modificações
        assert mock_requests.patch.call_count >= 1  # pelo menos uma associação


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
