#!/usr/bin/env python3
"""
Script de teste para demonstrar o orquestrador sequencial
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.docx_compare.processors.orquestrador import ProcessorOrchestrator


def main():
    """Demonstra o funcionamento do orquestrador sequencial"""
    print("🎯 Testando Orquestrador Sequencial")
    print("=" * 50)

    # Criar orquestrador em modo sequencial
    orquestrador = ProcessorOrchestrator(
        modo_execucao="sequencial", verbose=True, intervalo_verificacao=10
    )

    print("\n📊 Configuração:")
    print(f"   Modo: {orquestrador.modo_execucao}")
    print(f"   Intervalo: {orquestrador.intervalo_verificacao}s")
    print(f"   Verbose: {orquestrador.verbose}")

    print("\n🔄 Executando pipeline sequencial uma vez...")
    try:
        # Simular execução de um ciclo
        resultado = orquestrador._executar_sequencial()
        print(f"\n✅ Pipeline executado com sucesso: {resultado}")

        # Mostrar estatísticas
        print("\n📊 Estatísticas:")
        for processador, info in orquestrador.stats["status_processadores"].items():
            status = "✅" if info["sucesso"] else "❌"
            print(f"   {status} {processador}: {info['timestamp']}")

    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

    print("\n🎉 Teste concluído!")


if __name__ == "__main__":
    main()
