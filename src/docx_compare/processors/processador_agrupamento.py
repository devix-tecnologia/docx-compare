#!/usr/bin/env python3
"""
Processador de Agrupamento de Modificações
Agrupa modificações de versões por capítulos baseado na correspondência de conteúdo
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.docx_compare.utils.agrupador_modificacoes_v2 import AgrupadorModificacoes

# Carregar configurações do environment
load_dotenv()

DIRECTUS_BASE_URL = os.getenv("DIRECTUS_BASE_URL", "https://admin.devix.ai")
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN", "token_aqui")

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProcessadorAgrupamento:
    """Processador que agrupa modificações de versões por capítulos"""

    def __init__(
        self,
        threshold: float = 0.6,
        intervalo_verificacao: int = 300,
        verbose: bool = False,
    ):
        self.threshold = threshold
        self.intervalo_verificacao = intervalo_verificacao
        self.verbose = verbose
        self.running = True
        self.agrupador = AgrupadorModificacoes(
            directus_base_url=DIRECTUS_BASE_URL, directus_token=DIRECTUS_TOKEN
        )

    def buscar_versoes_para_agrupar(self) -> list:
        """
        Busca versões que têm modificações sem cláusula associada
        """
        try:
            if self.verbose:
                print("🔍 Buscando versões com modificações para agrupar...")

            # Buscar modificações que não têm cláusula associada
            url = f"{DIRECTUS_BASE_URL}/items/modificacao"
            params = {
                "filter[clausula][_null]": "true",
                "fields": "versao.id,versao.status",
                "limit": 1000,
            }

            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {DIRECTUS_TOKEN}"},
                params=params,
                timeout=30,
            )

            if response.status_code == 200:
                modificacoes = response.json().get("data", [])
                versoes_ids = []

                for mod in modificacoes:
                    versao = mod.get("versao")
                    if versao and isinstance(versao, dict):
                        versao_id = versao.get("id")
                        status = versao.get("status", "")

                        # Processar versões com status 'concluido' ou 'erro' (que podem ter modificações válidas)
                        if (
                            versao_id
                            and status in ["concluido", "erro"]
                            and versao_id not in versoes_ids
                        ):
                            versoes_ids.append(versao_id)

                if self.verbose:
                    print(
                        f"✅ Encontradas {len(versoes_ids)} versões para agrupar: {versoes_ids}"
                    )

                return versoes_ids
            else:
                logger.error(f"Erro ao buscar versões: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Erro ao buscar versões para agrupar: {e}")
            return []

    def processar_versao(self, versao_id: str) -> bool:
        """
        Processa uma versão específica agrupando suas modificações
        """
        try:
            if self.verbose:
                print(f"\n🎯 Processando agrupamento da versão: {versao_id}")
                print("-" * 50)

            resultado = self.agrupador.processar_agrupamento_versao(
                versao_id=versao_id, threshold=self.threshold, dry_run=False
            )

            if "erro" in resultado:
                logger.error(
                    f"Erro no processamento da versão {versao_id}: {resultado['erro']}"
                )
                return False

            # Log de estatísticas
            total = resultado.get("total_modificacoes", 0)
            associadas = resultado.get("associacoes_criadas", 0)
            falharam = resultado.get("associacoes_falharam", 0)
            sem_correspondencia = resultado.get("modificacoes_sem_correspondencia", 0)

            if self.verbose:
                print(f"📊 Versão {versao_id} processada:")
                print(f"   📝 Total: {total}")
                print(f"   ✅ Associadas: {associadas}")
                print(f"   ❌ Falharam: {falharam}")
                print(f"   🔍 Sem correspondência: {sem_correspondencia}")

            logger.info(
                f"Versão {versao_id}: {associadas}/{total} modificações agrupadas"
            )

            return True

        except Exception as e:
            logger.error(f"Erro no processamento da versão {versao_id}: {e}")
            return False

    def executar_ciclo(self) -> bool:
        """
        Executa um ciclo completo de agrupamento
        """
        try:
            inicio = datetime.now()

            if self.verbose:
                print(f"\n🚀 Iniciando ciclo de agrupamento - {inicio}")
                print("=" * 60)

            # Buscar versões para processar
            versoes = self.buscar_versoes_para_agrupar()

            if not versoes:
                if self.verbose:
                    print("ℹ️ Nenhuma versão encontrada para agrupar")
                return True

            # Processar cada versão
            sucessos = 0
            erros = 0

            for versao_id in versoes:
                try:
                    if self.processar_versao(versao_id):
                        sucessos += 1
                    else:
                        erros += 1

                    # Pequena pausa entre processamentos para não sobrecarregar
                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Erro no processamento da versão {versao_id}: {e}")
                    erros += 1

            # Resumo do ciclo
            fim = datetime.now()
            duracao = (fim - inicio).total_seconds()

            logger.info(
                f"Ciclo concluído: {sucessos} sucessos, {erros} erros em {duracao:.1f}s"
            )

            if self.verbose:
                print("\n📊 Resumo do ciclo:")
                print(f"   ⏱️ Duração: {duracao:.1f} segundos")
                print(f"   ✅ Sucessos: {sucessos}")
                print(f"   ❌ Erros: {erros}")
                print(f"   📋 Total processado: {len(versoes)} versões")

            return erros == 0

        except Exception as e:
            logger.error(f"Erro no ciclo de agrupamento: {e}")
            return False

    def executar_loop(self):
        """
        Executa o loop principal de monitoramento e processamento
        """
        logger.info("🎯 Iniciando processador de agrupamento")
        logger.info("⚙️ Configurações:")
        logger.info(f"   🎚️ Threshold: {self.threshold}")
        logger.info(f"   ⏰ Intervalo: {self.intervalo_verificacao}s")
        logger.info(f"   🔊 Verbose: {self.verbose}")

        while self.running:
            try:
                sucesso = self.executar_ciclo()

                if not sucesso:
                    logger.warning("Ciclo executado com erros")

                # Aguardar próximo ciclo
                if self.running:
                    if self.verbose:
                        print(
                            f"\n💤 Aguardando {self.intervalo_verificacao} segundos para próximo ciclo..."
                        )

                    for _ in range(self.intervalo_verificacao):
                        if not self.running:
                            break
                        time.sleep(1)

            except KeyboardInterrupt:
                logger.info("Interrupção solicitada pelo usuário")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                if self.running:
                    time.sleep(60)  # Pausa em caso de erro

        logger.info("🛑 Processador de agrupamento encerrado")

    def executar_single_run(self):
        """
        Executa apenas um ciclo de processamento (para integração com orquestrador)
        """
        logger.info("🎯 Executando ciclo único de agrupamento")
        sucesso = self.executar_ciclo()

        if sucesso:
            logger.info("✅ Ciclo de agrupamento concluído com sucesso")
        else:
            logger.error("❌ Ciclo de agrupamento concluído com erros")

        return sucesso

    def parar(self):
        """Para o processador"""
        self.running = False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Processador de Agrupamento de Modificações"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="Threshold de similaridade (0.0-1.0, padrão: 0.6)",
    )
    parser.add_argument(
        "--intervalo",
        type=int,
        default=300,
        help="Intervalo entre verificações em segundos (padrão: 300)",
    )
    parser.add_argument(
        "--single-run", action="store_true", help="Executa apenas um ciclo e encerra"
    )
    parser.add_argument("--verbose", action="store_true", help="Ativar modo verbose")

    args = parser.parse_args()

    # Criar processador
    processador = ProcessadorAgrupamento(
        threshold=args.threshold,
        intervalo_verificacao=args.intervalo,
        verbose=args.verbose,
    )

    try:
        if args.single_run:
            # Executar apenas um ciclo
            sucesso = processador.executar_single_run()
            sys.exit(0 if sucesso else 1)
        else:
            # Executar loop contínuo
            processador.executar_loop()

    except KeyboardInterrupt:
        logger.info("Interrupção solicitada")
        processador.parar()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro não tratado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
