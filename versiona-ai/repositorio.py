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
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


class DirectusRepository:
    """
    Repositório para acesso aos dados do Directus.

    Centraliza todas as operações de I/O com o Directus, permitindo
    testabilidade através de mocks e separação clara de responsabilidades.
    """

    def __init__(self, base_url: str, token: str | None = None):
        """
        Inicializa o repositório.

        Args:
            base_url: URL base do Directus (ex: https://api.exemplo.com)
            token: Token de autenticação (se None, busca de DIRECTUS_TOKEN env var)
        """
        self.base_url = base_url.rstrip("/")

        # Configurar headers com token
        if token is None:
            token = os.getenv("DIRECTUS_TOKEN")

        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    # ============================================================================
    # MÉTODOS DE VERSÃO
    # ============================================================================

    def get_versao(
        self,
        versao_id: str,
        fields: list[str] | None = None,
        deep: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """
        Busca uma versão pelo ID.

        Args:
            versao_id: ID da versão
            fields: Lista de campos a buscar (suporta nested: "contrato.modelo_contrato.arquivo_original")
            deep: Parâmetros deep para limitar relacionamentos nested
                  Ex: {"contrato.modelo_contrato.tags": {"_limit": 100}}

        Returns:
            dict com dados da versão ou None se não encontrada

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        params = {}
        if fields:
            params["fields"] = ",".join(fields)

        if deep:
            for key, value in deep.items():
                for param_name, param_value in value.items():
                    params[f"deep[{key}][{param_name}]"] = param_value

        response = requests.get(
            f"{self.base_url}/items/versao/{versao_id}",
            headers=self.headers,
            params=params,
            timeout=30,
        )

        if response.status_code == 200:
            return response.json().get("data")
        elif response.status_code == 404:
            return None
        else:
            response.raise_for_status()
            return None

    def get_versao_para_processar(self, versao_id: str) -> dict[str, Any] | None:
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
        # Usar wildcards para evitar problemas de permissão com campos específicos
        # O Directus retorna apenas os campos que o token tem permissão de acessar
        fields = [
            "*",  # Todos os campos da versão
            "contrato.*",  # Dados do contrato
            "contrato.modelo_contrato.*",  # Dados do modelo incluindo arquivos
            "contrato.modelo_contrato.tags.*",  # Tags do modelo com posições
            "contrato.modelo_contrato.tags.clausulas.*",  # Cláusulas vinculadas
        ]

        # -1 = buscar todos os itens (sem limite)
        deep = {
            "contrato.modelo_contrato.tags": {"_limit": -1},
            "contrato.modelo_contrato.tags.clausulas": {"_limit": -1},
        }

        return self.get_versao(versao_id, fields=fields, deep=deep)

    def get_versao_completa_para_view(self, versao_id: str) -> dict[str, Any] | None:
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
            "contrato.modelo_contrato.*",  # Dados do modelo
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
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            response.raise_for_status()
            return []

    def update_versao(
        self, versao_id: str, data: dict[str, Any], timeout: int = 300
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
                timeout=timeout,
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": 200,
                    "data": response.json().get("data", {}),
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}: {response.text[:500]}",
                }

        except Exception as e:
            return {"success": False, "status_code": 0, "error": f"Exceção: {str(e)}"}

    def registrar_resultado_processamento_versao(
        self,
        versao_id: str,
        modificacoes: list[dict[str, Any]],
        status: str = "concluido",
        arquivo_original_id: str | None = None,
        metricas: dict[str, Any] | None = None,
        timeout: int = 300,
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
            ...         "posicao_fim": 200,
            ...     }
            ... ]
            >>> result = repo.registrar_resultado_processamento_versao(
            ...     versao_id="versao-123",
            ...     modificacoes=modificacoes,
            ...     arquivo_original_id="arquivo-456",
            ... )
            >>> if result["success"]:
            ...     print(f"Criadas {result['modificacoes_criadas']} modificações")
        """
        # Montar dados de atualização
        update_data: dict[str, Any] = {
            "modificacoes": modificacoes,
            "status": status,
            "data_hora_processamento": datetime.now().isoformat(),
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
        if result["success"]:
            response_data = result.get("data", {})
            modificacoes_criadas = response_data.get("modificacoes", [])

            return {
                "success": True,
                "status_code": result["status_code"],
                "modificacoes_criadas": len(modificacoes_criadas),
                "ids_criados": [
                    m if isinstance(m, str) else m.get("id")
                    for m in modificacoes_criadas
                ]
                if modificacoes_criadas
                else [],
                "data": response_data,
            }
        else:
            return {
                "success": False,
                "status_code": result["status_code"],
                "modificacoes_criadas": 0,
                "ids_criados": [],
                "error": result.get("error", "Erro desconhecido"),
            }

    def get_modificacoes_versao(
        self, versao_id: str, fields: list[str] | None = None
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
            "filter[versao][_eq]": versao_id,
            "limit": -1,  # Sem limite
        }

        if fields:
            params["fields"] = ",".join(fields)

        response = requests.get(
            f"{self.base_url}/items/modificacao",
            headers=self.headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        return response.json().get("data", [])

    def get_resumo_processamento_versao(self, versao_id: str) -> dict[str, Any]:
        """
        Retorna um resumo do processamento de uma versão.

        Útil para verificar se o processamento foi bem-sucedido e
        se as modificações foram registradas corretamente.

        Args:
            versao_id: ID da versão a verificar

        Returns:
            dict com:
                - versao_id: str
                - status: str (status da versão no Directus)
                - total_modificacoes: int
                - modificacoes_por_categoria: dict[str, int]
                - modificacoes_com_clausula: int
                - taxa_vinculacao: float (%)
                - data_processamento: str (ISO 8601)
                - modificacoes_sample: list[dict] (primeiras 3)

        Raises:
            requests.RequestException: Em caso de erro de comunicação
        """
        # Buscar modificações com informações básicas + cláusula
        modificacoes = self.get_modificacoes_versao(
            versao_id,
            fields=[
                "id",
                "categoria",
                "clausula",
                "date_created",
                "posicao_inicio",
                "posicao_fim",
            ],
        )

        # Calcular estatísticas
        total = len(modificacoes)
        categorias: dict[str, int] = {}
        com_clausula = 0

        for mod in modificacoes:
            categoria = mod.get("categoria", "unknown")
            categorias[categoria] = categorias.get(categoria, 0) + 1

            if mod.get("clausula"):
                com_clausula += 1

        taxa_vinculacao = (com_clausula / total * 100) if total > 0 else 0.0

        # Pegar data de processamento da modificação mais recente
        data_processamento = None
        if modificacoes:
            # Ordenar por data e pegar a mais recente
            sorted_mods = sorted(
                modificacoes, key=lambda m: m.get("date_created", ""), reverse=True
            )
            data_processamento = sorted_mods[0].get("date_created")

        # Buscar status da versão (simples, sem nested)
        versao_response = requests.get(
            f"{self.base_url}/items/versao/{versao_id}",
            headers=self.headers,
            params={"fields": "status"},
            timeout=10,
        )

        status = "unknown"
        if versao_response.status_code == 200:
            versao_data = versao_response.json().get("data", {})
            status = versao_data.get("status", "unknown")

        return {
            "versao_id": versao_id,
            "status": status,
            "total_modificacoes": total,
            "modificacoes_por_categoria": categorias,
            "modificacoes_com_clausula": com_clausula,
            "taxa_vinculacao": round(taxa_vinculacao, 2),
            "data_processamento": data_processamento,
            "modificacoes_sample": modificacoes[:3],  # Primeiras 3 para inspeção
        }

    def verificar_modificacoes_versao(self, versao_id: str) -> dict[str, Any]:
        """
        Verifica se a versão foi processada e se possui modificações registradas.

        Método simples que retorna True/False sobre o estado do processamento.
        Use este método para validações rápidas e checks de sanidade.

        Args:
            versao_id: ID da versão a verificar

        Returns:
            dict com:
                - sucesso: bool (True se tem modificações)
                - total_modificacoes: int
                - possui_vinculacao: bool (pelo menos 1 modificação tem cláusula)
                - status_versao: str
                - erro: Optional[str] (mensagem de erro se falhou)
        """
        try:
            # Buscar apenas contagem de modificações
            modificacoes = self.get_modificacoes_versao(
                versao_id, fields=["id", "clausula"]
            )

            total = len(modificacoes)
            possui_vinculacao = any(mod.get("clausula") for mod in modificacoes)

            # Buscar status da versão
            versao_response = requests.get(
                f"{self.base_url}/items/versao/{versao_id}",
                headers=self.headers,
                params={"fields": "status"},
                timeout=10,
            )

            status_versao = "unknown"
            if versao_response.status_code == 200:
                versao_data = versao_response.json().get("data", {})
                status_versao = versao_data.get("status", "unknown")

            return {
                "sucesso": total > 0,
                "total_modificacoes": total,
                "possui_vinculacao": possui_vinculacao,
                "status_versao": status_versao,
                "erro": None,
            }

        except requests.RequestException as e:
            return {
                "sucesso": False,
                "total_modificacoes": 0,
                "possui_vinculacao": False,
                "status_versao": "error",
                "erro": str(e),
            }

    def comparar_modificacoes_entre_versoes(
        self, versao_id_1: str, versao_id_2: str
    ) -> dict[str, Any]:
        """
        Compara modificações entre duas versões (útil para verificar reprocessamento).

        Use este método para confirmar se reprocessamento substitui ou acumula modificações.

        Args:
            versao_id_1: ID da primeira versão
            versao_id_2: ID da segunda versão (geralmente reprocessamento da primeira)

        Returns:
            dict com:
                - versao_1_total: int
                - versao_2_total: int
                - diferenca: int (pode ser negativa)
                - ids_apenas_v1: list[str]
                - ids_apenas_v2: list[str]
                - ids_comuns: list[str]
                - conclusao: str ("substitui", "acumula", "igual", ou "erro")
        """
        try:
            # Buscar IDs de ambas as versões
            mods_v1 = self.get_modificacoes_versao(versao_id_1, fields=["id"])
            mods_v2 = self.get_modificacoes_versao(versao_id_2, fields=["id"])

            ids_v1 = {mod["id"] for mod in mods_v1}
            ids_v2 = {mod["id"] for mod in mods_v2}

            apenas_v1 = list(ids_v1 - ids_v2)
            apenas_v2 = list(ids_v2 - ids_v1)
            comuns = list(ids_v1 & ids_v2)

            # Determinar conclusão
            if versao_id_1 == versao_id_2:
                conclusao = "igual"
            elif len(comuns) == 0 and len(apenas_v2) > 0:
                conclusao = "substitui"
            elif len(apenas_v1) > 0 and len(apenas_v2) > 0:
                conclusao = "acumula"
            elif len(apenas_v1) == 0 and len(apenas_v2) == 0:
                conclusao = "igual"
            else:
                conclusao = "parcial"

            return {
                "versao_1_total": len(ids_v1),
                "versao_2_total": len(ids_v2),
                "diferenca": len(ids_v2) - len(ids_v1),
                "ids_apenas_v1": apenas_v1,
                "ids_apenas_v2": apenas_v2,
                "ids_comuns": comuns,
                "conclusao": conclusao,
            }

        except requests.RequestException as e:
            return {
                "versao_1_total": 0,
                "versao_2_total": 0,
                "diferenca": 0,
                "ids_apenas_v1": [],
                "ids_apenas_v2": [],
                "ids_comuns": [],
                "conclusao": f"erro: {e}",
            }

    # ============================================================================
    # MÉTODOS DE ARQUIVO
    # ============================================================================

    def get_arquivo_id(self, versao_data: dict[str, Any]) -> str | None:
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
            contrato = versao_data.get("contrato", {})
            if not contrato:
                return None

            modelo = contrato.get("modelo_contrato", {})
            if not modelo:
                return None

            arquivo = modelo.get("arquivo_original")
            if not arquivo:
                return None

            # Se arquivo é dict (nested object), pegar o 'id'
            if isinstance(arquivo, dict):
                return arquivo.get("id")

            # Se arquivo é string, é o próprio ID
            if isinstance(arquivo, str):
                return arquivo

            return None

        except (AttributeError, TypeError):
            return None

    def download_file(
        self, file_id: str, output_path: Path | None = None
    ) -> Path | None:
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
            f"{self.base_url}/assets/{file_id}", headers=self.headers, timeout=60
        )

        if response.status_code != 200:
            response.raise_for_status()
            return None

        # Se não forneceu path, criar arquivo temporário
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
            output_path = Path(temp_file.name)
            temp_file.close()

        # Escrever conteúdo
        output_path.write_bytes(response.content)
        return output_path

    # ============================================================================
    # MÉTODOS DE CLÁUSULA
    # ============================================================================

    def get_clausulas_modelo(
        self, modelo_contrato_id: str, fields: list[str] | None = None
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
        params = {"filter[modelo_contrato][_eq]": modelo_contrato_id, "limit": -1}

        if fields:
            params["fields"] = ",".join(fields)

        response = requests.get(
            f"{self.base_url}/items/clausula",
            headers=self.headers,
            params=params,
            timeout=30,
        )

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()
            return []

    # ============================================================================
    # MÉTODOS DE CONTRATO
    # ============================================================================

    def get_contratos(
        self,
        filters: dict[str, Any] | None = None,
        fields: list[str] | None = None,
        limit: int = -1,
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
        params: dict[str, Any] = {"limit": limit}

        if fields:
            params["fields"] = ",".join(fields)

        if filters:
            # Converter dict de filtros para query params do Directus
            for key, value in filters.items():
                params[f"filter[{key}]"] = value

        response = requests.get(
            f"{self.base_url}/items/contrato",
            headers=self.headers,
            params=params,
            timeout=30,
        )

        if response.status_code == 200:
            return response.json().get("data", [])
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
                f"{self.base_url}/server/info", headers=self.headers, timeout=10
            )

            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "message": "Conectado"
                if response.status_code == 200
                else f"HTTP {response.status_code}",
            }

        except Exception as e:
            return {"success": False, "status_code": 0, "message": f"Erro: {str(e)}"}
