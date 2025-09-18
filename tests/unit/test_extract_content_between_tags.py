#!/usr/bin/env python3
"""
Testes para extração de conteúdo entre tags - segunda ocorrência como fechamento
Testa o padrão: {{tag}} conteúdo {{tag}} (sem barra de fechamento)
"""

import os
import sys

# Adicionar o diretório raiz ao path para importar o processador
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.docx_compare.processors.processador_modelo_contrato import (
    extract_content_between_tags,
)


def test_extract_content_segunda_ocorrencia_simples():
    """Testa tag simples com segunda ocorrência como fechamento"""
    texto = "Início {{nome}} João Silva {{nome}} fim do documento"
    result = extract_content_between_tags(texto)

    expected = {"nome": "João Silva"}
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_segunda_ocorrencia_multiplas():
    """Testa múltiplas tags com segunda ocorrência como fechamento"""
    texto = "{{cargo}} Diretor {{cargo}} da empresa {{empresa}} ACME Corp {{empresa}}"
    result = extract_content_between_tags(texto)

    expected = {"cargo": "Diretor", "empresa": "ACME Corp"}
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_mix_padroes():
    """Testa mix de padrões - deve priorizar fechamento explícito"""
    texto = "{{secao}} Conteúdo da seção {{/secao}} e {{item}} Item importante {{item}}"
    result = extract_content_between_tags(texto)

    expected = {"secao": "Conteúdo da seção", "item": "Item importante"}
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_conteudo_complexo():
    """Testa tag com conteúdo mais complexo"""
    texto = """{{clausula}}
    Esta é uma cláusula muito importante que contém
    múltiplas linhas e deve ser capturada corretamente
    {{clausula}}"""
    result = extract_content_between_tags(texto)

    # Verificar se capturou o conteúdo (normalizado)
    assert "clausula" in result, "Tag 'clausula' deveria estar presente"
    assert "múltiplas linhas" in result["clausula"], (
        "Conteúdo deveria incluir 'múltiplas linhas'"
    )


def test_extract_content_tags_numericas():
    """Testa tags numéricas com segunda ocorrência"""
    texto = "{{1}} Primeira cláusula do contrato {{1}} seguida de {{2.1}} subcláusula importante {{2.1}}"
    result = extract_content_between_tags(texto)

    expected = {"1": "Primeira cláusula do contrato", "2.1": "subcláusula importante"}
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_tres_ocorrencias():
    """Testa três ocorrências da mesma tag (deve usar primeira e segunda)"""
    texto = "{{tag}} primeiro {{tag}} meio {{tag}} final"
    result = extract_content_between_tags(texto)

    expected = {"tag": "primeiro"}  # Deve capturar entre primeira e segunda
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_tag_vazia():
    """Testa tag vazia (sem conteúdo entre elas)"""
    texto = "{{vazia}}{{vazia}}"
    result = extract_content_between_tags(texto)

    # Deve retornar vazio ou não incluir a tag
    expected = {}
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_tag_sozinha():
    """Testa apenas uma ocorrência (não deve capturar por segunda ocorrência)"""
    texto = "Texto com {{sozinha}} apenas uma tag"
    result = extract_content_between_tags(texto)

    expected = {}  # Não deve capturar nada
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_tag_com_espacos():
    """Testa tags com espaços ao redor do conteúdo"""
    texto = "{{espaco}}   conteúdo com espaços   {{espaco}}"
    result = extract_content_between_tags(texto)

    # Deve normalizar e remover espaços extras
    assert "espaco" in result
    assert "conteúdo com espaços" in result["espaco"]


def test_extract_content_tag_com_html():
    """Testa tags com conteúdo HTML que deve ser limpo"""
    texto = "{{html}} <p>Parágrafo com <strong>negrito</strong></p> {{html}}"
    result = extract_content_between_tags(texto)

    # Deve remover tags HTML
    assert "html" in result
    content = result["html"]
    assert "<p>" not in content
    assert "<strong>" not in content
    assert "Parágrafo com negrito" in content


def test_extract_content_tag_com_hifen_fechamento_explicito():
    """Testa padrão {{TAG-XXXX}} conteudo {{/TAG-XXXX}} com fechamento explícito"""
    texto = "{{TAG-001}} Este é o conteúdo da tag 001 {{/TAG-001}}"
    result = extract_content_between_tags(texto)

    # A função remove o prefixo TAG- e usa apenas a parte numérica
    expected = {"001": "Este é o conteúdo da tag 001"}
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_multiplas_tags_hifen():
    """Testa múltiplas tags com hífen e fechamento explícito"""
    texto = "{{TAG-001}} Primeiro conteúdo {{/TAG-001}} e {{TAG-002}} Segundo conteúdo {{/TAG-002}}"
    result = extract_content_between_tags(texto)

    # A função remove o prefixo TAG- e usa apenas a parte numérica
    expected = {"001": "Primeiro conteúdo", "002": "Segundo conteúdo"}
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_tag_hifen_numerica_complexa():
    """Testa tags com hífen e numeração complexa - apenas TAG- é suportado pelo padrão atual"""
    texto = "{{TAG-12.3}} Tag doze ponto três do contrato {{/TAG-12.3}}"
    result = extract_content_between_tags(texto)

    # A função remove o prefixo TAG- e usa apenas a parte numérica
    expected = {"12.3": "Tag doze ponto três do contrato"}
    assert result == expected, f"Esperado {expected}, obtido {result}"


def test_extract_content_tag_clause_nao_suportado():
    """Testa que CLAUSE- não é suportado pelo padrão atual (apenas TAG- é aceito)"""
    texto = "{{CLAUSE-12.3}} Cláusula doze ponto três do contrato {{/CLAUSE-12.3}}"
    result = extract_content_between_tags(texto)

    # CLAUSE- não é reconhecido pelo padrão regex atual
    expected = {}
    assert result == expected, f"CLAUSE- não deveria ser reconhecido. Obtido {result}"


def test_extract_content_mix_hifen_e_segunda_ocorrencia():
    """Testa mix de tags com hífen (fechamento explícito) e segunda ocorrência"""
    texto = "{{TAG-001}} Conteúdo explícito {{/TAG-001}} e {{simples}} Conteúdo segunda ocorrência {{simples}}"
    result = extract_content_between_tags(texto)

    # A função remove o prefixo TAG- para a primeira tag
    expected = {"001": "Conteúdo explícito", "simples": "Conteúdo segunda ocorrência"}
    assert result == expected, f"Esperado {expected}, obtido {result}"
