"""
Repositório para acesso aos dados do Directus.

Este módulo implementa o padrão Repository, separando a lógica de acesso a dados
da lógica de negócio. Todos os métodos que fazem requisições HTTP ao Directus
devem estar aqui.

Responsabilidades:
- Fazer requisições HTTP ao Directus
- Converter respostas para objetos Python
- Lidar com erros de comunicação
- NÃO conter lógica de negócio
"""

import os
import requests
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Any


class DirectusRepository:
    """
    Repositório para acesso aos dados do Directus.

    Centraliza todas as operações de I/O com o Directus, permitindo
    testabilidade através de mocks e separação clara de responsabilidades.
    """

    def __init__(self, base_url: str, token: Optional[str] = None):
        """
        Inicializa o repositório.

        Args:
            base_url: URL base do Directus (ex: https://api.exemplo.com)
            token: Token de autenticação (se None, busca de DIRECTUS_TOKEN env var)
        """
        self.base_url = base_url.rstrip('/')

        # Configurar headers com token
        if token is None:
            token = os.getenv('DIRECTUS_TOKEN')

        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    # ============================================================================
    # MÉTODOS DE VERSÃO
    # ============================================================================

    def get_versao(
        self,
        versao_id: str,
        fields: Optional[list[str]] = None
    ) -> Optional[dict[str, Any]]:
        """
        Busca uma versão específica com campos aninhados.

        Args:
            versao_id: ID da versão
            fields: Lista de campos a buscar (suporta nested: "contrato.modelo_contrato.arquivo_original")

        Returns:
            dict com dados da versão ou None se não encontrada

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        params = {}
        if fields:
            params['fields'] = ','.join(fields)

        response = requests.get(
            f"{self.base_url}/items/versao/{versao_id}",
            headers=self.headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get('data')
        elif response.status_code == 404:
            return None
        else:
            response.raise_for_status()
            return None

    def get_versao_para_processar(self, versao_id: str) -> Optional[dict[str, Any]]:
        """
        Busca uma versão com TODOS os campos necessários para processamento.

        Este método encapsula o conhecimento sobre quais campos são necessários
        para processar uma versão, incluindo todos os relacionamentos nested.

        Args:
            versao_id: ID da versão a processar

        Returns:
            dict com versão completa incluindo:
                - Dados da versão (id, status, datas, arquivo, etc.)
                - Contrato relacionado
                - Modelo de contrato
                - Tags do modelo com suas posições e cláusulas
                - Arquivo original do modelo

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        # Campos necessários para processamento completo
        fields = [
            # Campos da versão
            "id", "status", "date_created", "date_updated", "versao",
            "observacao", "origem", "arquivo", "modifica_arquivo",

            # Contrato
            "contrato.id",

            # Modelo de contrato
            "contrato.modelo_contrato.id",
            "contrato.modelo_contrato.arquivo_com_tags",
            "contrato.modelo_contrato.arquivo_original",

            # Tags do modelo com posições e conteúdo
            "contrato.modelo_contrato.tags.id",
            "contrato.modelo_contrato.tags.tag_nome",
            "contrato.modelo_contrato.tags.caminho_tag_inicio",
            "contrato.modelo_contrato.tags.caminho_tag_fim",
            "contrato.modelo_contrato.tags.posicao_inicio_texto",
            "contrato.modelo_contrato.tags.posicao_fim_texto",
            "contrato.modelo_contrato.tags.conteudo",

            # Cláusulas vinculadas às tags
            "contrato.modelo_contrato.tags.clausulas.id",
            "contrato.modelo_contrato.tags.clausulas.numero",
            "contrato.modelo_contrato.tags.clausulas.nome"
        ]

        return self.get_versao(versao_id, fields=fields)

    def get_versao_completa_para_view(self, versao_id: str) -> Optional[dict[str, Any]]:
        """
        Busca uma versão com TODOS os relacionamentos para exibição no frontend.

        Este método encapsula o conhecimento sobre quais campos são necessários
        para exibir uma versão processada, incluindo todas as modificações e metadados.

        Args:
            versao_id: ID da versão a exibir

        Returns:
            dict com versão completa incluindo:
                - Dados da versão
                - Modificações com suas cláusulas
                - Contrato relacionado
                - Modelo de contrato

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        # Usar wildcard para pegar todos os campos nested
        # Padrão: "*" pega todos os campos diretos
        # "modificacoes.*" pega todos os campos de cada modificação
        # "modificacoes.clausula.*" pega todos os campos da cláusula vinculada
        fields = [
            "*",  # Todos os campos da versão
            "modificacoes.*",  # Todos os campos de cada modificação
            "modificacoes.clausula.*",  # Cláusula vinculada de cada modificação
            "contrato.*",  # Dados do contrato
            "contrato.modelo_contrato.*"  # Dados do modelo
        ]

        return self.get_versao(versao_id, fields=fields)

    def get_versoes_por_modelo(self, modelo_id: str) -> list[dict]:
        """
        Busca todas as versões vinculadas a um modelo de contrato.

        Este método encapsula a lógica de navegação da estrutura:
        modelo_contrato → contrato → versao

        Args:
            modelo_id: ID do modelo de contrato

        Returns:
            Lista de versões encontradas, ordenadas por número da versão

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        params = {
            "filter[contrato][modelo_contrato][_eq]": modelo_id,  # Deep filter
            "fields": "id,versao,status,date_created,contrato.id,contrato.numero",
            "sort": "versao",
            "limit": -1,  # Sem limite
        }

        response = requests.get(
            f"{self.base_url}/items/versao",
            headers=self.headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            response.raise_for_status()
            return []

    def update_versao(
        self,
        versao_id: str,
        data: dict[str, Any],
        timeout: int = 300
    ) -> dict[str, Any]:
        """
        Atualiza uma versão no Directus.

        Args:
            versao_id: ID da versão a atualizar
            data: Dados a atualizar (pode incluir relacionamentos)
            timeout: Timeout em segundos (padrão: 5 minutos para transações grandes)

        Returns:
            dict com:
                - success: bool
                - status_code: int
                - data: dict (se sucesso)
                - error: str (se falha)

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        try:
            response = requests.patch(
                f"{self.base_url}/items/versao/{versao_id}",
                headers=self.headers,
                json=data,
                timeout=timeout
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'status_code': 200,
                    'data': response.json().get('data', {})
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': f"HTTP {response.status_code}: {response.text[:500]}"
                }

        except Exception as e:
            return {
                'success': False,
                'status_code': 0,
                'error': f"Exceção: {str(e)}"
            }

    def registrar_resultado_processamento_versao(
        self,
        versao_id: str,
        modificacoes: list[dict[str, Any]],
        status: str = "concluido",
        arquivo_original_id: Optional[str] = None,
        metricas: Optional[dict[str, Any]] = None,
        timeout: int = 300
    ) -> dict[str, Any]:
        """
        Registra o resultado do processamento de uma versão no Directus.

        Este método encapsula toda a lógica de persistência do resultado
        de processamento, incluindo modificações, status e metadados.

        Args:
            versao_id: ID da versão processada
            modificacoes: Lista de modificações no formato Directus (sem id)
            status: Status final da versão (padrão: "concluido")
            arquivo_original_id: ID do arquivo original para referência (opcional)
            metricas: Métricas do processamento (total_blocos, vinculacao, etc.)
            timeout: Timeout em segundos (padrão: 5 minutos)

        Returns:
            dict com:
                - success: bool
                - status_code: int
                - modificacoes_criadas: int (número de modificações criadas)
                - ids_criados: list[str] (IDs das modificações criadas)
                - data: dict (dados completos da resposta)
                - error: str (se falha)

        Raises:
            requests.RequestException: Em caso de erro de comunicação

        Example:
            >>> repo = DirectusRepository("https://directus.test")
            >>> modificacoes = [
            ...     {
            ...         "versao": "versao-123",
            ...         "categoria": "modificacao",
            ...         "conteudo": "texto original",
            ...         "alteracao": "texto novo",
            ...         "posicao_inicio": 100,
            ...         "posicao_fim": 200
            ...     }
            ... ]
            >>> result = repo.registrar_resultado_processamento_versao(
            ...     versao_id="versao-123",
            ...     modificacoes=modificacoes,
            ...     arquivo_original_id="arquivo-456"
            ... )
            >>> if result['success']:
            ...     print(f"Criadas {result['modificacoes_criadas']} modificações")
        """
        # Montar dados de atualização
        update_data: dict[str, Any] = {
            "modificacoes": modificacoes,
            "status": status,
            "data_hora_processamento": datetime.now().isoformat()
        }

        # Adicionar arquivo original se fornecido
        if arquivo_original_id:
            update_data["modifica_arquivo"] = arquivo_original_id

        # Adicionar métricas se fornecidas
        if metricas:
            # Extrair métricas conhecidas para campos específicos
            if "total_blocos" in metricas:
                update_data["total_blocos"] = metricas["total_blocos"]
            if "taxa_vinculacao" in metricas:
                update_data["taxa_vinculacao"] = metricas["taxa_vinculacao"]
            if "metodo_processamento" in metricas:
                update_data["metodo_processamento"] = metricas["metodo_processamento"]

        # Usar update_versao base para fazer a atualização
        result = self.update_versao(versao_id, update_data, timeout=timeout)

        # Enriquecer resultado com informações específicas
        if result['success']:
            response_data = result.get("data", {})
            modificacoes_criadas = response_data.get("modificacoes", [])

            return {
                "success": True,
                "status_code": result['status_code'],
                "modificacoes_criadas": len(modificacoes_criadas),
                "ids_criados": [
                    m if isinstance(m, str) else m.get("id")
                    for m in modificacoes_criadas
                ] if modificacoes_criadas else [],
                "data": response_data
            }
        else:
            return {
                "success": False,
                "status_code": result['status_code'],
                "modificacoes_criadas": 0,
                "ids_criados": [],
                "error": result.get('error', 'Erro desconhecido')
            }

    def get_modificacoes_versao(
        self,
        versao_id: str,
        fields: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        """
        Busca todas as modificações de uma versão.

        Args:
            versao_id: ID da versão
            fields: Campos a retornar nas modificações

        Returns:
            Lista de modificações (pode ser vazia)

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        params = {
            'filter[versao][_eq]': versao_id,
            'limit': -1  # Sem limite
        }

        if fields:
            params['fields'] = ','.join(fields)

        response = requests.get(
            f"{self.base_url}/items/modificacao",
            headers=self.headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            response.raise_for_status()
            return []

    # ============================================================================
    # MÉTODOS DE ARQUIVO
    # ============================================================================

    def get_arquivo_id(self, versao_data: dict[str, Any]) -> Optional[str]:
        """
        Extrai o ID do arquivo original de uma versão.

        Lida com duas estruturas:
        1. Nested object: contrato.modelo_contrato.arquivo_original.id
        2. Simple ID: contrato.modelo_contrato.arquivo_original (string)

        Args:
            versao_data: Dados da versão (resultado de get_versao)

        Returns:
            ID do arquivo ou None se não encontrado
        """
        try:
            contrato = versao_data.get('contrato', {})
            if not contrato:
                return None

            modelo = contrato.get('modelo_contrato', {})
            if not modelo:
                return None

            arquivo = modelo.get('arquivo_original')
            if not arquivo:
                return None

            # Se arquivo é dict (nested object), pegar o 'id'
            if isinstance(arquivo, dict):
                return arquivo.get('id')

            # Se arquivo é string, é o próprio ID
            if isinstance(arquivo, str):
                return arquivo

            return None

        except (AttributeError, TypeError):
            return None

    def download_file(
        self,
        file_id: str,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Faz download de um arquivo do Directus.

        Args:
            file_id: ID do arquivo no Directus
            output_path: Caminho de destino (se None, cria arquivo temporário)

        Returns:
            Path do arquivo baixado ou None em caso de erro

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        response = requests.get(
            f"{self.base_url}/assets/{file_id}",
            headers=self.headers,
            timeout=60
        )

        if response.status_code != 200:
            response.raise_for_status()
            return None

        # Se não forneceu path, criar arquivo temporário
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.docx'
            )
            output_path = Path(temp_file.name)
            temp_file.close()

        # Escrever conteúdo
        output_path.write_bytes(response.content)
        return output_path

    # ============================================================================
    # MÉTODOS DE CLÁUSULA
    # ============================================================================

    def get_clausulas_modelo(
        self,
        modelo_contrato_id: str,
        fields: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        """
        Busca todas as cláusulas de um modelo de contrato.

        Args:
            modelo_contrato_id: ID do modelo de contrato
            fields: Campos a retornar

        Returns:
            Lista de cláusulas (pode ser vazia)

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        params = {
            'filter[modelo_contrato][_eq]': modelo_contrato_id,
            'limit': -1
        }

        if fields:
            params['fields'] = ','.join(fields)

        response = requests.get(
            f"{self.base_url}/items/clausula",
            headers=self.headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            response.raise_for_status()
            return []

    # ============================================================================
    # MÉTODOS DE CONTRATO
    # ============================================================================

    def get_contratos(
        self,
        filters: Optional[dict[str, Any]] = None,
        fields: Optional[list[str]] = None,
        limit: int = -1
    ) -> list[dict[str, Any]]:
        """
        Lista contratos com filtros opcionais.

        Args:
            filters: Filtros no formato Directus
            fields: Campos a retornar (suporta nested)
            limit: Limite de resultados (-1 = sem limite)

        Returns:
            Lista de contratos

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        params: dict[str, Any] = {'limit': limit}

        if fields:
            params['fields'] = ','.join(fields)

        if filters:
            # Converter dict de filtros para query params do Directus
            for key, value in filters.items():
                params[f'filter[{key}]'] = value

        response = requests.get(
            f"{self.base_url}/items/contrato",
            headers=self.headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            response.raise_for_status()
            return []

    # ============================================================================
    # MÉTODOS DE TESTE/DIAGNÓSTICO
    # ============================================================================

    def test_connection(self) -> dict[str, Any]:
        """
        Testa conexão com o Directus.

        Returns:
            dict com:
                - success: bool
                - status_code: int
                - message: str
        """
        try:
            response = requests.get(
                f"{self.base_url}/server/info",
                headers=self.headers,
                timeout=10
            )

            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'message': 'Conectado' if response.status_code == 200 else f'HTTP {response.status_code}'
            }

        except Exception as e:
            return {
                'success': False,
                'status_code': 0,
                'message': f'Erro: {str(e)}'
            }
