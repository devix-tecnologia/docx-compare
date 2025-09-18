#!/usr/bin/env python3
"""
Teste de Dados de Agrupamento
Valida os dados e estruturas utilizadas nos testes de processamento
"""

import os
import sys

import pytest

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from src.docx_compare.utils.agrupador_posicional import AgrupadorPosicional


class TestDadosAgrupamento:
    """Testa a estrutura de dados utilizada no agrupamento"""

    def test_dados_mock_estrutura_valida(self):
        """Valida se os dados mock têm a estrutura esperada"""

        # Dados de exemplo como os usados no sistema real
        tag_exemplo = {
            "id": "tag-test-1",
            "tag_nome": "PRAZO_VIGENCIA",
            "posicao_inicio_texto": 100,
            "posicao_fim_texto": 200,
            "clausulas": [{"id": "clausula-1", "nome": "Prazo de Vigência"}],
        }

        modificacao_exemplo = {
            "id": "mod-test-1",
            "categoria": "modificacao",
            "conteudo": "texto original",
            "alteracao": "texto modificado",
            "posicao_inicio": 150,
            "posicao_fim": 170,
            "clausula": None,
        }

        # Validar estrutura da tag
        assert "id" in tag_exemplo
        assert "tag_nome" in tag_exemplo
        assert "posicao_inicio_texto" in tag_exemplo
        assert "posicao_fim_texto" in tag_exemplo
        assert "clausulas" in tag_exemplo
        assert len(tag_exemplo["clausulas"]) > 0

        # Validar estrutura da modificação
        assert "id" in modificacao_exemplo
        assert "categoria" in modificacao_exemplo
        assert "posicao_inicio" in modificacao_exemplo
        assert "posicao_fim" in modificacao_exemplo
        assert (
            modificacao_exemplo["posicao_inicio"] < modificacao_exemplo["posicao_fim"]
        )

    def test_associacao_logica_simples(self):
        """Testa a lógica básica de associação sem mocks"""

        agrupador = AgrupadorPosicional()

        # Cenários de teste realistas
        cenarios = [
            {
                "nome": "Modificação dentro da tag",
                "modificacao": {
                    "posicao_inicio_numero": 150,
                    "posicao_fim_numero": 170,
                },
                "tag": {
                    "tag_nome": "PRAZO",
                    "posicao_inicio_texto": 100,
                    "posicao_fim_texto": 200,
                    "clausulas": [{"id": "clausula-1"}],
                },
                "deve_associar": True,
            },
            {
                "nome": "Modificação sobreposta",
                "modificacao": {
                    "posicao_inicio_numero": 180,
                    "posicao_fim_numero": 220,
                },
                "tag": {
                    "tag_nome": "PRAZO",
                    "posicao_inicio_texto": 100,
                    "posicao_fim_texto": 200,
                    "clausulas": [{"id": "clausula-1"}],
                },
                "deve_associar": True,  # Com threshold 0%, deve associar
            },
            {
                "nome": "Modificação fora da tag",
                "modificacao": {
                    "posicao_inicio_numero": 300,
                    "posicao_fim_numero": 320,
                },
                "tag": {
                    "tag_nome": "PRAZO",
                    "posicao_inicio_texto": 100,
                    "posicao_fim_texto": 200,
                    "clausulas": [{"id": "clausula-1"}],
                },
                "deve_associar": False,
            },
        ]

        for cenario in cenarios:
            resultado = agrupador.associar_modificacao_a_tag(
                cenario["modificacao"], [cenario["tag"]]
            )

            if cenario["deve_associar"]:
                assert resultado is not None, f"Falhou: {cenario['nome']}"
                assert resultado["tag_nome"] == cenario["tag"]["tag_nome"]
            else:
                assert resultado is None, f"Falhou: {cenario['nome']}"

    def test_cenarios_edge_cases(self):
        """Testa casos extremos de posicionamento"""

        agrupador = AgrupadorPosicional()

        # Caso 1: Modificação exatamente nos limites da tag
        mod_limite = {"posicao_inicio_numero": 100, "posicao_fim_numero": 200}
        tag_limite = {
            "tag_nome": "EXATO",
            "posicao_inicio_texto": 100,
            "posicao_fim_texto": 200,
            "clausulas": [{"id": "clausula-1"}],
        }

        resultado_limite = agrupador.associar_modificacao_a_tag(
            mod_limite, [tag_limite]
        )
        assert resultado_limite is not None  # Deve associar limites exatos

        # Caso 2: Modificação de tamanho zero (posição pontual)
        mod_pontual = {"posicao_inicio_numero": 150, "posicao_fim_numero": 150}

        resultado_pontual = agrupador.associar_modificacao_a_tag(
            mod_pontual, [tag_limite]
        )
        assert (
            resultado_pontual is not None
        )  # Deve associar posição pontual dentro da tag

        # Caso 3: Tag de tamanho zero
        tag_pontual = {
            "tag_nome": "PONTUAL",
            "posicao_inicio_texto": 150,
            "posicao_fim_texto": 150,
            "clausulas": [{"id": "clausula-1"}],
        }

        resultado_tag_pontual = agrupador.associar_modificacao_a_tag(
            mod_pontual, [tag_pontual]
        )
        assert resultado_tag_pontual is not None  # Posições idênticas devem associar

    def test_escolha_melhor_tag_multiplas_opcoes(self):
        """Testa seleção da melhor tag quando há múltiplas opções"""

        agrupador = AgrupadorPosicional()

        # Modificação que sobrepõe com duas tags
        modificacao = {"posicao_inicio_numero": 190, "posicao_fim_numero": 210}

        tags = [
            {
                "tag_nome": "TAG_A",
                "posicao_inicio_texto": 100,
                "posicao_fim_texto": 200,  # Sobreposição: 190-200 = 10 chars
                "clausulas": [{"id": "clausula-a"}],
            },
            {
                "tag_nome": "TAG_B",
                "posicao_inicio_texto": 200,
                "posicao_fim_texto": 300,  # Sobreposição: 200-210 = 10 chars
                "clausulas": [{"id": "clausula-b"}],
            },
            {
                "tag_nome": "TAG_C",
                "posicao_inicio_texto": 180,
                "posicao_fim_texto": 220,  # Sobreposição: 190-210 = 20 chars (melhor)
                "clausulas": [{"id": "clausula-c"}],
            },
        ]

        resultado = agrupador.associar_modificacao_a_tag(modificacao, tags)

        # Deve escolher TAG_C por ter maior sobreposição
        assert resultado is not None
        assert resultado["tag_nome"] == "TAG_C"

    def test_calculo_sobreposicao_precisao(self):
        """Testa precisão dos cálculos de sobreposição"""

        agrupador = AgrupadorPosicional()

        # Teste com valores conhecidos
        casos_teste = [
            {
                "intervalo1": (0, 100),
                "intervalo2": (50, 150),
                "sobreposicao_esperada": 50 / 150,  # 50 chars sobrepostos / 150 total
                "descricao": "Sobreposição de 50%",
            },
            {
                "intervalo1": (100, 200),
                "intervalo2": (100, 200),
                "sobreposicao_esperada": 1.0,  # 100% idênticos
                "descricao": "Intervalos idênticos",
            },
            {
                "intervalo1": (100, 200),
                "intervalo2": (300, 400),
                "sobreposicao_esperada": 0.0,  # Sem sobreposição
                "descricao": "Sem sobreposição",
            },
            {
                "intervalo1": (100, 200),
                "intervalo2": (150, 175),
                "sobreposicao_esperada": 25 / 100,  # 25 chars sobrepostos / 100 total
                "descricao": "Contenção completa",
            },
        ]

        for caso in casos_teste:
            resultado = agrupador.calcular_sobreposicao(
                caso["intervalo1"], caso["intervalo2"]
            )

            assert abs(resultado - caso["sobreposicao_esperada"]) < 0.001, (
                f"Falhou: {caso['descricao']} - Esperado: {caso['sobreposicao_esperada']}, Obtido: {resultado}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
