"""
Testes da Fase 1: Fundação
Valida estruturas de dados, normalização e similaridade
"""

import os
import sys

# Adicionar o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from directus_server import (
    ResultadoVinculacao,
    TagMapeada,
    calcular_similaridade,
    normalizar_texto,
)


def test_normalizacao_consistente():
    """Testa se a normalização é consistente em diferentes formatos."""
    print("🧪 Teste 1: Normalização consistente")

    # Mesmo texto com diferentes formatações
    texto1 = "O  contratante\t\tpagará\no valor   acordado"
    texto2 = "O contratante pagará o valor acordado"
    texto3 = (
        "O\u00a0contratante\u2000pagará\no\u00a0valor   acordado"  # nbsp e thin space
    )

    norm1 = normalizar_texto(texto1)
    norm2 = normalizar_texto(texto2)
    norm3 = normalizar_texto(texto3)

    print(f"   Texto 1: '{texto1[:40]}...' → '{norm1}'")
    print(f"   Texto 2: '{texto2}' → '{norm2}'")
    print(f"   Texto 3 (com nbsp): → '{norm3}'")

    assert norm1 == norm2 == norm3, (
        f"Normalizações diferentes: {norm1} != {norm2} != {norm3}"
    )
    assert norm1 == "O contratante pagará o valor acordado"

    print("   ✅ Normalização consistente!")


def test_similaridade_threshold():
    """Testa o cálculo de similaridade com diferentes níveis."""
    print("\n🧪 Teste 2: Cálculo de similaridade")

    # Textos idênticos
    texto_a = "Este é um contrato de prestação de serviços"
    texto_b = "Este é um contrato de prestação de serviços"
    sim_identicos = calcular_similaridade(texto_a, texto_b)
    print(f"   Textos idênticos: {sim_identicos:.3f}")
    assert sim_identicos == 1.0, f"Esperado 1.0, obteve {sim_identicos}"

    # Textos muito similares (apenas capitalização diferente)
    texto_c = "Este é um contrato de prestação de serviços"
    texto_d = "este é um contrato de prestação de serviços"
    sim_similar = calcular_similaridade(texto_c, texto_d)
    print(f"   Textos similares (case): {sim_similar:.3f}")
    assert sim_similar > 0.95, f"Esperado >0.95, obteve {sim_similar}"

    # Textos diferentes
    texto_e = "Este é um contrato de prestação de serviços"
    texto_f = "Documento completamente diferente sobre outro assunto"
    sim_diferentes = calcular_similaridade(texto_e, texto_f)
    print(f"   Textos diferentes: {sim_diferentes:.3f}")
    assert sim_diferentes < 0.5, f"Esperado <0.5, obteve {sim_diferentes}"

    print("   ✅ Cálculos de similaridade corretos!")


def test_estruturas_dados():
    """Testa as estruturas de dados TagMapeada e ResultadoVinculacao."""
    print("\n🧪 Teste 3: Estruturas de dados")

    # Criar TagMapeada
    tag = TagMapeada(
        tag_id="tag-1",
        tag_nome="1.1",
        posicao_inicio_original=0,
        posicao_fim_original=100,
        clausulas=[{"id": "clausula-1", "numero": "1.1"}],
        score_inferencia=1.0,
        metodo="offset",
    )
    print(
        f"   TagMapeada criada: {tag.tag_nome} [{tag.posicao_inicio_original}-{tag.posicao_fim_original}]"
    )
    assert tag.score_inferencia == 1.0
    assert tag.metodo == "offset"

    # Criar ResultadoVinculacao
    resultado = ResultadoVinculacao()

    # Adicionar vinculações
    mod1 = {"id": 1, "tipo": "modificacao"}
    mod2 = {"id": 2, "tipo": "adicao"}
    mod3 = {"id": 3, "tipo": "remocao"}

    resultado.vinculadas.append((mod1, "clausula-1", 0.95))
    resultado.vinculadas.append((mod2, "clausula-2", 0.85))
    resultado.nao_vinculadas.append(mod3)

    print(
        f"   ResultadoVinculacao: {len(resultado.vinculadas)} vinculadas, {len(resultado.nao_vinculadas)} não vinculadas"
    )

    # Testar métodos
    taxa_sucesso = resultado.taxa_sucesso()
    taxa_cobertura = resultado.taxa_cobertura()
    print(f"   Taxa de sucesso: {taxa_sucesso:.1%}")
    print(f"   Taxa de cobertura: {taxa_cobertura:.1%}")

    assert taxa_sucesso == 2 / 3, f"Esperado 0.666, obteve {taxa_sucesso}"
    assert taxa_cobertura == 2 / 3, f"Esperado 0.666, obteve {taxa_cobertura}"

    print("   ✅ Estruturas de dados funcionando corretamente!")


def test_normalizacao_unicode():
    """Testa normalização de caracteres Unicode (acentos)."""
    print("\n🧪 Teste 4: Normalização Unicode")

    # é pode ser representado de duas formas:
    # U+00E9 (único) ou U+0065 + U+0301 (e + acento combinante)
    texto_nfc = "José"  # NFC (forma composta)
    texto_nfd = "Jose\u0301"  # NFD (forma decomposta)

    norm_nfc = normalizar_texto(texto_nfc)
    norm_nfd = normalizar_texto(texto_nfd)

    print(f"   Texto NFC: '{texto_nfc}' → '{norm_nfc}'")
    print(f"   Texto NFD: '{texto_nfd}' → '{norm_nfd}'")

    assert norm_nfc == norm_nfd, (
        f"Unicode normalization falhou: '{norm_nfc}' != '{norm_nfd}'"
    )
    print("   ✅ Normalização Unicode correta!")


if __name__ == "__main__":
    print("=" * 70)
    print("FASE 1: TESTES DE FUNDAÇÃO")
    print("=" * 70)

    try:
        test_normalizacao_consistente()
        test_similaridade_threshold()
        test_estruturas_dados()
        test_normalizacao_unicode()

        print("\n" + "=" * 70)
        print("✅ FASE 1 COMPLETA: Todos os testes passaram!")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n❌ Teste falhou: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
