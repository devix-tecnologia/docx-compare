"""
Testes unitários básicos para o Agrupador Posicional.
"""

from src.docx_compare.utils.agrupador_posicional import AgrupadorPosicional


class TestAgrupadorPosicional:
    """Testes básicos para o agrupador baseado em posições."""

    def setup_method(self):
        """Configuração para cada teste."""
        self.agrupador = AgrupadorPosicional()

    def test_extrair_posicao_numerica_valida(self):
        """Testa extração de posição numérica de caminhos válidos."""
        assert (
            self.agrupador.extrair_posicao_numerica("modificacao_1_linha_5_pos_100")
            == 100
        )
        assert (
            self.agrupador.extrair_posicao_numerica("adicao_3_linha_10_pos_250") == 250
        )
        assert self.agrupador.extrair_posicao_numerica("remocao_2_linha_7_pos_0") == 0

    def test_extrair_posicao_numerica_invalida(self):
        """Testa extração de posição com caminhos inválidos."""
        assert self.agrupador.extrair_posicao_numerica("sem_pos_no_path") is None
        assert self.agrupador.extrair_posicao_numerica("pos_string_texto") is None
        assert self.agrupador.extrair_posicao_numerica("") is None

    def test_modificacao_esta_dentro_da_tag(self):
        """Testa detecção de overlap entre modificação e tag."""
        tag_info = {"posicao_inicio": 100, "posicao_fim": 200}

        # Modificação dentro da tag
        modificacao = {"posicao_inicio": 150, "posicao_fim": 150}
        assert self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

        # Modificação fora da tag
        modificacao = {"posicao_inicio": 50, "posicao_fim": 50}
        assert not self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

    def test_agrupador_instanciado(self):
        """Verifica que o agrupador pode ser instanciado."""
        assert self.agrupador is not None
        assert hasattr(self.agrupador, "extrair_posicao_numerica")
        assert hasattr(self.agrupador, "modificacao_esta_dentro_da_tag")
        assert hasattr(self.agrupador, "processar_agrupamento_posicional")


from unittest.mock import MagicMock, patch


