#!/usr/bin/env python3
"""
Teste das implementações do Pipeline Funcional
Demonstra as funções implementadas funcionando com dados reais.
"""

from pathlib import Path

from src.docx_compare.core.pipeline_funcional import (
    ConteudoTexto,
    ContextoProcessamento,
    ModeloContrato,
    ModeloId,
    Modificacao,
    PosicaoTexto,
    PrioridadeProcessamento,
    StatusProcessamento,
    TagId,
    TipoModificacao,
    aplicar_paralelo,
    calcular_estatisticas,
    compor_pipeline,
    executar_em_lote,
    filtrar_por_tipo,
    pipeline_sequencial,
    processar_modelos_pendentes,
)


def criar_modificacao_mock(
    tipo: TipoModificacao, conteudo: str, confianca: float
) -> Modificacao:
    """Cria uma modificação mock para teste."""
    return Modificacao(
        id=f"mod_{tipo.value}_{hash(conteudo)}",
        tipo=tipo,
        posicao_original=PosicaoTexto(linha=1, coluna=1, offset=0),
        posicao_nova=PosicaoTexto(linha=1, coluna=10, offset=10),
        conteudo_original=ConteudoTexto(conteudo),
        conteudo_novo=ConteudoTexto(f"novo_{conteudo}"),
        confianca=confianca,
        tags_relacionadas=set(),
    )


def teste_calcular_estatisticas():
    """Testa a função calcular_estatisticas com dados reais."""
    print("🧮 Testando calcular_estatisticas...")

    # Criar modificações de teste
    modificacoes = [
        criar_modificacao_mock(TipoModificacao.INSERCAO, "texto1", 0.9),
        criar_modificacao_mock(TipoModificacao.INSERCAO, "texto2", 0.8),
        criar_modificacao_mock(TipoModificacao.ALTERACAO, "texto3", 0.7),
        criar_modificacao_mock(TipoModificacao.REMOCAO, "texto4", 0.85),
    ]

    # Calcular estatísticas
    stats = calcular_estatisticas(modificacoes)

    print(f"  📊 Total de modificações: {stats['total']}")
    print(f"  📈 Tipos encontrados: {stats['tipos']}")
    print(f"  🎯 Confiança média: {stats['confianca_media']:.2f}")
    print(f"  ✅ Status: {stats['status']}")

    assert stats["total"] == 4
    assert stats["tipos"]["insercao"] == 2
    assert stats["tipos"]["alteracao"] == 1
    assert stats["tipos"]["remocao"] == 1
    assert 0.8 <= stats["confianca_media"] <= 0.85

    print("  ✅ Teste passou!")


def teste_filtrar_por_tipo():
    """Testa a função filtrar_por_tipo."""
    print("\n🔍 Testando filtrar_por_tipo...")

    # Criar modificações de teste
    modificacoes = [
        criar_modificacao_mock(TipoModificacao.INSERCAO, "insert1", 0.9),
        criar_modificacao_mock(TipoModificacao.ALTERACAO, "alter1", 0.8),
        criar_modificacao_mock(TipoModificacao.INSERCAO, "insert2", 0.7),
        criar_modificacao_mock(TipoModificacao.REMOCAO, "remove1", 0.85),
    ]

    # Filtrar apenas inserções e alterações
    tipos_permitidos = {TipoModificacao.INSERCAO, TipoModificacao.ALTERACAO}
    filtradas = filtrar_por_tipo(modificacoes, tipos_permitidos)

    print(f"  📝 Modificações originais: {len(modificacoes)}")
    print(f"  🎯 Tipos permitidos: {[t.value for t in tipos_permitidos]}")
    print(f"  ✂️ Modificações filtradas: {len(filtradas)}")

    assert len(filtradas) == 3  # 2 inserções + 1 alteração
    assert all(mod.tipo in tipos_permitidos for mod in filtradas)

    print("  ✅ Teste passou!")


def teste_executar_em_lote():
    """Testa a função executar_em_lote."""
    print("\n📦 Testando executar_em_lote...")

    def processar_numero(n: int) -> str:
        return f"processado_{n}"

    # Lista de números para processar
    numeros = list(range(1, 11))  # 1 a 10

    # Processar em lotes de 3
    resultados = executar_em_lote(numeros, processar_numero, tamanho_lote=3)

    print(f"  📥 Itens originais: {numeros}")
    print(f"  📤 Resultados processados: {len(resultados)}")
    print(f"  🎯 Primeiros 5 resultados: {resultados[:5]}")

    assert len(resultados) == 10
    assert resultados[0] == "processado_1"
    assert resultados[-1] == "processado_10"

    print("  ✅ Teste passou!")


