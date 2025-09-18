#!/usr/bin/env python3
"""
Agrupador por Conteúdo - Associa modificações às tags por palavras-chave no conteúdo
Abordagem simples e eficaz baseada em busca textual
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "")


class AgrupadorConteudo:
    """
    Agrupador que associa modificações às tags baseado no conteúdo
    Usa palavras-chave para identificar o contexto das modificações
    """

    def __init__(self):
        self.directus_headers = {
            "Authorization": f"Bearer {DIRECTUS_TOKEN}",
            "Content-Type": "application/json",
        }

    def buscar_tags(self, modelo_id):
        """
        Busca todas as tags do modelo de contrato
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

    def buscar_modificacoes(self, versao_id):
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

    def associar_por_conteudo(self, modificacoes, tags):
        """
        Associa modificações às tags baseado no conteúdo
        """
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

        associacoes = []

        for modificacao in modificacoes:
            conteudo = modificacao.get("conteudo", "")

            for tag in tags:
                tag_nome = tag.get("nome", "").lower()

                # Buscar palavras-chave da tag no conteúdo
                if tag_nome in palavras_chave:
                    palavras = palavras_chave[tag_nome]
                    for palavra in palavras:
                        if palavra.lower() in conteudo.lower():
                            print(
                                f"   ✅ MATCH '{palavra}' em '{conteudo[:50]}...' → tag '{tag_nome}'"
                            )
                            associacoes.append(
                                {
                                    "modificacao": modificacao,
                                    "tag": tag,
                                    "confianca": 0.8,
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

    def processar_agrupamento_posicional(self, versao_id, dry_run=False):
        """
        Processa agrupamento usando conteúdo (mantém nome para compatibilidade)
        """
        print(f"\n🎯 Processamento por conteúdo - Versão: {versao_id}")
        print("=" * 60)

        # 1. Buscar modelo de contrato
        try:
            url = f"{DIRECTUS_BASE_URL}/items/versao/{versao_id}"
            params = {"fields": "contrato.modelo_contrato.id"}
            response = requests.get(
                url, headers=self.directus_headers, params=params, timeout=30
            )

            if response.status_code != 200:
                return {"erro": "Versão não encontrada"}

            versao_data = response.json().get("data", {})
            modelo_id = (
                versao_data.get("contrato", {}).get("modelo_contrato", {}).get("id")
            )

            if not modelo_id:
                return {"erro": "Modelo de contrato não encontrado"}

        except Exception as e:
            return {"erro": f"Erro ao buscar versão: {e}"}

        # 2. Buscar tags
        tags = self.buscar_tags(modelo_id)
        if not tags:
            return {"erro": "Nenhuma tag encontrada"}

        # 3. Buscar modificações
        modificacoes = self.buscar_modificacoes(versao_id)
        if not modificacoes:
            return {"info": "Nenhuma modificação para processar"}

        # 4. Processar associações por conteúdo
        print("\n🎯 Processando associações por conteúdo...")
        associacoes = self.associar_por_conteudo(modificacoes, tags)

        estatisticas = {
            "total_modificacoes": len(modificacoes),
            "associacoes_criadas": 0,
            "associacoes_falharam": 0,
            "sem_correspondencia": len(modificacoes),
            "detalhes": [],
        }

        for associacao in associacoes:
            modificacao = associacao["modificacao"]
            tag = associacao["tag"]

            mod_id = modificacao["id"]
            conteudo = (
                modificacao["conteudo"][:50] + "..."
                if len(modificacao["conteudo"]) > 50
                else modificacao["conteudo"]
            )

            print(f"\n🔍 Modificação {mod_id}")
            print(f"   📝 Conteúdo: {conteudo}")
            print(f"   🏷️ Tag: {tag['nome']}")
            print(f"   💡 Motivo: {associacao['motivo']}")

            # Buscar cláusula da tag
            clausulas = tag.get("clausulas", [])
            if clausulas:
                clausula_id = clausulas[0]  # Pegar primeira cláusula

                if not dry_run:
                    sucesso = self.associar_modificacao_clausula(mod_id, clausula_id)
                    if sucesso:
                        print(f"   ✅ Associação criada com cláusula {clausula_id}")
                        estatisticas["associacoes_criadas"] += 1
                        estatisticas["sem_correspondencia"] -= 1
                    else:
                        print("   ❌ Falha ao associar")
                        estatisticas["associacoes_falharam"] += 1
                else:
                    print(f"   🧪 DRY-RUN: Associaria com cláusula {clausula_id}")
                    estatisticas["associacoes_criadas"] += 1
                    estatisticas["sem_correspondencia"] -= 1

                estatisticas["detalhes"].append(
                    {
                        "modificacao_id": mod_id,
                        "tag_nome": tag["nome"],
                        "clausula_id": clausula_id,
                        "confianca": associacao["confianca"],
                        "status": "dry_run"
                        if dry_run
                        else ("associada" if sucesso else "falha"),
                    }
                )

            else:
                print(f"   ⚠️ Tag '{tag['nome']}' sem cláusula")
                estatisticas["associacoes_falharam"] += 1

        # 5. Resumo
        print("\n📊 Resumo do processamento por conteúdo:")
        print(f"   📝 Total: {estatisticas['total_modificacoes']}")
        print(f"   ✅ Associadas: {estatisticas['associacoes_criadas']}")
        print(f"   ❌ Falharam: {estatisticas['associacoes_falharam']}")
        print(f"   🔍 Sem correspondência: {estatisticas['sem_correspondencia']}")

        return estatisticas


def main():
    """Teste do agrupador por conteúdo"""
    agrupador = AgrupadorConteudo()

    print("🚀 Testando Agrupador por Conteúdo")
    print("=" * 50)

    # Usar uma versão conhecida
    versao_id = "c2b1dfa0-c664-48b8-a5ff-84b70041b428"
    print(f"\n🎯 Processando versão: {versao_id}")

    resultado = agrupador.processar_agrupamento_posicional(versao_id, dry_run=True)

    if "erro" in resultado:
        print(f"❌ Erro: {resultado['erro']}")
    else:
        print("\n✅ Processamento concluído!")


if __name__ == "__main__":
    main()
