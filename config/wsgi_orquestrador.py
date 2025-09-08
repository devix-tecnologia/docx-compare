#!/usr/bin/env python3
"""
Aplicação Flask para o Orquestrador de Processadores
Configurada para execução com Gunicorn em produção
"""

import os
import signal
import sys
import threading

# Adicionar o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.docx_compare.processors.orquestrador import ProcessorOrchestrator, app

# Instância global do orquestrador
orquestrador_instance = None
orquestrador_thread = None


def init_orquestrador():
    """Inicializa o orquestrador em background"""
    global orquestrador_instance, orquestrador_thread

    if orquestrador_instance is None:
        # Configurações do ambiente
        modo_execucao = os.getenv("ORQUESTRADOR_MODO", "sequencial")
        intervalo_verificacao = int(os.getenv("ORQUESTRADOR_INTERVALO", "60"))
        porta_monitoramento = int(os.getenv("ORQUESTRADOR_PORTA", "5007"))
        verbose = os.getenv("ORQUESTRADOR_VERBOSE", "false").lower() == "true"

        print("🎯 Inicializando orquestrador:")
        print(f"   Modo: {modo_execucao}")
        print(f"   Intervalo: {intervalo_verificacao}s")
        print(f"   Porta: {porta_monitoramento}")
        print(f"   Verbose: {verbose}")

        # Criar instância do orquestrador
        orquestrador_instance = ProcessorOrchestrator(
            modo_execucao=modo_execucao,
            intervalo_verificacao=intervalo_verificacao,
            porta_monitoramento=porta_monitoramento,
            verbose=verbose,
        )

        # Iniciar em thread separada para modo contínuo
        if os.getenv("ORQUESTRADOR_SINGLE_RUN", "false").lower() != "true":
            orquestrador_thread = threading.Thread(
                target=orquestrador_instance.iniciar,
                daemon=True,
                name="OrquestradorThread",
            )
            orquestrador_thread.start()
            print("🚀 Orquestrador iniciado em background")
        else:
            # Modo single-run para desenvolvimento/testes
            print("🎯 Modo single-run: executando apenas um ciclo")
            orquestrador_instance._ciclo_processamento()
            print("✅ Ciclo único completado")


def handle_signal(signum, _frame):
    """Handler para sinais de encerramento"""
    global orquestrador_instance
    print(f"\n🛑 Recebido sinal {signum}, encerrando orquestrador...")

    if orquestrador_instance:
        orquestrador_instance.running = False
        print("✅ Orquestrador parado graciosamente")

    sys.exit(0)


# Configurar handlers de sinal
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)
if hasattr(signal, "SIGHUP"):
    signal.signal(signal.SIGHUP, handle_signal)


# Inicializar quando em produção
if os.getenv("FLASK_ENV") == "production":
    init_orquestrador()

if __name__ == "__main__":
    # Modo desenvolvimento
    init_orquestrador()
    app.run(
        host="0.0.0.0", port=int(os.getenv("ORQUESTRADOR_PORTA", "5007")), debug=False
    )
else:
    # Modo produção - será servido pelo Gunicorn
    init_orquestrador()
