"""
Processador de Tags para Modelos de Contrato
Extrai tags dos arquivos tagged e salva no Directus
Adaptado do processador histórico para o ambiente versiona-ai
"""

import os
import re
import tempfile

import requests


class ProcessadorTagsModelo:
    """
    Processa modelos de contrato extraindo tags e salvando no Directus
    """

    def __init__(self, directus_base_url: str, directus_token: str):
        self.base_url = directus_base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {directus_token}",
            "Content-Type": "application/json",
        }

    def processar_modelo(self, modelo_id: str, dry_run: bool = False) -> dict:
        """
        Processa um modelo de contrato e extrai suas tags

        Args:
            modelo_id: ID do modelo de contrato
            dry_run: Se True, não faz alterações no Directus

        Returns:
            dict com resultado do processamento
        """
        try:
            print(f"\n🚀 Processando modelo de contrato {modelo_id}")

            # 1. Buscar dados do modelo
            modelo_data = self._buscar_modelo(modelo_id)

            arquivo_original_id = modelo_data.get("arquivo_original")
            arquivo_tagged_id = modelo_data.get("arquivo_com_tags")

            if not arquivo_original_id or not arquivo_tagged_id:
                raise ValueError("Modelo sem arquivos configurados")

            print(f"📁 Arquivo original: {arquivo_original_id}")
            print(f"🏷️  Arquivo com tags: {arquivo_tagged_id}")

            # 2. Baixar e processar arquivos
            texto_original = self._baixar_e_extrair_texto(arquivo_original_id)
            texto_tagged = self._baixar_e_extrair_texto(arquivo_tagged_id)

            print(f"📊 Texto original: {len(texto_original)} caracteres")
            print(f"📊 Texto tagged: {len(texto_tagged)} caracteres")

            # 3. Analisar diferenças
            modificacoes = self._analisar_diferencas(texto_original, texto_tagged)
            print(f"🔍 Encontradas {len(modificacoes)} modificações")

            # 4. Extrair tags das diferenças
            tags_encontradas = self._extrair_tags(modificacoes)
            tag_names = [tag["nome"] for tag in tags_encontradas]
            print(
                f"🏷️  Extraídas {len(tags_encontradas)} tags únicas: {sorted(tag_names)}"
            )

            # 5. Extrair conteúdo entre tags
            conteudo_tags = self._extrair_conteudo_entre_tags(texto_tagged)
            print(f"📝 Conteúdo extraído para {len(conteudo_tags)} tags")

            # 6. Enriquecer tags com conteúdo e filtrar tags órfãs
            tags_validas = []
            tags_orfas = []

            for tag_info in tags_encontradas:
                tag_nome = tag_info["nome"]
                if tag_nome in conteudo_tags:
                    # Adicionar dados do conteúdo extraído
                    conteudo_data = conteudo_tags[tag_nome]
                    tag_info["conteudo"] = conteudo_data["conteudo"]
                    tag_info["posicao_inicial_texto"] = conteudo_data[
                        "posicao_inicial_texto"
                    ]
                    tag_info["posicao_final_texto"] = conteudo_data[
                        "posicao_final_texto"
                    ]
                    tags_validas.append(tag_info)
                else:
                    tags_orfas.append(tag_nome)

            print(f"✨ {len(tags_validas)} tags válidas com conteúdo")
            if tags_orfas:
                print(
                    f"⚠️  {len(tags_orfas)} tags órfãs descartadas: {', '.join(sorted(tags_orfas))}"
                )

            # 7. Atualizar modelo com tags válidas (Directus cria os registros atomicamente)
            if not dry_run:
                self._atualizar_modelo_com_tags(modelo_id, tags_validas)
                print(f"💾 {len(tags_validas)} tags salvas no Directus")
            else:
                print(f"🏃‍♂️ DRY-RUN: {len(tags_validas)} tags seriam criadas")

            return {
                "modelo_id": modelo_id,
                "tags_encontradas": len(tags_encontradas),
                "tags_criadas": len(tags_validas),
                "tags_orfas": len(tags_orfas),
                "modificacoes_analisadas": len(modificacoes),
                "status": "sucesso",
                "dry_run": dry_run,
            }

        except Exception as e:
            print(f"❌ Erro ao processar modelo {modelo_id}: {e}")
            return {"modelo_id": modelo_id, "status": "erro", "erro": str(e)}

    def _buscar_modelo(self, modelo_id: str) -> dict:
        """Busca dados do modelo no Directus"""
        url = f"{self.base_url}/items/modelo_contrato/{modelo_id}"
        params = {"fields": "id,nome,status,arquivo_original,arquivo_com_tags"}

        print(f"🔍 Buscando modelo: {url}")
        print(
            f"🔍 Headers: Authorization Bearer {self.headers.get('Authorization', 'N/A')[:20]}..."
        )

        response = requests.get(url, headers=self.headers, params=params, timeout=10)

        print(f"🔍 Status da resposta: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Resposta de erro: {response.text[:200]}")
            raise ValueError(
                f"Modelo {modelo_id} não encontrado (HTTP {response.status_code})"
            )

        return response.json()["data"]

    def _baixar_e_extrair_texto(self, arquivo_id: str) -> str:
        """Baixa arquivo do Directus e extrai texto"""
        import sys

        # Importar docx_utils do diretório pai
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from docx_utils import convert_docx_to_text

        # Baixar arquivo
        download_url = f"{self.base_url}/assets/{arquivo_id}"
        response = requests.get(download_url, headers=self.headers, timeout=30)

        if response.status_code != 200:
            raise ValueError(
                f"Erro ao baixar arquivo {arquivo_id}: HTTP {response.status_code}"
            )

        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name

        try:
            # Extrair texto usando docx_utils existente
            texto = convert_docx_to_text(temp_path)
            return texto
        finally:
            # Limpar arquivo temporário
            os.unlink(temp_path)

    def _analisar_diferencas(
        self, texto_original: str, texto_modificado: str
    ) -> list[dict]:
        """Analisa diferenças entre os textos"""
        import difflib

        # Dividir em linhas para análise
        linhas_original = texto_original.splitlines()
        linhas_modificado = texto_modificado.splitlines()

        modificacoes = []
        matcher = difflib.SequenceMatcher(None, linhas_original, linhas_modificado)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "replace":
                # Conteúdo substituído
                modificacoes.append(
                    {
                        "categoria": "modificacao",
                        "conteudo": "\n".join(linhas_original[i1:i2]),
                        "alteracao": "\n".join(linhas_modificado[j1:j2]),
                        "linha_inicio": i1,
                        "linha_fim": i2,
                    }
                )
            elif tag == "insert":
                # Conteúdo adicionado
                modificacoes.append(
                    {
                        "categoria": "adicao",
                        "conteudo": "",
                        "alteracao": "\n".join(linhas_modificado[j1:j2]),
                        "linha_inicio": j1,
                        "linha_fim": j2,
                    }
                )
            elif tag == "delete":
                # Conteúdo removido
                modificacoes.append(
                    {
                        "categoria": "remocao",
                        "conteudo": "\n".join(linhas_original[i1:i2]),
                        "alteracao": "",
                        "linha_inicio": i1,
                        "linha_fim": i2,
                    }
                )

        return modificacoes

    def _extrair_tags(self, modificacoes: list[dict]) -> list[dict]:
        """
        Extrai tags das modificações encontradas
        Suporta: {{tag}}, {{ tag }}, {{tag /}}, {{/tag}}, {{1.2.3}}
        """
        tag_patterns = [
            # Tags textuais
            r"(?<!\{)\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",  # {{tag}}
            r"(?<!\{)\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*/\s*\}\}(?!\})",  # {{tag /}}
            r"(?<!\{)\{\{\s*/\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",  # {{/tag}}
            # Tags com prefixo TAG-
            r"(?<!\{)\{\{\s*TAG-([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",  # {{TAG-nome}}
            r"(?<!\{)\{\{\s*TAG-([a-zA-Z_][a-zA-Z0-9_]*)\s*/\s*\}\}(?!\})",  # {{TAG-nome /}}
            r"(?<!\{)\{\{\s*/\s*TAG-([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",  # {{/TAG-nome}}
            # Tags numéricas
            r"(?<!\{)\{\{\s*(\d+(?:\.\d+)*)\s*\}\}(?!\})",  # {{1.2.3}}
            r"(?<!\{)\{\{\s*(\d+(?:\.\d+)*)\s*/\s*\}\}(?!\})",  # {{1 /}}
            r"(?<!\{)\{\{\s*/\s*(\d+(?:\.\d+)*)\s*\}\}(?!\})",  # {{/1}}
        ]

        tags_encontradas = {}

        for idx, modification in enumerate(modificacoes):
            # Verificar tanto o conteúdo original quanto a alteração
            textos_para_analisar = [
                ("original", modification.get("conteudo", "")),
                ("alteracao", modification.get("alteracao", "")),
            ]

            for fonte, texto in textos_para_analisar:
                if not texto:
                    continue

                # Aplicar todos os padrões de regex
                for pattern in tag_patterns:
                    matches = re.finditer(pattern, texto, re.IGNORECASE)
                    for match in matches:
                        # Limpar e normalizar o nome da tag
                        tag_nome = match.group(1).strip()

                        # Para tags numéricas, manter formato original
                        if re.match(r"^\d+(?:\.\d+)*$", tag_nome):
                            tag_nome_normalizado = tag_nome  # Manter formato numérico
                        else:
                            tag_nome_normalizado = (
                                tag_nome.lower()
                            )  # Minúscula para tags textuais

                        # Calcular posições no texto
                        pos_inicio = match.start()
                        pos_fim = match.end()
                        texto_completo = match.group(0)

                        # Se a tag já existe, manter a versão com mais contexto
                        if tag_nome_normalizado not in tags_encontradas or len(
                            texto
                        ) > len(
                            tags_encontradas[tag_nome_normalizado].get("contexto", "")
                        ):
                            # Calcular linha aproximada
                            linha_aproximada = texto[:pos_inicio].count("\n") + 1

                            tags_encontradas[tag_nome_normalizado] = {
                                "nome": tag_nome_normalizado,
                                "texto_completo": texto_completo,
                                "posicao_inicio": pos_inicio,
                                "posicao_fim": pos_fim,
                                "contexto": texto[
                                    max(0, pos_inicio - 100) : pos_fim + 100
                                ],
                                "fonte": fonte,
                                "linha_aproximada": linha_aproximada,
                                "modificacao_indice": idx,
                                "caminho_tag_inicio": f"modificacao_{idx}_linha_{linha_aproximada}_pos_{pos_inicio}",
                                "caminho_tag_fim": f"modificacao_{idx}_linha_{linha_aproximada}_pos_{pos_fim}",
                            }

        return list(tags_encontradas.values())

    def _extrair_conteudo_entre_tags(self, texto: str) -> dict[str, dict]:
        """
        Extrai conteúdo entre tags de abertura e fechamento
        Ex: {{TAG-nome}}...conteúdo...{{/TAG-nome}} ou {{6}}...conteúdo...{{/6}}

        Returns:
            dict com {tag_nome: {"conteudo": str, "posicao_inicial_texto": int, "posicao_final_texto": int}}
        """
        conteudo_map = {}
        total_aberturas = 0
        total_pares = 0

        # Padrões para tags de abertura e fechamento
        patterns = [
            # Tags com prefixo TAG-
            (
                r"\{\{TAG-([a-zA-Z_][a-zA-Z0-9_]*)\}\}",
                r"\{\{/TAG-\1\}\}",
            ),  # {{TAG-nome}}...{{/TAG-nome}}
            # Tags textuais
            (
                r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}",
                r"\{\{/\1\}\}",
            ),  # {{nome}}...{{/nome}}
            # Tags numéricas
            (
                r"\{\{(\d+(?:\.\d+)*)\}\}",
                r"\{\{/\1\}\}",
            ),  # {{6}}...{{/6}} ou {{7.4}}...{{/7.4}}
        ]

        for _pattern_idx, (open_pattern, close_pattern_template) in enumerate(patterns):
            # Encontrar todas as tags de abertura
            for open_match in re.finditer(open_pattern, texto):
                total_aberturas += 1
                tag_nome = open_match.group(1).lower()
                open_pos = open_match.end()

                # Construir padrão de fechamento específico para esta tag
                close_pattern = close_pattern_template.replace(
                    r"\1", re.escape(open_match.group(1))
                )

                # Buscar tag de fechamento correspondente
                close_match = re.search(close_pattern, texto[open_pos:], re.IGNORECASE)

                if close_match:
                    total_pares += 1
                    # Extrair conteúdo entre as tags (sem incluir as tags)
                    conteudo_inicio = open_pos
                    conteudo_fim = open_pos + close_match.start()
                    conteudo = texto[conteudo_inicio:conteudo_fim].strip()

                    conteudo_map[tag_nome] = {
                        "conteudo": conteudo,
                        "posicao_inicial_texto": conteudo_inicio,
                        "posicao_final_texto": conteudo_fim,
                    }
                else:
                    # Log quando não encontra par
                    if total_aberturas <= 5:  # Log apenas primeiras 5 falhas
                        contexto = texto[open_pos : open_pos + 100].replace("\n", " ")
                        print(
                            f"❌ Sem par para tag {open_match.group(1)}: {contexto[:50]}..."
                        )

        print(f"🔍 Tags de abertura encontradas: {total_aberturas}")
        print(f"✓ Pares completos encontrados: {total_pares}")
        print(f"📝 Tags com conteúdo extraído: {len(conteudo_map)}")

        # Log amostra do texto para debug
        if total_aberturas == 0:
            print(f"⚠️ TEXTO SAMPLE (primeiros 500 chars): {texto[:500]}")
            print("⚠️ Buscando tags numéricas explicitamente...")
            numeric_tags = re.findall(r"\{\{(\d+(?:\.\d+)*)\}\}", texto)
            print(f"⚠️ Tags numéricas encontradas: {numeric_tags[:10]}")

        return conteudo_map

    def _atualizar_modelo_com_tags(self, modelo_id: str, tags_encontradas: list[dict]):
        """
        Atualiza o modelo com as tags encontradas
        O Directus cria automaticamente os registros em modelo_contrato_tag
        """
        # Ordenar tags por posição no documento
        tags_ordenadas = sorted(
            tags_encontradas, key=lambda x: x.get("posicao_inicio", 0)
        )

        # Preparar dados das tags
        tags_data = []
        for tag_info in tags_ordenadas:
            tag_data = {
                # "modelo_contrato": modelo_id,
                "tag_nome": tag_info["nome"],
                "caminho_tag_inicio": tag_info.get("caminho_tag_inicio", ""),
                "caminho_tag_fim": tag_info.get("caminho_tag_fim", ""),
                "conteudo": tag_info.get("conteudo", ""),
                "contexto": tag_info.get("contexto", "")[:500],
                "posicao_inicio": tag_info.get("posicao_inicio", 0),
                "posicao_fim": tag_info.get("posicao_fim", 0),
                "posicao_inicial_texto": tag_info.get("posicao_inicial_texto", 0),
                "posicao_final_texto": tag_info.get("posicao_final_texto", 0),
                "status": "published",
            }
            tags_data.append(tag_data)

        # Atualizar modelo com tags (Directus cria os registros atomicamente)
        update_url = f"{self.base_url}/items/modelo_contrato/{modelo_id}"
        update_data = {"tags": tags_data, "status": "concluido"}

        print(f"🔄 Atualizando modelo {modelo_id} com {len(tags_data)} tags...")

        response = requests.patch(
            update_url, headers=self.headers, json=update_data, timeout=30
        )

        if response.status_code == 200:
            print(f"  ✅ Modelo atualizado com {len(tags_data)} tags")
        else:
            error_msg = response.text[:500]
            print(f"  ⚠️ Erro ao atualizar modelo: HTTP {response.status_code}")
            print(f"  ⚠️ Erro: {error_msg}")
            raise ValueError(f"Falha ao atualizar modelo: {error_msg}")
