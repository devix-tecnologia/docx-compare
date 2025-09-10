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

    def test_modificacao_esta_dentro_da_tag_posicao_exata(self):
        """Testa se modificação dentro da tag é detectada corretamente."""
        tag_info = {"posicao_inicio_texto": 100, "posicao_fim_texto": 200}

        # Modificação dentro do intervalo
        modificacao = {"posicao_inicio": 150, "posicao_fim": 150}
        assert self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

        # Modificação no início exato
        modificacao = {"posicao_inicio": 100, "posicao_fim": 100}
        assert self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

        # Modificação no final exato
        modificacao = {"posicao_inicio": 200, "posicao_fim": 200}
        assert self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

    def test_modificacao_fora_da_tag(self):
        """Testa se modificação fora da tag é rejeitada."""
        tag_info = {"posicao_inicio_texto": 100, "posicao_fim_texto": 200}

        # Modificação antes da tag
        modificacao = {"posicao_inicio": 50, "posicao_fim": 50}
        assert not self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

        # Modificação depois da tag
        modificacao = {"posicao_inicio": 250, "posicao_fim": 250}
        assert not self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

    def test_associar_modificacao_tag_sucesso(self):
        """Testa associação bem-sucedida de modificação à tag."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"id": "mod1"}}

        with patch(
            "src.docx_compare.utils.agrupador_posicional.requests.patch"
        ) as mock_patch:
            mock_patch.return_value = mock_response
            resultado = self.agrupador.associar_modificacao_tag("mod1", "tag1")
            assert resultado

    def test_associar_modificacao_tag_erro(self):
        """Testa tratamento de erro na associação."""
        mock_response = Mock()
        mock_response.status_code = 400

        with patch(
            "src.docx_compare.utils.agrupador_posicional.requests.patch"
        ) as mock_patch:
            mock_patch.return_value = mock_response
            resultado = self.agrupador.associar_modificacao_tag("mod1", "tag1")
            assert not resultado


class TestIntegracaoAgrupadorPosicional:
    """Testes de integração do agrupador posicional."""

    def setup_method(self):
        """Setup para cada teste."""
        self.agrupador = AgrupadorPosicional()

    @patch.object(AgrupadorPosicional, "buscar_tags_com_posicoes")
    @patch.object(AgrupadorPosicional, "buscar_modificacoes_com_posicoes")
    @patch.object(AgrupadorPosicional, "associar_modificacao_tag")
    def test_processar_agrupamento_posicional_sucesso(
        self, mock_associar, mock_buscar_mods, mock_buscar_tags
    ):
        """Testa processamento completo de agrupamento posicional."""
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
                "posicao_inicio": 150,
                "posicao_fim": 170,
                "categoria": "modificacao",
            }
        ]

        # Mock associação bem-sucedida
        mock_associar.return_value = True

        resultado = self.agrupador.processar_agrupamento_posicional(
            versao_id="v1", modelo_id="m1"
        )

        assert resultado["sucesso"]
        assert resultado["estatisticas"]["associacoes_criadas"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
