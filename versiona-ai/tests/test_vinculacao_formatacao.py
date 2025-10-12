#!/usr/bin/env python3
"""
Teste de vinculação com formatações variadas

Este teste tenta reproduzir problemas reais de formatação:
- Espaços múltiplos
- Tabs vs espaços
- Quebras de linha diferentes
- Espaços no início/fim de linhas

Usa mocks para requisições HTTP externas ao Directus
"""

import os
import sys

# Adicionar o diretório versiona-ai ao path
versiona_ai_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, versiona_ai_dir)

# ruff: noqa: E402
from directus_server import DirectusAPI


def test_vinculacao_com_formatacao_variada():
    """Testa vinculação com diferentes tipos de formatação"""
    print("\n" + "=" * 80)
    print("🧪 TESTE: Vinculação com Formatação Variada")
    print("=" * 80 + "\n")

    # Modelo COM tags (com formatações reais: espaços extras, tabs, quebras variadas)
    modelo_com_tags = """{{1}}
Cláusula  1   -   DO OBJETO

    Este contrato   tem por   objeto    a prestação
    de serviços  de consultoria    em tecnologia.
{{/1}}

{{2}}
Cláusula 2  -  DO VALOR
	O valor total    do contrato é   de R$   10.000,00
	(dez   mil reais).
{{/2}}

{{3}}
Cláusula   3   -   DO PRAZO

O prazo de execução   será de    30   (trinta)
dias   corridos.
{{/3}}
"""

    print("📄 MODELO COM TAGS:")
    print(f"   Tamanho: {len(modelo_com_tags)} caracteres")
    tem_tabs = "Sim" if "\t" in modelo_com_tags else "Não"
    print(f"   Contém tabs: {tem_tabs}")

    # Tags do modelo (posições no texto COM tags)
    tags_modelo = [
        {
            "tag_nome": "1",
            "posicao_inicio_texto": modelo_com_tags.find("{{1}}"),
            "posicao_fim_texto": modelo_com_tags.find("{{/1}}") + len("{{/1}}"),
            "clausulas": [{"id": "cl-1", "numero": "1", "nome": "DO OBJETO"}],
        },
        {
            "tag_nome": "2",
            "posicao_inicio_texto": modelo_com_tags.find("{{2}}"),
            "posicao_fim_texto": modelo_com_tags.find("{{/2}}") + len("{{/2}}"),
            "clausulas": [{"id": "cl-2", "numero": "2", "nome": "DO VALOR"}],
        },
        {
            "tag_nome": "3",
            "posicao_inicio_texto": modelo_com_tags.find("{{3}}"),
            "posicao_fim_texto": modelo_com_tags.find("{{/3}}") + len("{{/3}}"),
            "clausulas": [{"id": "cl-3", "numero": "3", "nome": "DO PRAZO"}],
        },
    ]

    print(f"\n🏷️  TAGS DO MODELO: {len(tags_modelo)}")
    for tag in tags_modelo:
        print(
            f"   - Tag {tag['tag_nome']}: pos {tag['posicao_inicio_texto']}-{tag['posicao_fim_texto']}"
        )

    # Modificações (simulando extraídas do diff HTML)
    # PROBLEMA: Os textos têm formatação DIFERENTE do modelo!
    modificacoes = [
        {
            "id": 1,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "Este contrato tem por objeto a prestação",  # Sem espaços extras!
                "novo": "Este contrato tem como objetivo a prestação",
            },
        },
        {
            "id": 2,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "O valor total do contrato é de R$ 10.000,00",  # Sem tabs!
                "novo": "O valor total do contrato é de R$ 15.000,00",
            },
        },
        {
            "id": 3,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "O prazo de execução será de 30 (trinta)",  # Espaçamento normal!
                "novo": "O prazo de execução será de 60 (sessenta)",
            },
        },
    ]

    print(f"\n📝 MODIFICAÇÕES: {len(modificacoes)}")
    for mod in modificacoes:
        texto = mod["conteudo"].get("original", mod["conteudo"].get("novo", ""))
        print(f"   - Mod #{mod['id']}: '{texto[:50]}...'")

    # Executar vinculação
    api = DirectusAPI()
    resultado = api._vincular_modificacoes_clausulas(
        modificacoes, tags_modelo, modelo_com_tags
    )

    # Verificar resultados
    print("\n" + "=" * 80)
    print("📊 RESULTADOS DA VINCULAÇÃO")
    print("=" * 80)

    vinculadas = 0
    for mod in resultado:
        mod_id = mod.get("id")
        clausula_id = mod.get("clausula_id")
        clausula_numero = mod.get("clausula_numero")
        tag_nome = mod.get("tag_nome")
        pos_inicio = mod.get("posicao_inicio")
        pos_fim = mod.get("posicao_fim")

        if clausula_id:
            vinculadas += 1
            status = "✅"
        else:
            status = "⚠️ "

        print(
            f"{status} Mod #{mod_id}: "
            f"Tag={tag_nome or 'N/A'}, "
            f"Cláusula={clausula_numero or 'N/A'}, "
            f"Pos={pos_inicio}-{pos_fim if pos_fim else 'N/A'}"
        )

    print(f"\n📈 RESUMO: {vinculadas}/{len(modificacoes)} modificações vinculadas")

    # Análise do problema
    print("\n" + "=" * 80)
    print("🔍 ANÁLISE DO PROBLEMA")
    print("=" * 80)

    if vinculadas < len(modificacoes):
        print("\n❌ PROBLEMA DETECTADO:")
        print("   As modificações têm formatação DIFERENTE do modelo:")
        print("   - Modelo: espaços extras, tabs, quebras variadas")
        print("   - Modificações: texto 'normalizado' do diff")
        print("\n💡 SOLUÇÃO NECESSÁRIA:")
        print("   1. Normalizar espaços antes de buscar (substituir múltiplos por um)")
        print("   2. Usar busca fuzzy/aproximada")
        print("   3. OU: extrair texto limpo do modelo e usar para comparação")
    else:
        print("\n✅ VINCULAÇÃO FUNCIONOU!")
        print(
            "   A implementação atual conseguiu lidar com as diferenças de formatação"
        )

    print("\n" + "=" * 80 + "\n")

    # Assertion para o teste
    assert vinculadas == len(modificacoes), (
        f"Esperado {len(modificacoes)} vinculações, obteve {vinculadas}"
    )


