#!/usr/bin/env python3
"""
Agrupador de modificações por capítulo
Compara o conteúdo das modificações com as tags do modelo e agrupá-las por capítulos/cláusulas
"""

import re
from difflib import SequenceMatcher

import requests


class AgrupadorModificacoes:
    """
    Classe responsável por agrupar modificações de versões por capítulos
    baseado na correspondência entre conteúdo das modificações e tags do modelo
    """

    def __init__(self, directus_base_url: str, directus_token: str, request_timeout: int = 30):
        self.directus_base_url = directus_base_url
        self.directus_headers = {
            "Authorization": f"Bearer {directus_token}",
            "Content-Type": "application/json",
        }
        self.request_timeout = request_timeout

    def normalizar_texto(self, texto: str) -> str:
        """
        Normaliza texto para comparação:
        - Remove espaços extras
        - Converte para minúsculas
        - Remove pontuação especial
        """
        if not texto:
            return ""

        # Remover espaços extras e quebras de linha
        texto = re.sub(r"\s+", " ", texto.strip())

        # Converter para minúsculas
        texto = texto.lower()

        # Remover pontuação que pode variar
        texto = re.sub(r'[.,;:!?()"\[\]{}]', "", texto)

        return texto

    def calcular_similaridade(self, texto1: str, texto2: str) -> float:
        """
        Calcula similaridade entre dois textos usando SequenceMatcher
        Retorna valor entre 0 e 1 (1 = textos idênticos)
        """
        texto1_norm = self.normalizar_texto(texto1)
        texto2_norm = self.normalizar_texto(texto2)

        if not texto1_norm or not texto2_norm:
            return 0.0

        return SequenceMatcher(None, texto1_norm, texto2_norm).ratio()

    def buscar_tags_modelo(self, modelo_contrato_id: str) -> list[dict]:
        """
        Busca todas as tags de um modelo de contrato específico
        """
        try:
            print(f"🔍 Buscando tags do modelo de contrato {modelo_contrato_id}")

            url = f"{self.directus_base_url}/items/modelo_contrato_tag"
            params = {
                "filter[modelo_contrato][_eq]": modelo_contrato_id,
                "fields": "id,tag_nome,conteudo,contexto,caminho_tag_inicio,caminho_tag_fim",
                "limit": 1000,
                "sort": "tag_nome"
            }

            response = requests.get(
                url,
                headers=self.directus_headers,
                params=params,
                timeout=self.request_timeout
            )

            if response.status_code == 200:
                tags = response.json().get("data", [])
                print(f"✅ Encontradas {len(tags)} tags no modelo")
                return tags
            else:
                print(f"❌ Erro ao buscar tags: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Erro ao buscar tags do modelo: {e}")
            return []

    def buscar_clausulas_por_tag(self, tag_id: str) -> dict | None:
        """
        Busca a cláusula associada a uma tag específica
        """
        try:
            url = f"{self.directus_base_url}/items/clausula"
            params = {
                "filter[tag][_eq]": tag_id,
                "fields": "id,numero,nome,conteudo,tag.tag_nome",
                "limit": 1
            }

            response = requests.get(
                url,
                headers=self.directus_headers,
                params=params,
                timeout=self.request_timeout
            )

            if response.status_code == 200:
                clausulas = response.json().get("data", [])
                return clausulas[0] if clausulas else None
            else:
                print(f"⚠️ Erro ao buscar cláusula para tag {tag_id}: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Erro ao buscar cláusula para tag {tag_id}: {e}")
            return None

    def encontrar_melhor_correspondencia(
        self,
        modificacao: dict,
        tags_modelo: list[dict],
        threshold: float = 0.6
    ) -> tuple[dict | None, float]:
        """
        Encontra a tag do modelo que melhor corresponde à modificação usando análise ponderada:
        - Conteúdo: 60% do peso
        - Caminho: 30% do peso
        - Contexto: 10% do peso

        Args:
            modificacao: Dados completos da modificação incluindo caminho_inicio/fim
            tags_modelo: Lista de tags do modelo de contrato
            threshold: Limiar mínimo de similaridade (padrão: 0.6)

        Returns:
            Tupla (tag_correspondente, score_similaridade)
        """
        melhor_tag = None
        melhor_score = 0.0

        conteudo_modificacao = modificacao.get("conteudo", "")
        caminho_inicio_mod = modificacao.get("caminho_inicio", "")
        caminho_fim_mod = modificacao.get("caminho_fim", "")

        if not conteudo_modificacao:
            return None, 0.0

        for tag in tags_modelo:
            tag_conteudo = tag.get("conteudo", "")
            tag_contexto = tag.get("contexto", "")
            caminho_inicio_tag = tag.get("caminho_tag_inicio", "")
            caminho_fim_tag = tag.get("caminho_tag_fim", "")

            # 1. Similaridade de caminho (50% do peso) - Tags são posicionais por natureza
            score_caminho = 0.0
            if caminho_inicio_mod and caminho_inicio_tag:
                score_caminho_inicio = self.calcular_similaridade(caminho_inicio_mod, caminho_inicio_tag)
                score_caminho_fim = 0.0
                if caminho_fim_mod and caminho_fim_tag:
                    score_caminho_fim = self.calcular_similaridade(caminho_fim_mod, caminho_fim_tag)
                score_caminho = max(score_caminho_inicio, score_caminho_fim)
            peso_caminho = score_caminho * 0.5

            # 2. Similaridade de conteúdo (40% do peso)
            score_conteudo = self.calcular_similaridade(conteudo_modificacao, tag_conteudo)
            peso_conteudo = score_conteudo * 0.4

            # 3. Similaridade de contexto (10% do peso)
            score_contexto = self.calcular_similaridade(conteudo_modificacao, tag_contexto)
            peso_contexto = score_contexto * 0.1

            # Score final ponderado
            score_final = peso_conteudo + peso_caminho + peso_contexto

            # Log detalhado para debugging (ordem de prioridade: caminho, conteúdo, contexto)
            print(f"    🔍 Tag '{tag.get('tag', 'sem_tag')}': caminho={score_caminho:.3f}, conteúdo={score_conteudo:.3f}, contexto={score_contexto:.3f}, final={score_final:.3f}")

            if score_final > melhor_score and score_final >= threshold:
                melhor_score = score_final
                melhor_tag = tag

        return melhor_tag, melhor_score

    def associar_modificacao_clausula(self, modificacao_id: str, clausula_id: str) -> bool:
        """
        Associa uma modificação a uma cláusula específica
        """
        try:
            print(f"🔗 Associando modificação {modificacao_id} à cláusula {clausula_id}")

            url = f"{self.directus_base_url}/items/modificacao/{modificacao_id}"
            data = {"clausula": clausula_id}

            response = requests.patch(
                url,
                headers=self.directus_headers,
                json=data,
                timeout=self.request_timeout
            )

            if response.status_code in [200, 204]:
                print("✅ Associação criada com sucesso")
                return True
            else:
                print(f"❌ Erro ao criar associação: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Erro ao associar modificação à cláusula: {e}")
            return False

    def limpar_modificacoes_versao(self, versao_id: str, dry_run: bool = False) -> dict:
        """
        Remove todas as modificações associadas a uma versão específica
        Útil quando uma versão volta para status 'draft'

        Args:
            versao_id: ID da versão
            dry_run: Se True, não faz alterações no banco

        Returns:
            Dicionário com estatísticas da limpeza
        """
        try:
            print(f"🧹 Limpando modificações da versão {versao_id}")

            # Buscar todas as modificações da versão em lotes
            todas_modificacoes = []
            offset = 0
            limite_por_lote = 1000

            while True:
                url = f"{self.directus_base_url}/items/modificacao"
                params = {
                    "filter[versao][_eq]": versao_id,
                    "fields": "id",
                    "limit": limite_por_lote,
                    "offset": offset
                }

                response = requests.get(
                    url,
                    headers=self.directus_headers,
                    params=params,
                    timeout=self.request_timeout
                )

                if response.status_code != 200:
                    print(f"❌ Erro ao buscar modificações: HTTP {response.status_code}")
                    return {"erro": f"Erro ao buscar modificações: HTTP {response.status_code}"}

                lote = response.json().get("data", [])
                if not lote:
                    break

                todas_modificacoes.extend(lote)
                offset += limite_por_lote

                # Se retornou menos que o limite, chegamos ao fim
                if len(lote) < limite_por_lote:
                    break

            total_encontradas = len(todas_modificacoes)

            if total_encontradas == 0:
                print("ℹ️ Nenhuma modificação encontrada para esta versão")
                return {"info": "Nenhuma modificação encontrada", "total_removidas": 0}

            print(f"🔍 Encontradas {total_encontradas} modificações para remoção")

            # Remover modificações
            estatisticas = {
                "total_encontradas": total_encontradas,
                "total_removidas": 0,
                "falhas": 0,
                "detalhes": []
            }

            if dry_run:
                print("🏃‍♂️ DRY-RUN: Simulando remoção das modificações")
                estatisticas["total_removidas"] = total_encontradas
                # Apenas contar, sem logar cada item
                estatisticas["detalhes"] = [{"status": "dry_run"} for _ in todas_modificacoes]
            else:
                print("🗑️ Removendo modificações...")

                for i, mod in enumerate(todas_modificacoes, 1):
                    modificacao_id = mod["id"]

                    # Mostrar progresso apenas a cada 10% ou se há poucas modificações
                    if total_encontradas <= 10 or i % max(1, total_encontradas // 10) == 0:
                        progresso = (i / total_encontradas) * 100
                        print(f"   � Progresso: {i}/{total_encontradas} ({progresso:.0f}%)")

                    # Deletar modificação
                    delete_url = f"{self.directus_base_url}/items/modificacao/{modificacao_id}"
                    delete_response = requests.delete(
                        delete_url,
                        headers=self.directus_headers,
                        timeout=self.request_timeout
                    )

                    if delete_response.status_code in [200, 204]:
                        estatisticas["total_removidas"] += 1
                        estatisticas["detalhes"].append({
                            "modificacao_id": modificacao_id,
                            "status": "removida"
                        })
                    else:
                        estatisticas["falhas"] += 1
                        estatisticas["detalhes"].append({
                            "modificacao_id": modificacao_id,
                            "status": "falha",
                            "erro": f"HTTP {delete_response.status_code}"
                        })
                        # Logar apenas os erros
                        print(f"   ❌ Erro ao remover {modificacao_id}: HTTP {delete_response.status_code}")

            # Resumo final
            print("\n📊 Limpeza concluída:")
            print(f"   🔍 Modificações encontradas: {estatisticas['total_encontradas']}")
            print(f"   🗑️ Modificações removidas: {estatisticas['total_removidas']}")
            print(f"   ❌ Falhas: {estatisticas['falhas']}")

            return estatisticas

        except Exception as e:
            print(f"❌ Erro na limpeza de modificações: {e}")
            return {"erro": str(e)}

    def buscar_modificacoes_versao(self, versao_id: str) -> list[dict]:
        """
        Busca todas as modificações de uma versão específica
        """
        try:
            print(f"🔍 Buscando modificações da versão {versao_id}")

            url = f"{self.directus_base_url}/items/modificacao"
            params = {
                "filter[versao][_eq]": versao_id,
                "filter[clausula][_null]": "true",  # Apenas modificações ainda não associadas
                "fields": "id,categoria,conteudo,alteracao,sort,clausula,caminho_inicio,caminho_fim",
                "limit": 1000,
                "sort": "sort"
            }

            response = requests.get(
                url,
                headers=self.directus_headers,
                params=params,
                timeout=self.request_timeout
            )

            if response.status_code == 200:
                modificacoes = response.json().get("data", [])
                print(f"✅ Encontradas {len(modificacoes)} modificações não associadas")
                return modificacoes
            else:
                print(f"❌ Erro ao buscar modificações: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Erro ao buscar modificações da versão: {e}")
            return []

    def obter_modelo_contrato_id(self, versao_id: str) -> str | None:
        """
        Obtém o ID do modelo de contrato associado a uma versão
        """
        try:
            print(f"🔍 Obtendo modelo de contrato para versão {versao_id}")

            url = f"{self.directus_base_url}/items/versao/{versao_id}"
            params = {
                "fields": "contrato.modelo_contrato.id"
            }

            response = requests.get(
                url,
                headers=self.directus_headers,
                params=params,
                timeout=self.request_timeout
            )

            if response.status_code == 200:
                data = response.json().get("data", {})
                contrato = data.get("contrato", {})
                if isinstance(contrato, dict):
                    modelo_contrato = contrato.get("modelo_contrato", {})
                    if isinstance(modelo_contrato, dict):
                        modelo_id = modelo_contrato.get("id")
                        if modelo_id:
                            print(f"✅ Modelo de contrato encontrado: {modelo_id}")
                            return modelo_id

                print("❌ Modelo de contrato não encontrado na estrutura da versão")
                return None
            else:
                print(f"❌ Erro ao buscar versão: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Erro ao obter modelo de contrato: {e}")
            return None

    def processar_agrupamento_versao(self, versao_id: str, threshold: float = 0.6, dry_run: bool = False) -> dict:
        """
        Processa o agrupamento de modificações por capítulo para uma versão específica

        Args:
            versao_id: ID da versão a processar
            threshold: Limiar mínimo de similaridade
            dry_run: Se True, não faz alterações no banco

        Returns:
            Dicionário com estatísticas do processamento
        """
        try:
            print(f"\n🎯 Processando agrupamento de modificações por capítulo - Versão: {versao_id}")

            # 1. Obter modelo de contrato da versão
            modelo_contrato_id = self.obter_modelo_contrato_id(versao_id)
            if not modelo_contrato_id:
                return {"erro": "Modelo de contrato não encontrado"}

            # 2. Buscar tags do modelo de contrato
            tags_modelo = self.buscar_tags_modelo(modelo_contrato_id)
            if not tags_modelo:
                return {"erro": "Nenhuma tag encontrada no modelo de contrato"}

            # 3. Buscar modificações da versão não associadas
            modificacoes = self.buscar_modificacoes_versao(versao_id)
            if not modificacoes:
                return {"info": "Nenhuma modificação não associada encontrada"}

            # 4. Processar cada modificação
            estatisticas = {
                "total_modificacoes": len(modificacoes),
                "associacoes_criadas": 0,
                "associacoes_falharam": 0,
                "modificacoes_sem_correspondencia": 0,
                "detalhes": []
            }

            for modificacao in modificacoes:
                modificacao_id = modificacao["id"]
                conteudo = modificacao.get("conteudo", "")
                categoria = modificacao.get("categoria", "")

                print(f"\n🔍 Processando modificação {modificacao_id} ({categoria})")
                print(f"   Conteúdo: {conteudo[:100]}{'...' if len(conteudo) > 100 else ''}")

                # Encontrar melhor correspondência
                tag_correspondente, score = self.encontrar_melhor_correspondencia(
                    modificacao, tags_modelo, threshold
                )

                if tag_correspondente:
                    tag_nome = tag_correspondente.get("tag_nome", "N/A")
                    print(f"   ✅ Correspondência encontrada: Tag '{tag_nome}' (score: {score:.2f})")

                    # Buscar cláusula associada à tag
                    clausula = self.buscar_clausulas_por_tag(tag_correspondente["id"])

                    if clausula:
                        clausula_nome = clausula.get("nome", "N/A")
                        print(f"   📋 Cláusula encontrada: '{clausula_nome}'")

                        if not dry_run:
                            # Criar associação
                            sucesso = self.associar_modificacao_clausula(
                                modificacao_id, clausula["id"]
                            )

                            if sucesso:
                                estatisticas["associacoes_criadas"] += 1
                                estatisticas["detalhes"].append({
                                    "modificacao_id": modificacao_id,
                                    "tag_nome": tag_nome,
                                    "clausula_nome": clausula_nome,
                                    "score": score,
                                    "status": "associada"
                                })
                            else:
                                estatisticas["associacoes_falharam"] += 1
                                estatisticas["detalhes"].append({
                                    "modificacao_id": modificacao_id,
                                    "tag_nome": tag_nome,
                                    "clausula_nome": clausula_nome,
                                    "score": score,
                                    "status": "falha_associacao"
                                })
                        else:
                            print(f"   🏃‍♂️ DRY-RUN: Associaria à cláusula '{clausula_nome}'")
                            estatisticas["associacoes_criadas"] += 1
                            estatisticas["detalhes"].append({
                                "modificacao_id": modificacao_id,
                                "tag_nome": tag_nome,
                                "clausula_nome": clausula_nome,
                                "score": score,
                                "status": "dry_run"
                            })
                    else:
                        print("   ⚠️ Tag encontrada mas sem cláusula associada")
                        estatisticas["modificacoes_sem_correspondencia"] += 1
                        estatisticas["detalhes"].append({
                            "modificacao_id": modificacao_id,
                            "tag_nome": tag_nome,
                            "clausula_nome": None,
                            "score": score,
                            "status": "sem_clausula"
                        })
                else:
                    print(f"   ❌ Nenhuma correspondência encontrada (threshold: {threshold})")
                    estatisticas["modificacoes_sem_correspondencia"] += 1
                    estatisticas["detalhes"].append({
                        "modificacao_id": modificacao_id,
                        "tag_nome": None,
                        "clausula_nome": None,
                        "score": 0.0,
                        "status": "sem_correspondencia"
                    })

            # 5. Resumo final
            print("\n📊 Processamento concluído:")
            print(f"   📝 Total de modificações: {estatisticas['total_modificacoes']}")
            print(f"   ✅ Associações criadas: {estatisticas['associacoes_criadas']}")
            print(f"   ❌ Associações falharam: {estatisticas['associacoes_falharam']}")
            print(f"   🔍 Sem correspondência: {estatisticas['modificacoes_sem_correspondencia']}")

            return estatisticas

        except Exception as e:
            print(f"❌ Erro no processamento de agrupamento: {e}")
            return {"erro": str(e)}

    def listar_agrupamentos_versao(self, versao_id: str) -> dict:
        """
        Lista as modificações agrupadas por cláusula para uma versão específica
        """
        try:
            print(f"\n📋 Listando agrupamentos da versão {versao_id}")

            url = f"{self.directus_base_url}/items/modificacao"
            params = {
                "filter[versao][_eq]": versao_id,
                "fields": "id,categoria,conteudo,alteracao,sort,clausula.id,clausula.nome,clausula.numero",
                "limit": 1000,
                "sort": "clausula.numero,sort"
            }

            response = requests.get(
                url,
                headers=self.directus_headers,
                params=params,
                timeout=self.request_timeout
            )

            if response.status_code == 200:
                modificacoes = response.json().get("data", [])

                # Agrupar por cláusula
                agrupamentos = {}
                sem_clausula = []

                for mod in modificacoes:
                    clausula = mod.get("clausula")
                    if clausula and isinstance(clausula, dict):
                        clausula_id = clausula.get("id")
                        clausula_nome = clausula.get("nome", "N/A")
                        clausula_numero = clausula.get("numero", "N/A")

                        if clausula_id not in agrupamentos:
                            agrupamentos[clausula_id] = {
                                "clausula_nome": clausula_nome,
                                "clausula_numero": clausula_numero,
                                "modificacoes": []
                            }

                        agrupamentos[clausula_id]["modificacoes"].append({
                            "id": mod["id"],
                            "categoria": mod.get("categoria", "N/A"),
                            "conteudo": mod.get("conteudo", "")[:100] + "..." if len(mod.get("conteudo", "")) > 100 else mod.get("conteudo", ""),
                            "alteracao": mod.get("alteracao", "")[:100] + "..." if len(mod.get("alteracao", "")) > 100 else mod.get("alteracao", "")
                        })
                    else:
                        sem_clausula.append({
                            "id": mod["id"],
                            "categoria": mod.get("categoria", "N/A"),
                            "conteudo": mod.get("conteudo", "")[:100] + "..." if len(mod.get("conteudo", "")) > 100 else mod.get("conteudo", "")
                        })

                resultado = {
                    "agrupamentos": agrupamentos,
                    "sem_clausula": sem_clausula,
                    "total_modificacoes": len(modificacoes),
                    "clausulas_com_modificacoes": len(agrupamentos),
                    "modificacoes_sem_clausula": len(sem_clausula)
                }

                print("✅ Listagem concluída:")
                print(f"   📝 Total de modificações: {resultado['total_modificacoes']}")
                print(f"   📋 Cláusulas com modificações: {resultado['clausulas_com_modificacoes']}")
                print(f"   🔍 Modificações sem cláusula: {resultado['modificacoes_sem_clausula']}")

                return resultado
            else:
                print(f"❌ Erro ao listar modificações: HTTP {response.status_code}")
                return {"erro": f"Erro HTTP {response.status_code}"}

        except Exception as e:
            print(f"❌ Erro ao listar agrupamentos: {e}")
            return {"erro": str(e)}
