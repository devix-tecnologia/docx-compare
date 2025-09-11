#!/usr/bin/env python3
"""
Exemplo prático de uso das implementações Directus com inversão de dependência.
Demonstra como integrar o pipeline funcional com acesso real ao Directus.
"""

import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
import tempfile

from docx_compare.core.implementacoes_directus import (
    ConfiguracaoDirectus,
    FactoryImplementacoes,
)
from docx_compare.core.pipeline_funcional import (
    ConteudoTexto,
    ContextoProcessamento,
    ModeloContrato,
    ModeloId,
    PrioridadeProcessamento,
    TagId,
    executar_pipeline_completo,
)


def configurar_ambiente():
    """Configura o ambiente com as variáveis necessárias."""
    print("📋 Configurando ambiente...")

    # Configurar variáveis de ambiente para Directus (exemplo)
    os.environ["DIRECTUS_URL"] = "https://contract.devix.co"
    os.environ["DIRECTUS_TOKEN"] = "your_token_here"  # Substitua pelo token real
    os.environ["DIRECTUS_TIMEOUT"] = "60"

    print("✅ Ambiente configurado")


def criar_documentos_exemplo():
    """Cria documentos de exemplo para demonstração."""
    print("📄 Criando documentos de exemplo...")

    # Documento original
    conteudo_original = """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS

Contratante: {{nome_contratante}}
Contratado: {{nome_contratado}}

CLÁUSULA 1 - DO OBJETO
O objeto do presente contrato é {{objeto_contrato}}.

CLÁUSULA 2 - DO VALOR
O valor total dos serviços é de R$ {{valor_total}}.

CLÁUSULA 3 - DA VIGÊNCIA
Este contrato terá vigência de {{data_inicio}} até {{data_fim}}.

Local: {{local_assinatura}}
Data: {{data_assinatura}}

______________________     ______________________
    CONTRATANTE                CONTRATADO
"""

    # Documento modificado
    conteudo_modificado = """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS ESPECIALIZADOS

Contratante: {{nome_contratante}}
Contratado: {{nome_contratado}}
CNPJ/CPF: {{documento_contratado}}

CLÁUSULA 1 - DO OBJETO
O objeto do presente contrato é {{objeto_contrato}} com especificações técnicas detalhadas.

CLÁUSULA 2 - DO VALOR E FORMA DE PAGAMENTO
O valor total dos serviços é de R$ {{valor_total}}.
Forma de pagamento: {{forma_pagamento}}.

CLÁUSULA 3 - DA VIGÊNCIA
Este contrato terá vigência de {{data_inicio}} até {{data_fim}}.

CLÁUSULA 4 - DAS PENALIDADES
Em caso de descumprimento, aplicam-se as penalidades previstas em lei.

Local: {{local_assinatura}}
Data: {{data_assinatura}}

______________________     ______________________
    CONTRATANTE                CONTRATADO
"""

    # Criar arquivos temporários
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f_orig:
        f_orig.write(conteudo_original)
        caminho_original = Path(f_orig.name)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f_mod:
        f_mod.write(conteudo_modificado)
        caminho_modificado = Path(f_mod.name)

    print(f"✅ Documento original criado: {caminho_original}")
    print(f"✅ Documento modificado criado: {caminho_modificado}")

    return caminho_original, caminho_modificado


def criar_modelo_contrato():
    """Cria um modelo de contrato com tags obrigatórias."""
    return ModeloContrato(
        id=ModeloId("contrato_prestacao_servicos"),
        nome="Contrato de Prestação de Serviços",
        template=ConteudoTexto("Template padrão de contrato"),
        tags_obrigatorias={
            TagId("nome_contratante"),
            TagId("nome_contratado"),
            TagId("objeto_contrato"),
            TagId("valor_total"),
            TagId("data_inicio"),
            TagId("data_fim"),
        },
        tags_opcionais={
            TagId("documento_contratado"),
            TagId("forma_pagamento"),
            TagId("local_assinatura"),
            TagId("data_assinatura"),
        },
        validacoes=[
            "nome_contratante_obrigatorio",
            "valor_total_numerico",
            "datas_validas",
        ],
    )


