#!/usr/bin/env python3
"""
Implementações reais dos Protocols para acesso ao Directus
Inversão de dependência com implementações concretas.
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from src.docx_compare.core.pipeline_funcional import (
    AgrupadorModificacoes,
    AnalisadorTags,
    BlocoId,
    BlocoModificacao,
    ComparadorDocumentos,
    ConteudoTexto,
    Documento,
    HashDocumento,
    Metadados,
    ModeloContrato,
    Modificacao,
    PosicaoTexto,
    ProcessadorTexto,
    Tag,
    TagId,
    TipoModificacao,
)


@dataclass
class ConfiguracaoDirectus:
    """Configuração de conexão com Directus."""

    url_base: str
    token: str
    timeout: int = 30

    @classmethod
    def from_env(cls) -> "ConfiguracaoDirectus":
        """Cria configuração a partir de variáveis de ambiente."""
        url_base = os.getenv("DIRECTUS_BASE_URL")
        token = os.getenv("DIRECTUS_TOKEN")

        if not url_base:
            raise ValueError("DIRECTUS_BASE_URL deve ser definida no arquivo .env")
        if not token:
            raise ValueError("DIRECTUS_TOKEN deve ser definido no arquivo .env")

        return cls(
            url_base=url_base,
            token=token,
            timeout=int(os.getenv("DIRECTUS_TIMEOUT", "30")),
        )


class ProcessadorTextoDirectus:
    """Implementação real do ProcessadorTexto usando Directus."""

    def __init__(self, config: ConfiguracaoDirectus):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {config.token}",
                "Content-Type": "application/json",
            }
        )

    def extrair_texto(self, caminho: Path) -> ConteudoTexto:
        """
        Extrai texto de um arquivo DOCX usando pandoc.

        Args:
            caminho: Caminho para o arquivo DOCX

        Returns:
            Texto extraído do documento
        """
        try:
            import subprocess

            # Usar pandoc para converter DOCX para texto
            resultado = subprocess.run(
                ["pandoc", str(caminho), "-t", "plain"],
                capture_output=True,
                text=True,
                check=True,
            )

            return ConteudoTexto(resultado.stdout.strip())

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: tentar ler como texto simples
            try:
                with open(caminho, encoding="utf-8") as f:
                    return ConteudoTexto(f.read())
            except Exception:
                return ConteudoTexto("")

    def extrair_metadados(self, caminho: Path) -> Metadados:
        """
        Extrai metadados de um documento.

        Args:
            caminho: Caminho para o arquivo

        Returns:
            Metadados do documento
        """
        try:
            stat = caminho.stat()

            # Calcular hash do arquivo
            import hashlib

            with open(caminho, "rb") as f:
                hash_conteudo = hashlib.md5(f.read()).hexdigest()

            return Metadados(
                autor=os.getenv("USER", "desconhecido"),
                data_criacao=datetime.fromtimestamp(stat.st_ctime),
                data_modificacao=datetime.fromtimestamp(stat.st_mtime),
                versao="1.0",
                tamanho_bytes=stat.st_size,
                hash_conteudo=HashDocumento(hash_conteudo),
            )

        except Exception:
            # Metadados padrão em caso de erro
            return Metadados(
                autor="desconhecido",
                data_criacao=datetime.now(),
                data_modificacao=datetime.now(),
                versao="1.0",
                tamanho_bytes=0,
                hash_conteudo=HashDocumento("error"),
            )


class AnalisadorTagsDirectus:
    """Implementação real do AnalisadorTags usando Directus."""

    def __init__(self, config: ConfiguracaoDirectus):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {config.token}",
                "Content-Type": "application/json",
            }
        )

    def extrair_tags(self, texto: ConteudoTexto) -> list[Tag]:
        """
        Extrai tags do texto usando regex e validação via Directus.

        Args:
            texto: Texto para analisar

        Returns:
            Lista de tags encontradas
        """
        tags = []

        # Padrões para diferentes tipos de tags
        padroes = [
            r"\{\{([a-zA-Z_][a-zA-Z0-9_.]*)\}\}",  # {{tag}}
            r"\{\{([0-9]+(?:\.[0-9]+)*)\}\}",  # {{1.2.3}}
            r"\{\{TAG-([a-zA-Z0-9_.]+)\}\}",  # {{TAG-xyz}}
        ]

        for padrao in padroes:
            matches = re.finditer(padrao, texto, re.IGNORECASE)

            for match in matches:
                nome_tag = match.group(1).strip().lower()
                posicao_inicio = PosicaoTexto(
                    linha=texto[: match.start()].count("\n") + 1,
                    coluna=match.start() - texto.rfind("\n", 0, match.start()),
                    offset=match.start(),
                )
                posicao_fim = PosicaoTexto(
                    linha=texto[: match.end()].count("\n") + 1,
                    coluna=match.end() - texto.rfind("\n", 0, match.end()),
                    offset=match.end(),
                )

                tag = Tag(
                    id=TagId(f"tag_{nome_tag}_{match.start()}"),
                    nome=nome_tag,
                    conteudo=ConteudoTexto(match.group(0)),
                    posicao_inicio=posicao_inicio,
                    posicao_fim=posicao_fim,
                    tipo="automatica",
                    aninhada=False,
                )

                tags.append(tag)

        return tags

    def validar_tags(self, tags: list[Tag], modelo: ModeloContrato) -> bool:
        """
        Valida tags contra um modelo de contrato via Directus.

        Args:
            tags: Lista de tags para validar
            modelo: Modelo de contrato

        Returns:
            True se as tags são válidas

        Raises:
            requests.RequestException: Se houver erro na comunicação com Directus
        """
        # Buscar validações do modelo no Directus
        url = f"{self.config.url_base}/items/contratos_modelos/{modelo.id}"
        response = self.session.get(url, timeout=self.config.timeout)

        if response.status_code == 200:
            dados_modelo = response.json().get("data", {})
            tags_obrigatorias = set(dados_modelo.get("tags_obrigatorias", []))

            # Verificar se todas as tags obrigatórias estão presentes
            tags_encontradas = {tag.nome for tag in tags}

            return tags_obrigatorias.issubset(tags_encontradas)

        # Se não encontrar o modelo, usar dados locais
        elif response.status_code == 404:
            tags_encontradas = {tag.nome for tag in tags}
            return modelo.tags_obrigatorias.issubset(tags_encontradas)

        # Para outros erros, lançar exceção
        else:
            response.raise_for_status()
            return False  # Never reached, but satisfies type checker


class ComparadorDocumentosDirectus:
    """Implementação real do ComparadorDocumentos usando Directus para logging."""

    def __init__(self, config: ConfiguracaoDirectus):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {config.token}",
                "Content-Type": "application/json",
            }
        )

    def comparar(self, original: Documento, modificado: Documento) -> list[Modificacao]:
        """
        Compara dois documentos e registra no Directus.

        Args:
            original: Documento original
            modificado: Documento modificado

        Returns:
            Lista de modificações encontradas
        """
        modificacoes = []

        try:
            # Análise básica de diferenças
            texto_original = original.conteudo_texto
            texto_modificado = modificado.conteudo_texto

            # Usar difflib para encontrar diferenças
            import difflib

            linhas_original = texto_original.splitlines()
            linhas_modificado = texto_modificado.splitlines()

            diff = difflib.unified_diff(
                linhas_original,
                linhas_modificado,
                lineterm="",
                n=0,  # Sem contexto
            )

            linha_atual = 0
            for linha_diff in diff:
                if linha_diff.startswith("@@"):
                    # Extrair número da linha do cabeçalho @@
                    match = re.search(r"-(\d+)", linha_diff)
                    if match:
                        linha_atual = int(match.group(1))

                elif linha_diff.startswith("-"):
                    # Linha removida
                    conteudo = linha_diff[1:]
                    modificacao = Modificacao(
                        id=f"mod_rem_{hash(conteudo)}_{linha_atual}",
                        tipo=TipoModificacao.REMOCAO,
                        posicao_original=PosicaoTexto(
                            linha=linha_atual, coluna=0, offset=0
                        ),
                        posicao_nova=None,
                        conteudo_original=ConteudoTexto(conteudo),
                        conteudo_novo=None,
                        confianca=0.9,
                        tags_relacionadas=set(),
                    )
                    modificacoes.append(modificacao)

                elif linha_diff.startswith("+"):
                    # Linha adicionada
                    conteudo = linha_diff[1:]
                    modificacao = Modificacao(
                        id=f"mod_add_{hash(conteudo)}_{linha_atual}",
                        tipo=TipoModificacao.INSERCAO,
                        posicao_original=PosicaoTexto(
                            linha=linha_atual, coluna=0, offset=0
                        ),
                        posicao_nova=PosicaoTexto(
                            linha=linha_atual, coluna=0, offset=0
                        ),
                        conteudo_original=ConteudoTexto(""),  # Vazio para inserção
                        conteudo_novo=ConteudoTexto(conteudo),
                        confianca=0.9,
                        tags_relacionadas=set(),
                    )
                    modificacoes.append(modificacao)

                linha_atual += 1

            # Registrar comparação no Directus
            self._registrar_comparacao(original, modificado, modificacoes)

            return modificacoes

        except Exception as e:
            # Em caso de erro, retornar lista vazia
            print(f"Erro na comparação: {e}")
            return []

    def _registrar_comparacao(
        self,
        original: Documento,
        modificado: Documento,
        modificacoes: list[Modificacao],
    ):
        """
        Registra a comparação no Directus para auditoria.

        Raises:
            requests.RequestException: Se houver erro na comunicação com Directus
        """
        dados_log = {
            "documento_original_id": original.id,
            "documento_modificado_id": modificado.id,
            "total_modificacoes": len(modificacoes),
            "data_comparacao": datetime.now().isoformat(),
            "tipos_modificacao": {
                tipo.value: len([m for m in modificacoes if m.tipo == tipo])
                for tipo in TipoModificacao
            },
        }

        url = f"{self.config.url_base}/items/logs_comparacao"
        response = self.session.post(url, json=dados_log, timeout=self.config.timeout)
        response.raise_for_status()


class AgrupadorModificacoesDirectus:
    """Implementação real do AgrupadorModificacoes usando Directus para configurações."""

    def __init__(self, config: ConfiguracaoDirectus):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {config.token}",
                "Content-Type": "application/json",
            }
        )

    def agrupar_por_proximidade(
        self, modificacoes: list[Modificacao]
    ) -> list[BlocoModificacao]:
        """
        Agrupa modificações por proximidade usando configurações do Directus.

        Args:
            modificacoes: Lista de modificações

        Returns:
            Lista de blocos de modificações
        """
        if not modificacoes:
            return []

        # Buscar configurações de agrupamento do Directus
        distancia_maxima = self._obter_configuracao("distancia_maxima_agrupamento", 50)

        blocos = []
        modificacoes_ordenadas = sorted(
            modificacoes,
            key=lambda m: m.posicao_original.linha
            if m.posicao_original
            else m.posicao_nova.linha
            if m.posicao_nova
            else 0,
        )

        bloco_atual = []
        posicao_anterior = None

        for modificacao in modificacoes_ordenadas:
            posicao_atual = modificacao.posicao_original or modificacao.posicao_nova

            if posicao_atual is None:
                continue

            # Verificar se deve criar novo bloco
            if (
                posicao_anterior is None
                or abs(posicao_atual.linha - posicao_anterior.linha) > distancia_maxima
            ):
                # Finalizar bloco anterior se existir
                if bloco_atual:
                    blocos.append(self._criar_bloco(bloco_atual))

                # Iniciar novo bloco
                bloco_atual = [modificacao]
            else:
                # Adicionar ao bloco atual
                bloco_atual.append(modificacao)

            posicao_anterior = posicao_atual

        # Finalizar último bloco
        if bloco_atual:
            blocos.append(self._criar_bloco(bloco_atual))

        return blocos

    def _obter_configuracao(self, chave: str, valor_padrao: Any) -> Any:
        """
        Obtém configuração do Directus ou retorna valor padrão.

        Raises:
            requests.RequestException: Se houver erro na comunicação com Directus
        """
        url = f"{self.config.url_base}/items/configuracoes"
        params = {"filter[chave][_eq]": chave}
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()

        if response.status_code == 200:
            dados = response.json().get("data", [])
            if dados:
                return dados[0].get("valor", valor_padrao)

        return valor_padrao

    def _criar_bloco(self, modificacoes: list[Modificacao]) -> BlocoModificacao:
        """Cria um bloco de modificações."""
        if not modificacoes:
            raise ValueError("Lista de modificações não pode estar vazia")

        # Determinar posições de início e fim
        posicoes = []
        for mod in modificacoes:
            if mod.posicao_original:
                posicoes.append(mod.posicao_original)
            if mod.posicao_nova:
                posicoes.append(mod.posicao_nova)

        posicoes.sort(key=lambda p: p.linha)
        posicao_inicio = posicoes[0]
        posicao_fim = posicoes[-1]

        # Determinar tipo predominante
        tipos_count = {}
        for mod in modificacoes:
            tipos_count[mod.tipo] = tipos_count.get(mod.tipo, 0) + 1

        tipo_predominante = max(tipos_count.keys(), key=lambda t: tipos_count[t])

        # Calcular relevância baseada no número de modificações
        relevancia = min(1.0, len(modificacoes) / 10.0)

        return BlocoModificacao(
            id=BlocoId(f"bloco_{hash(str(modificacoes))}"),
            modificacoes=modificacoes,
            posicao_inicio=posicao_inicio,
            posicao_fim=posicao_fim,
            tipo_predominante=tipo_predominante,
            relevancia=relevancia,
        )


class FactoryImplementacoes:
    """Factory para criar implementações com configuração do Directus."""

    def __init__(self, config: ConfiguracaoDirectus | None = None):
        self.config = config or ConfiguracaoDirectus.from_env()

    def criar_processador_texto(self) -> ProcessadorTexto:
        """Cria implementação do ProcessadorTexto."""
        return ProcessadorTextoDirectus(self.config)

    def criar_analisador_tags(self) -> AnalisadorTags:
        """Cria implementação do AnalisadorTags."""
        return AnalisadorTagsDirectus(self.config)

    def criar_comparador_documentos(self) -> ComparadorDocumentos:
        """Cria implementação do ComparadorDocumentos."""
        return ComparadorDocumentosDirectus(self.config)

    def criar_agrupador_modificacoes(self) -> AgrupadorModificacoes:
        """Cria implementação do AgrupadorModificacoes."""
        return AgrupadorModificacoesDirectus(self.config)

    def criar_todos(
        self,
    ) -> tuple[
        ProcessadorTexto, AnalisadorTags, ComparadorDocumentos, AgrupadorModificacoes
    ]:
        """Cria todas as implementações de uma vez."""
        return (
            self.criar_processador_texto(),
            self.criar_analisador_tags(),
            self.criar_comparador_documentos(),
            self.criar_agrupador_modificacoes(),
        )
