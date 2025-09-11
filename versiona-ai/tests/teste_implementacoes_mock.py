#!/usr/bin/env python3
"""
Testes para as implementações Mock dos Protocols
Testes rápidos e independentes que não dependem de serviços externos.
"""

import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from docx_compare.core.implementacoes_mock import (
    AgrupadorModificacoesMock,
    AnalisadorTagsMock,
    ComparadorDocumentosMock,
    FactoryImplementacoesMock,
    ProcessadorTextoMock,
)
from docx_compare.core.pipeline_funcional import (
    ConteudoTexto,
    ContextoProcessamento,
    Documento,
    DocumentoId,
    HashDocumento,
    Metadados,
    ModeloContrato,
    ModeloId,
    PrioridadeProcessamento,
    TagId,
    executar_pipeline_completo,
)


def criar_documento_teste(conteudo: str, nome: str = "teste.docx") -> Documento:
    """Cria um documento de teste."""
    hash_conteudo = HashDocumento(str(hash(conteudo)))
    return Documento(
        id=DocumentoId(f"doc_{hash(conteudo)}"),
        caminho=Path(f"/tmp/{nome}"),
        conteudo_texto=ConteudoTexto(conteudo),
        tags=[],
        metadados=Metadados(
            autor="teste",
            data_criacao=datetime.now(),
            data_modificacao=datetime.now(),
            versao="1.0",
            tamanho_bytes=len(conteudo),
            hash_conteudo=hash_conteudo,
        ),
        hash=hash_conteudo,
    )


def criar_modelo_teste() -> ModeloContrato:
    """Cria um modelo de contrato de teste."""
    return ModeloContrato(
        id=ModeloId("modelo_teste"),
        nome="Modelo de Teste Mock",
        template=ConteudoTexto("Template com {{nome}} e {{valor}}"),
        tags_obrigatorias={TagId("nome"), TagId("valor")},
        tags_opcionais={TagId("preco"), TagId("prazo")},
        validacoes=["mock_validation"],
    )


def teste_processador_texto_mock():
    """Testa ProcessadorTexto mock."""
    print("=== Teste: ProcessadorTexto Mock ===")

    processador = ProcessadorTextoMock()

    # Criar arquivo temporário para teste
    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_original.txt", delete=False
    ) as f:
        f.write("Conteúdo do arquivo original")
        caminho_teste = Path(f.name)

    try:
        # Testar extração de texto
        texto = processador.extrair_texto(caminho_teste)
        assert isinstance(texto, str)
        assert "original" in texto
        assert "{{nome}}" in texto
        print("✅ Extração de texto mock funciona")

        # Testar extração de metadados
        metadados = processador.extrair_metadados(caminho_teste)
        assert metadados.autor == "Mock Author"
        assert metadados.versao == "1.0.0"
        assert metadados.tamanho_bytes == 1024
        print("✅ Extração de metadados mock funciona")

    finally:
        # Limpar arquivo temporário
        caminho_teste.unlink()

    print()


def teste_analisador_tags_mock():
    """Testa AnalisadorTags mock."""
    print("=== Teste: AnalisadorTags Mock ===")

    analisador = AnalisadorTagsMock()

    # Texto com tags
    texto_teste = ConteudoTexto(
        "Este documento contém {{nome}} do contratante. O valor é {{valor}} reais."
    )

    # Testar extração de tags
    tags = analisador.extrair_tags(texto_teste)

    assert len(tags) > 0
    nomes_tags = {tag.nome for tag in tags}

    print(f"Tags encontradas: {nomes_tags}")
    assert "nome" in nomes_tags
    assert "valor" in nomes_tags
    print("✅ Extração de tags mock funciona")

    # Testar validação de tags
    modelo = criar_modelo_teste()
    valido = analisador.validar_tags(tags, modelo)

    print(f"Tags obrigatórias do modelo: {list(modelo.tags_obrigatorias)}")
    print(f"Validação: {'✅ Válido' if valido else '❌ Inválido'}")
    assert valido is True
    print("✅ Validação de tags mock funciona")

    print()


def teste_comparador_documentos_mock():
    """Testa ComparadorDocumentos mock."""
    print("=== Teste: ComparadorDocumentos Mock ===")

    comparador = ComparadorDocumentosMock()

    # Criar documentos de teste
    doc_original = criar_documento_teste(
        "Documento original com {{nome}} e {{valor}}. O prazo é de {{prazo}} dias úteis.",
        "original.txt",
    )

    doc_modificado = criar_documento_teste(
        "Documento modificado com {{nome}} e {{preco}}. O prazo é de {{prazo}} dias corridos.",
        "modificado.txt",
    )

    # Testar comparação
    modificacoes = comparador.comparar(doc_original, doc_modificado)

    assert len(modificacoes) > 0
    print(f"Modificações encontradas: {len(modificacoes)}")

    for mod in modificacoes:
        print(f"  - {mod.tipo.value}: {mod.conteudo_original} → {mod.conteudo_novo}")

    # Verificar modificações específicas esperadas
    tipos_encontrados = {mod.tipo for mod in modificacoes}
    print(f"Tipos de modificação: {[t.value for t in tipos_encontrados]}")

    print("✅ Comparação de documentos mock funciona")
    print()


