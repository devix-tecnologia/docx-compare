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

from repositorio import DirectusRepository

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

    def buscar_clausula_por_tag(self, tag_id: str) -> dict:
        """
        Busca os detalhes da cláusula vinculada a uma tag específica
        """
        try:
            url = f"{self.directus_base_url}/items/clausula"
            params = {
                "filter[tag][_eq]": tag_id,
                "fields": "id,numero,nome,objetivo",
                "limit": 1,
            }

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=10
            )

            if response.status_code == 200:
                data = response.json().get("data", [])
                if data and len(data) > 0:
                    clausula = data[0]
                    # Buscar referências separadamente
                    clausula_id = clausula.get("id")
                    if clausula_id:
                        referencias = self.buscar_referencias_clausula(clausula_id)
                        clausula["referencias"] = referencias
                    return clausula

            return {}
        except Exception as e:
            print(f"⚠️  Erro ao buscar cláusula da tag {tag_id}: {e}")
            return {}

    def buscar_referencias_clausula(self, clausula_id: str) -> list:
        """
        Busca as referências vinculadas a uma cláusula específica
        """
        try:
            url = f"{self.directus_base_url}/items/referencia"
            params = {
                "filter[clausula][_eq]": clausula_id,
                "fields": "id,descricao",
                "limit": 100,
            }

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=10
            )

            if response.status_code == 200:
                data = response.json().get("data", [])
                # Retornar lista de descrições
                return [
                    ref.get("descricao", "") for ref in data if ref.get("descricao")
                ]

            return []
        except Exception as e:
            print(f"⚠️  Erro ao buscar referências da cláusula {clausula_id}: {e}")
            return []

    def buscar_tags_modelo(self, modelo_id: str) -> list[dict]:
        """
        Busca tags do modelo de contrato que são relevantes para processamento
        """
        try:
            url = f"{self.directus_base_url}/items/modelo_contrato_tag"
            params = {
                "filter[modelo_contrato][_eq]": modelo_id,
                "fields": "id,tag_nome,caminho_tag_inicio,caminho_tag_fim,posicao_inicio_texto,posicao_fim_texto,conteudo,clausulas.id,clausulas.numero,clausulas.nome,clausulas.objetivo,clausulas.referencias",
                "limit": -1,  # -1 = sem limite (buscar todas as tags)
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
                "limit": -1,  # -1 = sem limite (buscar todas as cláusulas)
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

    def _encontrar_tag_mais_proxima(
        self, pos_inicio: int, pos_fim: int, tags_modelo: list[dict]
    ) -> dict | None:
        """
        Encontra a tag mais próxima/relevante para um bloco
        Usa overlap de posições para determinar qual tag é mais relevante
        """
        melhor_tag = None
        melhor_overlap = 0

        for tag in tags_modelo:
            tag_inicio = tag.get("posicao_inicio_texto")
            tag_fim = tag.get("posicao_fim_texto")

            if tag_inicio is None or tag_fim is None:
                continue

            # Calcular overlap entre bloco e tag
            overlap_inicio = max(pos_inicio, tag_inicio)
            overlap_fim = min(pos_fim, tag_fim)

            if overlap_fim > overlap_inicio:
                overlap = overlap_fim - overlap_inicio
                if overlap > melhor_overlap:
                    melhor_overlap = overlap
                    melhor_tag = tag

        return melhor_tag

    def processar_agrupamento_posicional_versao(
        self, versao_id: str, modificacoes: list[dict]
    ) -> dict:
        """
        Agrupa modificações em blocos baseado em proximidade posicional

        IMPORTANTE: Blocos NÃO são tags nem cláusulas!
        - Tags servem para enriquecer blocos com contexto (qual cláusula)
        - Blocos são agrupamentos de modificações próximas

        Args:
            versao_id: ID da versão
            modificacoes: Lista de modificações detectadas

        Returns:
            dict com blocos agrupados
        """
        print(f"\n🎯 Agrupamento de Modificações - Versão: {versao_id}")
        print("=" * 60)
        print(f"📊 Total de modificações a agrupar: {len(modificacoes)}")

        try:
            # 1. Buscar dados da versão (para obter tags/contexto)
            versao_data = self.buscar_dados_versao(versao_id)
            if not versao_data:
                return {"erro": "Dados da versão não encontrados"}

            modelo_id = versao_data["modelo_id"]
            print(f"✅ Modelo de contrato: {modelo_id}")

            # 2. Buscar tags do modelo (para contexto/enriquecimento)
            tags_modelo = self.buscar_tags_modelo(modelo_id)
            print(f"🏷️ Tags do modelo: {len(tags_modelo)}")

            # 3. Agrupar modificações por proximidade posicional
            DISTANCIA_MAXIMA = 2000  # Modificações a menos de 2000 chars são agrupadas

            blocos_agrupados = []
            modificacoes_ordenadas = sorted(
                modificacoes, key=lambda m: m.get("posicao_inicio") or 0
            )

            bloco_atual = None

            for mod in modificacoes_ordenadas:
                pos_inicio = mod.get("posicao_inicio") or 0
                pos_fim = mod.get("posicao_fim") or 0

                # Se não há bloco atual ou a modificação está longe, criar novo bloco
                if bloco_atual is None or (
                    pos_inicio - (bloco_atual["posicao_fim"] or 0) > DISTANCIA_MAXIMA
                ):
                    # Finalizar bloco anterior
                    if bloco_atual:
                        blocos_agrupados.append(bloco_atual)

                    # Criar novo bloco
                    bloco_atual = {
                        "posicao_inicio": pos_inicio,
                        "posicao_fim": pos_fim,
                        "modificacoes": [mod],
                        "tipo": "agrupamento_posicional",
                    }
                else:
                    # Adicionar modificação ao bloco atual
                    bloco_atual["modificacoes"].append(mod)
                    bloco_atual["posicao_fim"] = max(
                        bloco_atual["posicao_fim"] or 0, pos_fim
                    )

            # Adicionar último bloco
            if bloco_atual:
                blocos_agrupados.append(bloco_atual)

            # 4. Enriquecer blocos com contexto de tags/cláusulas
            for bloco in blocos_agrupados:
                # Encontrar tag mais relevante para este bloco
                tag_relevante = self._encontrar_tag_mais_proxima(
                    bloco["posicao_inicio"], bloco["posicao_fim"], tags_modelo
                )

                if tag_relevante:
                    bloco["nome"] = tag_relevante.get("tag_nome", "Sem tag")
                    bloco["clausula_id"] = tag_relevante.get("id")
                    bloco["conteudo_estimado"] = tag_relevante.get("conteudo", "")[:100]
                else:
                    bloco["nome"] = (
                        f"Bloco {bloco['posicao_inicio']}-{bloco['posicao_fim']}"
                    )
                    bloco["conteudo_estimado"] = ""

                # Adicionar contador de modificações para o frontend
                bloco["total_modificacoes"] = len(bloco.get("modificacoes", []))

                # Propagar dados da cláusula para cada modificação dentro do bloco
                for mod in bloco.get("modificacoes", []):
                    if tag_relevante:
                        tag_id = tag_relevante.get("id")
                        mod["clausula_nome"] = tag_relevante.get("tag_nome", "Sem tag")
                        mod["clausula_id"] = tag_id
                        mod["clausula_conteudo"] = tag_relevante.get("conteudo", "")[
                            :200
                        ]

                        # Buscar informações completas da cláusula vinculada
                        clausula_detalhes = None
                        if tag_id:
                            clausula_detalhes = self.buscar_clausula_por_tag(tag_id)
                        if clausula_detalhes:
                            # Sobrescrever clausula_id com o ID real da cláusula
                            # (tag_id é o ID da tag, não da cláusula)
                            clausula_real_id = clausula_detalhes.get("id")
                            if clausula_real_id:
                                mod["clausula_id"] = clausula_real_id
                            mod["clausula_objetivo"] = clausula_detalhes.get(
                                "objetivo", ""
                            )
                            # Referencias é uma lista de strings
                            referencias = clausula_detalhes.get("referencias", [])
                            mod["clausula_referencias"] = (
                                referencias if isinstance(referencias, list) else []
                            )
                            mod["clausula_numero"] = clausula_detalhes.get("numero", "")
                            # Usar nome da cláusula se disponível, senão usar nome da tag
                            clausula_nome = clausula_detalhes.get("nome", "")
                            if clausula_nome:
                                mod["clausula_nome"] = clausula_nome
                        else:
                            # Sem cláusula vinculada: não enviar tag ID como FK
                            mod["clausula_id"] = None
                    else:
                        mod["clausula_nome"] = "Sem cláusula vinculada"

            # 5. Gerar estatísticas
            resultado = {
                "versao_id": versao_id,
                "modelo_id": modelo_id,
                "total_blocos": len(blocos_agrupados),
                "total_modificacoes": len(modificacoes),
                "blocos": blocos_agrupados,
                "estatisticas": {
                    "distancia_maxima_usada": DISTANCIA_MAXIMA,
                    "tags_modelo_disponiveis": len(tags_modelo),
                    "blocos_com_tag": len(
                        [b for b in blocos_agrupados if b.get("clausula_id")]
                    ),
                    "blocos_sem_tag": len(
                        [b for b in blocos_agrupados if not b.get("clausula_id")]
                    ),
                },
            }

            print("\n📊 RELATÓRIO DE AGRUPAMENTO")
            print("=" * 60)
            print(f"📈 Blocos criados: {resultado['total_blocos']}")
            print(f"🔧 Modificações agrupadas: {resultado['total_modificacoes']}")
            print(
                f"🏷️ Blocos com contexto de tag: {resultado['estatisticas']['blocos_com_tag']}"
            )
            print(
                f"⚠️ Blocos sem contexto: {resultado['estatisticas']['blocos_sem_tag']}"
            )

            # Mostrar detalhes de cada bloco
            for idx, bloco in enumerate(blocos_agrupados, 1):
                print(f"\n  📦 Bloco {idx}: {bloco['nome']}")
                print(
                    f"     - Posição: {bloco['posicao_inicio']} → {bloco['posicao_fim']}"
                )
                print(f"     - Modificações: {len(bloco['modificacoes'])}")

            return resultado

        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
            import traceback

            traceback.print_exc()
            return {"erro": f"Erro no processamento: {e}"}


def main():
    """Teste do agrupador posicional"""
    agrupador = AgrupadorPosicional()
    repo = DirectusRepository(
        base_url=os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
    )

    print("🚀 Testando Agrupador Posicional Versiona AI")
    print("=" * 50)

    # Usar uma versão de exemplo - pode ser modificado conforme necessário
    versao_id = "10f99b61-dd4a-4041-9753-4fa88e359830"  # Exemplo do sistema

    # Buscar modificações da versão
    modificacoes = repo.get_modificacoes_versao(versao_id)
    print(f"📊 Modificações encontradas: {len(modificacoes)}")

    resultado = agrupador.processar_agrupamento_posicional_versao(
        versao_id, modificacoes
    )

    if "erro" in resultado:
        print(f"❌ Erro: {resultado['erro']}")
    else:
        print("✅ Processamento concluído!")
        print(f"📊 Blocos identificados: {resultado['total_blocos']}")


if __name__ == "__main__":
    main()
