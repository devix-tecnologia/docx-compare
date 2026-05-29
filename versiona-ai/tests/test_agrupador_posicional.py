"""
Testes para AgrupadorPosicional

Seguindo TDD: escrever testes antes da implementação
"""

import pytest

from agrupador_posicional import AgrupadorPosicional


class TestExtrairPosicaoNumerica:
    """Testes para extração de posição numérica de caminhos"""

    def test_caminho_simples_com_um_indice(self):
        """Deve extrair posição de caminho com um índice"""
        agrupador = AgrupadorPosicional()
        resultado = agrupador.extrair_posicao_numerica("blocks[5].c")

        assert resultado == 5

    def test_caminho_aninhado_com_multiplos_indices(self):
        """Deve calcular posição de caminho aninhado"""

        agrupador = AgrupadorPosicional()
        resultado = agrupador.extrair_posicao_numerica("blocks[2].c[3].c")

        # 2 * 1000 + 3 = 2003
        assert resultado == 2003

    def test_caminho_vazio_retorna_none(self):
        """Deve retornar None para caminho vazio"""

        agrupador = AgrupadorPosicional()
        resultado = agrupador.extrair_posicao_numerica("")

        assert resultado is None

    def test_caminho_sem_numeros_retorna_zero(self):
        """Deve retornar 0 para caminho sem números"""

        agrupador = AgrupadorPosicional()
        resultado = agrupador.extrair_posicao_numerica("blocks.content")

        assert resultado == 0

    def test_caminho_com_padrao_pos_numero(self):
        """Deve extrair posição do padrão pos_123"""

        agrupador = AgrupadorPosicional()
        resultado = agrupador.extrair_posicao_numerica("pos_150")

        assert resultado == 150


class TestEncontrarTagMaisProxima:
    """Testes para encontrar tag mais próxima de um bloco"""

    def test_bloco_sem_overlap_retorna_none(self):
        """Deve retornar None quando bloco não tem overlap com nenhuma tag"""

        agrupador = AgrupadorPosicional()
        tags = [
            {"id": "tag1", "posicao_inicio_texto": 0, "posicao_fim_texto": 100},
            {"id": "tag2", "posicao_inicio_texto": 500, "posicao_fim_texto": 600},
        ]

        resultado = agrupador._encontrar_tag_mais_proxima(
            pos_inicio=200, pos_fim=300, tags_modelo=tags
        )

        assert resultado is None

    def test_bloco_com_overlap_retorna_tag_correta(self):
        """Deve retornar tag com maior overlap"""

        agrupador = AgrupadorPosicional()
        tags = [
            {
                "id": "tag1",
                "tag_nome": "Tag 1",
                "posicao_inicio_texto": 0,
                "posicao_fim_texto": 150,
            },  # overlap de 50
            {
                "id": "tag2",
                "tag_nome": "Tag 2",
                "posicao_inicio_texto": 100,
                "posicao_fim_texto": 300,
            },  # overlap de 100
        ]

        resultado = agrupador._encontrar_tag_mais_proxima(
            pos_inicio=100, pos_fim=200, tags_modelo=tags
        )

        assert resultado is not None
        assert resultado["id"] == "tag2"
        assert resultado["tag_nome"] == "Tag 2"

    def test_ignora_tags_sem_posicao(self):
        """Deve ignorar tags que não têm posições definidas"""

        agrupador = AgrupadorPosicional()
        tags = [
            {"id": "tag1", "posicao_inicio_texto": None, "posicao_fim_texto": 100},
            {
                "id": "tag2",
                "tag_nome": "Tag 2",
                "posicao_inicio_texto": 100,
                "posicao_fim_texto": 200,
            },
        ]

        resultado = agrupador._encontrar_tag_mais_proxima(
            pos_inicio=100, pos_fim=150, tags_modelo=tags
        )

        assert resultado is not None
        assert resultado["id"] == "tag2"


