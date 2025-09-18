#!/usr/bin/env python3
"""
Testes para o AgrupadorPosicional
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.docx_compare.utils.agrupador_posicional import AgrupadorPosicional


class TestAgrupadorPosicional:
    """Testes básicos para o agrupador baseado em posições."""

    def setup_method(self):
        """Setup para cada teste."""
        self.agrupador = AgrupadorPosicional()

    def test_associar_modificacao_a_tag_posicao_exata(self):
        """Testa se modificação dentro da tag é detectada corretamente."""
        tags = [
            {"posicao_inicio_texto": 100, "posicao_fim_texto": 200, "tag_nome": "PRAZO"}
        ]

        # Modificação dentro do intervalo
        modificacao = {"posicao_inicio_numero": 150, "posicao_fim_numero": 150}
        result = self.agrupador.associar_modificacao_a_tag(modificacao, tags)
        assert result is not None
        assert result["tag_nome"] == "PRAZO"

        # Modificação no início exato
        modificacao = {"posicao_inicio_numero": 100, "posicao_fim_numero": 100}
        result = self.agrupador.associar_modificacao_a_tag(modificacao, tags)
        assert result is not None

        # Modificação no final exato
        modificacao = {"posicao_inicio_numero": 200, "posicao_fim_numero": 200}
        result = self.agrupador.associar_modificacao_a_tag(modificacao, tags)
        assert result is not None

    def test_modificacao_fora_da_tag(self):
        """Testa se modificação fora da tag é rejeitada."""
        tags = [
            {"posicao_inicio_texto": 100, "posicao_fim_texto": 200, "tag_nome": "PRAZO"}
        ]

        # Modificação antes da tag
        modificacao = {"posicao_inicio_numero": 50, "posicao_fim_numero": 50}
        result = self.agrupador.associar_modificacao_a_tag(modificacao, tags)
        assert result is None

        # Modificação depois da tag
        modificacao = {"posicao_inicio_numero": 250, "posicao_fim_numero": 250}
        result = self.agrupador.associar_modificacao_a_tag(modificacao, tags)
        assert result is None

    def test_associar_modificacao_clausula_sucesso(self):
        """Testa associação bem-sucedida de modificação à cláusula."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"id": "mod1"}}

        with patch(
            "src.docx_compare.utils.agrupador_posicional.requests.patch"
        ) as mock_patch:
            mock_patch.return_value = mock_response
            resultado = self.agrupador.associar_modificacao_clausula_api(
                "mod1", "clausula1"
            )
            assert resultado

    def test_associar_modificacao_clausula_erro(self):
        """Testa tratamento de erro na associação."""
        mock_response = Mock()
        mock_response.status_code = 400

        with patch(
            "src.docx_compare.utils.agrupador_posicional.requests.patch"
        ) as mock_patch:
            mock_patch.return_value = mock_response
            resultado = self.agrupador.associar_modificacao_clausula_api(
                "mod1", "clausula1"
            )
            assert not resultado


class TestIntegracaoAgrupadorPosicional:
    """Testes de integração do agrupador posicional."""

    def setup_method(self):
        """Setup para cada teste."""
        self.agrupador = AgrupadorPosicional()

    @patch.object(AgrupadorPosicional, "buscar_tags_com_posicoes_validas")
    @patch.object(AgrupadorPosicional, "buscar_modificacoes_com_posicoes_validas")
    @patch.object(AgrupadorPosicional, "associar_modificacao_clausula_api")
    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_processar_agrupamento_posicional_sucesso(
        self, mock_get, mock_associar, mock_buscar_mods, mock_buscar_tags
    ):
        """Testa processamento completo de agrupamento posicional."""
        # Mock busca da versão
        mock_response_versao = Mock()
        mock_response_versao.status_code = 200
        mock_response_versao.json.return_value = {
            "data": {"contrato": {"modelo_contrato": {"id": "modelo1"}}}
        }
        mock_get.return_value = mock_response_versao

        # Mock dados de tags
        mock_buscar_tags.return_value = [
            {
                "id": "tag1",
                "tag_nome": "PRAZO",
                "posicao_inicio_texto": 100,
                "posicao_fim_texto": 200,
                "clausulas": [{"id": "clausula1"}],
            }
        ]

        # Mock dados de modificações
        mock_buscar_mods.return_value = [
            {
                "id": "mod1",
                "posicao_inicio_numero": 150,
                "posicao_fim_numero": 170,
                "conteudo": "texto modificado",
            }
        ]

        # Mock associação bem-sucedida
        mock_associar.return_value = True

        resultado = self.agrupador.processar_agrupamento_posicional(
            versao_id="v1", dry_run=True
        )

        assert resultado["associacoes_criadas"] == 1
        assert resultado["total_modificacoes"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
