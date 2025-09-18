#!/usr/bin/env python3
"""
Implementações Mock dos Protocols para testes
Versões mockadas que não dependem de serviços externos.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from .pipeline_funcional import (
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


class ProcessadorTextoMock:
    """Implementação mock do ProcessadorTexto para testes."""

    def extrair_texto(self, caminho: Path) -> ConteudoTexto:
        """
        Extrai texto mockado baseado no nome do arquivo.

        Args:
            caminho: Caminho do arquivo (usado para gerar conteúdo específico)

        Returns:
            Texto mockado predefinido
        """
        nome_arquivo = caminho.name.lower()

        if "original" in nome_arquivo:
            return ConteudoTexto(
                "Documento original com {{nome}} e {{valor}}.\n"
                "Este é um contrato de prestação de serviços.\n"
                "O prazo é de {{prazo}} dias úteis."
            )
        elif "modificado" in nome_arquivo or "alterado" in nome_arquivo:
            return ConteudoTexto(
                "Documento modificado com {{nome}} e {{preco}}.\n"
                "Este é um contrato de prestação de serviços alterado.\n"
                "O prazo é de {{prazo}} dias corridos."
            )
        else:
            return ConteudoTexto(
                "Texto mock padrão com {{tag1}} e {{tag2}}.\n"
                "Conteúdo de exemplo para testes."
            )

    def extrair_metadados(self, caminho: Path) -> Metadados:
        """
        Extrai metadados mockados.

        Args:
            caminho: Caminho do arquivo

        Returns:
            Metadados mockados consistentes
        """
        return Metadados(
            autor="Mock Author",
            data_criacao=datetime(2024, 1, 1, 10, 0, 0),
            data_modificacao=datetime(2024, 1, 2, 15, 30, 0),
            versao="1.0.0",
            tamanho_bytes=1024,
            hash_conteudo=HashDocumento(f"mock_hash_{hash(str(caminho))}"),
        )


class AnalisadorTagsMock:
    """Implementação mock do AnalisadorTags para testes."""

    def extrair_tags(self, texto: ConteudoTexto) -> list[Tag]:
        """
        Extrai tags mockadas do texto.

        Args:
            texto: Texto para analisar

        Returns:
            Lista de tags mockadas baseadas no conteúdo
        """
        tags = []

        # Tags padrão sempre presentes
        tags_padrao = [
            ("nome", "{{nome}}"),
            ("valor", "{{valor}}"),
            ("preco", "{{preco}}"),
            ("prazo", "{{prazo}}"),
            ("tag1", "{{tag1}}"),
            ("tag2", "{{tag2}}"),
        ]

        for i, (nome_tag, conteudo_tag) in enumerate(tags_padrao):
            if conteudo_tag in texto:
                tag = Tag(
                    id=TagId(f"mock_tag_{nome_tag}_{i}"),
                    nome=nome_tag,
                    conteudo=ConteudoTexto(conteudo_tag),
                    posicao_inicio=PosicaoTexto(linha=i + 1, coluna=1, offset=i * 10),
                    posicao_fim=PosicaoTexto(
                        linha=i + 1,
                        coluna=len(conteudo_tag),
                        offset=i * 10 + len(conteudo_tag),
                    ),
                    tipo="mock",
                    aninhada=False,
                )
                tags.append(tag)

        return tags

    def validar_tags(self, tags: list[Tag], modelo: ModeloContrato) -> bool:
        """
        Valida tags mockadas (sempre válidas para simplificar testes).

        Args:
            tags: Lista de tags para validar
            modelo: Modelo de contrato

        Returns:
            True se as tags obrigatórias estão presentes
        """
        tags_encontradas = {tag.nome for tag in tags}
        tags_obrigatorias = {str(tag_id) for tag_id in modelo.tags_obrigatorias}

        # Retorna True se todas as tags obrigatórias foram encontradas
        return tags_obrigatorias.issubset(tags_encontradas)


class ComparadorDocumentosMock:
    """Implementação mock do ComparadorDocumentos para testes."""

    def comparar(self, original: Documento, modificado: Documento) -> list[Modificacao]:
        """
        Compara documentos e retorna modificações mockadas.

        Args:
            original: Documento original
            modificado: Documento modificado

        Returns:
            Lista de modificações mockadas previsíveis
        """
        modificacoes = []

        # Modificação 1: Alteração de "valor" para "preco"
        if (
            "{{valor}}" in original.conteudo_texto
            and "{{preco}}" in modificado.conteudo_texto
        ):
            modificacoes.append(
                Modificacao(
                    id="mock_mod_1_valor_preco",
                    tipo=TipoModificacao.ALTERACAO,
                    posicao_original=PosicaoTexto(linha=1, coluna=25, offset=25),
                    posicao_nova=PosicaoTexto(linha=1, coluna=25, offset=25),
                    conteudo_original=ConteudoTexto("{{valor}}"),
                    conteudo_novo=ConteudoTexto("{{preco}}"),
                    confianca=0.95,
                    tags_relacionadas={TagId("valor"), TagId("preco")},
                )
            )

        # Modificação 2: Alteração de "dias úteis" para "dias corridos"
        if (
            "dias úteis" in original.conteudo_texto
            and "dias corridos" in modificado.conteudo_texto
        ):
            modificacoes.append(
                Modificacao(
                    id="mock_mod_2_dias_uteis_corridos",
                    tipo=TipoModificacao.ALTERACAO,
                    posicao_original=PosicaoTexto(linha=3, coluna=15, offset=85),
                    posicao_nova=PosicaoTexto(linha=3, coluna=15, offset=85),
                    conteudo_original=ConteudoTexto("dias úteis"),
                    conteudo_novo=ConteudoTexto("dias corridos"),
                    confianca=0.90,
                    tags_relacionadas={TagId("prazo")},
                )
            )

        # Modificação 3: Inserção de "alterado"
        if (
            "alterado" in modificado.conteudo_texto
            and "alterado" not in original.conteudo_texto
        ):
            modificacoes.append(
                Modificacao(
                    id="mock_mod_3_insercao_alterado",
                    tipo=TipoModificacao.INSERCAO,
                    posicao_original=PosicaoTexto(linha=2, coluna=50, offset=70),
                    posicao_nova=PosicaoTexto(linha=2, coluna=50, offset=70),
                    conteudo_original=ConteudoTexto(""),
                    conteudo_novo=ConteudoTexto(" alterado"),
                    confianca=0.85,
                    tags_relacionadas=set(),
                )
            )

        # Se não encontrou modificações específicas, criar uma genérica
        if not modificacoes:
            modificacoes.append(
                Modificacao(
                    id="mock_mod_generica",
                    tipo=TipoModificacao.ALTERACAO,
                    posicao_original=PosicaoTexto(linha=1, coluna=1, offset=0),
                    posicao_nova=PosicaoTexto(linha=1, coluna=1, offset=0),
                    conteudo_original=ConteudoTexto("mock original"),
                    conteudo_novo=ConteudoTexto("mock modificado"),
                    confianca=0.80,
                    tags_relacionadas=set(),
                )
            )

        return modificacoes


class AgrupadorModificacoesMock:
    """Implementação mock do AgrupadorModificacoes para testes."""

    def agrupar_por_proximidade(
        self, modificacoes: list[Modificacao]
    ) -> list[BlocoModificacao]:
        """
        Agrupa modificações mockadas de forma previsível.

        Args:
            modificacoes: Lista de modificações para agrupar

        Returns:
            Lista de blocos mockados
        """
        if not modificacoes:
            return []

        blocos = []

        # Agrupar modificações em blocos de até 3 modificações
        tamanho_bloco = 3
        for i in range(0, len(modificacoes), tamanho_bloco):
            grupo = modificacoes[i : i + tamanho_bloco]

            # Determinar posições do bloco
            posicoes = []
            for mod in grupo:
                if mod.posicao_original:
                    posicoes.append(mod.posicao_original)
                if mod.posicao_nova:
                    posicoes.append(mod.posicao_nova)

            if posicoes:
                posicoes.sort(key=lambda p: p.linha)
                posicao_inicio = posicoes[0]
                posicao_fim = posicoes[-1]
            else:
                posicao_inicio = PosicaoTexto(linha=1, coluna=1, offset=0)
                posicao_fim = PosicaoTexto(linha=1, coluna=10, offset=10)

            # Determinar tipo predominante
            tipos_count = {}
            for mod in grupo:
                tipos_count[mod.tipo] = tipos_count.get(mod.tipo, 0) + 1

            tipo_predominante = max(tipos_count.keys(), key=lambda t: tipos_count[t])

            # Calcular relevância mockada
            relevancia = min(1.0, len(grupo) / 5.0)

            bloco = BlocoModificacao(
                id=BlocoId(f"mock_bloco_{i // tamanho_bloco + 1}"),
                modificacoes=grupo,
                posicao_inicio=posicao_inicio,
                posicao_fim=posicao_fim,
                tipo_predominante=tipo_predominante,
                relevancia=relevancia,
            )

            blocos.append(bloco)

        return blocos


class FactoryImplementacoesMock:
    """Factory para criar implementações mock para testes."""

    def __init__(self, dados_customizados: dict[str, Any] | None = None):
        """
        Inicializa factory com dados customizados opcionais.

        Args:
            dados_customizados: Dados para customizar comportamento dos mocks
        """
        self.dados_customizados = dados_customizados or {}

    def criar_processador_texto(self) -> ProcessadorTexto:
        """Cria implementação mock do ProcessadorTexto."""
        return ProcessadorTextoMock()

    def criar_analisador_tags(self) -> AnalisadorTags:
        """Cria implementação mock do AnalisadorTags."""
        return AnalisadorTagsMock()

    def criar_comparador_documentos(self) -> ComparadorDocumentos:
        """Cria implementação mock do ComparadorDocumentos."""
        return ComparadorDocumentosMock()

    def criar_agrupador_modificacoes(self) -> AgrupadorModificacoes:
        """Cria implementação mock do AgrupadorModificacoes."""
        return AgrupadorModificacoesMock()

    def criar_todos(
        self,
    ) -> tuple[
        ProcessadorTexto, AnalisadorTags, ComparadorDocumentos, AgrupadorModificacoes
    ]:
        """Cria todas as implementações mock de uma vez."""
        return (
            self.criar_processador_texto(),
            self.criar_analisador_tags(),
            self.criar_comparador_documentos(),
            self.criar_agrupador_modificacoes(),
        )