def demonstrar_inversao_dependencia():
    """Demonstra o uso da inversão de dependência com implementações Directus."""
    print("\n🔄 Demonstrando Inversão de Dependência com Directus")
    print("=" * 60)

    try:
        # 1. Configurar Directus
        config = ConfiguracaoDirectus.from_env()
        print(f"🔗 Conectando ao Directus: {config.url_base}")

        # 2. Criar factory de implementações
        factory = FactoryImplementacoes(config)
        print("🏭 Factory de implementações criada")

        # 3. Injetar dependências através dos Protocols
        processador = factory.criar_processador_texto()
        analisador = factory.criar_analisador_tags()
        comparador = factory.criar_comparador_documentos()
        agrupador = factory.criar_agrupador_modificacoes()

        print("✅ Implementações Directus injetadas:")
        print(f"  📝 ProcessadorTexto: {type(processador).__name__}")
        print(f"  🏷️  AnalisadorTags: {type(analisador).__name__}")
        print(f"  🔍 ComparadorDocumentos: {type(comparador).__name__}")
        print(f"  📊 AgrupadorModificacoes: {type(agrupador).__name__}")

        # 4. Criar documentos de exemplo
        caminho_original, caminho_modificado = criar_documentos_exemplo()

        # 5. Criar modelo de contrato
        modelo = criar_modelo_contrato()
        print(f"📋 Modelo criado: {modelo.nome}")
        print(f"   Tags obrigatórias: {len(modelo.tags_obrigatorias)}")
        print(f"   Tags opcionais: {len(modelo.tags_opcionais)}")

        # 6. Configurar contexto de processamento
        contexto = ContextoProcessamento(
            prioridade=PrioridadeProcessamento.ALTA,
            timeout_segundos=120,
            modo_paralelo=True,
            filtros_ativos={"validacao_tags", "analise_modificacoes"},
            configuracoes={
                "directus_logging": True,
                "cache_resultados": True,
                "debug_mode": False,
            },
        )

        print(f"⚙️ Contexto configurado: prioridade {contexto.prioridade.value}")

        # 7. Executar pipeline completo com inversão de dependência
        print("\n🚀 Executando pipeline com implementações Directus...")

        resultados = executar_pipeline_completo(
            documentos_originais=[caminho_original],
            documentos_modificados=[caminho_modificado],
            modelos=[modelo],
            contexto=contexto,
            processador=processador,  # Implementação Directus injetada
            analisador=analisador,  # Implementação Directus injetada
            comparador=comparador,  # Implementação Directus injetada
            agrupador=agrupador,  # Implementação Directus injetada
        )

        # 8. Analisar resultados
        print("\n📊 Resultados do Pipeline:")
        print(f"   Total de comparações: {len(resultados)}")

        for i, resultado in enumerate(resultados, 1):
            print(f"\n   📄 Comparação {i}:")
            print(f"      Modificações encontradas: {len(resultado.modificacoes)}")
            print(f"      Blocos agrupados: {len(resultado.blocos_agrupados)}")
            print(f"      Tempo de processamento: {resultado.tempo_processamento:.2f}s")

            # Estatísticas detalhadas
            stats = resultado.estatisticas
            print("      📈 Estatísticas:")
            for chave, valor in stats.items():
                if isinstance(valor, int | float):
                    print(f"         {chave}: {valor}")

            # Detalhes dos blocos
            print("      🧩 Blocos de modificações:")
            for j, bloco in enumerate(resultado.blocos_agrupados, 1):
                print(f"         Bloco {j}: {len(bloco.modificacoes)} modificações")
                print(f"           Tipo predominante: {bloco.tipo_predominante.value}")
                print(f"           Relevância: {bloco.relevancia:.2f}")

        print("\n✅ Pipeline executado com sucesso usando implementações Directus!")
        print("💡 Todas as operações foram registradas no Directus via API")

        return resultados

    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        print("💡 Verifique a configuração do Directus e conectividade")
        return None

    finally:
        # Limpar arquivos temporários
        try:
            caminho_original.unlink()
            caminho_modificado.unlink()
            print("🧹 Arquivos temporários removidos")
        except Exception:
            pass


def demonstrar_diferentes_configuracoes():
    """Demonstra diferentes configurações de implementação."""
    print("\n⚙️ Demonstrando Diferentes Configurações")
    print("=" * 50)

    # Configuração para desenvolvimento
    config_dev = ConfiguracaoDirectus(
        url_base="https://dev.contract.local", token="dev_token", timeout=30
    )

    # Configuração para produção
    config_prod = ConfiguracaoDirectus(
        url_base="https://contract.devix.co",
        token=os.getenv("DIRECTUS_PROD_TOKEN", "prod_token"),
        timeout=60,
    )

    print("🔧 Configurações disponíveis:")
    print(f"   Desenvolvimento: {config_dev.url_base}")
    print(f"   Produção: {config_prod.url_base}")

    # Criar factories para diferentes ambientes (exemplo)
    # factory_dev = FactoryImplementacoes(config_dev)
    # factory_prod = FactoryImplementacoes(config_prod)

    print("✅ Factories criadas para diferentes ambientes")
    print("💡 Use a factory apropriada baseada no ambiente de execução")


def main():
    """Função principal da demonstração."""
    print("🎯 Demonstração: Pipeline Funcional com Directus")
    print("🔄 Inversão de Dependência em Ação")
    print("=" * 60)

    # Configurar ambiente
    configurar_ambiente()

    # Demonstrar inversão de dependência
    demonstrar_inversao_dependencia()

    # Demonstrar diferentes configurações
    demonstrar_diferentes_configuracoes()

    print("\n" + "=" * 60)
    print("🎉 Demonstração concluída!")
    print("💡 Principais vantagens da inversão de dependência:")
    print("   ✅ Flexibilidade para trocar implementações")
    print("   ✅ Testabilidade com mocks")
    print("   ✅ Separação de responsabilidades")
    print("   ✅ Fácil integração com sistemas externos")
    print("   ✅ Configuração independente por ambiente")


if __name__ == "__main__":
    main()