def teste_agrupador_modificacoes_mock():
    """Testa AgrupadorModificacoes mock."""
    print("=== Teste: AgrupadorModificacoes Mock ===")

    agrupador = AgrupadorModificacoesMock()

    # Criar documentos de teste para gerar modificações
    doc_original = criar_documento_teste(
        "Documento original com {{nome}} e {{valor}}. O prazo é de {{prazo}} dias úteis."
    )
    doc_modificado = criar_documento_teste(
        "Documento modificado com {{nome}} e {{preco}}. O prazo é de {{prazo}} dias corridos."
    )

    comparador = ComparadorDocumentosMock()
    modificacoes = comparador.comparar(doc_original, doc_modificado)

    # Testar agrupamento
    blocos = agrupador.agrupar_por_proximidade(modificacoes)

    print(f"Modificações: {len(modificacoes)}")
    print(f"Blocos agrupados: {len(blocos)}")

    for i, bloco in enumerate(blocos):
        print(f"  Bloco {i + 1}: {len(bloco.modificacoes)} modificações")
        print(f"    Tipo predominante: {bloco.tipo_predominante.value}")
        print(f"    Relevância: {bloco.relevancia:.2f}")

    assert len(blocos) > 0
    print("✅ Agrupamento de modificações mock funciona")
    print()


def teste_factory_implementacoes_mock():
    """Testa Factory de implementações mock."""
    print("=== Teste: Factory de Implementações Mock ===")

    # Testar criação da factory
    factory = FactoryImplementacoesMock()

    # Criar implementações individuais
    processador = factory.criar_processador_texto()
    analisador = factory.criar_analisador_tags()
    comparador = factory.criar_comparador_documentos()
    agrupador = factory.criar_agrupador_modificacoes()

    assert isinstance(processador, ProcessadorTextoMock)
    assert isinstance(analisador, AnalisadorTagsMock)
    assert isinstance(comparador, ComparadorDocumentosMock)
    assert isinstance(agrupador, AgrupadorModificacoesMock)

    print("✅ Factory cria implementações mock individuais")

    # Testar criação de todas de uma vez
    implementacoes = factory.criar_todos()
    assert len(implementacoes) == 4

    print("✅ Factory cria todas as implementações mock de uma vez")
    print()


def teste_pipeline_completo_com_mock():
    """Testa pipeline completo usando implementações mock."""
    print("=== Teste: Pipeline Completo com Mock ===")

    # Configurar factory mock
    factory = FactoryImplementacoesMock()

    # Criar implementações
    processador, analisador, comparador, agrupador = factory.criar_todos()

    # Criar arquivos temporários para teste
    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_original.txt", delete=False
    ) as f1:
        f1.write("Documento original com {{nome}} e {{valor}}")
        caminho_original = Path(f1.name)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix="_modificado.txt", delete=False
    ) as f2:
        f2.write("Documento modificado com {{nome}} e {{preco}}")
        caminho_modificado = Path(f2.name)

    try:
        modelos = [criar_modelo_teste()]

        contexto = ContextoProcessamento(
            prioridade=PrioridadeProcessamento.NORMAL,
            timeout_segundos=30,
            modo_paralelo=False,
            filtros_ativos=set(),
            configuracoes={},
        )

        # Executar pipeline
        resultados = executar_pipeline_completo(
            documentos_originais=[caminho_original],
            documentos_modificados=[caminho_modificado],
            _modelos=modelos,
            _contexto=contexto,
            processador=processador,
            analisador=analisador,
            comparador=comparador,
            agrupador=agrupador,
        )

        print("Pipeline executado com sucesso!")
        print(f"Resultados gerados: {len(resultados)}")

        for i, resultado in enumerate(resultados):
            print(
                f"  Resultado {i + 1}: {len(resultado.blocos_agrupados)} blocos de modificações"
            )
            print(f"    Modificações: {len(resultado.modificacoes)}")
            print(f"    Tempo: {resultado.tempo_processamento:.2f}s")

        assert len(resultados) > 0
        print("✅ Pipeline completo com Mock funciona")

    finally:
        # Limpar arquivos temporários
        caminho_original.unlink()
        caminho_modificado.unlink()

    print()


def main():
    """Executa todos os testes das implementações mock."""
    print("🧪 Testando Implementações Mock dos Protocols")
    print("=" * 60)

    try:
        teste_processador_texto_mock()
        teste_analisador_tags_mock()
        teste_comparador_documentos_mock()
        teste_agrupador_modificacoes_mock()
        teste_factory_implementacoes_mock()
        teste_pipeline_completo_com_mock()

        print("=" * 60)
        print("🎉 TODOS OS TESTES MOCK PASSARAM!")
        print("✅ Implementações mock funcionando corretamente")
        print("⚡ Testes rápidos e independentes de serviços externos")
        print("🚀 Pronto para desenvolvimento e CI/CD!")

    except Exception as e:
        print(f"❌ ERRO NOS TESTES MOCK: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
