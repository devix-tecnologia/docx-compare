"""
Agrupador Posicional para Versiona AI
Implementa o sistema de agrupamento posicional baseado na task-001
"""

import os
import re
import subprocess
import tempfile

import requests
from dotenv import load_dotenv

load_dotenv()


class AgrupadorPosicional:
    """
    Agrupador que usa posições no documento para associar modificações às tags
    Integrado ao sistema Versiona AI
    """

    def __init__(self):
        self.directus_base_url = os.getenv(
            "DIRECTUS_BASE_URL", "https://contract.devix.co"
        )
        self.directus_token = os.getenv("DIRECTUS_TOKEN", "")
        self.directus_headers = {
            "Authorization": f"Bearer {self.directus_token}",
            "Content-Type": "application/json",
        }

    def extrair_posicao_numerica(self, caminho: str) -> int | None:
        """
        Extrai posição numérica do caminho tipo 'blocks[0].c[1].c'
        Converte caminhos estruturais em posições numéricas aproximadas
        """
        if not caminho:
            return None

        # Extrair números dos índices do caminho
        numeros = re.findall(r"\[(\d+)\]", caminho)
        if not numeros:
            # Tentar padrão alternativo pos_número
            match = re.search(r"pos_(\d+)", caminho)
            return int(match.group(1)) if match else 0

        # Calcular posição aproximada baseada na estrutura
        posicao = 0
        for i, num in enumerate(numeros):
            # Peso decrescente para níveis mais profundos
            peso = 1000 ** (len(numeros) - i - 1)
            posicao += int(num) * peso

        return posicao

    def buscar_dados_versao(self, versao_id: str) -> dict | None:
        """
        Busca dados completos da versão incluindo informações do modelo
        """
        try:
            url = f"{self.directus_base_url}/items/versao/{versao_id}"
            params = {
                "fields": "id,contrato.modelo_contrato.id,contrato.modelo_contrato.arquivo_com_tags,arquivo"
            }

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code == 200:
                data = response.json().get("data", {})
                contrato = data.get("contrato", {})
                modelo_contrato = contrato.get("modelo_contrato", {})

                return {
                    "versao_id": data.get("id"),
                    "modelo_id": modelo_contrato.get("id"),
                    "arquivo_com_tags_id": modelo_contrato.get("arquivo_com_tags"),
                    "arquivo_modificado_id": data.get("arquivo"),
                }

            print(f"❌ Erro ao buscar versão: HTTP {response.status_code}")
            return None

        except Exception as e:
            print(f"❌ Erro ao buscar dados da versão: {e}")
            return None

    def buscar_tags_modelo(self, modelo_id: str) -> list[dict]:
        """
        Busca tags do modelo de contrato que são relevantes para processamento
        """
        try:
            url = f"{self.directus_base_url}/items/modelo_contrato_tag"
            params = {
                "filter[modelo_contrato][_eq]": modelo_id,
                "fields": "id,tag_nome,caminho_tag_inicio,caminho_tag_fim,posicao_inicio_texto,posicao_fim_texto,conteudo,clausulas.id,clausulas.numero",
                "limit": 100,
            }

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code == 200:
                tags = response.json().get("data", [])
                print(f"✅ Encontradas {len(tags)} tags para modelo {modelo_id}")

                # Log detalhado das tags encontradas
                print("\n📋 DETALHES DAS TAGS ENCONTRADAS:")
                print("=" * 80)
                for i, tag in enumerate(tags, 1):
                    print(f"🏷️  Tag {i}: {tag.get('tag_nome', 'N/A')}")
                    print(f"   📂 ID: {tag.get('id', 'N/A')}")
                    print(
                        f"   📍 Posição início: {tag.get('posicao_inicio_texto', 'NÃO DEFINIDA')}"
                    )
                    print(
                        f"   📍 Posição fim: {tag.get('posicao_fim_texto', 'NÃO DEFINIDA')}"
                    )
                    print(
                        f"   🛤️  Caminho início: {tag.get('caminho_tag_inicio', 'N/A')}"
                    )
                    print(f"   🛤️  Caminho fim: {tag.get('caminho_tag_fim', 'N/A')}")
                    print(f"   📄 Conteúdo: {str(tag.get('conteudo', 'N/A'))[:100]}...")
                    if tag.get("clausulas"):
                        clausulas = tag.get("clausulas", [])
                        if isinstance(clausulas, list) and clausulas:
                            print(
                                f"   📝 Cláusulas: {[c.get('numero', 'N/A') for c in clausulas]}"
                            )
                        else:
                            print(f"   📝 Cláusulas: {clausulas}")
                    print("   " + "-" * 40)
                print("=" * 80)

                return tags
            else:
                print(f"❌ Erro ao buscar tags: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Erro ao buscar tags: {e}")
            return []

    def buscar_clausulas_relacionadas(
        self, modelo_id: str, tags_encontradas: list[dict]
    ) -> list[dict]:
        """
        Busca cláusulas relacionadas às tags encontradas no modelo de contrato
        """
        try:
            # Extrair nomes das tags encontradas
            nomes_tags = [
                tag.get("tag_nome", "").strip()
                for tag in tags_encontradas
                if tag.get("tag_nome")
            ]

            if not nomes_tags:
                print("⚠️  Nenhuma tag com nome encontrada para buscar cláusulas")
                return []

            print(f"🔍 Buscando cláusulas relacionadas às tags: {nomes_tags}")

            # Buscar cláusulas do modelo
            url = f"{self.directus_base_url}/items/clausula"
            params = {
                "filter[modelo_contrato][_eq]": modelo_id,
                "fields": "id,numero,titulo,conteudo,tipo,posicao_no_documento,tags_relacionadas",
                "limit": 100,
            }

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code == 200:
                clausulas = response.json().get("data", [])
                clausulas_relacionadas = []

                print(f"📄 Encontradas {len(clausulas)} cláusulas no modelo")

                for clausula in clausulas:
                    # Verificar se a cláusula está relacionada a alguma das tags
                    clausula_relacionada = False
                    tags_da_clausula = []

                    # Buscar por referências às tags no título ou conteúdo da cláusula
                    titulo = clausula.get("titulo", "").lower()
                    conteudo = clausula.get("conteudo", "").lower()

                    for tag_nome in nomes_tags:
                        tag_lower = tag_nome.lower()
                        if tag_lower in titulo or tag_lower in conteudo:
                            clausula_relacionada = True
                            tags_da_clausula.append(tag_nome)

                    # Verificar tags_relacionadas se existir
                    if clausula.get("tags_relacionadas"):
                        tags_rel = clausula.get("tags_relacionadas", [])
                        if isinstance(tags_rel, list):
                            for tag_rel in tags_rel:
                                if (
                                    isinstance(tag_rel, dict)
                                    and tag_rel.get("tag_nome") in nomes_tags
                                ):
                                    clausula_relacionada = True
                                    tags_da_clausula.append(tag_rel.get("tag_nome"))
                                elif isinstance(tag_rel, str) and tag_rel in nomes_tags:
                                    clausula_relacionada = True
                                    tags_da_clausula.append(tag_rel)

                    if clausula_relacionada:
                        clausula_info = {
                            "id": clausula.get("id"),
                            "numero": clausula.get("numero"),
                            "titulo": clausula.get("titulo"),
                            "tipo": clausula.get("tipo"),
                            "posicao_no_documento": clausula.get(
                                "posicao_no_documento"
                            ),
                            "tags_relacionadas": list(
                                set(tags_da_clausula)
                            ),  # Remove duplicatas
                        }
                        clausulas_relacionadas.append(clausula_info)

                        print(
                            f"✅ Cláusula relacionada: {clausula.get('numero', 'N/A')} - {clausula.get('titulo', 'N/A')}"
                        )
                        print(f"   🏷️  Tags: {tags_da_clausula}")

                print(
                    f"🎯 Total de cláusulas relacionadas encontradas: {len(clausulas_relacionadas)}"
                )
                return clausulas_relacionadas
            else:
                print(f"❌ Erro ao buscar cláusulas: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Erro ao buscar cláusulas relacionadas: {e}")
            return []

    def baixar_arquivo_directus(self, file_id: str) -> str | None:
        """
        Baixa um arquivo do Directus e retorna o caminho local
        """
        try:
            download_url = f"{self.directus_base_url}/assets/{file_id}"

            response = requests.get(
                download_url, headers=self.directus_headers, timeout=30
            )

            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".docx"
                ) as temp_file:
                    temp_file.write(response.content)
                    return temp_file.name
            else:
                print(
                    f"❌ Erro ao baixar arquivo {file_id}: HTTP {response.status_code}"
                )
                return None

        except Exception as e:
            print(f"❌ Erro ao baixar arquivo {file_id}: {e}")
            return None

    def converter_docx_para_texto(self, arquivo_path: str) -> str:
        """
        Converte arquivo DOCX para texto usando pandoc
        """
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as html_temp:
                html_temp_name = html_temp.name

            # Converter usando pandoc
            subprocess.run(
                ["pandoc", arquivo_path, "-o", html_temp_name],
                check=True,
                capture_output=True,
            )

            # Ler HTML
            with open(html_temp_name, encoding="utf-8") as f:
                html_content = f.read()

            # Converter HTML para texto limpo
            texto_limpo = self.html_para_texto(html_content)

            # Limpar arquivo temporário
            os.unlink(html_temp_name)

            return texto_limpo

        except Exception as e:
            print(f"❌ Erro ao converter DOCX para texto: {e}")
            return ""

    def html_para_texto(self, html_content: str) -> str:
        """
        Converte HTML para texto limpo removendo tags e formatação
        """
        # Remover comentários HTML
        html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)

        # Remover tags de formatação preservando conteúdo
        html_content = re.sub(
            r"<(strong|b|em|i|u|mark)[^>]*>(.*?)</\1>",
            r"\2",
            html_content,
            flags=re.DOTALL,
        )

        # Converter listas
        html_content = re.sub(
            r"<li[^>]*><p[^>]*>(.*?)</p></li>", r"• \1", html_content, flags=re.DOTALL
        )
        html_content = re.sub(
            r"<li[^>]*>(.*?)</li>", r"• \1", html_content, flags=re.DOTALL
        )
        html_content = re.sub(r"<(ol|ul)[^>]*>|</(ol|ul)>", "", html_content)

        # Converter parágrafos e quebras
        html_content = re.sub(r"<p[^>]*>|</p>", "\n", html_content)
        html_content = re.sub(r"<br[^>]*/?>", "\n", html_content)

        # Remover todas as outras tags
        html_content = re.sub(r"<[^>]+>", "", html_content)

        # Decodificar entidades HTML
        html_content = re.sub(r"&nbsp;", " ", html_content)
        html_content = re.sub(r"&amp;", "&", html_content)
        html_content = re.sub(r"&lt;", "<", html_content)
        html_content = re.sub(r"&gt;", ">", html_content)
        html_content = re.sub(r"&quot;", '"', html_content)

        # Limpar quebras de linha excessivas
        html_content = re.sub(r"\n\s*\n", "\n", html_content)

        return html_content.strip()

    def extrair_tags_das_diferencas(
        self, texto_original: str, texto_com_tags: str
    ) -> list[dict]:
        """
        Extrai informações de posicionamento das tags comparando texto original vs texto com tags
        """
        # Padrões para identificar tags
        tag_patterns = [
            # Tags textuais: {{tag}} com espaços opcionais
            r"(?<!\{)\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",
            # Tags numéricas: {{1}}, {{1.1}}, {{1.2.3}}
            r"(?<!\{)\{\{\s*(\d+(?:\.\d+)*)\s*\}\}(?!\})",
        ]

        tags_encontradas = {}

        for pattern in tag_patterns:
            matches = re.finditer(pattern, texto_com_tags, re.IGNORECASE)
            for match in matches:
                tag_nome = match.group(1).strip()

                # Normalizar nome da tag
                if re.match(r"^\d+(?:\.\d+)*$", tag_nome):
                    tag_nome_normalizado = tag_nome  # Manter formato numérico
                else:
                    tag_nome_normalizado = (
                        tag_nome.lower()
                    )  # Minúscula para tags textuais

                # Encontrar posição no texto original
                conteudo_tag = self.extrair_conteudo_tag(
                    texto_com_tags, match.start(), match.end()
                )
                posicao_no_original = self.encontrar_posicao_no_original(
                    conteudo_tag, texto_original
                )

                if posicao_no_original is not None:
                    tags_encontradas[tag_nome_normalizado] = {
                        "nome": tag_nome_normalizado,
                        "posicao_inicio_texto": posicao_no_original,
                        "posicao_fim_texto": posicao_no_original + len(conteudo_tag),
                        "conteudo": conteudo_tag,
                    }

        return list(tags_encontradas.values())

    def extrair_conteudo_tag(self, texto: str, inicio_tag: int, fim_tag: int) -> str:
        """
        Extrai o conteúdo entre as tags do texto
        """
        # Implementação simplificada - pode ser melhorada
        # Por enquanto, retorna uma substring ao redor da posição
        inicio_conteudo = max(0, inicio_tag - 50)
        fim_conteudo = min(len(texto), fim_tag + 50)
        return texto[inicio_conteudo:fim_conteudo].strip()

    def encontrar_posicao_no_original(
        self, conteudo: str, texto_original: str
    ) -> int | None:
        """
        Encontra a posição do conteúdo no texto original
        """
        # Implementação simplificada usando busca de substring
        posicao = texto_original.find(conteudo)
        return posicao if posicao != -1 else None

    def calcular_sobreposicao(
        self, intervalo1: tuple[int, int], intervalo2: tuple[int, int]
    ) -> float:
        """
        Calcula a sobreposição entre dois intervalos
        """
        inicio1, fim1 = intervalo1
        inicio2, fim2 = intervalo2

        inicio_sobreposicao = max(inicio1, inicio2)
        fim_sobreposicao = min(fim1, fim2)

        if inicio_sobreposicao <= fim_sobreposicao:
            tamanho_sobreposicao = fim_sobreposicao - inicio_sobreposicao
            tamanho_total = max(fim1, fim2) - min(inicio1, inicio2)
            return tamanho_sobreposicao / tamanho_total if tamanho_total > 0 else 0
        else:
            return 0

    def processar_agrupamento_posicional_versao(self, versao_id: str) -> dict:
        """
        Processa o agrupamento posicional para uma versão específica
        Retorna informações sobre blocos e tags identificados
        """
        print(f"\n🎯 Processamento posicional - Versão: {versao_id}")
        print("=" * 60)

        try:
            # 1. Buscar dados da versão
            versao_data = self.buscar_dados_versao(versao_id)
            if not versao_data:
                return {"erro": "Dados da versão não encontrados"}

            modelo_id = versao_data["modelo_id"]
            arquivo_com_tags_id = versao_data["arquivo_com_tags_id"]
            arquivo_modificado_id = versao_data["arquivo_modificado_id"]

            print(f"✅ Modelo de contrato: {modelo_id}")
            print(f"📁 Arquivo com tags: {arquivo_com_tags_id}")
            print(f"📁 Arquivo modificado: {arquivo_modificado_id}")

            # 2. Buscar tags existentes do modelo
            tags_modelo = self.buscar_tags_modelo(modelo_id)

            # 3. Baixar arquivos para análise
            print("📥 Baixando arquivos...")
            arquivo_com_tags_path = self.baixar_arquivo_directus(arquivo_com_tags_id)
            arquivo_modificado_path = self.baixar_arquivo_directus(
                arquivo_modificado_id
            )

            if not arquivo_com_tags_path or not arquivo_modificado_path:
                return {"erro": "Não foi possível baixar os arquivos"}

            try:
                # 4. Converter arquivos para texto
                print("📊 Convertendo arquivos para análise...")
                texto_com_tags = self.converter_docx_para_texto(arquivo_com_tags_path)
                texto_modificado = self.converter_docx_para_texto(
                    arquivo_modificado_path
                )

                # 5. Analisar posições das tags (se modelo tiver tags com posições)
                blocos_identificados = []
                tags_com_posicoes = []

                for tag in tags_modelo:
                    if tag.get("posicao_inicio_texto") and tag.get("posicao_fim_texto"):
                        tags_com_posicoes.append(
                            {
                                "nome": tag["tag_nome"],
                                "posicao_inicio": tag["posicao_inicio_texto"],
                                "posicao_fim": tag["posicao_fim_texto"],
                                "tipo": "existente",
                            }
                        )

                # 6. Se não há tags com posições, tentar extrair do texto modificado
                if not tags_com_posicoes:
                    print("🔍 Extraindo tags das diferenças...")
                    tags_extraidas = self.extrair_tags_das_diferencas(
                        texto_com_tags, texto_modificado
                    )
                    for tag in tags_extraidas:
                        tags_com_posicoes.append(
                            {
                                "nome": tag["nome"],
                                "posicao_inicio": tag["posicao_inicio_texto"],
                                "posicao_fim": tag["posicao_fim_texto"],
                                "tipo": "extraida",
                            }
                        )

                # 7. Identificar blocos baseado nas tags
                for tag in tags_com_posicoes:
                    blocos_identificados.append(
                        {
                            "nome": tag["nome"],
                            "posicao_inicio": tag["posicao_inicio"],
                            "posicao_fim": tag["posicao_fim"],
                            "tipo": tag["tipo"],
                            "conteudo_estimado": texto_modificado[
                                tag["posicao_inicio"] : tag["posicao_fim"]
                            ][:100]
                            + "...",
                        }
                    )

                # 8. Gerar estatísticas
                resultado = {
                    "versao_id": versao_id,
                    "modelo_id": modelo_id,
                    "total_blocos": len(blocos_identificados),
                    "total_tags_modelo": len(tags_modelo),
                    "tags_com_posicoes": len(tags_com_posicoes),
                    "blocos": blocos_identificados,
                    "estatisticas": {
                        "tags_existentes": len(
                            [t for t in tags_com_posicoes if t["tipo"] == "existente"]
                        ),
                        "tags_extraidas": len(
                            [t for t in tags_com_posicoes if t["tipo"] == "extraida"]
                        ),
                        "texto_com_tags_tamanho": len(texto_com_tags),
                        "texto_modificado_tamanho": len(texto_modificado),
                    },
                }

                print("\n📊 RELATÓRIO FINAL")
                print("=" * 60)
                print(f"📈 Total de blocos identificados: {resultado['total_blocos']}")
                print(f"🏷️ Tags do modelo: {resultado['total_tags_modelo']}")
                print(f"📍 Tags com posições: {resultado['tags_com_posicoes']}")

                for bloco in blocos_identificados:
                    print(
                        f"   📋 Bloco '{bloco['nome']}' ({bloco['tipo']}): pos {bloco['posicao_inicio']}-{bloco['posicao_fim']}"
                    )

                return resultado

            finally:
                # Limpar arquivos temporários
                for arquivo in [arquivo_com_tags_path, arquivo_modificado_path]:
                    if arquivo and os.path.exists(arquivo):
                        os.unlink(arquivo)

        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
            return {"erro": f"Erro no processamento: {e}"}


def main():
    """Teste do agrupador posicional"""
    agrupador = AgrupadorPosicional()

    print("🚀 Testando Agrupador Posicional Versiona AI")
    print("=" * 50)

    # Usar uma versão de exemplo - pode ser modificado conforme necessário
    versao_id = "10f99b61-dd4a-4041-9753-4fa88e359830"  # Exemplo do sistema

    resultado = agrupador.processar_agrupamento_posicional_versao(versao_id)

    if "erro" in resultado:
        print(f"❌ Erro: {resultado['erro']}")
    else:
        print("✅ Processamento concluído!")
        print(f"📊 Blocos identificados: {resultado['total_blocos']}")


if __name__ == "__main__":
    main()
