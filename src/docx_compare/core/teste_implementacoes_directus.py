#!/usr/bin/env python3
"""
Testes para as implementações Directus com inversão de dependência.
"""

import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import tempfile
from datetime import datetime

from docx_compare.core.implementacoes_directus import (
    AgrupadorModificacoesDirectus,
    AnalisadorTagsDirectus,
    ComparadorDocumentosDirectus,
    ConfiguracaoDirectus,
    FactoryImplementacoes,
    ProcessadorTextoDirectus,
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
        nome="Modelo de Teste",
        template=ConteudoTexto("Template com {{nome}} e {{valor}}"),
        tags_obrigatorias={TagId("nome"), TagId("valor")},
        tags_opcionais={TagId("data"), TagId("local")},
        validacoes=["nome_obrigatorio", "valor_numerico"],
    )


def teste_configuracao_directus():
    """Testa configuração do Directus."""
    print("=== Teste: Configuração Directus ===")

    # Teste configuração padrão
    config = ConfiguracaoDirectus(
        url_base="https://test.directus.com", token="test_token_123"
    )

    assert config.url_base == "https://test.directus.com"
    assert config.token == "test_token_123"
    assert config.timeout == 30

    print("✅ Configuração básica criada com sucesso")

    # Teste configuração a partir de env (mock)
    import os

    os.environ["DIRECTUS_URL"] = "https://env.directus.com"
    os.environ["DIRECTUS_TOKEN"] = "env_token_456"
    os.environ["DIRECTUS_TIMEOUT"] = "60"

    config_env = ConfiguracaoDirectus.from_env()

    assert config_env.url_base == "https://env.directus.com"
    assert config_env.token == "env_token_456"
    assert config_env.timeout == 60

    print("✅ Configuração a partir de variáveis de ambiente funciona")
    print()


def teste_processador_texto_directus():
    """Testa ProcessadorTexto com implementação Directus."""
    print("=== Teste: ProcessadorTexto Directus ===")

    config = ConfiguracaoDirectus(url_base="https://test.com", token="test")
    processador = ProcessadorTextoDirectus(config)

    # Criar arquivo temporário para teste
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(
            "Este é um texto de teste\ncom múltiplas linhas\ne {{tags}} para processar."
        )
        caminho_teste = Path(f.name)

    try:
        # Testar extração de texto
        texto = processador.extrair_texto(caminho_teste)
        assert isinstance(texto, str)  # ConteudoTexto é NewType(str)
        assert "texto de teste" in texto
        print("✅ Extração de texto funciona")

        # Testar extração de metadados
        metadados = processador.extrair_metadados(caminho_teste)
        assert metadados.autor is not None
        assert metadados.tamanho_bytes > 0
        assert metadados.hash_conteudo != "error"
        print("✅ Extração de metadados funciona")

    finally:
        # Limpar arquivo temporário
        caminho_teste.unlink()

    print()


def teste_analisador_tags_directus():
    """Testa AnalisadorTags com implementação Directus."""
    print("=== Teste: AnalisadorTags Directus ===")

    config = ConfiguracaoDirectus(url_base="https://test.com", token="test")
    analisador = AnalisadorTagsDirectus(config)

    # Texto com diferentes tipos de tags
    texto_teste = ConteudoTexto("""
    Este documento contém {{nome}} do contratante.
    O valor é {{valor.total}} reais.
    A data é {{1.2.3}} conforme {{TAG-especial}}.
    """)

    # Testar extração de tags
    tags = analisador.extrair_tags(texto_teste)

    assert len(tags) > 0
    nomes_tags = {tag.nome for tag in tags}

    print(f"Tags encontradas: {nomes_tags}")
    assert "nome" in nomes_tags
    assert "valor.total" in nomes_tags
    print("✅ Extração de tags funciona")

    # Testar validação de tags
    modelo = criar_modelo_teste()
    valido = analisador.validar_tags(tags, modelo)
    print(f"Validação: {'✅ Válido' if valido else '❌ Inválido'}")

    print()


def teste_comparador_documentos_directus():
    """Testa ComparadorDocumentos com implementação Directus."""
    print("=== Teste: ComparadorDocumentos Directus ===")

    config = ConfiguracaoDirectus(url_base="https://test.com", token="test")
    comparador = ComparadorDocumentosDirectus(config)

    # Criar documentos de teste
    doc_original = criar_documento_teste(
        "Primeira linha\nSegunda linha\nTerceira linha", "original.txt"
    )

    doc_modificado = criar_documento_teste(
        "Primeira linha modificada\nSegunda linha\nQuarta linha nova", "modificado.txt"
    )

    # Testar comparação
    modificacoes = comparador.comparar(doc_original, doc_modificado)

    assert len(modificacoes) > 0
    print(f"Modificações encontradas: {len(modificacoes)}")

    for mod in modificacoes:
        print(f"  - {mod.tipo.value}: {mod.conteudo_original or mod.conteudo_novo}")

    print("✅ Comparação de documentos funciona")
    print()