def test_vinculacao_com_normalizacao():
    """Testa vinculação COM normalização de espaços"""
    print("\n" + "=" * 80)
    print("🧪 TESTE: Vinculação com Normalização de Espaços")
    print("=" * 80 + "\n")

    # Mesmo modelo com formatação problemática
    modelo_com_tags = """{{1}}
Cláusula  1   -   DO OBJETO

    Este contrato   tem por   objeto    a prestação
    de serviços  de consultoria.
{{/1}}

{{2}}
Cláusula 2  -  DO VALOR
	O valor total    do contrato é   de R$   10.000,00
	(dez   mil reais).
{{/2}}
"""

    tags_modelo = [
        {
            "tag_nome": "1",
            "posicao_inicio_texto": modelo_com_tags.find("{{1}}"),
            "posicao_fim_texto": modelo_com_tags.find("{{/1}}") + len("{{/1}}"),
            "clausulas": [{"id": "cl-1", "numero": "1", "nome": "DO OBJETO"}],
        },
        {
            "tag_nome": "2",
            "posicao_inicio_texto": modelo_com_tags.find("{{2}}"),
            "posicao_fim_texto": modelo_com_tags.find("{{/2}}") + len("{{/2}}"),
            "clausulas": [{"id": "cl-2", "numero": "2", "nome": "DO VALOR"}],
        },
    ]

    # Modificações com texto normalizado
    modificacoes = [
        {
            "id": 1,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "Este contrato tem por objeto a prestação",
                "novo": "Este contrato tem como objetivo a prestação",
            },
        },
        {
            "id": 2,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "O valor total do contrato é de R$ 10.000,00",
                "novo": "O valor total do contrato é de R$ 15.000,00",
            },
        },
    ]

    print("💡 ESTRATÉGIA: Normalizar espaços no modelo antes de buscar")
    print("   - Remover tags")
    print("   - Substituir múltiplos espaços/tabs/quebras por um espaço único")
    print("   - Remover espaços no início/fim de linhas\n")

    # Simular normalização (o código real deveria fazer isso)
    import re

    texto_sem_tags = re.sub(r"\{\{/?[\w.]+\}\}", "", modelo_com_tags)
    texto_normalizado = re.sub(r"\s+", " ", texto_sem_tags).strip()

    print(f"📄 Texto original: {len(modelo_com_tags)} chars")
    print(f"📄 Texto sem tags: {len(texto_sem_tags)} chars")
    print(f"📄 Texto normalizado: {len(texto_normalizado)} chars\n")

    # Verificar se os textos das modificações existem no texto normalizado
    print("🔍 VERIFICANDO PRESENÇA DOS TEXTOS:\n")
    for mod in modificacoes:
        texto_orig = mod["conteudo"]["original"]
        encontrado = texto_orig in texto_normalizado

        if encontrado:
            pos = texto_normalizado.find(texto_orig)
            print(f"✅ Mod #{mod['id']}: ENCONTRADO na posição {pos}")
        else:
            print(f"❌ Mod #{mod['id']}: NÃO ENCONTRADO")
            # Tentar busca parcial
            palavras = texto_orig.split()[:3]  # Primeiras 3 palavras
            busca_parcial = " ".join(palavras)
            if busca_parcial in texto_normalizado:
                pos = texto_normalizado.find(busca_parcial)
                print(f"   💡 Busca parcial '{busca_parcial}' encontrada em {pos}")

    print("\n" + "=" * 80 + "\n")


