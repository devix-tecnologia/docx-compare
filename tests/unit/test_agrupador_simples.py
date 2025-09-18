#!/usr/bin/env python3
"""
Teste Simples do AgrupadorPosicional
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.docx_compare.utils.agrupador_posicional import AgrupadorPosicional


class TestAgrupadorPosicionalBasico:
    """Testes básicos do agrupador posicional."""

    def setup_method(self):
        """Setup para cada teste."""
        self.agrupador = AgrupadorPosicional()

    def test_extrair_posicao_numerica(self):
        """Testa extração de posição de caminhos estruturais."""
        # Caso com posição válida
        resultado = self.agrupador.extrair_posicao_numerica("blocks[5].c[10].c")
        assert resultado is not None
        assert isinstance(resultado, int)

        # Caso sem posição
        resultado = self.agrupador.extrair_posicao_numerica("")
        assert resultado is None

    def test_calcular_sobreposicao(self):
        """Testa cálculo de sobreposição entre intervalos."""
        # Intervalos com sobreposição
        intervalo1 = (100, 200)
        intervalo2 = (150, 250)
        sobreposicao = self.agrupador.calcular_sobreposicao(intervalo1, intervalo2)
        assert sobreposicao > 0

        # Intervalos sem sobreposição
        intervalo1 = (100, 200)
        intervalo2 = (300, 400)
        sobreposicao = self.agrupador.calcular_sobreposicao(intervalo1, intervalo2)
        assert sobreposicao == 0

    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_buscar_tags_com_posicoes_validas(self, mock_get):
        """Testa busca de tags com posições válidas."""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "tag1",
                    "tag_nome": "PRAZO_VIGENCIA",
                    "posicao_inicio_texto": 100,
                    "posicao_fim_texto": 200,
                    "clausulas": [{"id": "clausula1"}],
                }
            ]
        }
        mock_get.return_value = mock_response

        resultado = self.agrupador.buscar_tags_com_posicoes_validas("modelo123")

        assert len(resultado) == 1
        assert resultado[0]["tag_nome"] == "PRAZO_VIGENCIA"
        assert resultado[0]["posicao_inicio_texto"] == 100

    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_buscar_modificacoes_com_posicoes_validas(self, mock_get):
        """Testa busca de modificações com posições válidas."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "mod1",
                    "categoria": "modificacao",
                    "conteudo": "texto original",
                    "alteracao": "texto modificado",
                    "posicao_inicio": 150,
                    "posicao_fim": 170,
                }
            ]
        }
        mock_get.return_value = mock_response

        resultado = self.agrupador.buscar_modificacoes_com_posicoes_validas("versao123")

        assert len(resultado) == 1
        assert resultado[0]["categoria"] == "modificacao"
        assert resultado[0]["posicao_inicio_numero"] == 150

    @patch("src.docx_compare.utils.agrupador_posicional.requests.patch")
    def test_associar_modificacao_clausula_api_sucesso(self, mock_patch):
        """Testa associação bem-sucedida via API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"id": "mod1"}}
        mock_patch.return_value = mock_response

        resultado = self.agrupador.associar_modificacao_clausula_api(
            "mod1", "clausula1"
        )
        assert resultado is True

    @patch("src.docx_compare.utils.agrupador_posicional.requests.patch")
    def test_associar_modificacao_clausula_api_erro(self, mock_patch):
        """Testa tratamento de erro na associação via API."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_patch.return_value = mock_response

        resultado = self.agrupador.associar_modificacao_clausula_api(
            "mod1", "clausula1"
        )
        assert resultado is False

    def test_associar_modificacao_a_tag_logic(self):
        """Testa lógica de associação de modificação a tag."""
        # Dados de teste
        modificacao = {
            "id": "mod1",
            "posicao_inicio_numero": 150,
            "posicao_fim_numero": 170,
            "categoria": "modificacao",
        }

        tags = [
            {
                "id": "tag1",
                "tag_nome": "PRAZO",
                "posicao_inicio_texto": 100,
                "posicao_fim_texto": 200,
                "clausulas": [{"id": "clausula1"}],
            },
            {
                "id": "tag2",
                "tag_nome": "VALOR",
                "posicao_inicio_texto": 300,
                "posicao_fim_texto": 400,
                "clausulas": [{"id": "clausula2"}],
            },
        ]

        resultado = self.agrupador.associar_modificacao_a_tag(modificacao, tags)

        # A modificação deve ser associada à primeira tag (PRAZO)
        # pois está dentro do intervalo 100-200
        assert resultado is not None
        assert "id" in resultado
        assert resultado["id"] == "tag1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