class TestAgrupadorPosicional:
    """Testes para o agrupador baseado em posições."""

    def setup_method(self):
        """Configuração para cada teste."""
        self.agrupador = AgrupadorPosicional()

    def test_extrair_posicao_numerica_valida(self):
        """Testa extração de posição numérica de caminhos válidos."""
        # Casos válidos
        assert (
            self.agrupador.extrair_posicao_numerica("modificacao_1_linha_5_pos_100")
            == 100
        )
        assert (
            self.agrupador.extrair_posicao_numerica("adicao_3_linha_10_pos_250") == 250
        )
        assert self.agrupador.extrair_posicao_numerica("remocao_2_linha_7_pos_0") == 0

    def test_extrair_posicao_numerica_invalida(self):
        """Testa extração de posição com caminhos inválidos."""
        # Casos inválidos retornam None
        assert self.agrupador.extrair_posicao_numerica("sem_pos_no_path") is None
        assert self.agrupador.extrair_posicao_numerica("pos_string_texto") is None
        assert self.agrupador.extrair_posicao_numerica("") is None
        assert self.agrupador.extrair_posicao_numerica("pos_") is None

    def test_modificacao_esta_dentro_da_tag_overlap(self):
        """Testa detecção de overlap entre modificação e tag."""
        # Tag cobrindo posições 100-200
        tag_info = {"posicao_inicio": 100, "posicao_fim": 200}

        # Modificação dentro da tag
        modificacao = {"posicao_inicio": 150, "posicao_fim": 150}
        assert self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

        # Modificação no início exato
        modificacao = {"posicao_inicio": 100, "posicao_fim": 100}
        assert self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

        # Modificação no final exato
        modificacao = {"posicao_inicio": 200, "posicao_fim": 200}
        assert self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

        # Modificação fora da tag (antes)
        modificacao = {"posicao_inicio": 50, "posicao_fim": 50}
        assert not self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

        # Modificação fora da tag (depois)
        modificacao = {"posicao_inicio": 250, "posicao_fim": 250}
        assert not self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)

    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_buscar_tags_com_posicoes_sucesso(self, mock_get):
        """Testa busca de tags com sucesso."""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "tag1",
                    "tag_nome": "clausula1",
                    "caminho_tag_inicio": "modificacao_1_linha_5_pos_100",
                    "caminho_tag_fim": "modificacao_1_linha_5_pos_200",
                },
                {
                    "id": "tag2",
                    "tag_nome": "clausula2",
                    "caminho_tag_inicio": "modificacao_1_linha_8_pos_300",
                    "caminho_tag_fim": "modificacao_1_linha_8_pos_400",
                },
            ]
        }
        mock_get.return_value = mock_response

        resultado = self.agrupador.buscar_tags_com_posicoes("modelo123")

        assert len(resultado) == 2
        assert resultado[0]["tag_nome"] == "clausula1"
        assert resultado[0]["posicao_inicio"] == 100
        assert resultado[0]["posicao_fim"] == 200

    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_buscar_modificacoes_com_posicoes_sucesso(self, mock_get):
        """Testa busca de modificações com sucesso."""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "mod1",
                    "categoria": "adicao",
                    "conteudo": "Texto adicionado",
                    "caminho_inicio": "modificacao_1_linha_5_pos_150",
                    "caminho_fim": "modificacao_1_linha_5_pos_180",
                },
                {
                    "id": "mod2",
                    "categoria": "remocao",
                    "conteudo": "Texto removido",
                    "caminho_inicio": "modificacao_2_linha_8_pos_350",
                    "caminho_fim": "modificacao_2_linha_8_pos_370",
                },
            ]
        }
        mock_get.return_value = mock_response

        resultado = self.agrupador.buscar_modificacoes_com_posicoes("versao123")

        assert len(resultado) == 2
        assert resultado[0]["posicao_inicio"] == 150
        assert resultado[0]["posicao_fim"] == 180
        assert resultado[1]["posicao_inicio"] == 350
        assert resultado[1]["posicao_fim"] == 370

    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_processar_agrupamento_erro_versao(self, mock_get):
        """Testa processamento com erro na busca da versão."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        resultado = self.agrupador.processar_agrupamento_posicional("versao123")

        assert "erro" in resultado
        assert resultado["erro"] == "Versão não encontrada"

    def test_performance_posicional(self):
        """Testa performance do algoritmo posicional."""
        agrupador = AgrupadorPosicional()

        # Simulação de muitas modificações
        modificacoes = []
        for i in range(1000):
            modificacoes.append({"posicao_inicio": i * 10, "posicao_fim": i * 10 + 5})

        # Simulação de muitas tags
        tags = []
        for i in range(100):
            tags.append({"posicao_inicio": i * 100, "posicao_fim": i * 100 + 50})

        # Testa eficiência do algoritmo
        import time

        start = time.time()

        associacoes_encontradas = 0
        for modificacao in modificacoes:
            for tag in tags:
                if agrupador.modificacao_esta_dentro_da_tag(modificacao, tag):
                    associacoes_encontradas += 1
                    break

        end = time.time()

        # Deve processar rapidamente (menos de 1 segundo)
        assert end - start < 1.0
        assert associacoes_encontradas > 0


class TestIntegracaoAgrupadorPosicional:
    """Testes de integração do agrupador posicional."""

    def test_agrupador_existe(self):
        """Verifica que o agrupador pode ser instanciado."""
        agrupador = AgrupadorPosicional()
        assert agrupador is not None
        assert hasattr(agrupador, "extrair_posicao_numerica")
        assert hasattr(agrupador, "modificacao_esta_dentro_da_tag")
        assert hasattr(agrupador, "processar_agrupamento_posicional")


from unittest.mock import patch


class TestAgrupadorPosicional:
    """Testes para o agrupador baseado em posições."""

    def setup_method(self):
        """Configuração para cada teste."""
        self.agrupador = AgrupadorPosicional()

    def test_extrair_posicao_numerica_valida(self):
        """Testa extração de posição numérica de caminhos válidos."""
        # Casos válidos
        assert (
            self.agrupador.extrair_posicao_numerica("modificacao_1_linha_5_pos_100")
            == 100
        )
        assert (
            self.agrupador.extrair_posicao_numerica("adicao_3_linha_10_pos_250") == 250
        )
        assert self.agrupador.extrair_posicao_numerica("remocao_2_linha_7_pos_0") == 0

    def test_extrair_posicao_numerica_invalida(self):
        """Testa extração de posição com caminhos inválidos."""
        # Casos inválidos retornam None
        assert self.agrupador.extrair_posicao_numerica("sem_pos_no_path") is None
        assert self.agrupador.extrair_posicao_numerica("pos_string_texto") is None
        assert self.agrupador.extrair_posicao_numerica("") is None
        assert self.agrupador.extrair_posicao_numerica("pos_") is None

    def test_modificacao_esta_dentro_da_tag_overlap(self):
        """Testa detecção de overlap entre modificação e tag."""
        # Tag cobrindo posições 100-200
        tag_info = {"posicao_inicio": 100, "posicao_fim": 200}

        # Modificação dentro da tag
        modificacao = {"posicao_inicio": 150, "posicao_fim": 150}
        assert (
            self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info) == True
        )

        # Modificação no início exato
        modificacao = {"posicao_inicio": 100, "posicao_fim": 100}
        assert (
            self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info) == True
        )

        # Modificação no final exato
        modificacao = {"posicao_inicio": 200, "posicao_fim": 200}
        assert (
            self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info) == True
        )

        # Modificação fora da tag (antes)
        modificacao = {"posicao_inicio": 50, "posicao_fim": 50}
        assert (
            self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)
            == False
        )

        # Modificação fora da tag (depois)
        modificacao = {"posicao_inicio": 250, "posicao_fim": 250}
        assert (
            self.agrupador.modificacao_esta_dentro_da_tag(modificacao, tag_info)
            == False
        )

    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_buscar_tags_com_posicoes_sucesso(self, mock_get):
        """Testa busca de tags com sucesso."""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "tag1",
                    "tag_nome": "clausula1",
                    "caminho_tag_inicio": "modificacao_1_linha_5_pos_100",
                    "caminho_tag_fim": "modificacao_1_linha_5_pos_200",
                },
                {
                    "id": "tag2",
                    "tag_nome": "clausula2",
                    "caminho_tag_inicio": "modificacao_1_linha_8_pos_300",
                    "caminho_tag_fim": "modificacao_1_linha_8_pos_400",
                },
            ]
        }
        mock_get.return_value = mock_response

        resultado = self.agrupador.buscar_tags_com_posicoes("modelo123")

        assert len(resultado) == 2
        assert resultado[0]["tag_nome"] == "clausula1"
        assert resultado[0]["posicao_inicio"] == 100
        assert resultado[0]["posicao_fim"] == 200

    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_buscar_modificacoes_com_posicoes_sucesso(self, mock_get):
        """Testa busca de modificações com sucesso."""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "mod1",
                    "categoria": "adicao",
                    "conteudo": "Texto adicionado",
                    "caminho_inicio": "modificacao_1_linha_5_pos_150",
                    "caminho_fim": "modificacao_1_linha_5_pos_180",
                },
                {
                    "id": "mod2",
                    "categoria": "remocao",
                    "conteudo": "Texto removido",
                    "caminho_inicio": "modificacao_2_linha_8_pos_350",
                    "caminho_fim": "modificacao_2_linha_8_pos_370",
                },
            ]
        }
        mock_get.return_value = mock_response

        resultado = self.agrupador.buscar_modificacoes_com_posicoes("versao123")

        assert len(resultado) == 2
        assert resultado[0]["posicao_inicio"] == 150
        assert resultado[0]["posicao_fim"] == 180
        assert resultado[1]["posicao_inicio"] == 350
        assert resultado[1]["posicao_fim"] == 370

    @patch("src.docx_compare.utils.agrupador_posicional.requests.post")
    def test_associar_modificacao_sucesso(self, mock_post):
        """Testa associação de modificação com sucesso."""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        resultado = self.agrupador.associar_modificacao_tag("mod1", "tag1")

        assert resultado == True

    @patch("src.docx_compare.utils.agrupador_posicional.requests.post")
    def test_associar_modificacao_erro(self, mock_post):
        """Testa associação com erro."""
        # Mock de erro HTTP
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        resultado = self.agrupador.associar_modificacao_tag("mod1", "tag1")

        assert resultado == False

    @patch.object(AgrupadorPosicional, "buscar_tags_com_posicoes")
    @patch.object(AgrupadorPosicional, "buscar_modificacoes_com_posicoes")
    @patch.object(AgrupadorPosicional, "associar_modificacao_tag")
    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_processar_agrupamento_posicional_sucesso(
        self, mock_get_versao, mock_associar, mock_mod, mock_tags
    ):
        """Testa processamento completo com sucesso."""
        # Mock da busca da versão para obter o modelo
        mock_versao_response = MagicMock()
        mock_versao_response.status_code = 200
        mock_versao_response.json.return_value = {
            "data": {"contrato": {"modelo_contrato": {"id": "modelo123"}}}
        }
        mock_get_versao.return_value = mock_versao_response

        # Mock das respostas
        mock_tags.return_value = [
            {
                "id": "tag1",
                "tag_nome": "clausula1",
                "posicao_inicio": 100,
                "posicao_fim": 200,
            }
        ]

        mock_mod.return_value = [
            {"id": "mod1", "posicao_inicio": 150, "posicao_fim": 170}  # Dentro da tag
        ]

        mock_associar.return_value = True

        resultado = self.agrupador.processar_agrupamento_posicional("versao123")

        assert "total_modificacoes" in resultado
        assert "associacoes_criadas" in resultado
        assert mock_associar.called

    @patch("src.docx_compare.utils.agrupador_posicional.requests.get")
    def test_processar_agrupamento_erro_versao(self, mock_get):
        """Testa processamento com erro na busca da versão."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        resultado = self.agrupador.processar_agrupamento_posicional("versao123")

        assert "erro" in resultado
        assert resultado["erro"] == "Versão não encontrada"


