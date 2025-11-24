"""
Testes para categorização de modificações usando processamento AST.

Este teste reproduz o cenário real encontrado na versão 10f99b61-dd4a-4041-9753-4fa88e359830
onde o algoritmo está quebrando ALTERAÇÕEs em REMOCAO + INSERCAO incorretamente.

Caso de teste baseado em dados reais:
- Modificação 1: ✅ ALTERACAO (preenchimento de endereço) - CORRETO
- Modificações 2-3: ❌ REMOCAO + INSERCAO (deveria ser 1 ALTERACAO) - INCORRETO
- Modificação 4: ✅ ALTERACAO (preenchimento de datas) - CORRETO
- Modificações 5-6: ❌ REMOCAO + INSERCAO (deveria ser 1 ALTERACAO) - INCORRETO
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_repositorio():
    """Mock do repositório Directus"""
    from repositorio import DirectusRepository

    repo = MagicMock(spec=DirectusRepository)

    # Simular versao_data como viria do Directus
    versao_data = {
        "id": "10f99b61-dd4a-4041-9753-4fa88e359830",
        "arquivo": "arquivo-modificado-id",
        "contrato": {
            "id": "contrato-id",
            "modelo_contrato": {
                "id": "modelo-id",
                "arquivo_original": "arquivo-original-id",
            },
        },
        "date_created": "2025-10-22T00:00:00Z",
    }

    repo.get_versao.return_value = versao_data
    repo.get_arquivo_id.return_value = "arquivo-original-id"

    return repo


@pytest.fixture
def mock_pandoc_ast_original():
    """AST do Pandoc para documento ORIGINAL (com campos em branco)"""
    return {
        "pandoc-api-version": [1, 23, 1],
        "meta": {},
        "blocks": [
            # Parágrafo 1: Endereço com campo em branco
            {
                "t": "Para",
                "c": [
                    {
                        "t": "Str",
                        "c": "O",
                    },
                    {"t": "Space"},
                    {"t": "Str", "c": "presente"},
                    {"t": "Space"},
                    {"t": "Str", "c": "contrato"},
                    {"t": "Space"},
                    {"t": "Str", "c": "tem"},
                    {"t": "Space"},
                    {"t": "Str", "c": "por"},
                    {"t": "Space"},
                    {"t": "Str", "c": "objeto"},
                    {"t": "Space"},
                    {"t": "Str", "c": "o"},
                    {"t": "Space"},
                    {"t": "Str", "c": "imóvel"},
                    {"t": "Space"},
                    {"t": "Str", "c": "localizado"},
                    {"t": "Space"},
                    {"t": "Str", "c": "em"},
                    {"t": "Space"},
                    {"t": "Str", "c": "____________________"},
                    {"t": "Space"},
                    {"t": "Str", "c": "que"},
                    {"t": "Space"},
                    {"t": "Str", "c": "será"},
                    {"t": "Space"},
                    {"t": "Str", "c": "destinado"},
                    {"t": "Space"},
                    {"t": "Str", "c": "exclusivamente"},
                    {"t": "Space"},
                    {"t": "Str", "c": "para"},
                    {"t": "Space"},
                    {"t": "Str", "c": "fins"},
                    {"t": "Space"},
                    {"t": "Str", "c": "residenciais."},
                ],
            },
            # Parágrafo 2: Aluguel com valores em branco
            {
                "t": "Para",
                "c": [
                    {"t": "Str", "c": "O"},
                    {"t": "Space"},
                    {"t": "Str", "c": "aluguel"},
                    {"t": "Space"},
                    {"t": "Str", "c": "mensal"},
                    {"t": "Space"},
                    {"t": "Str", "c": "será"},
                    {"t": "Space"},
                    {"t": "Str", "c": "de"},
                    {"t": "Space"},
                    {"t": "Str", "c": "R$"},
                    {"t": "Space"},
                    {"t": "Str", "c": "__________"},
                    {"t": "Space"},
                    {"t": "Str", "c": "a"},
                    {"t": "Space"},
                    {"t": "Str", "c": "ser"},
                    {"t": "Space"},
                    {"t": "Str", "c": "pago"},
                    {"t": "Space"},
                    {"t": "Str", "c": "até"},
                    {"t": "Space"},
                    {"t": "Str", "c": "o"},
                    {"t": "Space"},
                    {"t": "Str", "c": "dia"},
                    {"t": "Space"},
                    {"t": "Str", "c": "05"},
                    {"t": "Space"},
                    {"t": "Str", "c": "de"},
                    {"t": "Space"},
                    {"t": "Str", "c": "cada"},
                    {"t": "Space"},
                    {"t": "Str", "c": "mês."},
                ],
            },
        ],
    }


@pytest.fixture
def mock_pandoc_ast_modificado():
    """AST do Pandoc para documento MODIFICADO (campos preenchidos)"""
    return {
        "pandoc-api-version": [1, 23, 1],
        "meta": {},
        "blocks": [
            # Parágrafo 1: Endereço preenchido
            {
                "t": "Para",
                "c": [
                    {"t": "Str", "c": "O"},
                    {"t": "Space"},
                    {"t": "Str", "c": "presente"},
                    {"t": "Space"},
                    {"t": "Str", "c": "contrato"},
                    {"t": "Space"},
                    {"t": "Str", "c": "tem"},
                    {"t": "Space"},
                    {"t": "Str", "c": "por"},
                    {"t": "Space"},
                    {"t": "Str", "c": "objeto"},
                    {"t": "Space"},
                    {"t": "Str", "c": "o"},
                    {"t": "Space"},
                    {"t": "Str", "c": "imóvel"},
                    {"t": "Space"},
                    {"t": "Str", "c": "localizado"},
                    {"t": "Space"},
                    {"t": "Str", "c": "em"},
                    {"t": "Space"},
                    {"t": "Str", "c": "Jardim"},
                    {"t": "Space"},
                    {"t": "Str", "c": "da"},
                    {"t": "Space"},
                    {"t": "Str", "c": "Penha"},
                    {"t": "Space"},
                    {"t": "Str", "c": "que"},
                    {"t": "Space"},
                    {"t": "Str", "c": "será"},
                    {"t": "Space"},
                    {"t": "Str", "c": "destinado"},
                    {"t": "Space"},
                    {"t": "Str", "c": "exclusivamente"},
                    {"t": "Space"},
                    {"t": "Str", "c": "para"},
                    {"t": "Space"},
                    {"t": "Str", "c": "fins"},
                    {"t": "Space"},
                    {"t": "Str", "c": "residenciais."},
                ],
            },
            # Parágrafo 2: Aluguel com valores preenchidos
            {
                "t": "Para",
                "c": [
                    {"t": "Str", "c": "O"},
                    {"t": "Space"},
                    {"t": "Str", "c": "aluguel"},
                    {"t": "Space"},
                    {"t": "Str", "c": "mensal"},
                    {"t": "Space"},
                    {"t": "Str", "c": "será"},
                    {"t": "Space"},
                    {"t": "Str", "c": "de"},
                    {"t": "Space"},
                    {"t": "Str", "c": "R$"},
                    {"t": "Space"},
                    {"t": "Str", "c": "2.000,00"},
                    {"t": "Space"},
                    {"t": "Str", "c": "a"},
                    {"t": "Space"},
                    {"t": "Str", "c": "ser"},
                    {"t": "Space"},
                    {"t": "Str", "c": "pago"},
                    {"t": "Space"},
                    {"t": "Str", "c": "até"},
                    {"t": "Space"},
                    {"t": "Str", "c": "o"},
                    {"t": "Space"},
                    {"t": "Str", "c": "dia"},
                    {"t": "Space"},
                    {"t": "Str", "c": "05"},
                    {"t": "Space"},
                    {"t": "Str", "c": "de"},
                    {"t": "Space"},
                    {"t": "Str", "c": "cada"},
                    {"t": "Space"},
                    {"t": "Str", "c": "mês."},
                ],
            },
        ],
    }


def test_preenchimento_campo_deve_ser_alteracao_nao_remocao_insercao(
    mock_repositorio, mock_pandoc_ast_original, mock_pandoc_ast_modificado
):
    """
    Testa que preenchimento de campos em branco deve gerar ALTERACAO,
    não REMOCAO + INSERCAO.

    Cenário:
    - Original: "R$ __________" (campo em branco)
    - Modificado: "R$ 2.000,00" (campo preenchido)

    Comportamento esperado:
    - 1 modificação do tipo ALTERACAO

    Comportamento atual (INCORRETO):
    - 1 modificação do tipo REMOCAO
    - 1 modificação do tipo INSERCAO
    """
    from directus_server import DirectusAPI, PandocASTProcessor

    # Criar instância da API com repositório mockado
    with patch("directus_server.DirectusRepository", return_value=mock_repositorio):
        api = DirectusAPI()
        api.repo = mock_repositorio

    # Mock do diff HTML que simula o bug real:
    # O diff está gerando REMOCAO + INSERCAO ao invés de ALTERACAO
    # Critério: Sem data-clause OU posições muito distantes (>200 chars)
    mock_diff_html = """
    <div class='diff-removed'>- O aluguel mensal será de R$ __________ (____________________________________________), a ser pago até o dia 05 de cada mês, mediante depósito em conta bancária.</div>
    <p>Texto intermediário para aumentar a distância entre remoção e inserção, simulando o caso onde o algoritmo não consegue parear corretamente...</p>
    <p>Mais texto para garantir que a distância seja maior que 200 caracteres, forçando o algoritmo a tratar como duas modificações separadas ao invés de uma única alteração...</p>
    <div class='diff-added'>+ O aluguel mensal será de R$ 2.000,00 (dois mil reais), a ser pago até o dia 05 de cada mês, mediante depósito em conta bancária.</div>
    """

    # Mock do Pandoc para retornar nossos ASTs controlados
    with (
        patch.object(PandocASTProcessor, "convert_docx_to_ast") as mock_convert,
        patch.object(api, "_download_docx_to_temp") as mock_download,
        patch.object(api, "_generate_diff_html_from_ast") as mock_diff,
    ):
        # Configurar mocks
        mock_convert.side_effect = [
            mock_pandoc_ast_original,  # Primeira chamada = original
            mock_pandoc_ast_modificado,  # Segunda chamada = modificado
        ]

        mock_download.side_effect = [
            "/tmp/original.docx",
            "/tmp/modificado.docx",
        ]

        # Retornar o diff HTML que simula o bug
        mock_diff.return_value = mock_diff_html

        # Processar versão
        resultado = api._process_versao_com_ast(
            "10f99b61-dd4a-4041-9753-4fa88e359830",
            mock_repositorio.get_versao.return_value,
        )

    # Validações
    assert "modificacoes" in resultado, "Deve retornar modificações"
    modificacoes = resultado["modificacoes"]

    # Debug: mostrar modificações retornadas
    print(f"\n🔍 Total de modificações retornadas: {len(modificacoes)}")
    for i, mod in enumerate(modificacoes, 1):
        tipo = mod.get("tipo", mod.get("categoria", "UNKNOWN"))
        print(f"  Mod {i}: tipo={tipo}")
        conteudo_dict = mod.get("conteudo", {})
        if isinstance(conteudo_dict, dict):
            original = str(conteudo_dict.get("original", ""))[:80]
            novo = str(conteudo_dict.get("novo", ""))[:80]
            print(f"    original: {original}...")
            print(f"    novo: {novo}...")

    # TESTE PRINCIPAL: Validar categorização
    # Cenário esperado (CORRETO): 1 modificação do tipo ALTERACAO
    # Cenário atual (INCORRETO): 1 REMOCAO + 1 INSERCAO = 2 modificações

    tipos_modificacoes = [
        mod.get("tipo", mod.get("categoria", "UNKNOWN")) for mod in modificacoes
    ]

    # Contar por tipo
    total_alteracoes = tipos_modificacoes.count("ALTERACAO")
    total_remocoes = tipos_modificacoes.count("REMOCAO")
    total_insercoes = tipos_modificacoes.count("INSERCAO")

    print("\n📊 Distribuição por tipo:")
    print(f"   ALTERACAO: {total_alteracoes}")
    print(f"   REMOCAO: {total_remocoes}")
    print(f"   INSERCAO: {total_insercoes}")

    # VALIDAÇÃO: Deve ser 1 ALTERACAO, não 1 REMOCAO + 1 INSERCAO
    assert len(modificacoes) == 1, (
        f"Deve ter 1 modificação (ALTERACAO), mas tem {len(modificacoes)}. "
        f"Breakdown: {total_alteracoes} ALTERACAO, {total_remocoes} REMOCAO, {total_insercoes} INSERCAO"
    )

    assert tipos_modificacoes[0] == "ALTERACAO", (
        f"Modificação deve ser ALTERACAO, mas é {tipos_modificacoes[0]}"
    )

    # Validar conteúdo da modificação
    mod = modificacoes[0]
    conteudo_dict = mod.get("conteudo", {})

    if isinstance(conteudo_dict, dict):
        original_text = conteudo_dict.get("original", "")
        novo_text = conteudo_dict.get("novo", "")

        assert "R$ __________" in original_text or "R$ 2.000,00" in novo_text, (
            "Modificação deve conter o preenchimento do campo de aluguel"
        )


def test_similaridade_threshold_para_alteracao():
    """
    Testa que textos com alta similaridade (>60%) devem ser categorizados
    como ALTERACAO, não como REMOCAO + INSERCAO.

    O limite de 60% é baseado em análise empírica:
    - "R$ __________" vs "R$ 2.000,00" = ~80% similar (mesma estrutura)
    - Apenas o campo específico foi preenchido
    """
    from difflib import SequenceMatcher

    original = (
        "O aluguel mensal será de R$ __________ a ser pago até o dia 05 de cada mês."
    )
    modificado = (
        "O aluguel mensal será de R$ 2.000,00 a ser pago até o dia 05 de cada mês."
    )

    # Calcular similaridade
    ratio = SequenceMatcher(None, original, modificado).ratio()

    # Deve ser alta similaridade (acima de 60%)
    assert ratio > 0.6, f"Similaridade deve ser > 60%, mas é {ratio * 100:.1f}%"

    print(
        f"✅ Similaridade: {ratio * 100:.1f}% - Deve ser ALTERACAO, não REMOCAO+INSERCAO"
    )


def test_categorization_logic_split_incorreto():
    """
    Teste que demonstra o bug atual: quando difflib retorna 'replace',
    o código está criando REMOCAO + INSERCAO ao invés de ALTERACAO.

    Este é o comportamento INCORRETO que queremos corrigir.
    """
    import difflib

    original_lines = [
        "O aluguel mensal será de R$ __________ a ser pago até o dia 05 de cada mês."
    ]
    modified_lines = [
        "O aluguel mensal será de R$ 2.000,00 a ser pago até o dia 05 de cada mês."
    ]

    diff = list(difflib.unified_diff(original_lines, modified_lines, lineterm=""))

    # O diff retorna isso (simplificado):
    # - O aluguel mensal será de R$ __________ ...
    # + O aluguel mensal será de R$ 2.000,00 ...

    # Contém tanto remoção (-) quanto adição (+)
    has_removal = any(
        line.startswith("-") and not line.startswith("---") for line in diff
    )
    has_addition = any(
        line.startswith("+") and not line.startswith("+++") for line in diff
    )

    assert has_removal and has_addition, "Diff deve conter remoção E adição"

    # O código atual trata isso como 2 modificações separadas (BUG!)
    # Deveria ser 1 ALTERACAO

    print("❌ Bug reproduzido: diff com - e + cria REMOCAO + INSERCAO")
    print("✅ Solução: Verificar similaridade e criar 1 ALTERACAO quando > 60%")


def test_alteracao_case_insensitive_deve_ser_pareada(mock_repositorio):
    """
    Textos idênticos exceto por case devem ser pareados como ALTERACAO (Task 007)

    Caso real da versão 95174b7a:
    - Original: "2.2. Se aplicável, a retroatividade..."
    - Novo: "2.2. SE APLICÁVEL, A RETROATIVIDADE..."

    Similaridade esperada: ~95% (apenas case diferente)
    Comportamento esperado: 1 ALTERACAO (não 2 modificações separadas)
    """
    from directus_server import DirectusAPI, PandocASTProcessor

    # Criar instância da API com repositório mockado
    with patch("directus_server.DirectusRepository", return_value=mock_repositorio):
        api = DirectusAPI()
        api.repo = mock_repositorio

    # Mock do diff HTML com textos case-different
    # SEM data-clause E distância > 200 chars para forçar critério 3 (similaridade)
    mock_diff_html = """
    <div class='diff-removed'>- 2.2. Se aplicável, a retroatividade dos efeitos do CONTRATO, não ocasionará qualquer prejuízo das obrigações da CONTRATADA sem acarretar quaisquer penalidades, compensação ou lucros cessantes para a CONTRATANTE, conforme prazo descrito no QUADRO RESUMO.</div>
    <p>Texto intermediário para aumentar a distância além de 200 caracteres no HTML...</p>
    <p>Mais texto intermediário para forçar o algoritmo a usar o critério 3 (similaridade textual)...</p>
    <p>Ainda mais texto para garantir distância > 200 chars e desabilitar critério 2 (proximidade)...</p>
    <div class='diff-added'>+ 2.2. SE APLICÁVEL, A RETROATIVIDADE DOS EFEITOS DO CONTRATO NÃO OCASIONARÁ QUALQUER PREJUÍZO DAS OBRIGAÇÕES DA CONTRATADA, SEM ACARRETAR QUAISQUER PENALIDADES, COMPENSAÇÃO OU LUCROS CESSANTES PARA A CONTRATANTE, CONFORME PRAZO DESCRITO NO QUADRO RESUMO.</div>
    """

    # Mock ASTs simples (não precisamos de conteúdo real para este teste)
    mock_ast_original = {"pandoc-api-version": [1, 23, 1], "meta": {}, "blocks": []}
    mock_ast_modificado = {"pandoc-api-version": [1, 23, 1], "meta": {}, "blocks": []}

    # Mock do Pandoc
    with (
        patch.object(PandocASTProcessor, "convert_docx_to_ast") as mock_convert,
        patch.object(api, "_download_docx_to_temp") as mock_download,
        patch.object(api, "_generate_diff_html_from_ast") as mock_diff,
    ):
        # Configurar mocks
        mock_convert.side_effect = [mock_ast_original, mock_ast_modificado]
        mock_download.side_effect = ["/tmp/original.docx", "/tmp/modificado.docx"]
        mock_diff.return_value = mock_diff_html

        # Processar versão
        resultado = api._process_versao_com_ast(
            "test-version-id", mock_repositorio.get_versao.return_value
        )

    # Validações
    assert "modificacoes" in resultado, "Deve retornar modificações"
    modificacoes = resultado["modificacoes"]

    # Debug
    print(f"\n🔍 Total de modificações: {len(modificacoes)}")
    for i, mod in enumerate(modificacoes, 1):
        tipo = mod.get("tipo", mod.get("categoria", "UNKNOWN"))
        print(f"  Mod {i}: {tipo}")

    # TESTE PRINCIPAL: Deve ser 1 ALTERACAO (não 2 mods separadas)
    assert len(modificacoes) == 1, (
        f"Deve ter 1 ALTERACAO, mas tem {len(modificacoes)} modificações. "
        f"Textos case-different devem ser pareados!"
    )

    mod = modificacoes[0]
    tipo = mod.get("tipo", mod.get("categoria", "UNKNOWN"))
    assert tipo == "ALTERACAO", f"Deve ser ALTERACAO, mas é {tipo}"

    # Verificar que textos originais foram preservados (case mantido)
    conteudo_dict = mod.get("conteudo", {})
    if isinstance(conteudo_dict, dict):
        original = conteudo_dict.get("original", "")
        novo = conteudo_dict.get("novo", "")

        # Original deve ter case misto ("Se aplicável")
        assert "Se aplicável" in original or "se aplicável" in original.lower()

        # Novo deve ter UPPERCASE
        assert "SE APLICÁVEL" in novo

        print("✅ Case original preservado: 'Se aplicável' → 'SE APLICÁVEL'")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
