#!/usr/bin/env python3
"""
Orquestrador de Processadores
Executa os processadores automático e de modelo de contrato em paralelo ou sequencial
"""

import argparse
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)


class ProcessorOrchestrator:
    """Orquestrador que gerencia múltiplos processadores"""

    def __init__(
        self,
        modo_execucao: str = "paralelo",
        intervalo_verificacao: int = 60,
        porta_monitoramento: int = 5007,
        verbose: bool = False,
        dry_run: bool = False,
    ):
        self.modo_execucao = modo_execucao  # "paralelo" ou "sequencial"
        self.intervalo_verificacao = intervalo_verificacao
        self.porta_monitoramento = porta_monitoramento
        self.verbose = verbose
        self.dry_run = dry_run
        self.running = True
        self.processes: dict[str, subprocess.Popen] = {}
        self.threads: list[threading.Thread] = []
        self.stats = {
            "inicio": datetime.now(),
            "ciclos_executados": 0,
            "ultimo_ciclo": None,
            "processadores_ativos": [],
            "status_processadores": {},
        }

        # Configurar handlers de sinal para encerramento gracioso
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print("🎯 Orquestrador de Processadores")
        print(f"📊 Modo de execução: {modo_execucao}")
        print(f"📁 Porta de monitoramento: {porta_monitoramento}")
        print(f"⏰ Intervalo de verificação: {intervalo_verificacao} segundos")
        print(f"🏃‍♂️ Modo: {'VERBOSE' if verbose else 'NORMAL'}")
        if dry_run:
            print("🔍 Modo DRY-RUN: Simulação sem execução real")

    def _signal_handler(self, signum, frame):
        """Handler para sinais de encerramento"""
        print(f"\n🛑 Recebido sinal {signum} - Iniciando encerramento gracioso...")
        self.running = False

    def _executar_processador_automatico(self) -> tuple[bool, str]:
        """Executa o processador automático uma vez"""
        try:
            cmd = [
                sys.executable,
                "src/docx_compare/processors/processador_automatico.py",
                "--single-run",
            ]
            if self.verbose:
                cmd.append("--verbose")
            if self.dry_run:
                cmd.append("--dry-run")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos de timeout
                cwd=os.getcwd(),
            )

            if result.returncode == 0:
                if self.verbose:
                    print("✅ Processador automático executado com sucesso")
                    print(f"📤 Stdout: {result.stdout}")
                return True, result.stdout
            else:
                print(f"❌ Erro no processador automático: {result.stderr}")
                return False, result.stderr

        except subprocess.TimeoutExpired:
            print("⏰ Timeout no processador automático")
            return False, "Timeout na execução"
        except Exception as e:
            print(f"❌ Exceção no processador automático: {e}")
            return False, str(e)

    def _executar_processador_modelo_contrato(self) -> tuple[bool, str]:
        """Executa o processador de modelo de contrato uma vez"""
        try:
            cmd = [
                sys.executable,
                "src/docx_compare/processors/processador_modelo_contrato.py",
                "--single-run",
            ]
            if self.verbose:
                cmd.append("--verbose")
            if self.dry_run:
                cmd.append("--dry-run")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos de timeout
                cwd=os.getcwd(),
            )

            if result.returncode == 0:
                if self.verbose:
                    print("✅ Processador de modelo de contrato executado com sucesso")
                    print(f"📤 Stdout: {result.stdout}")
                return True, result.stdout
            else:
                print(f"❌ Erro no processador de modelo de contrato: {result.stderr}")
                return False, result.stderr

        except subprocess.TimeoutExpired:
            print("⏰ Timeout no processador de modelo de contrato")
            return False, "Timeout na execução"
        except Exception as e:
            print(f"❌ Exceção no processador de modelo de contrato: {e}")
            return False, str(e)

    def _executar_paralelo(self):
        """Executa ambos os processadores em paralelo"""
        threads = []

        def run_automatico():
            success, output = self._executar_processador_automatico()
            self.stats["status_processadores"]["automatico"] = {
                "sucesso": success,
                "output": output,
                "timestamp": datetime.now(),
            }

        def run_modelo_contrato():
            success, output = self._executar_processador_modelo_contrato()
            self.stats["status_processadores"]["modelo_contrato"] = {
                "sucesso": success,
                "output": output,
                "timestamp": datetime.now(),
            }

        # Criar e iniciar threads
        thread_automatico = threading.Thread(
            target=run_automatico, name="ProcessadorAutomatico"
        )
        thread_modelo = threading.Thread(
            target=run_modelo_contrato, name="ProcessadorModelo"
        )

        threads.extend([thread_automatico, thread_modelo])

        for thread in threads:
            thread.start()

        # Aguardar conclusão de todas as threads
        for thread in threads:
            thread.join()

        # Verificar resultados
        automatico_ok = (
            self.stats["status_processadores"]
            .get("automatico", {})
            .get("sucesso", False)
        )
        modelo_ok = (
            self.stats["status_processadores"]
            .get("modelo_contrato", {})
            .get("sucesso", False)
        )

        print("📊 Resultados paralelos:")
        print(f"   🔄 Processador automático: {'✅' if automatico_ok else '❌'}")
        print(f"   🏷️  Processador modelo: {'✅' if modelo_ok else '❌'}")

    def _executar_sequencial(self):
        """Executa os processadores sequencialmente"""
        print("🏷️ Executando processador de modelo de contrato...")
        modelo_success, modelo_output = self._executar_processador_modelo_contrato()
        self.stats["status_processadores"]["modelo_contrato"] = {
            "sucesso": modelo_success,
            "output": modelo_output,
            "timestamp": datetime.now(),
        }

        print("🔄 Executando processador automático...")
        automatico_success, automatico_output = self._executar_processador_automatico()
        self.stats["status_processadores"]["automatico"] = {
            "sucesso": automatico_success,
            "output": automatico_output,
            "timestamp": datetime.now(),
        }

        print("📊 Resultados sequenciais:")
        print(f"   🏷️  Processador modelo: {'✅' if modelo_success else '❌'}")
        print(f"   🔄 Processador automático: {'✅' if automatico_success else '❌'}")

    def _ciclo_processamento(self):
        """Executa um ciclo completo de processamento"""
        inicio_ciclo = datetime.now()
        print(
            f"\n🚀 Iniciando ciclo de processamento - {inicio_ciclo.strftime('%H:%M:%S')}"
        )

        if self.modo_execucao == "paralelo":
            self._executar_paralelo()
        else:
            self._executar_sequencial()

        self.stats["ciclos_executados"] += 1
        self.stats["ultimo_ciclo"] = datetime.now()

        duracao = (self.stats["ultimo_ciclo"] - inicio_ciclo).total_seconds()
        print(f"⏱️  Ciclo completado em {duracao:.2f} segundos")

    def _loop_processamento(self):
        """Loop principal do orquestrador"""
        print("\n🔄 Loop do orquestrador iniciado!")

        while self.running:
            try:
                self._ciclo_processamento()

                if self.running:
                    print(f"😴 Aguardando {self.intervalo_verificacao} segundos...")
                    for _ in range(self.intervalo_verificacao):
                        if not self.running:
                            break
                        time.sleep(1)

            except Exception as e:
                print(f"❌ Erro no ciclo de processamento: {e}")
                if self.running:
                    print(
                        f"😴 Aguardando {self.intervalo_verificacao} segundos antes de tentar novamente..."
                    )
                    time.sleep(self.intervalo_verificacao)

        print("🔄 Loop do orquestrador finalizado")

    def iniciar(self):
        """Inicia o orquestrador"""
        print("\n📋 Endpoints de monitoramento:")
        print("  • GET  /health - Verificação de saúde")
        print("  • GET  /status - Status do orquestrador")
        print("  • GET  /metrics - Métricas detalhadas")
        print("  • GET  /logs - Logs dos processadores")

        # Iniciar thread do processamento
        processing_thread = threading.Thread(
            target=self._loop_processamento, name="OrquestradorLoop"
        )
        processing_thread.daemon = True
        processing_thread.start()
        self.threads.append(processing_thread)

        # Iniciar servidor Flask para monitoramento (em thread separada)
        flask_thread = threading.Thread(
            target=self._iniciar_flask_server, name="FlaskServer"
        )
        flask_thread.daemon = True
        flask_thread.start()
        self.threads.append(flask_thread)

        # Loop principal para capturar sinais
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Recebido SIGINT (Ctrl+C) - Iniciando encerramento gracioso...")
        finally:
            self._encerrar()

    def _iniciar_flask_server(self):
        """Inicia o servidor Flask em thread separada"""
        try:
            app.run(
                host="127.0.0.1",
                port=self.porta_monitoramento,
                debug=False,
                use_reloader=False,
                threaded=True,
            )
        except Exception as e:
            if self.running:  # Só reportar erro se não estiver encerrando
                print(f"❌ Erro no servidor Flask: {e}")

    def _encerrar(self):
        """Encerra o orquestrador graciosamente"""
        print("⏳ Aguardando threads terminarem...")
        self.running = False

        # Aguardar threads terminarem
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=3)  # Timeout reduzido

        # Terminar processos ativos
        for nome, processo in self.processes.items():
            if processo.poll() is None:
                print(f"🛑 Terminando processo {nome}...")
                processo.terminate()
                try:
                    processo.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    print(f"💀 Forçando término do processo {nome}...")
                    processo.kill()

        print("🔄 Loop do orquestrador finalizado")
        # Forçar saída se necessário
        import os

        os._exit(0)


