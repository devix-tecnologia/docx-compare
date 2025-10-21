"""
Testes unitários para o repositório Directus.

Testa todas as operações de I/O com o Directus usando mocks,
garantindo que a camada de acesso a dados funciona corretamente.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os
import sys

# Adicionar diretório versiona-ai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from repositorio import DirectusRepository


@pytest.fixture
def repo():
    """Cria uma instância do repositório para testes."""
    return DirectusRepository(
        base_url='https://test.directus.io',
        token='test-token-123'
    )


class TestDirectusRepository:
    """Testes para DirectusRepository."""

    def test_init_with_token(self):
        """Testa inicialização com token fornecido."""
        repo = DirectusRepository(
            base_url='https://test.directus.io',
            token='my-token'
        )

        assert repo.base_url == 'https://test.directus.io'
        assert repo.headers['Authorization'] == 'Bearer my-token'
        assert repo.headers['Content-Type'] == 'application/json'

    def test_init_with_env_token(self):
        """Testa inicialização buscando token de variável de ambiente."""
        with patch.dict(os.environ, {'DIRECTUS_TOKEN': 'env-token'}):
            repo = DirectusRepository(base_url='https://test.directus.io')
            assert repo.headers['Authorization'] == 'Bearer env-token'

    def test_base_url_trailing_slash_removal(self):
        """Testa que barra final é removida da URL base."""
        repo = DirectusRepository(
            base_url='https://test.directus.io/',
            token='token'
        )
        assert repo.base_url == 'https://test.directus.io'


class TestGetVersao:
    """Testes para get_versao()."""

    @patch('repositorio.requests.get')
    def test_get_versao_success(self, mock_get, repo):
        """Testa busca bem-sucedida de versão."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'id': 'v123',
                'nome': 'Versão 1.0',
                'status': 'processando'
            }
        }
        mock_get.return_value = mock_response

        result = repo.get_versao('v123')

        assert result is not None
        assert result['id'] == 'v123'
        assert result['nome'] == 'Versão 1.0'
        mock_get.assert_called_once()

    @patch('repositorio.requests.get')
    def test_get_versao_not_found(self, mock_get, repo):
        """Testa busca de versão inexistente."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = repo.get_versao('v999')

        assert result is None

    @patch('repositorio.requests.get')
    def test_get_versao_with_fields(self, mock_get, repo):
        """Testa busca com campos específicos."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {}}
        mock_get.return_value = mock_response

        fields = ['id', 'nome', 'contrato.modelo_contrato.arquivo_original']
        repo.get_versao('v123', fields=fields)

        # Verificar que fields foi passado como query param
        call_args = mock_get.call_args
        assert 'params' in call_args.kwargs
        assert call_args.kwargs['params']['fields'] == ','.join(fields)


class TestUpdateVersao:
    """Testes para update_versao()."""

    @patch('repositorio.requests.patch')
    def test_update_versao_success(self, mock_patch, repo):
        """Testa atualização bem-sucedida."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'id': 'v123',
                'status': 'concluido'
            }
        }
        mock_patch.return_value = mock_response

        data = {'status': 'concluido'}
        result = repo.update_versao('v123', data)

        assert result['success'] is True
        assert result['status_code'] == 200
        assert 'data' in result
        assert result['data']['status'] == 'concluido'

    @patch('repositorio.requests.patch')
    def test_update_versao_failure(self, mock_patch, repo):
        """Testa atualização com erro HTTP."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request: Invalid data'
        mock_patch.return_value = mock_response

        data = {'invalid': 'data'}
        result = repo.update_versao('v123', data)

        assert result['success'] is False
        assert result['status_code'] == 400
        assert 'error' in result
        assert 'HTTP 400' in result['error']

    @patch('repositorio.requests.patch')
    def test_update_versao_exception(self, mock_patch, repo):
        """Testa atualização com exceção."""
        mock_patch.side_effect = Exception('Network error')

        data = {'status': 'concluido'}
        result = repo.update_versao('v123', data)

        assert result['success'] is False
        assert result['status_code'] == 0
        assert 'error' in result
        assert 'Network error' in result['error']


