#!/usr/bin/env python3
"""
Calculadora de posições utilitária para uniformizar o cálculo de posições
entre tags e modificações no sistema de agrupamento posicional.

Garante que ambos usem o mesmo sistema de coordenadas baseado em texto limpo.
"""

import re
import subprocess
import tempfile


class PositionCalculator:
    """
    Classe utilitária para calcular posições consistentes no documento
    """

    @staticmethod
    def docx_to_clean_text(docx_path: str) -> str:
        """
        Converte DOCX para texto limpo usando pandoc

        Args:
            docx_path: Caminho para o arquivo DOCX

        Returns:
            str: Texto limpo sem formatação
        """
        try:
            # Converter para HTML temporário
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as html_temp:
                html_temp_name = html_temp.name

            # Usar pandoc para conversão
            subprocess.run(
                ["pandoc", docx_path, "-o", html_temp_name],
                check=True,
                capture_output=True,
            )

            # Ler HTML e converter para texto limpo
            with open(html_temp_name, encoding="utf-8") as f:
                html_content = f.read()

            # Limpar HTML para texto puro
            clean_text = PositionCalculator.html_to_clean_text(html_content)

            return clean_text

        except Exception as e:
            print(f"❌ Erro ao converter DOCX para texto: {e}")
            return ""

    @staticmethod
    def html_to_clean_text(html_content: str) -> str:
        """
        Converte HTML para texto limpo consistente

        Args:
            html_content: Conteúdo HTML

        Returns:
            str: Texto limpo
        """
        # Remover comentários HTML
        html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)

        # Remover tags de formatação preservando conteúdo
        html_content = re.sub(
            r"<strong[^>]*>(.*?)</strong>", r"\1", html_content, flags=re.DOTALL
        )
        html_content = re.sub(
            r"<b[^>]*>(.*?)</b>", r"\1", html_content, flags=re.DOTALL
        )
        html_content = re.sub(
            r"<em[^>]*>(.*?)</em>", r"\1", html_content, flags=re.DOTALL
        )
        html_content = re.sub(
            r"<i[^>]*>(.*?)</i>", r"\1", html_content, flags=re.DOTALL
        )
        html_content = re.sub(
            r"<u[^>]*>(.*?)</u>", r"\1", html_content, flags=re.DOTALL
        )
        html_content = re.sub(
            r"<mark[^>]*>(.*?)</mark>", r"\1", html_content, flags=re.DOTALL
        )

        # Converter listas para texto simples
        html_content = re.sub(
            r"<li[^>]*><p[^>]*>(.*?)</p></li>", r"• \1\n", html_content, flags=re.DOTALL
        )
        html_content = re.sub(
            r"<li[^>]*>(.*?)</li>", r"• \1\n", html_content, flags=re.DOTALL
        )
        html_content = re.sub(r"<ol[^>]*>|</ol>", "", html_content)
        html_content = re.sub(r"<ul[^>]*>|</ul>", "", html_content)

        # Converter parágrafos e quebras
        html_content = re.sub(r"<p[^>]*>|</p>", "\n", html_content)
        html_content = re.sub(r"<br[^>]*/?>", "\n", html_content)

        # Remover todas as outras tags HTML
        html_content = re.sub(r"<[^>]+>", "", html_content)

        # Decodificar entidades HTML
        html_content = re.sub(r"&nbsp;", " ", html_content)
        html_content = re.sub(r"&amp;", "&", html_content)
        html_content = re.sub(r"&lt;", "<", html_content)
        html_content = re.sub(r"&gt;", ">", html_content)
        html_content = re.sub(r"&quot;", '"', html_content)

        # Normalizar espaços em branco
        html_content = re.sub(r"\n\s*\n", "\n", html_content)
        html_content = re.sub(r"[ \t]+", " ", html_content)

        return html_content.strip()

    @staticmethod
    def calculate_text_position(content: str, reference_text: str) -> tuple[int, int]:
        """
        Calcula posição de um conteúdo no texto de referência

        Args:
            content: Conteúdo a ser localizado
            reference_text: Texto de referência

        Returns:
            tuple[int, int]: (posição_início, posição_fim) ou (0, 0) se não encontrado
        """
        if not content or not reference_text:
            return (0, 0)

        # Limpar conteúdo para busca
        content_clean = content.strip()

        # Busca exata primeiro
        pos_inicio = reference_text.find(content_clean)
        if pos_inicio != -1:
            pos_fim = pos_inicio + len(content_clean)
            return (pos_inicio, pos_fim)

        # Busca por fragmentos se não encontrou exato
        words = content_clean.split()[:5]  # Primeiras 5 palavras
        for word in words:
            if len(word) > 3:  # Ignorar palavras muito pequenas
                pos = reference_text.find(word)
                if pos != -1:
                    # Estimar fim baseado no tamanho do conteúdo original
                    estimated_end = pos + len(content_clean)
                    return (pos, estimated_end)

        return (0, 0)

    @staticmethod
    def normalize_position_from_path(path: str) -> int | None:
        """
        Extrai posição numérica de caminhos estruturais
        Compatível com o método existente do agrupador

        Args:
            path: Caminho estrutural como 'modificacao_X_linha_Y_pos_Z'

        Returns:
            int: Posição extraída ou None se não encontrada
        """
        if not path:
            return None

        # Padrão pos_número (preferido)
        match = re.search(r"pos_(\d+)", path)
        if match:
            return int(match.group(1))

        # Padrão de índices estruturais como fallback
        numeros = re.findall(r"\[(\d+)\]", path)
        if numeros:
            posicao = 0
            for i, num in enumerate(numeros):
                peso = 1000 ** (len(numeros) - i - 1)
                posicao += int(num) * peso
            return posicao

        return 0

    @staticmethod
    def calculate_unified_positions(
        arquivo_original_path: str,
        arquivo_modificado_path: str,
        tags_content: list,
        modificacoes_content: list,
    ) -> dict:
        """
        Calcula posições unificadas para tags e modificações usando o mesmo texto base

        Args:
            arquivo_original_path: Caminho do arquivo original
            arquivo_modificado_path: Caminho do arquivo modificado
            tags_content: Lista de tags com conteúdo
            modificacoes_content: Lista de modificações com conteúdo

        Returns:
            dict: Dicionário com posições calculadas para tags e modificações
        """
        try:
            # Usar arquivo original como base de referência
            reference_text = PositionCalculator.docx_to_clean_text(
                arquivo_original_path
            )

            if not reference_text:
                print("❌ Não foi possível extrair texto de referência")
                return {"tags": {}, "modificacoes": {}, "reference_text": ""}

            print(f"📄 Texto de referência extraído: {len(reference_text)} caracteres")

            # Calcular posições das tags
            tags_positions = {}
            for tag in tags_content:
                tag_id = tag.get("id")
                tag_content = tag.get("conteudo", "")

                if tag_id and tag_content:
                    pos_inicio, pos_fim = PositionCalculator.calculate_text_position(
                        tag_content, reference_text
                    )
                    tags_positions[tag_id] = {
                        "inicio": pos_inicio,
                        "fim": pos_fim,
                        "nome": tag.get("tag_nome", ""),
                        "conteudo": tag_content[:50] + "..."
                        if len(tag_content) > 50
                        else tag_content,
                    }
                    print(f"🏷️  Tag '{tag.get('tag_nome')}': {pos_inicio}-{pos_fim}")

            # Calcular posições das modificações
            modificacoes_positions = {}
            for mod in modificacoes_content:
                mod_id = mod.get("id")
                mod_content = mod.get("conteudo", "")

                if mod_id and mod_content:
                    pos_inicio, pos_fim = PositionCalculator.calculate_text_position(
                        mod_content, reference_text
                    )
                    modificacoes_positions[mod_id] = {
                        "inicio": pos_inicio,
                        "fim": pos_fim,
                        "conteudo": mod_content[:50] + "..."
                        if len(mod_content) > 50
                        else mod_content,
                    }

            print(f"✅ Calculadas {len(tags_positions)} posições de tags")
            print(
                f"✅ Calculadas {len(modificacoes_positions)} posições de modificações"
            )

            return {
                "tags": tags_positions,
                "modificacoes": modificacoes_positions,
                "reference_text": reference_text,
            }

        except Exception as e:
            print(f"❌ Erro ao calcular posições unificadas: {e}")
            return {"tags": {}, "modificacoes": {}, "reference_text": ""}