# Instância global do orquestrador para os endpoints Flask
orquestrador_instance: ProcessorOrchestrator | None = None


@app.route("/health")
def health():
    """Endpoint de verificação de saúde"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/status")
def status():
    """Endpoint de status do orquestrador"""
    if not orquestrador_instance:
        return jsonify({"error": "Orquestrador não inicializado"}), 500

    return jsonify(
        {
            "status": "running" if orquestrador_instance.running else "stopped",
            "modo_execucao": orquestrador_instance.modo_execucao,
            "intervalo_verificacao": orquestrador_instance.intervalo_verificacao,
            "ciclos_executados": orquestrador_instance.stats["ciclos_executados"],
            "ultimo_ciclo": orquestrador_instance.stats["ultimo_ciclo"].isoformat()
            if orquestrador_instance.stats["ultimo_ciclo"]
            else None,
            "processadores_ativos": orquestrador_instance.stats["processadores_ativos"],
            "uptime_segundos": (
                datetime.now() - orquestrador_instance.stats["inicio"]
            ).total_seconds(),
        }
    )


@app.route("/metrics")
def metrics():
    """Endpoint de métricas detalhadas"""
    if not orquestrador_instance:
        return jsonify({"error": "Orquestrador não inicializado"}), 500

    return jsonify(orquestrador_instance.stats)


@app.route("/logs")
def logs():
    """Endpoint de logs dos processadores"""
    if not orquestrador_instance:
        return jsonify({"error": "Orquestrador não inicializado"}), 500

    return jsonify(
        {
            "status_processadores": orquestrador_instance.stats["status_processadores"],
            "timestamp": datetime.now().isoformat(),
        }
    )


def main():
    """Função principal"""
    global orquestrador_instance

    parser = argparse.ArgumentParser(description="Orquestrador de Processadores")
    parser.add_argument(
        "--modo",
        choices=["paralelo", "sequencial"],
        default="paralelo",
        help="Modo de execução dos processadores",
    )
    parser.add_argument(
        "--intervalo",
        type=int,
        default=60,
        help="Intervalo entre ciclos de processamento (segundos)",
    )
    parser.add_argument(
        "--porta",
        type=int,
        default=5007,
        help="Porta do servidor de monitoramento",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verbose com logs detalhados",
    )
    parser.add_argument(
        "--single-run",
        action="store_true",
        help="Executa apenas um ciclo e encerra",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Modo simulação - não executa processadores reais",
    )

    args = parser.parse_args()

    # Criar e configurar orquestrador
    orquestrador_instance = ProcessorOrchestrator(
        modo_execucao=args.modo,
        intervalo_verificacao=args.intervalo,
        porta_monitoramento=args.porta,
        verbose=args.verbose,
        dry_run=args.dry_run,
    )

    if args.single_run:
        print("🎯 Modo single-run: executando apenas um ciclo")
        orquestrador_instance._ciclo_processamento()
        print("✅ Ciclo único completado")
        sys.exit(0)  # Encerrar completamente
    else:
        orquestrador_instance.iniciar()


if __name__ == "__main__":
    main()