class TestIntegracaoAgrupadorPosicional:
    """Testes de integração do agrupador posicional."""

    @patch.object(AgrupadorPosicional, "processar_agrupamento_posicional")
    def test_integracao_main_sucesso(self, mock_processar):
        """Testa execução principal com sucesso."""
        mock_processar.return_value = {
            "sucesso": True,
            "estatisticas": {
                "total_modificacoes": 5,
                "associacoes_criadas": 3,
                "associacoes_falharam": 0,
                "sem_correspondencia": 2,
            },
        }

        # Simula execução principal
        agrupador = AgrupadorPosicional()
        resultado = agrupador.processar_agrupamento_posicional(
            "test_versao", "test_modelo"
        )

        assert resultado["sucesso"] == True
        assert resultado["estatisticas"]["associacoes_criadas"] == 3

    def test_performance_posicional(self):
        """Testa performance do algoritmo posicional."""
        agrupador = AgrupadorPosicional()

        # Simulação de muitas modificações
        modificacoes = []
        for i in range(1000):
            modificacoes.append({"id": f"mod{i}", "posicao": i * 10})

        # Simulação de muitas tags
        tags = []
        for i in range(100):
            tags.append(
                {
                    "id": f"tag{i}",
                    "posicao_inicio": i * 100,
                    "posicao_fim": i * 100 + 50,
                }
            )

        # Testa eficiência do algoritmo
        import time

        start = time.time()

        associacoes_encontradas = 0
        for modificacao in modificacoes:
            for tag in tags:
                if agrupador.modificacao_esta_dentro_da_tag(modificacao, tag):
                    associacoes_encontradas += 1
                    break

        end = time.time()

        # Deve processar rapidamente (menos de 1 segundo)
        assert end - start < 1.0
        assert associacoes_encontradas > 0
