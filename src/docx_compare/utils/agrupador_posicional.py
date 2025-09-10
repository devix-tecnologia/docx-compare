#!/usr/bin/env python3
"""
Agrupador Posicional
Associa modificações às tags por posição no documento
Abordagem simples: se a modificação está dentro da tag, associa.
"""

import os
import re
import sys

import requests
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path para import
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

try:
    from .position_calculator import PositionCalculator
except ImportError:
    # Fallback para execução direta
    from position_calculator import PositionCalculator

load_dotenv()

DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "")


class AgrupadorPosicional:
    """
    Agrupador que usa posições no documento para associar modificações às tags
    Muito mais simples e eficiente que algoritmos de similaridade
    """

    def __init__(self):
        self.directus_headers = {
            "Authorization": f"Bearer {DIRECTUS_TOKEN}",
            "Content-Type": "application/json",
        }

    def extrair_posicao_numerica(self, caminho):
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

    def buscar_tags_com_posicoes_validas(self, modelo_id):
        """
        Busca tags do modelo de contrato que têm posições válidas
        Atualizado para seguir a especificação da task-001
        """
        print(f"🏷️ INICIANDO buscar_tags_com_posicoes_validas para modelo {modelo_id}")

        try:
            url = f"{DIRECTUS_BASE_URL}/items/modelo_contrato_tag"
            params = {
                "filter[modelo_contrato][_eq]": modelo_id,
                "fields": "id,tag_nome,caminho_tag_inicio,caminho_tag_fim,posicao_inicio_texto,posicao_fim_texto,conteudo,clausulas.id,clausulas.numero",
                "limit": 100,
            }

            print(f"🔍 Buscando tags para modelo {modelo_id}")
            print(f"🔗 URL: {url}")
            print(f"📋 Params: {params}")

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            print(f"📊 Response status: {response.status_code}")

            if response.status_code == 200:
                tags = response.json().get("data", [])
                tags_processadas = []

                for tag in tags:
                    # Priorizar posições numéricas dos novos campos (task-001)
                    posicao_inicio_texto = tag.get("posicao_inicio_texto")
                    posicao_fim_texto = tag.get("posicao_fim_texto")

                    if (
                        posicao_inicio_texto is not None
                        and posicao_fim_texto is not None
                    ):
                        # Usar posições numéricas diretas (task-001)
                        posicao_inicio = posicao_inicio_texto
                        posicao_fim = posicao_fim_texto
                        clausulas = tag.get("clausulas", [])
                        print(
                            f"🏷️  Tag '{tag.get('tag_nome')}' - Posições: {posicao_inicio}-{posicao_fim} - Cláusulas: {len(clausulas)}"
                        )

                        tags_processadas.append(
                            {
                                "id": tag.get("id"),
                                "tag_nome": tag.get("tag_nome"),
                                "posicao_inicio_texto": posicao_inicio,
                                "posicao_fim_texto": posicao_fim,
                                "conteudo": tag.get("conteudo", ""),
                                "clausulas": clausulas,
                                "caminho_tag_inicio": tag.get("caminho_tag_inicio", ""),
                                "caminho_tag_fim": tag.get("caminho_tag_fim", ""),
                            }
                        )
                    else:
                        # Fallback para caminhos antigos se não houver posições numéricas
                        caminho_inicio = tag.get("caminho_tag_inicio", "")
                        caminho_fim = tag.get("caminho_tag_fim", "")

                        # Extrair posições numéricas dos caminhos
                        posicao_inicio = self.extrair_posicao_numerica(caminho_inicio)
                        posicao_fim = self.extrair_posicao_numerica(caminho_fim)

                        if posicao_inicio is not None and posicao_fim is not None:
                            clausulas = tag.get("clausulas", [])
                            print(
                                f"🏷️  Tag '{tag.get('tag_nome')}' - Posições: {posicao_inicio}-{posicao_fim} - Cláusulas: {len(clausulas)} (fallback)"
                            )

                            tags_processadas.append(
                                {
                                    "id": tag.get("id"),
                                    "tag_nome": tag.get("tag_nome"),
                                    "posicao_inicio_texto": posicao_inicio,
                                    "posicao_fim_texto": posicao_fim,
                                    "conteudo": tag.get("conteudo", ""),
                                    "clausulas": clausulas,
                                    "caminho_tag_inicio": caminho_inicio,
                                    "caminho_tag_fim": caminho_fim,
                                }
                            )
                        else:
                            print(
                                f"⚠️  Tag '{tag.get('tag_nome')}' ignorada - posições inválidas: {caminho_inicio} -> {posicao_inicio}, {caminho_fim} -> {posicao_fim}"
                            )

                print(
                    f"✅ {len(tags_processadas)} tags processadas com posições válidas"
                )
                return tags_processadas

            else:
                print(f"❌ Erro ao buscar tags: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return []

        except Exception as e:
            print(f"❌ Erro ao buscar tags: {e}")
            return []

    def buscar_modificacoes_com_posicoes_validas(self, versao_id):
        """
        Busca modificações da versão com suas posições numéricas
        Atualizado para seguir a especificação da task-001
        """
        try:
            url = f"{DIRECTUS_BASE_URL}/items/modificacao"
            params = {
                "filter[versao][_eq]": versao_id,
                "filter[clausula][_null]": "true",  # Só modificações sem cláusula
                "fields": "id,categoria,conteudo,alteracao,posicao_inicio,posicao_fim",
                "limit": 1000,
            }

            print(f"🔍 Buscando modificações não associadas para versão {versao_id}")

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code == 200:
                modificacoes = response.json().get("data", [])
                modificacoes_processadas = []

                for mod in modificacoes:
                    # Usar as posições numéricas dos novos campos
                    pos_inicio = mod.get("posicao_inicio")
                    pos_fim = mod.get("posicao_fim")

                    if pos_inicio is not None and pos_fim is not None:
                        modificacoes_processadas.append(
                            {
                                "id": mod["id"],
                                "categoria": mod.get("categoria", ""),
                                "conteudo": mod.get("conteudo", ""),
                                "alteracao": mod.get("alteracao", ""),
                                "posicao_inicio_numero": pos_inicio,
                                "posicao_fim_numero": pos_fim,
                            }
                        )

                print(
                    f"✅ Encontradas {len(modificacoes_processadas)} modificações com posições válidas"
                )
                return modificacoes_processadas

            else:
                print(f"❌ Erro ao buscar modificações: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Erro ao buscar modificações: {e}")
            return []

    def associar_modificacao_a_tag(self, modificacao, tags):
        """
        Encontra qual tag contém a modificação baseado em posições numéricas
        Implementa a lógica da especificação task-001
        """
        # Usar posições numéricas extraídas dos caminhos
        mod_inicio = modificacao.get("posicao_inicio_numero")
        mod_fim = modificacao.get("posicao_fim_numero")

        if mod_inicio is None or mod_fim is None:
            return None

        # Procurar tag que contém completamente a modificação
        for tag in tags:
            if tag.get("posicao_inicio_texto", 0) <= mod_inicio and mod_fim <= tag.get(
                "posicao_fim_texto", 0
            ):
                return tag  # Modificação está dentro da tag

        # Se não encontrou contenção completa, procurar melhor sobreposição
        melhor_tag = None
        maior_sobreposicao = 0

        for tag in tags:
            sobreposicao = self.calcular_sobreposicao(
                (mod_inicio, mod_fim),
                (tag.get("posicao_inicio_texto", 0), tag.get("posicao_fim_texto", 0)),
            )
            if sobreposicao > maior_sobreposicao:
                maior_sobreposicao = sobreposicao
                melhor_tag = tag

        return melhor_tag if maior_sobreposicao > 0.3 else None  # 30% threshold

    def calcular_sobreposicao(self, intervalo1, intervalo2):
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

    def atualizar_modificacao_com_posicoes(self, modificacao_id, pos_inicio, pos_fim):
        """
        Atualiza modificação com posições numéricas via API Directus
        """
        try:
            url = f"{DIRECTUS_BASE_URL}/items/modificacao/{modificacao_id}"
            data = {
                "posicao_inicio_numero": pos_inicio,
                "posicao_fim_numero": pos_fim,
            }

            response = requests.patch(
                url, headers=self.directus_headers, json=data, timeout=30
            )

            if response.status_code == 200:
                print(
                    f"✅ Modificação {modificacao_id} atualizada com posições {pos_inicio}-{pos_fim}"
                )
                return True
            else:
                print(
                    f"❌ Erro ao atualizar modificação {modificacao_id}: {response.status_code}"
                )
                return False

        except Exception as e:
            print(f"❌ Erro ao atualizar modificação {modificacao_id}: {e}")
            return False

    def associar_modificacao_clausula_api(self, modificacao_id, clausula_id):
        """
        Associa modificação à cláusula via API Directus
        """
        try:
            url = f"{DIRECTUS_BASE_URL}/items/modificacao/{modificacao_id}"
            data = {"clausula": clausula_id}

            response = requests.patch(
                url, headers=self.directus_headers, json=data, timeout=30
            )

            if response.status_code == 200:
                print(
                    f"✅ Modificação {modificacao_id} associada à cláusula {clausula_id}"
                )
                return True
            else:
                print(
                    f"❌ Erro ao associar modificação {modificacao_id}: {response.status_code}"
                )
                return False

        except Exception as e:
            print(f"❌ Erro ao associar modificação {modificacao_id}: {e}")
            return False

    def buscar_todas_tags(self, modelo_id):
        """
        Busca todas as tags do modelo de contrato (sem filtro de posição)
        """
        try:
            url = f"{DIRECTUS_BASE_URL}/items/modelo_contrato_tag"
            params = {
                "filter[modelo_contrato][_eq]": modelo_id,
                "fields": "id,tag_nome,clausulas",
                "limit": 100,
            }

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code == 200:
                tags = response.json().get("data", [])
                tags_processadas = []

                for tag in tags:
                    tags_processadas.append(
                        {
                            "id": tag["id"],
                            "nome": tag["tag_nome"],
                            "clausulas": tag.get("clausulas", []),
                        }
                    )

                print(f"✅ Encontradas {len(tags_processadas)} tags")
                return tags_processadas

            else:
                print(f"❌ Erro ao buscar tags: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Erro ao buscar tags: {e}")
            return []

    def buscar_todas_modificacoes(self, versao_id):
        """
        Busca todas as modificações da versão sem cláusula
        """
        try:
            url = f"{DIRECTUS_BASE_URL}/items/modificacao"
            params = {
                "filter[versao][_eq]": versao_id,
                "filter[clausula][_null]": "true",  # Só modificações sem cláusula
                "fields": "id,categoria,conteudo",
                "limit": 1000,
            }

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code == 200:
                modificacoes = response.json().get("data", [])
                print(f"✅ Encontradas {len(modificacoes)} modificações sem cláusula")
                return modificacoes

            else:
                print(f"❌ Erro ao buscar modificações: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Erro ao buscar modificações: {e}")
            return []

    def associar_modificacao_por_conteudo(self, modificacoes, tags):
        """
        Associa modificações às tags baseado no conteúdo
        Procura por palavras-chave das tags no conteúdo das modificações
        """
        associacoes = []

        # Mapeamento de palavras-chave para cada tipo de tag
        palavras_chave = {
            "locador": ["LOCADOR", "locador", "Locador"],
            "locatario": [
                "LOCATÁRIO",
                "LOCATARIO",
                "locatario",
                "Locatário",
                "locatário",
            ],
            "imovel": ["imóvel", "imovel", "IMÓVEL", "IMOVEL", "situado", "localizado"],
            "prazo": ["prazo", "meses", "anos", "vigência", "duração"],
            "valor": ["valor", "aluguel", "locação", "R$", "reais"],
        }

        for modificacao in modificacoes:
            conteudo = modificacao.get("conteudo", "").lower()

            for tag in tags:
                tag_nome = tag.get("nome", "").lower()

                # Buscar palavras-chave da tag no conteúdo
                if tag_nome in palavras_chave:
                    palavras = palavras_chave[tag_nome]
                    for palavra in palavras:
                        if palavra.lower() in conteudo:
                            print(
                                f"   ✅ MATCH por conteúdo: '{palavra}' em '{conteudo[:50]}...'"
                            )
                            associacoes.append(
                                {
                                    "modificacao": modificacao,
                                    "tag": tag,
                                    "confianca": 0.8,  # Alta confiança para match de palavra-chave
                                    "motivo": f"Palavra-chave '{palavra}' encontrada",
                                }
                            )
                            break  # Só uma associação por modificação
                    if (
                        associacoes
                        and associacoes[-1]["modificacao"]["id"] == modificacao["id"]
                    ):
                        break  # Já associou esta modificação

        return associacoes

    def buscar_versao_valida(self):
        """
        Busca uma versão válida no sistema para teste
        """
        try:
            # URL simples como no processador_automatico.py
            url = f"{DIRECTUS_BASE_URL}/items/versao?limit=5"

            response = requests.get(url, headers=self.directus_headers, timeout=30)

            if response.status_code == 200:
                versoes = response.json().get("data", [])
                if versoes:
                    print("📋 Versões disponíveis:")
                    for v in versoes[:5]:
                        print(f"   • {v['id']}: {v.get('versao', 'Sem nome')}")
                    return versoes[0]["id"]
                else:
                    print("❌ Nenhuma versão encontrada")
                    return None
            else:
                print(f"❌ Erro ao buscar versões: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return None

        except Exception as e:
            print(f"❌ Erro ao buscar versões: {e}")
            return None

    def buscar_clausula_por_tag(self, tag_data):
        """
        Busca a cláusula associada a uma tag usando os IDs diretos da tag
        """
        clausulas_ids = tag_data.get("clausulas", [])

        if not clausulas_ids:
            return None

        try:
            # Buscar a primeira cláusula associada
            url = f"{DIRECTUS_BASE_URL}/items/clausula/{clausulas_ids[0]}"
            params = {
                "fields": "id,nome",
            }

            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code == 200:
                return response.json().get("data")
            else:
                return None

        except Exception as e:
            print(f"❌ Erro ao buscar cláusula: {e}")
            return None

    def associar_modificacao_clausula(self, modificacao_id, clausula_id):
        """
        Associa uma modificação a uma cláusula
        """
        try:
            url = f"{DIRECTUS_BASE_URL}/items/modificacao/{modificacao_id}"
            response = requests.patch(
                url,
                headers=self.directus_headers,
                json={"clausula": clausula_id},
                timeout=30,
            )

            return response.status_code in [200, 204]

        except Exception as e:
            print(f"❌ Erro ao associar modificação: {e}")
            return False

    def processar_agrupamento_posicional_unificado(self, versao_id, dry_run=False):
        """
        Processa agrupamento usando posições unificadas calculadas pela PositionCalculator
        Garante que tags e modificações usem o mesmo sistema de coordenadas
        """
        print(f"\n🎯 Processamento Posicional Unificado - Versão: {versao_id}")
        print("=" * 60)

        try:
            # 1. Buscar dados da versão e arquivos
            versao_data = self._buscar_dados_versao(versao_id)
            if not versao_data:
                return {"erro": "Dados da versão não encontrados"}

            # 2. Baixar arquivos para análise
            arquivo_original_path, arquivo_modificado_path = (
                self._baixar_arquivos_versao(versao_data)
            )
            if not arquivo_original_path or not arquivo_modificado_path:
                return {"erro": "Não foi possível baixar os arquivos para análise"}

            # 3. Buscar tags e modificações
            modelo_id = versao_data.get("modelo_id")
            tags = self.buscar_tags_com_posicoes_validas(modelo_id)
            modificacoes = self.buscar_modificacoes_com_posicoes_validas(versao_id)

            if not tags or not modificacoes:
                return {"erro": "Tags ou modificações não encontradas"}

            # 4. Calcular posições unificadas usando PositionCalculator
            print("📐 Calculando posições unificadas...")
            positions_data = PositionCalculator.calculate_unified_positions(
                arquivo_original_path, arquivo_modificado_path, tags, modificacoes
            )

            if not positions_data.get("tags") or not positions_data.get("modificacoes"):
                return {"erro": "Falha no cálculo de posições unificadas"}

            # 5. Associar baseado nas posições unificadas
            associacoes = self._associar_por_posicoes_unificadas(
                positions_data["tags"],
                positions_data["modificacoes"],
                tags,
                modificacoes,
            )

            # 6. Salvar associações se não for dry_run
            if not dry_run and associacoes:
                self._salvar_associacoes(associacoes)

            # 7. Gerar estatísticas
            estatisticas = self._gerar_estatisticas_unificadas(
                len(tags), len(modificacoes), len(associacoes)
            )

            print("\n📊 RELATÓRIO FINAL")
            print("=" * 60)
            print(f"📈 Total de tags: {estatisticas['total_tags']}")
            print(f"📈 Total de modificações: {estatisticas['total_modificacoes']}")
            print(f"✅ Associações criadas: {estatisticas['associacoes_criadas']}")
            print(f"📊 Taxa de sucesso: {estatisticas['taxa_sucesso']:.1%}")

            return estatisticas

        except Exception as e:
            print(f"❌ Erro no processamento unificado: {e}")
            return {"erro": f"Erro no processamento: {e}"}

    def _buscar_dados_versao(self, versao_id):
        """Busca dados completos da versão"""
        try:
            url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
            params = {
                "fields": "contrato.modelo_contrato.id,contrato.modelo_contrato.arquivo_original,arquivo"
            }
            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code == 200:
                data = response.json().get("data", {})
                contrato = data.get("contrato", {})
                modelo_contrato = contrato.get("modelo_contrato", {})

                return {
                    "modelo_id": modelo_contrato.get("id"),
                    "arquivo_original_id": modelo_contrato.get("arquivo_original"),
                    "arquivo_modificado_id": data.get("arquivo"),
                }
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar dados da versão: {e}")
            return None

    def _baixar_arquivos_versao(self, versao_data):
        """Baixa arquivos original e modificado (placeholder - implementar download)"""
        # TODO: Implementar download real dos arquivos do Directus
        # Por enquanto, retornar caminhos mock para teste
        print("⚠️ MOCK: Download de arquivos não implementado")
        return None, None

    def _associar_por_posicoes_unificadas(
        self, tags_positions, modificacoes_positions, tags_data, modificacoes_data
    ):
        """Associa modificações às tags baseado nas posições unificadas"""
        associacoes = []

        for mod_id, mod_pos in modificacoes_positions.items():
            mod_inicio = mod_pos["inicio"]
            mod_fim = mod_pos["fim"]

            melhor_tag = None
            maior_sobreposicao = 0

            for tag_id, tag_pos in tags_positions.items():
                tag_inicio = tag_pos["inicio"]
                tag_fim = tag_pos["fim"]

                # Calcular sobreposição
                sobreposicao = self.calcular_sobreposicao(
                    (mod_inicio, mod_fim), (tag_inicio, tag_fim)
                )

                if (
                    sobreposicao > maior_sobreposicao and sobreposicao > 0.3
                ):  # 30% threshold
                    maior_sobreposicao = sobreposicao
                    melhor_tag = tag_id

            if melhor_tag:
                # Buscar dados originais da tag
                tag_data = next((t for t in tags_data if t["id"] == melhor_tag), None)
                mod_data = next(
                    (m for m in modificacoes_data if m["id"] == mod_id), None
                )

                if tag_data and mod_data:
                    associacoes.append(
                        {
                            "modificacao_id": mod_id,
                            "tag_id": melhor_tag,
                            "clausula_id": tag_data.get("clausulas", [{}])[0].get("id")
                            if tag_data.get("clausulas")
                            else None,
                            "sobreposicao": maior_sobreposicao,
                            "tag_nome": tag_data.get("tag_nome"),
                            "modificacao_conteudo": mod_data.get("conteudo", "")[:50]
                            + "...",
                        }
                    )

                    print(
                        f"✅ Associação: {tag_data.get('tag_nome')} ↔ {mod_data.get('conteudo', '')[:30]}... ({maior_sobreposicao:.1%})"
                    )

        return associacoes

    def _salvar_associacoes(self, associacoes):
        """Salva associações no banco de dados"""
        # Implementar salvamento via API Directus
        print(f"💾 {len(associacoes)} associações seriam salvas (não implementado)")

    def _gerar_estatisticas_unificadas(
        self, total_tags, total_modificacoes, associacoes_criadas
    ):
        """Gera estatísticas do processamento unificado"""
        taxa_sucesso = (
            associacoes_criadas / total_modificacoes if total_modificacoes > 0 else 0
        )

        return {
            "total_tags": total_tags,
            "total_modificacoes": total_modificacoes,
            "associacoes_criadas": associacoes_criadas,
            "taxa_sucesso": taxa_sucesso,
            "sucesso": True,
        }

    def processar_agrupamento_posicional(self, versao_id, dry_run=False):
        """
        Processa agrupamento usando posições no documento
        Implementa a especificação da task-001
        """
        print(f"\n🎯 Processamento posicional - Versão: {versao_id}")
        print("=" * 60)

        # 1. Buscar modelo de contrato
        try:
            url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
            params = {"fields": "contrato.modelo_contrato.id"}
            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code != 200:
                print(f"❌ Versão {versao_id} não encontrada")
                return {"erro": "Versão não encontrada"}

            versao_data = response.json().get("data", {})
            modelo_id = (
                versao_data.get("contrato", {}).get("modelo_contrato", {}).get("id")
            )

            if not modelo_id:
                print("❌ Modelo de contrato não encontrado")
                return {"erro": "Modelo de contrato não encontrado"}

            print(f"✅ Modelo de contrato encontrado: {modelo_id}")

        except Exception as e:
            print(f"❌ Erro ao buscar versão: {e}")
            return {"erro": f"Erro ao buscar versão: {e}"}

        # 2. Buscar tags com posições válidas via API Directus
        print(f"🔍 Buscando tags com posições válidas para modelo: {modelo_id}")
        tags = self.buscar_tags_com_posicoes_validas(modelo_id)
        if not tags:
            print("⚠️ Nenhuma tag com posições válidas encontrada")
            return {"erro": "Nenhuma tag com posições válidas"}

        print(f"✅ Encontradas {len(tags)} tags com posições válidas")

        # 3. Buscar modificações não associadas da versão
        print(f"🔍 Buscando modificações não associadas da versão: {versao_id}")
        modificacoes = self.buscar_modificacoes_com_posicoes_validas(versao_id)
        if not modificacoes:
            print("ℹ️ Nenhuma modificação não associada para processar")
            return {"info": "Nenhuma modificação para processar"}

        print(f"✅ Encontradas {len(modificacoes)} modificações para processar")

        # 4. Processar associações por posição
        estatisticas = {
            "total_modificacoes": len(modificacoes),
            "associacoes_criadas": 0,
            "associacoes_falharam": 0,
            "sem_correspondencia": 0,
            "detalhes": [],
        }

        for modificacao in modificacoes:
            mod_id = modificacao["id"]
            conteudo = (
                modificacao["conteudo"][:50] + "..."
                if len(modificacao["conteudo"]) > 50
                else modificacao["conteudo"]
            )

            print(f"\n🔍 Processando modificação {mod_id}")
            pos_inicio = modificacao.get("posicao_inicio_numero")
            pos_fim = modificacao.get("posicao_fim_numero")
            print(f"📍 Posições: {pos_inicio}-{pos_fim}")
            print(f"📝 Conteúdo: {conteudo}")

            if not dry_run:
                # 4.1. Atualizar modificação com posições numéricas
                self.atualizar_modificacao_com_posicoes(mod_id, pos_inicio, pos_fim)

            # 4.2. Encontrar tag que contém a modificação
            tag_correspondente = self.associar_modificacao_a_tag(modificacao, tags)

            if tag_correspondente and tag_correspondente.get("clausulas"):
                clausulas = tag_correspondente["clausulas"]
                if clausulas:
                    clausula_id = clausulas[0]["id"]
                    tag_nome = tag_correspondente["tag_nome"]

                    print(f"🎯 MATCH! Tag '{tag_nome}' contém modificação")
                    print(
                        f"📍 Tag posição: {tag_correspondente.get('posicao_inicio_texto')}-{tag_correspondente.get('posicao_fim_texto')}"
                    )
                    print(f"📍 Mod posição: {pos_inicio}-{pos_fim}")

                    if not dry_run:
                        # 4.3. Associar modificação à cláusula via API
                        sucesso = self.associar_modificacao_clausula_api(
                            mod_id, clausula_id
                        )
                        if sucesso:
                            estatisticas["associacoes_criadas"] += 1
                            estatisticas["detalhes"].append(
                                {
                                    "modificacao_id": mod_id,
                                    "tag": tag_nome,
                                    "clausula_id": clausula_id,
                                    "status": "sucesso",
                                }
                            )
                        else:
                            estatisticas["associacoes_falharam"] += 1
                    else:
                        print(f"🚀 DRY-RUN: Associaria à cláusula {clausula_id}")
                        estatisticas["associacoes_criadas"] += 1

                else:
                    print(
                        f"⚠️ Tag '{tag_correspondente['tag_nome']}' não tem cláusulas associadas"
                    )
                    estatisticas["sem_correspondencia"] += 1
            else:
                print("❌ Nenhuma tag correspondente encontrada")
                estatisticas["sem_correspondencia"] += 1

        # 5. Relatório final
        print("\n📊 RELATÓRIO FINAL")
        print("=" * 60)
        print(f"📈 Total de modificações: {estatisticas['total_modificacoes']}")
        print(f"✅ Associações criadas: {estatisticas['associacoes_criadas']}")
        print(f"❌ Associações falharam: {estatisticas['associacoes_falharam']}")
        print(f"⚠️ Sem correspondência: {estatisticas['sem_correspondencia']}")

        taxa_sucesso = (
            (
                estatisticas["associacoes_criadas"]
                / estatisticas["total_modificacoes"]
                * 100
            )
            if estatisticas["total_modificacoes"] > 0
            else 0
        )
        print(f"📊 Taxa de sucesso: {taxa_sucesso:.1f}%")

        return estatisticas


def main():
    """Teste do agrupador posicional"""
    agrupador = AgrupadorPosicional()

    print("🚀 Testando Agrupador Posicional")
    print("=" * 50)

    # Buscar uma versão válida automaticamente
    versao_id = agrupador.buscar_versao_valida()

    if not versao_id:
        print("❌ Nenhuma versão válida encontrada para teste")
        return

    print(f"\n🎯 Usando versão: {versao_id}")

    # Testar primeiro o método original
    print("\n📊 Método Original:")
    resultado_original = agrupador.processar_agrupamento_posicional(
        versao_id, dry_run=False
    )

    if "erro" in resultado_original:
        print(f"❌ Erro: {resultado_original['erro']}")
    else:
        print("✅ Processamento original concluído!")

    # Testar método unificado (comentado até implementar download)
    print("\n📐 Método Unificado (em desenvolvimento):")
    print("⚠️ Método unificado requer implementação de download de arquivos")

    # resultado_unificado = agrupador.processar_agrupamento_posicional_unificado(versao_id, dry_run=True)
    # if "erro" in resultado_unificado:
    #     print(f"❌ Erro: {resultado_unificado['erro']}")
    # else:
    #     print("✅ Processamento unificado concluído!")


if __name__ == "__main__":
    main()
