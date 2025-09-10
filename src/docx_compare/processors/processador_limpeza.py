#!/usr/bin/env python3
"""
Processador de limpeza de         try:
            print(f"🔍 Buscando versões draft com modificações...")

            # Buscar versões em draft
            url = f"{self.directus_base_url}/items/versao"
            params = {
                "filter[status][_eq]": "draft",
                "fields": "id,versao,status",  # Removido contrato.nome para evitar erro de permissão
                "limit": 100
            }es
Monitora versões que voltaram para status 'draft' e remove suas modificações automaticamente
"""

import os
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

# Adicionar o caminho src ao Python path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from docx_compare.utils.agrupador_modificacoes import AgrupadorModificacoes

# Carregar variáveis de ambiente
load_dotenv()


class ProcessadorLimpeza:
    """
    Processador responsável por limpar modificações de versões em status 'draft'
    """

    def __init__(self):
        self.directus_base_url = (
            os.getenv("DIRECTUS_BASE_URL", "https://contract.devix.co")
            .replace("/admin/", "")
            .rstrip("/")
        )
        self.directus_token = os.getenv("DIRECTUS_TOKEN", "")
        self.directus_headers = {
            "Authorization": f"Bearer {self.directus_token}",
            "Content-Type": "application/json",
        }
        self.request_timeout = 30

        # Instanciar agrupador para usar suas funções
        self.agrupador = AgrupadorModificacoes(
            self.directus_base_url, self.directus_token, self.request_timeout
        )

    def buscar_versoes_draft_com_modificacoes(self) -> list[dict]:
        """
        Busca versões com status 'draft' que possuem modificações
        """
        try:
            print(
                f"🔍 {datetime.now().strftime('%H:%M:%S')} - Buscando versões em draft com modificações..."
            )

            # Buscar versões em draft
            url = f"{self.directus_base_url}/items/versao"
            params = {
                "filter[status][_eq]": "draft",
                "fields": "id,versao,status",  # Removido contrato.nome que pode causar erro de permissão
                "limit": 100,
            }

            print(f"🔗 URL: {url}")
            print(f"📋 Params: {params}")

            response = requests.get(
                url,
                headers=self.directus_headers,
                params=params,
                timeout=self.request_timeout,
            )

            print(f"📊 Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Response text: {response.text}")
                print(f"❌ Erro ao buscar versões draft: HTTP {response.status_code}")
                return []

            versoes_draft = response.json().get("data", [])

            if not versoes_draft:
                print("ℹ️ Nenhuma versão em draft encontrada")
                return []

            # Para cada versão draft, verificar se tem modificações
            versoes_com_modificacoes = []

            for versao in versoes_draft:
                versao_id = versao["id"]

                # Contar modificações da versão
                mod_url = f"{self.directus_base_url}/items/modificacao"
                mod_params = {
                    "filter[versao][_eq]": versao_id,
                    "fields": "id",
                    "limit": 1,
                    "meta": "filter_count",
                }

                mod_response = requests.get(
                    mod_url,
                    headers=self.directus_headers,
                    params=mod_params,
                    timeout=self.request_timeout,
                )

                if mod_response.status_code == 200:
                    mod_data = mod_response.json()
                    total_modificacoes = mod_data.get("meta", {}).get("filter_count", 0)

                    if total_modificacoes > 0:
                        versao["total_modificacoes"] = total_modificacoes
                        versoes_com_modificacoes.append(versao)

            if versoes_com_modificacoes:
                print(
                    f"🎯 {len(versoes_com_modificacoes)} versões draft precisam de limpeza"
                )

            return versoes_com_modificacoes

        except Exception as e:
            print(f"❌ Erro ao buscar versões draft: {e}")
            return []

    def processar_limpeza_versao(
        self, versao_data: dict, dry_run: bool = False
    ) -> dict:
        """
        Processa a limpeza de modificações de uma versão específica
        """
        try:
            versao_id = versao_data["id"]
            versao_num = versao_data.get("versao", "N/A")
            total_mods = versao_data.get("total_modificacoes", 0)

            print(
                f"🧹 Limpando versão {versao_num} ({versao_id[:8]}...) - {total_mods} modificações"
            )

            # Usar o agrupador para limpar modificações
            resultado = self.agrupador.limpar_modificacoes_versao(versao_id, dry_run)

            if "erro" in resultado:
                print(f"❌ Erro na limpeza: {resultado['erro']}")
                return {
                    "status": "erro",
                    "versao_id": versao_id,
                    "erro": resultado["erro"],
                }

            total_removidas = resultado.get("total_removidas", 0)
            print(
                f"✅ Versão {versao_num} limpa - {total_removidas} modificações removidas"
            )

            return {
                "status": "sucesso",
                "versao_id": versao_id,
                "versao_num": versao_num,
                "total_removidas": total_removidas,
                "detalhes": resultado,
            }

        except Exception as e:
            print(f"❌ Erro ao processar limpeza da versão: {e}")
            return {
                "status": "erro",
                "versao_id": versao_data.get("id", "N/A"),
                "erro": str(e),
            }

    def processar_ciclo_limpeza(self, dry_run: bool = False) -> dict:
        """
        Executa um ciclo completo de limpeza
        """
        try:
            print(
                f"\n🚀 Iniciando ciclo de limpeza - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            if dry_run:
                print("🏃‍♂️ Modo DRY-RUN ativo - nenhuma alteração será feita")

            # Buscar versões que precisam de limpeza
            versoes = self.buscar_versoes_draft_com_modificacoes()

            if not versoes:
                print("ℹ️ Nenhuma versão draft com modificações encontrada")
                return {"info": "Nenhuma versão para limpar", "total_processadas": 0}

            # Processar cada versão
            estatisticas = {
                "total_versoes": len(versoes),
                "sucessos": 0,
                "erros": 0,
                "total_modificacoes_removidas": 0,
                "detalhes": [],
            }

            for versao in versoes:
                resultado = self.processar_limpeza_versao(versao, dry_run)

                estatisticas["detalhes"].append(resultado)

                if resultado["status"] == "sucesso":
                    estatisticas["sucessos"] += 1
                    estatisticas["total_modificacoes_removidas"] += resultado.get(
                        "total_removidas", 0
                    )
                else:
                    estatisticas["erros"] += 1

                # Pequena pausa entre processamentos
                time.sleep(0.5)

            # Resumo final conciso
            if estatisticas["total_versoes"] > 0:
                print(
                    f"📊 Limpeza: {estatisticas['sucessos']}/{estatisticas['total_versoes']} versões, {estatisticas['total_modificacoes_removidas']} modificações removidas"
                )

            return estatisticas

        except Exception as e:
            print(f"❌ Erro no ciclo de limpeza: {e}")
            return {"erro": str(e)}

    def executar_monitoramento(self, intervalo: int = 300, dry_run: bool = False):
        """
        Executa monitoramento contínuo de limpeza

        Args:
            intervalo: Intervalo em segundos entre verificações (padrão: 5 minutos)
            dry_run: Modo de simulação
        """
        print("🎯 Iniciando monitoramento de limpeza")
        print(f"   ⏰ Intervalo: {intervalo} segundos ({intervalo // 60} minutos)")
        print(f"   🏃‍♂️ Modo DRY-RUN: {'Ativo' if dry_run else 'Inativo'}")

        try:
            while True:
                try:
                    resultado = self.processar_ciclo_limpeza(dry_run)

                    if "erro" not in resultado:
                        print(
                            f"✅ Ciclo concluído - próximo em {intervalo // 60} minutos"
                        )
                    else:
                        print(f"❌ Erro no ciclo: {resultado['erro']}")

                except Exception as e:
                    print(f"❌ Erro inesperado no ciclo: {e}")

                # Aguardar próximo ciclo
                time.sleep(intervalo)

        except KeyboardInterrupt:
            print("\n⏹️ Monitoramento interrompido pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro crítico no monitoramento: {e}")


def main():
    """Função principal para execução standalone"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Processador de limpeza de modificações"
    )
    parser.add_argument(
        "--single-run", action="store_true", help="Executar apenas um ciclo"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Modo simulação (não faz alterações)"
    )
    parser.add_argument(
        "--intervalo",
        type=int,
        default=300,
        help="Intervalo entre verificações em segundos",
    )

    args = parser.parse_args()

    processador = ProcessadorLimpeza()

    if args.single_run:
        print("🎯 Executando ciclo único de limpeza")
        resultado = processador.processar_ciclo_limpeza(args.dry_run)
        if "erro" in resultado:
            print(f"❌ Erro: {resultado['erro']}")
            exit(1)
    else:
        print("🎯 Iniciando monitoramento contínuo")
        processador.executar_monitoramento(args.intervalo, args.dry_run)


if __name__ == "__main__":
    main()