def test_vinculacao_com_mock_completo():
    """
    Testa vinculação usando a implementação REAL com MOCKS para APIs externas
    Simula cenário completo: processo de versão com modelo e vinculação
    """
    print("\n" + "=" * 80)
    print("🧪 TESTE 3: Vinculação com Mock de APIs Externas (Implementação Real)")
    print("=" * 80 + "\n")

    from unittest.mock import Mock, patch

    # =============================================================================
    # SETUP: Preparar mocks de arquivos DOCX temporários
    # =============================================================================

    # Criar arquivo DOCX temporário do modelo (com tags e formatação variada)
    modelo_texto = """{{1}}
CLÁUSULA  PRIMEIRA   -   DO OBJETO

	Este   contrato   tem por    objeto    a prestação
de   serviços   de    consultoria.
{{/1}}

{{2}}
CLÁUSULA  SEGUNDA  -  DO VALOR
	O  valor   total do   contrato   é de R$   10.000,00.
{{/2}}
"""

    # Criar arquivo DOCX temporário da versão (sem tags, formatação normalizada)
    versao_texto = """CLÁUSULA PRIMEIRA - DO OBJETO

Este contrato tem por objeto a prestação
de serviços de consultoria.

CLÁUSULA SEGUNDA - DO VALOR
O valor total do contrato é de R$ 10.000,00.
"""

    # Modificações simuladas (como viriam do diff)
    modificacoes_mock = [
        {
            "id": 1,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "prestação de serviços de consultoria",  # Texto específico da cláusula 1
                "novo": "fornecimento de serviços de consultoria",
            },
        },
        {
            "id": 2,
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "valor total do contrato",  # Texto específico da cláusula 2
                "novo": "valor integral do contrato",
            },
        },
    ]

    print("📦 MOCKS CONFIGURADOS:")
    print(f"   - Modelo: {len(modelo_texto)} chars (COM tags e formatação variada)")
    print(f"   - Versão: {len(versao_texto)} chars (SEM tags, normalizado)")
    print(f"   - Modificações: {len(modificacoes_mock)} alterações\n")

    # =============================================================================
    # MOCK: Simular resposta do Directus para tags do modelo
    # =============================================================================

    tags_modelo_mock = {
        "data": [
            {
                "id": "tag-1-id",
                "tag_nome": "1",
                "posicao_inicio_texto": modelo_texto.find("{{1}}"),
                "posicao_fim_texto": modelo_texto.find("{{/1}}") + len("{{/1}}"),
                "clausulas": [
                    {
                        "id": "clausula-1-uuid",
                        "numero": "1",
                        "nome": "DO OBJETO",
                    }
                ],
            },
            {
                "id": "tag-2-id",
                "tag_nome": "2",
                "posicao_inicio_texto": modelo_texto.find("{{2}}"),
                "posicao_fim_texto": modelo_texto.find("{{/2}}") + len("{{/2}}"),
                "clausulas": [
                    {
                        "id": "clausula-2-uuid",
                        "numero": "2",
                        "nome": "DO VALOR",
                    }
                ],
            },
        ]
    }

    # =============================================================================
    # MOCK: Simular funções que fazem requisições externas
    # =============================================================================

    with patch("directus_server.requests.get") as mock_get:
        # Configurar mock de GET para buscar tags do modelo
        mock_response_tags = Mock()
        mock_response_tags.status_code = 200
        mock_response_tags.json.return_value = tags_modelo_mock
        mock_get.return_value = mock_response_tags

        # Criar instância da API
        api = DirectusAPI()

        # Simular passagem direta de dados (sem baixar arquivos)
        # Chamar DIRETAMENTE _vincular_modificacoes_clausulas
        print("🔗 EXECUTANDO VINCULAÇÃO:\n")

        resultado = api._vincular_modificacoes_clausulas(
            modificacoes=modificacoes_mock,
            tags_modelo=tags_modelo_mock["data"],
            texto_com_tags=modelo_texto,
            texto_original=None,  # Vai usar texto_com_tags como fallback
            texto_modificado=None,
        )

        # =============================================================================
        # VERIFICAÇÃO: Analisar resultados
        # =============================================================================

        print("=" * 80)
        print("📊 RESULTADOS DA VINCULAÇÃO COM MOCK")
        print("=" * 80 + "\n")

        vinculadas = 0
        for mod in resultado:
            mod_id = mod.get("id")
            clausula_id = mod.get("clausula_id")
            clausula_numero = mod.get("clausula_numero")
            tag_nome = mod.get("tag_nome")
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")

            if clausula_id:
                vinculadas += 1
                status = "✅"
                print(
                    f"{status} Mod #{mod_id}:"
                    f"\n   Tag: {tag_nome}"
                    f"\n   Cláusula: {clausula_numero} ({clausula_id})"
                    f"\n   Posição: {pos_inicio}-{pos_fim}"
                )
            else:
                status = "⚠️ "
                print(
                    f"{status} Mod #{mod_id}: SEM VINCULAÇÃO"
                    f"\n   Tag: {tag_nome or 'N/A'}"
                )

        print(
            f"\n📈 RESUMO FINAL: {vinculadas}/{len(modificacoes_mock)} modificações vinculadas"
        )

        # =============================================================================
        # VALIDAÇÕES
        # =============================================================================

        print("\n" + "=" * 80)
        print("✔️  VALIDAÇÕES")
        print("=" * 80 + "\n")

        # Validar que todas as modificações foram vinculadas
        assert vinculadas == len(modificacoes_mock), (
            f"Esperado {len(modificacoes_mock)} vinculações, obteve {vinculadas}"
        )
        print(f"✅ Todas as {len(modificacoes_mock)} modificações foram vinculadas")

        # Validar que modificação 1 foi vinculada à cláusula 1
        mod_1 = next(m for m in resultado if m["id"] == 1)
        assert mod_1.get("clausula_numero") == "1", "Mod 1 deveria estar na cláusula 1"
        assert mod_1.get("clausula_id") == "clausula-1-uuid"
        print("✅ Modificação 1 vinculada corretamente à Cláusula 1")

        # Validar que modificação 2 foi vinculada à cláusula 2
        mod_2 = next(m for m in resultado if m["id"] == 2)
        assert mod_2.get("clausula_numero") == "2", "Mod 2 deveria estar na cláusula 2"
        assert mod_2.get("clausula_id") == "clausula-2-uuid"
        print("✅ Modificação 2 vinculada corretamente à Cláusula 2")

        # Validar que posições foram atribuídas
        assert mod_1.get("posicao_inicio") is not None, "Mod 1 deve ter posição início"
        assert mod_1.get("posicao_fim") is not None, "Mod 1 deve ter posição fim"
        print("✅ Posições foram atribuídas corretamente")

        # Validar que normalização funcionou (textos com formatações diferentes foram encontrados)
        print(
            "✅ Normalização de espaços funcionou (formatações diferentes encontradas)"
        )

        print("\n" + "=" * 80)
        print("🎉 TESTE COM MOCKS PASSOU COM SUCESSO!")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n🚀 Executando testes de vinculação com formatação...\n")

    try:
        test_vinculacao_com_formatacao_variada()
        print("✅ Teste 1 passou!\n")
    except AssertionError as e:
        print(f"❌ Teste 1 falhou: {e}\n")
    except Exception as e:
        print(f"💥 Teste 1 erro: {e}\n")

    try:
        test_vinculacao_com_normalizacao()
        print("✅ Teste 2 passou!\n")
    except Exception as e:
        print(f"💥 Teste 2 erro: {e}\n")

    try:
        test_vinculacao_com_mock_completo()
        print("✅ Teste 3 (com mocks) passou!\n")
    except AssertionError as e:
        print(f"❌ Teste 3 falhou: {e}\n")
    except Exception as e:
        print(f"💥 Teste 3 erro: {e}\n")

    print("🏁 Testes concluídos!\n")
