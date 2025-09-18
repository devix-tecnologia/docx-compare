#!/usr/bin/env python3
"""
Exemplo de uso das implementações Real (Directus) vs Mock
Demonstra como alternar entre implementações para produção e testes.
"""

import os
import sys
import tempfile
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

from .implementacoes_directus import (
    ConfiguracaoDirectus,
)
from .implementacoes_directus import (
    FactoryImplementacoes as FactoryDirectus,
)
from .implementacoes_mock import FactoryImplementacoesMock
from .pipeline_funcional import (
    ConteudoTexto,
    ContextoProcessamento,
    ModeloContrato,
    ModeloId,
    PrioridadeProcessamento,
    TagId,
    executar_pipeline_completo,
)


def carregar_configuracao():
    """Carrega as configurações do arquivo .env"""
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)


def criar_modelo_exemplo() -> ModeloContrato:
    """Cria um modelo de contrato de exemplo."""
    return ModeloContrato(
        id=ModeloId("contrato_servicos"),
        nome="Contrato de Serviços",
        template=ConteudoTexto(
            "Contrato entre {{contratante}} e {{contratado}} no valor de {{valor}}."
        ),
        tags_obrigatorias={TagId("contratante"), TagId("contratado"), TagId("valor")},
        tags_opcionais={TagId("prazo"), TagId("local")},
        validacoes=["validacao_cpf", "validacao_valor"],
    )


def criar_arquivos_exemplo():
    """Cria arquivos de exemplo para demonstração."""
    print("📄 Criando arquivos de exemplo...")

    # Documento original
    conteudo_original = """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS

Entre {{contratante}} e {{contratado}}.
Valor total: {{valor}} reais.
Prazo: {{prazo}} dias úteis.
Local de execução: {{local}}.
"""

    # Documento modificado
    conteudo_modificado = """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS ALTERADO

Entre {{contratante}} e {{contratado}}.
Valor total: {{preco}} reais (com desconto).
Prazo: {{prazo}} dias corridos.
Local de execução: {{endereco}}.
Data de assinatura: {{data}}.
"""

    # Criar arquivos temporários
    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_original.txt", delete=False
    ) as f1:
        f1.write(conteudo_original)
        caminho_original = Path(f1.name)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_modificado.txt", delete=False
    ) as f2:
        f2.write(conteudo_modificado)
        caminho_modificado = Path(f2.name)

    print(f"✅ Arquivo original: {caminho_original.name}")
    print(f"✅ Arquivo modificado: {caminho_modificado.name}")

    return caminho_original, caminho_modificado


def demonstrar_implementacao_mock():
    """Demonstra o uso da implementação mock."""
    print("\n" + "=" * 60)
    print("🎭 DEMONSTRAÇÃO: Implementação MOCK")
    print("=" * 60)

    # Criar factory mock
    factory = FactoryImplementacoesMock()
    print("✅ Factory mock criada")

    # Criar implementações
    processador, analisador, comparador, agrupador = factory.criar_todos()
    print("✅ Implementações mock injetadas")

    # Criar arquivos e contexto
    caminho_original, caminho_modificado = criar_arquivos_exemplo()
    modelo = criar_modelo_exemplo()

    contexto = ContextoProcessamento(
        prioridade=PrioridadeProcessamento.ALTA,
        timeout_segundos=10,
        modo_paralelo=False,
        filtros_ativos=set(),
        configuracoes={"modo": "mock"},
    )

    try:
        print("🚀 Executando pipeline com implementações MOCK...")

        # Executar pipeline
        resultados = executar_pipeline_completo(
            documentos_originais=[caminho_original],
            documentos_modificados=[caminho_modificado],
            _modelos=[modelo],
            _contexto=contexto,
            processador=processador,
            analisador=analisador,
            comparador=comparador,
            agrupador=agrupador,
        )

        # Mostrar resultados
        print(f"📊 Resultados gerados: {len(resultados)}")

        for i, resultado in enumerate(resultados):
            print(f"   📋 Resultado {i + 1}:")
            print(f"      • Modificações: {len(resultado.modificacoes)}")
            print(f"      • Blocos: {len(resultado.blocos_agrupados)}")
            print(f"      • Tempo: {resultado.tempo_processamento:.3f}s")

        print("✅ Pipeline MOCK executado com sucesso!")
        print("⚡ Execução rápida e independente")

    except Exception as e:
        print(f"❌ Erro no pipeline mock: {e}")

    finally:
        # Limpar arquivos
        caminho_original.unlink()
        caminho_modificado.unlink()