class TestGetModificacoesVersao:
    """Testes para get_modificacoes_versao()."""

    @patch('repositorio.requests.get')
    def test_get_modificacoes_success(self, mock_get, repo):
        """Testa busca de modificações com sucesso."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'id': 'm1', 'tipo': 'adicao'},
                {'id': 'm2', 'tipo': 'remocao'}
            ]
        }
        mock_get.return_value = mock_response

        result = repo.get_modificacoes_versao('v123')

        assert len(result) == 2
        assert result[0]['id'] == 'm1'
        assert result[1]['tipo'] == 'remocao'

    @patch('repositorio.requests.get')
    def test_get_modificacoes_empty(self, mock_get, repo):
        """Testa busca sem modificações."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response

        result = repo.get_modificacoes_versao('v123')

        assert result == []


class TestGetArquivoId:
    """Testes para get_arquivo_id()."""

    def test_get_arquivo_id_nested_object(self, repo):
        """Testa extração de ID de objeto aninhado."""
        versao_data = {
            'contrato': {
                'modelo_contrato': {
                    'arquivo_original': {
                        'id': 'file-123',
                        'filename': 'documento.docx'
                    }
                }
            }
        }

        result = repo.get_arquivo_id(versao_data)

        assert result == 'file-123'

    def test_get_arquivo_id_simple_string(self, repo):
        """Testa extração de ID quando é string simples."""
        versao_data = {
            'contrato': {
                'modelo_contrato': {
                    'arquivo_original': 'file-456'
                }
            }
        }

        result = repo.get_arquivo_id(versao_data)

        assert result == 'file-456'

    def test_get_arquivo_id_missing_contrato(self, repo):
        """Testa quando contrato está ausente."""
        versao_data = {}

        result = repo.get_arquivo_id(versao_data)

        assert result is None

    def test_get_arquivo_id_missing_modelo(self, repo):
        """Testa quando modelo_contrato está ausente."""
        versao_data = {'contrato': {}}

        result = repo.get_arquivo_id(versao_data)

        assert result is None

    def test_get_arquivo_id_missing_arquivo(self, repo):
        """Testa quando arquivo_original está ausente."""
        versao_data = {
            'contrato': {
                'modelo_contrato': {}
            }
        }

        result = repo.get_arquivo_id(versao_data)

        assert result is None


class TestDownloadFile:
    """Testes para download_file()."""

    @patch('repositorio.requests.get')
    def test_download_file_success(self, mock_get, repo):
        """Testa download bem-sucedido de arquivo."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake docx content'
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test.docx'
            result = repo.download_file('file-123', output_path)

            assert result == output_path
            assert result.exists()
            assert result.read_bytes() == b'fake docx content'

    @patch('repositorio.requests.get')
    def test_download_file_temp_path(self, mock_get, repo):
        """Testa download para arquivo temporário."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake content'
        mock_get.return_value = mock_response

        result = repo.download_file('file-123')

        assert result is not None
        assert result.exists()
        assert result.suffix == '.docx'

        # Limpar arquivo temporário
        result.unlink()


