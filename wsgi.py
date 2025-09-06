#!/usr/bin/env python3
"""
Aplicação Flask para o Processador Automático de Versões
Separada para permitir execução com Gunicorn em produção
"""

import os
import threading

from processador_automatico import app, loop_processador, processador_thread


# Função para inicializar o processador em background
def init_processador():
    """Inicializa o processador automático em background"""
    global processador_thread

    # Verificar se já existe uma thread ativa
    if processador_thread is None or not processador_thread.is_alive():
        dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        processador_thread = threading.Thread(
            target=lambda: loop_processador(dry_run), daemon=True
        )
        processador_thread.start()
        print("🔄 Processador automático iniciado em background")


# Inicializar processador quando em produção
if os.getenv("FLASK_ENV") == "production":
    init_processador()

if __name__ == "__main__":
    # Modo desenvolvimento
    app.run(host="0.0.0.0", port=5005, debug=False)
else:
    # Modo produção - será servido pelo Gunicorn
    init_processador()
