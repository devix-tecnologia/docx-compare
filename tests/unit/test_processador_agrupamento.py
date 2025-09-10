#!/usr/bin/env python3
"""
Testes unitários para o Processador de Agrupamento de Modificações
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Adicionar o diretório raiz ao path para imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.docx_compare.processors.processador_agrupamento import ProcessadorAgrupamento
from src.docx_compare.utils.agrupador_modificacoes_v2 import AgrupadorModificacoes


class TestProcessadorAgrupamento(unittest.TestCase):
    """Testes para o ProcessadorAgrupamento"""

    def setUp(self):
        """Configurar dados de teste"""
        self.processador = ProcessadorAgrupamento(
            threshold=0.6, intervalo_verificacao=300, verbose=True
        )

    def test_inicializacao_processador(self):
        """Testa a inicialização correta do processador"""
        print("🧪 Teste: Inicialização do processador")

        assert self.processador.threshold == 0.6
        assert self.processador.intervalo_verificacao == 300
        assert self.processador.verbose is True
        assert self.processador.running is True
        assert isinstance(self.processador.agrupador, AgrupadorModificacoes)

        print("   ✅ Processador inicializado corretamente")

    @patch("requests.get")
    def test_buscar_versoes_para_agrupar_com_modificacoes(self, mock_get):
        """Testa busca de versões com modificações para agrupar"""
        print("🧪 Teste: Buscar versões com modificações")

        # Mock da resposta do Directus
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"versao": {"id": "versao-1", "status": "concluido"}},
                {"versao": {"id": "versao-2", "status": "concluido"}},
                {
                    "versao": {
                        "id": "versao-3",
                        "status": "draft",  # Este não deve ser incluído
                    }
                },
            ]
        }
        mock_get.return_value = mock_response

        versoes = self.processador.buscar_versoes_para_agrupar()

        # Verificar se foi feita a requisição correta
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args

        # Verificar parâmetros da requisição
        expected_params = {
            "filter[clausula][_null]": "true",
            "fields": "versao.id,versao.status",
            "limit": 1000,
        }
        assert kwargs["params"] == expected_params

        # Verificar resultado
        expected_versoes = ["versao-1", "versao-2"]  # versao-3 deve ser filtrada
        assert set(versoes) == set(expected_versoes)

        print(f"   ✅ Encontradas {len(versoes)} versões para agrupar")

    @patch("requests.get")
    def test_buscar_versoes_sem_modificacoes(self, mock_get):
        """Testa busca quando não há modificações"""
        print("🧪 Teste: Buscar versões sem modificações")

        # Mock da resposta vazia
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        versoes = self.processador.buscar_versoes_para_agrupar()

        assert versoes == []
        print("   ✅ Lista vazia retornada corretamente")

    @patch("requests.get")
    def test_buscar_versoes_erro_http(self, mock_get):
        """Testa tratamento de erro HTTP"""
        print("🧪 Teste: Erro HTTP na busca")

        # Mock de erro HTTP
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        versoes = self.processador.buscar_versoes_para_agrupar()

        assert versoes == []
        print("   ✅ Erro HTTP tratado corretamente")

    def test_processar_versao_sucesso(self):
        """Testa processamento bem-sucedido de uma versão"""
        print("🧪 Teste: Processamento bem-sucedido de versão")

        # Mock do agrupador
        mock_resultado = {
            "total_modificacoes": 10,
            "associacoes_criadas": 8,
            "associacoes_falharam": 1,
            "modificacoes_sem_correspondencia": 1,
        }

        with patch.object(
            self.processador.agrupador,
            "processar_agrupamento_versao",
            return_value=mock_resultado,
        ) as mock_processar:
            resultado = self.processador.processar_versao("versao-test")

            # Verificar que o agrupador foi chamado corretamente
            mock_processar.assert_called_once_with(
                versao_id="versao-test", threshold=0.6, dry_run=False
            )

            # Verificar resultado
            assert resultado is True

        print("   ✅ Versão processada com sucesso")

    def test_processar_versao_com_erro(self):
        """Testa tratamento de erro no processamento"""
        print("🧪 Teste: Erro no processamento de versão")

        # Mock com erro
        mock_resultado = {"erro": "Modelo de contrato não encontrado"}

        with patch.object(
            self.processador.agrupador,
            "processar_agrupamento_versao",
            return_value=mock_resultado,
        ):
            resultado = self.processador.processar_versao("versao-inexistente")

            assert resultado is False

        print("   ✅ Erro tratado corretamente")

    def test_executar_ciclo_com_versoes(self):
        """Testa execução de ciclo completo com versões"""
        print("🧪 Teste: Ciclo completo com versões")

        # Mock das versões
        with (
            patch.object(
                self.processador,
                "buscar_versoes_para_agrupar",
                return_value=["versao-1", "versao-2"],
            ),
            patch.object(
                self.processador, "processar_versao", return_value=True
            ) as mock_processar,
        ):
            resultado = self.processador.executar_ciclo()

            # Verificar que todas as versões foram processadas
            assert mock_processar.call_count == 2
            mock_processar.assert_any_call("versao-1")
            mock_processar.assert_any_call("versao-2")

            assert resultado is True

        print("   ✅ Ciclo executado com sucesso")

    def test_executar_ciclo_sem_versoes(self):
        """Testa execução de ciclo sem versões"""
        print("🧪 Teste: Ciclo sem versões")

        with patch.object(
            self.processador, "buscar_versoes_para_agrupar", return_value=[]
        ):
            resultado = self.processador.executar_ciclo()

            assert resultado is True

        print("   ✅ Ciclo vazio executado corretamente")

    def test_executar_single_run(self):
        """Testa execução de ciclo único"""
        print("🧪 Teste: Execução single-run")

        with patch.object(
            self.processador, "executar_ciclo", return_value=True
        ) as mock_ciclo:
            resultado = self.processador.executar_single_run()

            # Verificar que o ciclo foi executado uma vez
            mock_ciclo.assert_called_once()
            assert resultado is True

        print("   ✅ Single-run executado corretamente")

    def test_configuracao_threshold(self):
        """Testa diferentes configurações de threshold"""
        print("🧪 Teste: Configuração de threshold")

        # Threshold baixo
        processador_baixo = ProcessadorAgrupamento(threshold=0.3)
        assert processador_baixo.threshold == 0.3

        # Threshold alto
        processador_alto = ProcessadorAgrupamento(threshold=0.9)
        assert processador_alto.threshold == 0.9

        print("   ✅ Thresholds configurados corretamente")

    def test_parar_processador(self):
        """Testa parada do processador"""
        print("🧪 Teste: Parar processador")

        assert self.processador.running is True

        self.processador.parar()

        assert self.processador.running is False

        print("   ✅ Processador parado corretamente")


class TestIntegracaoAgrupamento(unittest.TestCase):
    """Testes de integração para agrupamento"""

    def test_fluxo_completo_mock(self):
        """Testa fluxo completo com dados mockados"""
        print("🧪 Teste: Fluxo completo mockado")

        processador = ProcessadorAgrupamento(threshold=0.5, verbose=True)

        # Dados de teste simulados
        versoes_mock = ["versao-teste-1"]
        resultado_agrupamento_mock = {
            "total_modificacoes": 5,
            "associacoes_criadas": 3,
            "associacoes_falharam": 0,
            "modificacoes_sem_correspondencia": 2,
        }

        with (
            patch.object(
                processador, "buscar_versoes_para_agrupar", return_value=versoes_mock
            ),
            patch.object(
                processador.agrupador,
                "processar_agrupamento_versao",
                return_value=resultado_agrupamento_mock,
            ),
        ):
            resultado = processador.executar_single_run()

            assert resultado is True

        print("   ✅ Fluxo completo executado com sucesso")
        print(
            f"   📊 Simuladas: {resultado_agrupamento_mock['associacoes_criadas']} associações"
        )


def run_tests():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do Processador de Agrupamento")
    print("=" * 60)

    # Teste de inicialização
    test = TestProcessadorAgrupamento()
    test.setUp()
    test.test_inicializacao_processador()
    test.test_buscar_versoes_para_agrupar_com_modificacoes()
    test.test_buscar_versoes_sem_modificacoes()
    test.test_buscar_versoes_erro_http()
    test.test_processar_versao_sucesso()
    test.test_processar_versao_com_erro()
    test.test_executar_ciclo_com_versoes()
    test.test_executar_ciclo_sem_versoes()
    test.test_executar_single_run()
    test.test_configuracao_threshold()
    test.test_parar_processador()

    # Teste de integração
    test_integracao = TestIntegracaoAgrupamento()
    test_integracao.test_fluxo_completo_mock()

    print("=" * 60)
    print("✅ Todos os testes do Processador de Agrupamento passaram!")


if __name__ == "__main__":
    run_tests()