def teste_pipeline_sequencial():
    """Testa a função pipeline_sequencial."""
    print("\n🔄 Testando pipeline_sequencial...")

    def multiplicar_por_2(x: int) -> int:
        return x * 2

    def adicionar_10(x: int) -> int:
        return x + 10

    def converter_para_string(x: int) -> str:
        return f"resultado_{x}"

    # Executar pipeline: 5 -> 10 -> 20 -> "resultado_20"
    resultado = pipeline_sequencial(
        5, multiplicar_por_2, adicionar_10, converter_para_string
    )

    print("  📥 Entrada: 5")
    print("  🔄 Pipeline: x2 -> +10 -> to_string")
    print(f"  📤 Resultado: {resultado}")

    assert resultado == "resultado_20"

    print("  ✅ Teste passou!")


def teste_aplicar_paralelo():
    """Testa a função aplicar_paralelo."""
    print("\n⚡ Testando aplicar_paralelo...")

    def elevar_ao_quadrado(x: int) -> int:
        return x**2

    # Lista de números
    numeros = [1, 2, 3, 4, 5]

    # Processar em paralelo
    resultados = aplicar_paralelo(numeros, elevar_ao_quadrado, max_workers=2)

    # Ordenar resultados pois ordem pode variar no processamento paralelo
    resultados_ordenados = sorted(resultados)
    esperados = [1, 4, 9, 16, 25]

    print(f"  📥 Números: {numeros}")
    print(f"  📤 Quadrados (ordenados): {resultados_ordenados}")
    print(f"  🎯 Esperados: {esperados}")

    assert resultados_ordenados == esperados

    print("  ✅ Teste passou!")


def teste_compor_pipeline():
    """Testa a função compor_pipeline."""
    print("\n🧩 Testando compor_pipeline...")

    def dobrar(x: int) -> int:
        return x * 2

    def somar_um(x: int) -> int:
        return x + 1

    def para_string(x: int) -> str:
        return f"valor_{x}"

    # Compor pipeline
    pipeline = compor_pipeline(dobrar, somar_um, para_string)

    # Testar pipeline: 3 -> 6 -> 7 -> "valor_7"
    resultado = pipeline(3)

    print("  📥 Entrada: 3")
    print("  🔄 Pipeline composto: dobrar -> +1 -> to_string")
    print(f"  📤 Resultado: {resultado}")

    assert resultado == "valor_7"

    print("  ✅ Teste passou!")


def teste_processar_modelos_pendentes():
    """Testa a função processar_modelos_pendentes."""
    print("\n📋 Testando processar_modelos_pendentes...")

    # Criar modelos mock
    modelo1 = ModeloContrato(
        id=ModeloId("modelo_1"),
        nome="Contrato Base",
        template=ConteudoTexto("Template base"),
        tags_obrigatorias={TagId("tag1"), TagId("tag2")},
        tags_opcionais={TagId("tag3")},
        validacoes=[],
    )

    modelo2 = ModeloContrato(
        id=ModeloId("modelo_2"),
        nome="Contrato Vazio",
        template=ConteudoTexto("Template vazio"),
        tags_obrigatorias=set(),  # Sem tags obrigatórias
        tags_opcionais=set(),
        validacoes=[],
    )

    modelos = [modelo1, modelo2]

    # Contexto de teste
    contexto = ContextoProcessamento(
        prioridade=PrioridadeProcessamento.CRITICA,
        timeout_segundos=30,
        modo_paralelo=False,
        filtros_ativos=set(),
        configuracoes={},
    )

    # Processador mock simples
    from datetime import datetime

    from src.docx_compare.core.pipeline_funcional import HashDocumento, Metadados

    class ProcessadorMock:
        def extrair_texto(self, caminho: Path) -> ConteudoTexto:
            return ConteudoTexto("texto mock")

        def extrair_metadados(self, caminho: Path) -> Metadados:
            return Metadados(
                autor="Teste",
                data_criacao=datetime.now(),
                data_modificacao=datetime.now(),
                versao="1.0",
                tamanho_bytes=1000,
                hash_conteudo=HashDocumento("abc123"),
            )

    processador = ProcessadorMock()

    # Processar modelos
    resultados = processar_modelos_pendentes(modelos, contexto, processador)

    print(f"  📥 Modelos para processar: {len(modelos)}")
    print(f"  ⚡ Prioridade: {contexto.prioridade.value}")

    for i, (modelo, status) in enumerate(resultados):
        print(f"  📋 Modelo {i + 1}: {modelo.nome} -> {status.value}")

    assert len(resultados) == 2
    assert resultados[0][1] == StatusProcessamento.CONCLUIDO  # Modelo com tags
    assert resultados[1][1] == StatusProcessamento.ERRO  # Modelo sem tags

    print("  ✅ Teste passou!")


def main():
    """Executa todos os testes das implementações."""
    print("🧪 Testando Implementações do Pipeline Funcional")
    print("=" * 60)

    try:
        teste_calcular_estatisticas()
        teste_filtrar_por_tipo()
        teste_executar_em_lote()
        teste_pipeline_sequencial()
        teste_aplicar_paralelo()
        teste_compor_pipeline()
        teste_processar_modelos_pendentes()

        print("\n" + "=" * 60)
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Pipeline funcional implementado e funcionando corretamente")
        print("🚀 Pronto para uso em produção!")

    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