class TestGetClausulasModelo:
    """Testes para get_clausulas_modelo()."""

    @patch('repositorio.requests.get')
    def test_get_clausulas_success(self, mock_get, repo):
        """Testa busca de cláusulas."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'id': 'c1', 'numero': '1.1', 'nome': 'Objeto'},
                {'id': 'c2', 'numero': '2.1', 'nome': 'Vigência'}
            ]
        }
        mock_get.return_value = mock_response

        result = repo.get_clausulas_modelo('modelo-123')

        assert len(result) == 2
        assert result[0]['numero'] == '1.1'


class TestGetContratos:
    """Testes para get_contratos()."""

    @patch('repositorio.requests.get')
    def test_get_contratos_no_filters(self, mock_get, repo):
        """Testa listagem sem filtros."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'id': '1', 'nome': 'Contrato A'},
                {'id': '2', 'nome': 'Contrato B'}
            ]
        }
        mock_get.return_value = mock_response

        result = repo.get_contratos()

        assert len(result) == 2

    @patch('repositorio.requests.get')
    def test_get_contratos_with_filters(self, mock_get, repo):
        """Testa listagem com filtros."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response

        filters = {'status': 'ativo', 'tipo': 'prestacao_servico'}
        repo.get_contratos(filters=filters)

        # Verificar que filtros foram passados como query params
        call_args = mock_get.call_args
        params = call_args.kwargs['params']
        assert params['filter[status]'] == 'ativo'
        assert params['filter[tipo]'] == 'prestacao_servico'


class TestTestConnection:
    """Testes para test_connection()."""

    @patch('repositorio.requests.get')
    def test_connection_success(self, mock_get, repo):
        """Testa conexão bem-sucedida."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = repo.test_connection()

        assert result['success'] is True
        assert result['status_code'] == 200
        assert result['message'] == 'Conectado'

    @patch('repositorio.requests.get')
    def test_connection_failure(self, mock_get, repo):
        """Testa falha na conexão."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = repo.test_connection()

        assert result['success'] is False
        assert result['status_code'] == 401

    @patch('repositorio.requests.get')
    def test_connection_exception(self, mock_get, repo):
        """Testa exceção na conexão."""
        mock_get.side_effect = Exception('Timeout')

        result = repo.test_connection()

        assert result['success'] is False
        assert result['status_code'] == 0
        assert 'Timeout' in result['message']


class TestGetVersaoParaProcessar:
    """Testes para get_versao_para_processar()."""

    @patch('repositorio.requests.get')
    def test_get_versao_para_processar_success(self, mock_get, repo):
        """Testa busca de versão para processamento com todos os campos."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "versao-123",
                "status": "processar",
                "contrato": {
                    "id": "contrato-456",
                    "modelo_contrato": {
                        "id": "modelo-789",
                        "arquivo_com_tags": "arquivo-com-tags-id",
                        "arquivo_original": "arquivo-original-id",
                        "tags": [
                            {
                                "id": "tag-1",
                                "tag_nome": "TAG-CLAUSULA-1",
                                "posicao_inicio_texto": 100,
                                "posicao_fim_texto": 200,
                                "conteudo": "Conteúdo da tag",
                                "clausulas": [
                                    {"id": "cl-1", "numero": "1.1", "nome": "Cláusula 1"}
                                ]
                            }
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        result = repo.get_versao_para_processar("versao-123")

        assert result is not None
        assert result["id"] == "versao-123"
        assert "contrato" in result
        assert "modelo_contrato" in result["contrato"]
        assert "tags" in result["contrato"]["modelo_contrato"]
        assert len(result["contrato"]["modelo_contrato"]["tags"]) == 1

        # Verificar que chamou get_versao com os campos corretos
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        fields = params["fields"]

        # Verificar campos principais estão incluídos
        assert "id" in fields
        assert "contrato.modelo_contrato.tags.id" in fields


class TestGetVersaoCompletaParaView:
    """Testes para get_versao_completa_para_view()."""

    @patch('repositorio.requests.get')
    def test_get_versao_completa_para_view_success(self, mock_get, repo):
        """Testa busca de versão completa para visualização."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "versao-123",
                "status": "concluido",
                "modificacoes": [
                    {
                        "id": "mod-1",
                        "categoria": "modificacao",
                        "conteudo": "texto original",
                        "alteracao": "texto modificado",
                        "clausula": {
                            "id": "cl-1",
                            "numero": "1.1",
                            "nome": "Cláusula 1"
                        }
                    }
                ],
                "contrato": {
                    "id": "contrato-456",
                    "modelo_contrato": {
                        "id": "modelo-789"
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        result = repo.get_versao_completa_para_view("versao-123")

        assert result is not None
        assert result["id"] == "versao-123"
        assert "modificacoes" in result
        assert len(result["modificacoes"]) == 1
        assert result["modificacoes"][0]["clausula"]["numero"] == "1.1"

        # Verificar que usou wildcards
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        fields = params["fields"]

        assert "*" in fields
        assert "modificacoes.*" in fields


class TestGetVersoesPorModelo:
    """Testes para get_versoes_por_modelo()."""

    @patch('repositorio.requests.get')
    def test_get_versoes_por_modelo_success(self, mock_get, repo):
        """Testa busca de versões por modelo."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "versao-1",
                    "versao": "v1.0",
                    "status": "concluido",
                    "contrato": {"id": "contrato-1", "numero": "CNT-001"}
                },
                {
                    "id": "versao-2",
                    "versao": "v2.0",
                    "status": "processar",
                    "contrato": {"id": "contrato-2", "numero": "CNT-002"}
                }
            ]
        }
        mock_get.return_value = mock_response

        result = repo.get_versoes_por_modelo("modelo-789")

        assert len(result) == 2
        assert result[0]["versao"] == "v1.0"
        assert result[1]["versao"] == "v2.0"

        # Verificar filtro correto
        call_args = mock_get.call_args
        params = call_args[1]["params"]

        assert "filter[contrato][modelo_contrato][_eq]" in params
        assert params["filter[contrato][modelo_contrato][_eq]"] == "modelo-789"

    @patch('repositorio.requests.get')
    def test_get_versoes_por_modelo_empty(self, mock_get, repo):
        """Testa busca sem resultados."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        result = repo.get_versoes_por_modelo("modelo-inexistente")

        assert result == []


class TestRegistrarResultadoProcessamentoVersao:
    """Testes para registrar_resultado_processamento_versao()."""

    @patch('repositorio.requests.patch')
    def test_registrar_resultado_success(self, mock_patch, repo):
        """Testa registro de resultado de processamento com sucesso."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "versao-123",
                "status": "concluido",
                "modificacoes": [
                    {"id": "mod-1"},
                    {"id": "mod-2"},
                    {"id": "mod-3"}
                ]
            }
        }
        mock_patch.return_value = mock_response

        modificacoes = [
            {
                "versao": "versao-123",
                "categoria": "modificacao",
                "conteudo": "texto 1",
                "posicao_inicio": 100,
                "posicao_fim": 200
            },
            {
                "versao": "versao-123",
                "categoria": "inclusao",
                "alteracao": "texto 2",
                "posicao_inicio": 300,
                "posicao_fim": 400
            }
        ]

        result = repo.registrar_resultado_processamento_versao(
            versao_id="versao-123",
            modificacoes=modificacoes,
            arquivo_original_id="arquivo-456"
        )

        assert result['success'] is True
        assert result['modificacoes_criadas'] == 3
        assert len(result['ids_criados']) == 3
        assert result['ids_criados'][0] == "mod-1"

        # Verificar dados enviados
        call_args = mock_patch.call_args
        json_data = call_args[1]['json']

        assert json_data['modificacoes'] == modificacoes
        assert json_data['status'] == "concluido"
        assert json_data['modifica_arquivo'] == "arquivo-456"
        assert 'data_hora_processamento' in json_data

    @patch('repositorio.requests.patch')
    def test_registrar_resultado_com_metricas(self, mock_patch, repo):
        """Testa registro com métricas adicionais."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "id": "versao-123",
                "status": "concluido",
                "modificacoes": ["mod-1"]
            }
        }
        mock_patch.return_value = mock_response

        modificacoes = [{"versao": "versao-123", "categoria": "modificacao"}]
        metricas = {
            "total_blocos": 5,
            "taxa_vinculacao": 85.5,
            "metodo_processamento": "AST"
        }

        result = repo.registrar_resultado_processamento_versao(
            versao_id="versao-123",
            modificacoes=modificacoes,
            metricas=metricas
        )

        assert result['success'] is True

        # Verificar que métricas foram incluídas
        call_args = mock_patch.call_args
        json_data = call_args[1]['json']

        assert json_data['total_blocos'] == 5
        assert json_data['taxa_vinculacao'] == 85.5
        assert json_data['metodo_processamento'] == "AST"

    @patch('repositorio.requests.patch')
    def test_registrar_resultado_failure(self, mock_patch, repo):
        """Testa falha no registro."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_patch.return_value = mock_response

        result = repo.registrar_resultado_processamento_versao(
            versao_id="versao-123",
            modificacoes=[]
        )

        assert result['success'] is False
        assert result['modificacoes_criadas'] == 0
        assert result['ids_criados'] == []
        assert 'error' in result

    @patch('repositorio.requests.patch')
    def test_registrar_resultado_status_customizado(self, mock_patch, repo):
        """Testa registro com status customizado."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"id": "versao-123", "modificacoes": []}
        }
        mock_patch.return_value = mock_response

        result = repo.registrar_resultado_processamento_versao(
            versao_id="versao-123",
            modificacoes=[],
            status="processando"
        )

        assert result['success'] is True

        # Verificar status customizado
        call_args = mock_patch.call_args
        json_data = call_args[1]['json']
        assert json_data['status'] == "processando"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
