#!/usr/bin/env python3
"""
Testes unitários para o módulo directus_utils.py
"""

import os
import sys
import unittest
from unittest.mock import Mock, mock_open, patch

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.docx_compare.utils.directus_utils import (
    DEFAULT_REQUEST_TIMEOUT,
    DIRECTUS_BASE_URL,
    DIRECTUS_HEADERS,
    DIRECTUS_TOKEN,
    buscar_versoes_para_processar,
    determine_original_file_id,
    determine_template_id,
    determine_versao_anterior,
    download_file_from_directus,
    update_versao_status,
    upload_file_to_directus,
)


class TestDirectusUtils(unittest.TestCase):
    """Testes unitários para as funções do directus_utils"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        self.sample_versao_data = {
            "id": "123",
            "date_created": "2023-12-01T10:00:00",
            "status": "processar",
            "codigo": "V001",
            "contrato": {
                "id": "contract123",
                "modelo_contrato": {"arquivo_original": "template456"},
                "versoes": [
                    {
                        "id": "122",
                        "date_created": "2023-11-01T10:00:00",
                        "arquivo": "file122",
                        "codigo": "V000",
                    },
                    {
                        "id": "123",
                        "date_created": "2023-12-01T10:00:00",
                        "arquivo": "file123",
                        "codigo": "V001",
                    },
                ],
            },
        }

    def test_constants_configuration(self):
        """Testa se as constantes estão configuradas corretamente"""
        self.assertIsInstance(DIRECTUS_BASE_URL, str)
        self.assertIsInstance(DIRECTUS_TOKEN, str)
        self.assertIsInstance(DIRECTUS_HEADERS, dict)
        self.assertEqual(DEFAULT_REQUEST_TIMEOUT, 30)
        self.assertIn("Authorization", DIRECTUS_HEADERS)
        self.assertIn("Content-Type", DIRECTUS_HEADERS)

    @patch("src.docx_compare.utils.directus_utils.requests.get")
    def test_buscar_versoes_para_processar_success(self, mock_get):
        """Testa busca bem-sucedida de versões para processar"""
        # Mock das responses
        mock_simple_response = Mock()
        mock_simple_response.status_code = 200
        mock_simple_response.text = '{"data": []}'

        mock_filtered_response = Mock()
        mock_filtered_response.status_code = 200
        mock_filtered_response.json.return_value = {
            "data": [
                {"id": "123", "status": "processar"},
                {"id": "124", "status": "processar"},
            ]
        }

        mock_get.side_effect = [mock_simple_response, mock_filtered_response]

        result = buscar_versoes_para_processar()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "123")
        self.assertEqual(result[1]["id"], "124")
        self.assertEqual(mock_get.call_count, 2)

    @patch("src.docx_compare.utils.directus_utils.requests.get")
    def test_buscar_versoes_para_processar_connectivity_failure(self, mock_get):
        """Testa falha de conectividade na busca de versões"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        result = buscar_versoes_para_processar()

        self.assertEqual(result, [])
        mock_get.assert_called_once()

    @patch("src.docx_compare.utils.directus_utils.requests.get")
    def test_buscar_versoes_para_processar_exception(self, mock_get):
        """Testa tratamento de exceção na busca de versões"""
        mock_get.side_effect = Exception("Connection error")

        result = buscar_versoes_para_processar()

        self.assertEqual(result, [])

    def test_determine_versao_anterior_success(self):
        """Testa determinação bem-sucedida da versão anterior"""
        result = determine_versao_anterior(self.sample_versao_data)

        self.assertIsNotNone(result)
        if result:  # Type guard para evitar problemas de type checking
            self.assertEqual(result["id"], "122")
            self.assertEqual(result["date_created"], "2023-11-01T10:00:00")

    def test_determine_versao_anterior_no_previous_version(self):
        """Testa quando não há versão anterior"""
        versao_data = {
            "id": "123",
            "date_created": "2023-12-01T10:00:00",
            "contrato": {
                "versoes": [
                    {
                        "id": "123",
                        "date_created": "2023-12-01T10:00:00",
                    }
                ]
            },
        }

        result = determine_versao_anterior(versao_data)
        self.assertIsNone(result)

    def test_determine_versao_anterior_empty_versions(self):
        """Testa quando não há versões no contrato"""
        versao_data = {
            "id": "123",
            "date_created": "2023-12-01T10:00:00",
            "contrato": {"versoes": []},
        }

        result = determine_versao_anterior(versao_data)
        self.assertIsNone(result)

    def test_determine_template_id_success(self):
        """Testa determinação bem-sucedida do template ID"""
        result = determine_template_id(self.sample_versao_data)

        self.assertEqual(result, "template456")

    def test_determine_template_id_missing_modelo_contrato(self):
        """Testa quando modelo_contrato está ausente"""
        versao_data = {"contrato": {}}

        result = determine_template_id(versao_data)
        self.assertIsNone(result)

    def test_determine_template_id_missing_arquivo_original(self):
        """Testa quando arquivo_original está ausente"""
        versao_data = {"contrato": {"modelo_contrato": {}}}

        result = determine_template_id(versao_data)
        self.assertIsNone(result)

    @patch("src.docx_compare.utils.directus_utils.determine_versao_anterior")
    @patch("src.docx_compare.utils.directus_utils.determine_template_id")
    def test_determine_original_file_id_with_previous_version(
        self, mock_template, mock_anterior
    ):
        """Testa determinação do arquivo original com versão anterior"""
        mock_anterior.return_value = {"arquivo": "file122"}

        file_id, source = determine_original_file_id(self.sample_versao_data)

        self.assertEqual(file_id, "file122")
        self.assertEqual(source, "versao_anterior")
        mock_template.assert_not_called()

    @patch("src.docx_compare.utils.directus_utils.determine_versao_anterior")
    @patch("src.docx_compare.utils.directus_utils.determine_template_id")
    def test_determine_original_file_id_with_template(
        self, mock_template, mock_anterior
    ):
        """Testa determinação do arquivo original usando template"""
        mock_anterior.return_value = None
        mock_template.return_value = "template456"

        file_id, source = determine_original_file_id(self.sample_versao_data)

        self.assertEqual(file_id, "template456")
        self.assertEqual(source, "modelo_contrato")

    @patch("src.docx_compare.utils.directus_utils.determine_versao_anterior")
    @patch("src.docx_compare.utils.directus_utils.determine_template_id")
    def test_determine_original_file_id_previous_version_no_file(
        self, mock_template, mock_anterior
    ):
        """Testa erro quando versão anterior não tem arquivo"""
        mock_anterior.return_value = {"id": "122"}  # Sem campo "arquivo"

        file_id, source = determine_original_file_id(self.sample_versao_data)

        self.assertIsNone(file_id)
        self.assertIsNone(source)

    @patch("src.docx_compare.utils.directus_utils.requests.get")
    @patch("src.docx_compare.utils.directus_utils.requests.head")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("os.makedirs")
    def test_download_file_from_directus_with_cache_hit(
        self, mock_makedirs, mock_getsize, mock_exists, mock_file, mock_head, mock_get
    ):
        """Testa download com cache válido"""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_head.return_value.status_code = 200
        mock_head.return_value.headers = {"content-length": "1024"}

        cache_dir = "/tmp/cache"
        file_path, status = download_file_from_directus("file123", cache_dir)

        self.assertEqual(file_path, "/tmp/cache/file123.docx")
        self.assertEqual(status, "cached")
        mock_get.assert_not_called()

    @patch("src.docx_compare.utils.directus_utils.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_download_file_from_directus_success(
        self, mock_makedirs, mock_file, mock_get
    ):
        """Testa download bem-sucedido"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake docx content"
        mock_get.return_value = mock_response

        cache_dir = "/tmp/cache"
        file_path, status = download_file_from_directus("file123", cache_dir)

        self.assertEqual(file_path, "/tmp/cache/file123.docx")
        self.assertEqual(status, "downloaded")
        mock_file.assert_called_once()

    @patch("src.docx_compare.utils.directus_utils.requests.get")
    def test_download_file_from_directus_http_error(self, mock_get):
        """Testa erro HTTP no download"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            download_file_from_directus("file123")

        self.assertIn("Erro HTTP 404", str(context.exception))

    @patch("src.docx_compare.utils.directus_utils.requests.post")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake html content")
    @patch("os.path.basename")
    def test_upload_file_to_directus_success(self, mock_basename, mock_file, mock_post):
        """Testa upload bem-sucedido"""
        mock_basename.return_value = "test.html"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"id": "uploaded123"}}
        mock_post.return_value = mock_response

        result = upload_file_to_directus("/tmp/test.html")

        self.assertEqual(result, "uploaded123")
        mock_post.assert_called_once()

    def test_upload_file_to_directus_dry_run(self):
        """Testa upload em modo dry-run"""
        with patch("src.docx_compare.utils.directus_utils.uuid.uuid4") as mock_uuid:
            mock_uuid.return_value = "mock-uuid-123"

            result = upload_file_to_directus("/tmp/test.html", dry_run=True)

            self.assertEqual(result, "mock-file-id-mock-uuid-123")

    @patch("src.docx_compare.utils.directus_utils.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.basename")
    def test_upload_file_to_directus_http_error(
        self, mock_basename, mock_file, mock_post
    ):
        """Testa erro HTTP no upload"""
        mock_basename.return_value = "test.html"
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        result = upload_file_to_directus("/tmp/test.html")

        self.assertIsNone(result)

    @patch("src.docx_compare.utils.directus_utils.upload_file_to_directus")
    @patch("src.docx_compare.utils.directus_utils.requests.patch")
    @patch("os.path.exists")
    def test_update_versao_status_success(self, mock_exists, mock_patch, mock_upload):
        """Testa atualização bem-sucedida do status"""
        mock_exists.return_value = True
        mock_upload.return_value = "report123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"id": "123", "status": "concluido"}}
        mock_patch.return_value = mock_response

        result = update_versao_status(
            versao_id="123",
            status="concluido",
            total_modifications=5,
            result_file_path="/tmp/report.html",
        )

        self.assertIsNotNone(result)
        if result:  # Type guard para evitar problemas de type checking
            self.assertEqual(result["status"], "concluido")
        mock_upload.assert_called_once()
        mock_patch.assert_called_once()

    def test_update_versao_status_dry_run(self):
        """Testa atualização em modo dry-run"""
        result = update_versao_status(versao_id="123", status="concluido", dry_run=True)

        self.assertIsNotNone(result)
        if result:  # Type guard para evitar problemas de type checking
            self.assertEqual(result["id"], "123")
            self.assertEqual(result["status"], "concluido")

    @patch("src.docx_compare.utils.directus_utils.requests.patch")
    def test_update_versao_status_http_error(self, mock_patch):
        """Testa erro HTTP na atualização do status"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_patch.return_value = mock_response

        result = update_versao_status("123", "erro")

        self.assertIsNone(result)

    @patch("src.docx_compare.utils.directus_utils.upload_file_to_directus")
    @patch("src.docx_compare.utils.directus_utils.requests.patch")
    @patch("os.path.exists")
    def test_update_versao_status_with_modifications(
        self, mock_exists, mock_patch, mock_upload
    ):
        """Testa atualização com modificações"""
        mock_exists.return_value = False
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"id": "123"}}
        mock_patch.return_value = mock_response

        modifications = [
            {
                "categoria": "adição",
                "conteudo": "Novo parágrafo",
                "alteracao": "Texto adicionado",
                "sort": 1,
            }
        ]

        result = update_versao_status(
            versao_id="123", status="concluido", modifications=modifications
        )

        self.assertIsNotNone(result)
        # Verificar se modificações foram incluídas na chamada
        call_args = mock_patch.call_args[1]["json"]
        self.assertIn("modificacoes", call_args)
        self.assertEqual(len(call_args["modificacoes"]), 1)


if __name__ == "__main__":
    unittest.main()