class TestProcessarAgrupamentoPosicional:
    """Testes para agrupamento posicional de modificações"""

    def test_agrupa_modificacoes_proximas(self):
        """Deve agrupar modificações próximas no mesmo bloco"""

        agrupador = AgrupadorPosicional()

        modificacoes = [
            {"id": "mod1", "posicao_inicio": 100, "posicao_fim": 150},
            {"id": "mod2", "posicao_inicio": 200, "posicao_fim": 250},  # Próxima
            {"id": "mod3", "posicao_inicio": 5000, "posicao_fim": 5100},  # Distante
        ]

        # Mock buscar_dados_versao e buscar_tags_modelo
        def mock_buscar_dados_versao(versao_id):
            return {
                "versao_id": versao_id,
                "modelo_id": "modelo1",
                "arquivo_com_tags_id": "arquivo1",
                "arquivo_modificado_id": "arquivo2",
            }

        def mock_buscar_tags_modelo(modelo_id):
            return []

        agrupador.buscar_dados_versao = mock_buscar_dados_versao
        agrupador.buscar_tags_modelo = mock_buscar_tags_modelo

        resultado = agrupador.processar_agrupamento_posicional_versao(
            versao_id="teste", modificacoes=modificacoes
        )

        assert "erro" not in resultado
        assert resultado["total_blocos"] == 2  # 2 blocos: próximas + distante
        assert resultado["total_modificacoes"] == 3

    def test_bloco_unico_para_modificacoes_muito_proximas(self):
        """Deve criar um único bloco para modificações muito próximas"""

        agrupador = AgrupadorPosicional()

        modificacoes = [
            {"id": "mod1", "posicao_inicio": 100, "posicao_fim": 150},
            {"id": "mod2", "posicao_inicio": 160, "posicao_fim": 200},
            {"id": "mod3", "posicao_inicio": 210, "posicao_fim": 250},
        ]

        def mock_buscar_dados_versao(versao_id):
            return {
                "versao_id": versao_id,
                "modelo_id": "modelo1",
                "arquivo_com_tags_id": "arquivo1",
                "arquivo_modificado_id": "arquivo2",
            }

        def mock_buscar_tags_modelo(modelo_id):
            return []

        agrupador.buscar_dados_versao = mock_buscar_dados_versao
        agrupador.buscar_tags_modelo = mock_buscar_tags_modelo

        resultado = agrupador.processar_agrupamento_posicional_versao(
            versao_id="teste", modificacoes=modificacoes
        )

        assert resultado["total_blocos"] == 1  # Todas no mesmo bloco
        assert resultado["blocos"][0]["total_modificacoes"] == 3

    def test_retorna_erro_quando_versao_nao_encontrada(self):
        """Deve retornar erro quando versão não existe"""

        agrupador = AgrupadorPosicional()

        def mock_buscar_dados_versao(versao_id):
            return None

        agrupador.buscar_dados_versao = mock_buscar_dados_versao

        resultado = agrupador.processar_agrupamento_posicional_versao(
            versao_id="inexistente", modificacoes=[]
        )

        assert "erro" in resultado
        assert "não encontrados" in resultado["erro"]

    def test_enriquece_blocos_com_tags_quando_disponivel(self):
        """Deve enriquecer blocos com informações de tags quando há overlap"""

        agrupador = AgrupadorPosicional()

        modificacoes = [{"id": "mod1", "posicao_inicio": 100, "posicao_fim": 150}]

        def mock_buscar_dados_versao(versao_id):
            return {
                "versao_id": versao_id,
                "modelo_id": "modelo1",
                "arquivo_com_tags_id": "arquivo1",
                "arquivo_modificado_id": "arquivo2",
            }

        def mock_buscar_tags_modelo(modelo_id):
            return [
                {
                    "id": "tag1",
                    "tag_nome": "Cláusula 1.1",
                    "posicao_inicio_texto": 50,
                    "posicao_fim_texto": 200,
                    "conteudo": "Conteúdo da cláusula",
                }
            ]

        def mock_buscar_clausula_por_tag(tag_id):
            return {
                "id": "clausula1",
                "numero": "1.1",
                "nome": "Objeto do Contrato",
                "objetivo": "Definir objeto",
                "referencias": ["Lei 123", "Lei 456"],
            }

        agrupador.buscar_dados_versao = mock_buscar_dados_versao
        agrupador.buscar_tags_modelo = mock_buscar_tags_modelo
        agrupador.buscar_clausula_por_tag = mock_buscar_clausula_por_tag

        resultado = agrupador.processar_agrupamento_posicional_versao(
            versao_id="teste", modificacoes=modificacoes
        )

        assert resultado["total_blocos"] == 1
        bloco = resultado["blocos"][0]
        assert bloco["nome"] == "Cláusula 1.1"
        assert bloco["clausula_id"] == "tag1"

        # Verificar que modificações foram enriquecidas
        mod = bloco["modificacoes"][0]
        assert mod["clausula_nome"] == "Objeto do Contrato"  # Nome da cláusula
        assert mod["clausula_numero"] == "1.1"
        assert mod["clausula_objetivo"] == "Definir objeto"
        assert mod["clausula_referencias"] == ["Lei 123", "Lei 456"]


class TestCalcularSobreposicao:
    """Testes para cálculo de sobreposição entre intervalos"""

    def test_intervalos_sem_sobreposicao_retorna_zero(self):
        """Deve retornar 0 para intervalos sem sobreposição"""

        agrupador = AgrupadorPosicional()
        resultado = agrupador.calcular_sobreposicao(
            intervalo1=(0, 100), intervalo2=(200, 300)
        )

        assert resultado == 0

    def test_intervalos_com_sobreposicao_parcial(self):
        """Deve calcular sobreposição parcial corretamente"""

        agrupador = AgrupadorPosicional()
        resultado = agrupador.calcular_sobreposicao(
            intervalo1=(0, 100), intervalo2=(50, 150)
        )

        # Overlap de 50 (50-100) sobre total de 150 (0-150)
        assert resultado == pytest.approx(50 / 150)

    def test_intervalos_com_sobreposicao_total(self):
        """Deve retornar 1 para intervalos idênticos"""

        agrupador = AgrupadorPosicional()
        resultado = agrupador.calcular_sobreposicao(
            intervalo1=(100, 200), intervalo2=(100, 200)
        )

        assert resultado == 1.0

    def test_intervalo_contido_no_outro(self):
        """Deve calcular sobreposição quando um intervalo contém o outro"""

        agrupador = AgrupadorPosicional()
        resultado = agrupador.calcular_sobreposicao(
            intervalo1=(0, 200), intervalo2=(50, 100)
        )

        # Overlap de 50 (50-100) sobre total de 200 (0-200)
        assert resultado == pytest.approx(50 / 200)