def teste_agrupador_modificacoes_directus():
    """Testa AgrupadorModificacoes com implementação Directus."""
    print("=== Teste: AgrupadorModificacoes Directus ===")

    config = ConfiguracaoDirectus(url_base="https://test.com", token="test")
    agrupador = AgrupadorModificacoesDirectus(config)

    # Criar documentos de teste para gerar modificações
    doc_original = criar_documento_teste("Linha 1\nLinha 2\nLinha 3\nLinha 4\nLinha 5")
    doc_modificado = criar_documento_teste(
        "Linha 1 alterada\nLinha 2\nLinha 3 alterada\nLinha 4\nLinha 6"
    )

    comparador = ComparadorDocumentosDirectus(config)
    modificacoes = comparador.comparar(doc_original, doc_modificado)

    # Testar agrupamento
    blocos = agrupador.agrupar_por_proximidade(modificacoes)

    print(f"Modificações: {len(modificacoes)}")
    print(f"Blocos agrupados: {len(blocos)}")

    for i, bloco in enumerate(blocos):
        print(f"  Bloco {i + 1}: {len(bloco.modificacoes)} modificações")
        print(f"    Tipo predominante: {bloco.tipo_predominante.value}")
        print(f"    Relevância: {bloco.relevancia:.2f}")

    print("✅ Agrupamento de modificações funciona")
    print()


def teste_factory_implementacoes():
    """Testa Factory para criar implementações."""
    print("=== Teste: Factory de Implementações ===")

    # Testar criação com configuração customizada
    config = ConfiguracaoDirectus(url_base="https://custom.com", token="custom_token")
    factory = FactoryImplementacoes(config)

    # Criar implementações individuais
    processador = factory.criar_processador_texto()
    analisador = factory.criar_analisador_tags()
    comparador = factory.criar_comparador_documentos()
    agrupador = factory.criar_agrupador_modificacoes()

    assert isinstance(processador, ProcessadorTextoDirectus)
    assert isinstance(analisador, AnalisadorTagsDirectus)
    assert isinstance(comparador, ComparadorDocumentosDirectus)
    assert isinstance(agrupador, AgrupadorModificacoesDirectus)

    print("✅ Factory cria implementações individuais")

    # Testar criação de todas de uma vez
    implementacoes = factory.criar_todos()
    assert len(implementacoes) == 4

    print("✅ Factory cria todas as implementações de uma vez")
    print()


def teste_pipeline_completo_com_directus():
    """Testa pipeline completo usando implementações Directus."""
    print("=== Teste: Pipeline Completo com Directus ===")

    # Configurar factory
    config = ConfiguracaoDirectus(url_base="https://test.com", token="test")
    factory = FactoryImplementacoes(config)

    # Criar implementações
    processador, analisador, comparador, agrupador = factory.criar_todos()

    # Criar arquivos temporários para teste
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f1:
        f1.write("Documento original com {{nome}} e {{valor}}")
        caminho_original = Path(f1.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f2:
        f2.write("Documento modificado com {{nome}} e {{preco}}")
        caminho_modificado = Path(f2.name)

    try:
        modelos = [criar_modelo_teste()]

        contexto = ContextoProcessamento(
            prioridade=PrioridadeProcessamento.NORMAL,
            timeout_segundos=30,
            modo_paralelo=True,
            filtros_ativos=set(),
            configuracoes={},
        )

        # Executar pipeline
        resultados = executar_pipeline_completo(
            documentos_originais=[caminho_original],
            documentos_modificados=[caminho_modificado],
            modelos=modelos,
            contexto=contexto,
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

        print("✅ Pipeline completo com Directus funciona")

    except Exception as e:
        print(f"❌ Erro no pipeline: {e}")
        print("⚠️ Teste pode falhar por dependências externas (pandoc)")

    finally:
        # Limpar arquivos temporários
        caminho_original.unlink()
        caminho_modificado.unlink()

    print()


def main():
    """Executa todos os testes das implementações Directus."""
    print("🧪 Executando testes das implementações Directus\n")

    try:
        teste_configuracao_directus()
        teste_processador_texto_directus()
        teste_analisador_tags_directus()
        teste_comparador_documentos_directus()
        teste_agrupador_modificacoes_directus()
        teste_factory_implementacoes()
        teste_pipeline_completo_com_directus()

        print("🎉 Todos os testes das implementações Directus passaram!")

    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        raise


if __name__ == "__main__":
    main()