def demonstrar_implementacao_directus():
    """Demonstra o uso da implementação real do Directus."""
    print("\n" + "=" * 60)
    print("🏢 DEMONSTRAÇÃO: Implementação DIRECTUS (Real)")
    print("=" * 60)

    try:
        # Criar factory Directus
        config = ConfiguracaoDirectus.from_env()
        factory = FactoryDirectus(config)
        print(f"✅ Factory Directus criada (URL: {config.url_base})")

        # Criar implementações
        processador, analisador, comparador, agrupador = factory.criar_todos()
        print("✅ Implementações Directus injetadas")

        # Criar arquivos e contexto
        caminho_original, caminho_modificado = criar_arquivos_exemplo()
        modelo = criar_modelo_exemplo()

        contexto = ContextoProcessamento(
            prioridade=PrioridadeProcessamento.CRITICA,
            timeout_segundos=60,
            modo_paralelo=True,
            filtros_ativos=set(),
            configuracoes={"modo": "producao"},
        )

        try:
            print("🚀 Executando pipeline com implementações DIRECTUS...")

            # Executar pipeline
            resultados = executar_pipeline_completo(
                documentos_originais=[caminho_original],
                documentos_modificados=[caminho_modificado],
                _modelos=[modelo],
                _contexto=contexto,
                processador=processador,
                analisador=analisador,
                comparador=comparador,
                agrupador=agrupador,
            )

            # Mostrar resultados
            print(f"📊 Resultados gerados: {len(resultados)}")

            for i, resultado in enumerate(resultados):
                print(f"   📋 Resultado {i + 1}:")
                print(f"      • Modificações: {len(resultado.modificacoes)}")
                print(f"      • Blocos: {len(resultado.blocos_agrupados)}")
                print(f"      • Tempo: {resultado.tempo_processamento:.3f}s")

            print("✅ Pipeline DIRECTUS executado com sucesso!")
            print("🌐 Dados reais integrados com Directus")

        except Exception as e:
            print(f"❌ Erro no pipeline Directus: {e}")
            print("⚠️ Isso é esperado se o Directus não estiver acessível")

        finally:
            # Limpar arquivos
            caminho_original.unlink()
            caminho_modificado.unlink()

    except Exception as e:
        print(f"❌ Erro na configuração Directus: {e}")
        print("⚠️ Verifique as variáveis de ambiente DIRECTUS_*")


def demonstrar_escolha_dinamica():
    """Demonstra escolha dinâmica entre implementações baseada em ambiente."""
    print("\n" + "=" * 60)
    print("🔄 DEMONSTRAÇÃO: Escolha Dinâmica de Implementação")
    print("=" * 60)

    # Simular diferentes ambientes
    ambientes = [
        ("development", "mock"),
        ("testing", "mock"),
        ("staging", "directus"),
        ("production", "directus"),
    ]

    for ambiente, tipo_implementacao in ambientes:
        print(f"\n🌍 Ambiente: {ambiente.upper()}")

        if tipo_implementacao == "mock":
            factory = FactoryImplementacoesMock()
            print("   ✅ Usando implementações MOCK (rápido, local)")
        else:
            try:
                config = ConfiguracaoDirectus.from_env()
                factory = FactoryDirectus(config)
                print("   ✅ Usando implementações DIRECTUS (real, externo)")
            except Exception:
                print("   ⚠️ Directus não disponível, fallback para MOCK")
                factory = FactoryImplementacoesMock()

        # Criar implementações
        implementacoes = factory.criar_todos()
        print(f"   📦 {len(implementacoes)} implementações criadas")


def main():
    """Executa todas as demonstrações."""
    print("🚀 Demonstração: Implementações Real vs Mock")
    print("Pipeline Funcional com Inversão de Dependência")

    # Verificar configuração
    directus_url = os.getenv("DIRECTUS_BASE_URL")
    directus_token = os.getenv("DIRECTUS_TOKEN")

    print("\n📋 Configuração atual:")
    print(f"   • Directus URL: {directus_url or 'NÃO CONFIGURADO'}")
    print(
        f"   • Directus Token: {'CONFIGURADO' if directus_token else 'NÃO CONFIGURADO'}"
    )

    try:
        # Demonstrar implementação mock (sempre funciona)
        demonstrar_implementacao_mock()

        # Demonstrar implementação Directus (pode falhar)
        demonstrar_implementacao_directus()

        # Demonstrar escolha dinâmica
        demonstrar_escolha_dinamica()

        print("\n" + "=" * 60)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print("✅ Implementações Mock: Rápidas, locais, para desenvolvimento/testes")
        print("✅ Implementações Directus: Reais, externas, para produção")
        print("🔄 Inversão de Dependência: Troca transparente entre implementações")
        print("🎯 Resultado: Máxima flexibilidade e testabilidade")

    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    carregar_configuracao()
    main()
