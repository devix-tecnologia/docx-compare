#!/usr/bin/env python3
"""
Agrupador de modificações por capítulo
Compara o conteúdo das modificações com as tags do modelo de contrato para agrupá-las por capítulos/cláusulas
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

    def calcular_similaridade_caminho(self, caminho1: str, caminho2: str) -> float:
        """
        Calcula similaridade entre dois caminhos de modificações/tags
        Considera a estrutura: modificacao_{numero}_linha_{linha}_pos_{pos}
        """
        if not caminho1 or not caminho2:
            return 0.0

        try:
            # Extrair componentes do caminho usando regex
            import re
            pattern = r"modificacao_(\d+)_linha_(\d+)_pos_(\d+)"

            match1 = re.match(pattern, caminho1)
            match2 = re.match(pattern, caminho2)

            if not match1 or not match2:
                # Fallback para similaridade de texto simples
                return SequenceMatcher(None, caminho1.lower(), caminho2.lower()).ratio()

            # Extrair números
            num1, linha1, pos1 = map(int, match1.groups())
            num2, linha2, pos2 = map(int, match2.groups())

            # Calcular similaridade baseada em proximidade
            # Peso maior para linhas próximas, menor para posições
            similarity_linha = 1.0 - min(abs(linha1 - linha2) / max(linha1, linha2, 1), 1.0)
            similarity_pos = 1.0 - min(abs(pos1 - pos2) / max(pos1, pos2, 1), 1.0)

            # Combinar com peso maior para linha (estrutura mais importante)
            return similarity_linha * 0.7 + similarity_pos * 0.3

        except Exception:
            # Em caso de erro, usar similaridade de texto
            return SequenceMatcher(None, caminho1.lower(), caminho2.lower()).ratio()

    def extrair_contexto_caminho(self, caminho_inicio: str, caminho_fim: str | None = None) -> str:
        """
        Extrai contexto útil dos caminhos para melhorar correspondência
        """
        contexto_parts = []

        try:
            import re
            pattern = r"modificacao_(\d+)_linha_(\d+)_pos_(\d+)"

            if caminho_inicio:
                match = re.match(pattern, caminho_inicio)
                if match:
                    num, linha, pos = match.groups()
                    contexto_parts.extend([f"linha_{linha}", f"modificacao_{num}"])

            if caminho_fim and caminho_fim != caminho_inicio:
                match = re.match(pattern, caminho_fim)
                if match:
                    num, linha, pos = match.groups()
                    contexto_parts.extend([f"linha_{linha}", f"modificacao_{num}"])

        except Exception:
            # Fallback simples
            if caminho_inicio:
                contexto_parts.append(caminho_inicio.replace("_", " "))

        return " ".join(set(contexto_parts))  # Remove duplicatas

    def buscar_tags_modelo(self, modelo_contrato_id: str) -> list:
        """
        Busca todas as tags de um modelo de contrato específico
        """
        try:
            print(f"🔍 Buscando tags do modelo de contrato {modelo_contrato_id}")

            url = f"{self.directus_base_url}/items/modelo_contrato_tag"
            params = {
                "filter[modelo_contrato][_eq]": modelo_contrato_id,
                "fields": "id,tag_nome,conteudo,caminho_tag_inicio,caminho_tag_fim",
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
        conteudo_modificacao: str,
        tags_modelo: list,
        threshold: float = 0.6,
        caminho_inicio_mod: str | None = None,
        caminho_fim_mod: str | None = None
    ) -> tuple:
        """
        Encontra a tag do modelo que melhor corresponde ao conteúdo da modificação
        Agora considera também os caminhos para melhorar a precisão

        Args:
            conteudo_modificacao: Texto original da modificação
            tags_modelo: Lista de tags do modelo de contrato
            threshold: Limiar mínimo de similaridade (padrão: 0.6)
            caminho_inicio_mod: Caminho de início da modificação
            caminho_fim_mod: Caminho de fim da modificação

        Returns:
            Tupla (tag_correspondente, score_similaridade)
        """
        melhor_tag = None
        melhor_score = 0.0

        if not conteudo_modificacao:
            return None, 0.0

        # Extrair contexto dos caminhos da modificação
        contexto_modificacao = self.extrair_contexto_caminho(
            caminho_inicio_mod or "",
            caminho_fim_mod or ""
        )

        for tag in tags_modelo:
            tag_conteudo = tag.get("conteudo", "")
            tag_caminho_inicio = tag.get("caminho_tag_inicio", "")
            tag_caminho_fim = tag.get("caminho_tag_fim", "")

            # 1. Calcular similaridade de conteúdo
            score_conteudo = self.calcular_similaridade(conteudo_modificacao, tag_conteudo)

            # 2. Calcular similaridade de caminhos (se disponível)
            score_caminho = 0.0
            if caminho_inicio_mod and tag_caminho_inicio:
                score_caminho_inicio = self.calcular_similaridade_caminho(
                    caminho_inicio_mod, tag_caminho_inicio
                )
                score_caminho_fim = self.calcular_similaridade_caminho(
                    caminho_fim_mod or caminho_inicio_mod,
                    tag_caminho_fim or tag_caminho_inicio
                )
                score_caminho = max(score_caminho_inicio, score_caminho_fim)

            # 3. Calcular similaridade de contexto (palavras-chave dos caminhos)
            score_contexto = 0.0
            if contexto_modificacao:
                contexto_tag = self.extrair_contexto_caminho(tag_caminho_inicio, tag_caminho_fim)
                if contexto_tag:
                    score_contexto = self.calcular_similaridade(contexto_modificacao, contexto_tag)

            # 4. Score final ponderado:
            # - Conteúdo: peso 0.6 (mais importante)
            # - Caminho: peso 0.3 (estrutura hierárquica)
            # - Contexto: peso 0.1 (palavras-chave)
            if score_caminho > 0 or score_contexto > 0:
                score_final = (
                    score_conteudo * 0.6 +
                    score_caminho * 0.3 +
                    score_contexto * 0.1
                )
            else:
                # Se não há informação de caminho, usar apenas conteúdo
                score_final = score_conteudo

            print(f"    🔍 Tag '{tag.get('tag_nome', 'N/A')}': "
                  f"conteúdo={score_conteudo:.3f}, "
                  f"caminho={score_caminho:.3f}, "
                  f"contexto={score_contexto:.3f}, "
                  f"final={score_final:.3f}")

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

    def buscar_modificacoes_versao(self, versao_id: str) -> list:
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
                caminho_inicio = modificacao.get("caminho_inicio", "")
                caminho_fim = modificacao.get("caminho_fim", "")

                print(f"\n🔍 Processando modificação {modificacao_id} ({categoria})")
                print(f"   Conteúdo: {conteudo[:100]}{'...' if len(conteudo) > 100 else ''}")
                if caminho_inicio:
                    print(f"   📍 Caminho: {caminho_inicio}")
                    if caminho_fim and caminho_fim != caminho_inicio:
                        print(f"   📍 Até: {caminho_fim}")

                # Encontrar melhor correspondência (agora usando caminhos)
                tag_correspondente, score = self.encontrar_melhor_correspondencia(
                    conteudo, tags_modelo, threshold, caminho_inicio, caminho_fim
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
