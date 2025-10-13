"""
Teste de taxa de sucesso em cenário realista de produção.

Valida que ambas estratégias encontram > 90% das cláusulas.
"""

import sys
from pathlib import Path

import pytest

# Adiciona versiona-ai ao path
versiona_ai_path = Path(__file__).parent.parent / "versiona-ai"
sys.path.insert(0, str(versiona_ai_path))

from matching import DifflibMatcher, RapidFuzzMatcher  # noqa: E402


def create_contract_document() -> str:
    """Cria documento de contrato realista."""
    return """
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS PROFISSIONAIS

    Entre as partes qualificadas, firmam o presente contrato.

    CLÁUSULA PRIMEIRA - DO OBJETO
    O presente contrato tem como objeto a prestação de serviços técnicos
    especializados em tecnologia da informação.

    1.1 - Desenvolvimento de software sob demanda
    1.2 - Consultoria técnica especializada
    1.3 - Manutenção e suporte de sistemas

    CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DA CONTRATADA
    Compete à CONTRATADA executar os serviços com qualidade.

    2.1 - Alocar profissionais qualificados
    2.2 - Fornecer relatórios periódicos
    2.3 - Manter sigilo das informações

    CLÁUSULA TERCEIRA - DO PRAZO E VIGÊNCIA
    O prazo de vigência será de 24 meses, renovável.

    3.1 - Início da vigência na data da assinatura
    3.2 - Renovação automática por igual período
    3.3 - Rescisão mediante aviso prévio de 90 dias

    CLÁUSULA QUARTA - DOS VALORES E PAGAMENTOS
    Os valores serão pagos mensalmente.

    4.1 - Valor mensal de R$ 50.000,00
    4.2 - Pagamento até o 5º dia útil
    4.3 - Reajuste anual pelo IPCA

    CLÁUSULA QUINTA - DAS RESPONSABILIDADES
    As partes respondem pelos seus atos.

    5.1 - CONTRATADA responde por danos causados
    5.2 - CONTRATANTE fornecerá infraestrutura
    5.3 - Seguro obrigatório de responsabilidade civil

    CLÁUSULA SEXTA - DA PROPRIEDADE INTELECTUAL
    Os direitos autorais pertencem à CONTRATANTE.

    6.1 - Código fonte é propriedade da CONTRATANTE
    6.2 - Licenças de terceiros conforme acordado
    6.3 - Documentação técnica incluída

    CLÁUSULA SÉTIMA - DA CONFIDENCIALIDADE
    As informações são confidenciais.

    7.1 - Sigilo de informações comerciais
    7.2 - Proteção de dados pessoais (LGPD)
    7.3 - Acordo de confidencialidade permanente

    CLÁUSULA OITAVA - DAS PENALIDADES
    O descumprimento acarreta penalidades.

    8.1 - Multa de 10% sobre o valor mensal
    8.2 - Indenização por perdas e danos
    8.3 - Rescisão por justa causa

    CLÁUSULA NONA - DA RESCISÃO
    O contrato pode ser rescindido.

    9.1 - Rescisão imotivada com aviso prévio
    9.2 - Rescisão motivada sem aviso
    9.3 - Efeitos da rescisão

    CLÁUSULA DÉCIMA - DO FORO
    Fica eleito o foro da comarca de Vitória-ES.

    10.1 - Renúncia a qualquer outro foro
    10.2 - Mediação prévia obrigatória
    10.3 - Arbitragem como alternativa
    """


def create_modified_document() -> str:
    """Cria documento modificado (como seria em produção)."""
    return """
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS PROFISSIONAIS - VERSÃO MODIFICADA

    Entre as partes qualificadas, firmam o presente contrato revisado.

    CLÁUSULA PRIMEIRA - DO OBJETO E ESCOPO
    O presente contrato tem como objetivo a prestação de serviços tecnicos
    especializados em tecnologia da informaçao e inovação digital.

    1.1 - Desenvolvimento de software sob demanda e customizado
    1.2 - Consultoria tecnica especializada em arquitetura
    1.3 - Manutençao e suporte continuado de sistemas

    CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES E RESPONSABILIDADES DA CONTRATADA
    Compete a CONTRATADA executar os servicos com qualidade e eficiencia.

    2.1 - Alocar profissionais qualificados e certificados
    2.2 - Fornecer relatorios periodicos de acompanhamento
    2.3 - Manter sigilo absoluto das informacoes confidenciais

    CLÁUSULA TERCEIRA - DO PRAZO, VIGÊNCIA E RENOVAÇÃO
    O prazo de vigencia sera de 24 meses, renovavel automaticamente.

    3.1 - Inicio da vigencia na data da assinatura do instrumento
    3.2 - Renovacao automatica por igual periodo subsequente
    3.3 - Rescisao mediante aviso previo de 90 dias corridos

    CLÁUSULA QUARTA - DOS VALORES, PAGAMENTOS E REAJUSTES
    Os valores serao pagos mensalmente conforme cronograma.

    4.1 - Valor mensal fixo de R$ 50.000,00 (cinquenta mil reais)
    4.2 - Pagamento ate o 5 dia util do mes subsequente
    4.3 - Reajuste anual pelo indice IPCA acumulado

    CLÁUSULA QUINTA - DAS RESPONSABILIDADES E OBRIGAÇÕES
    As partes respondem integralmente pelos seus atos e omissões.

    5.1 - CONTRATADA responde por danos materiais causados
    5.2 - CONTRATANTE fornecera toda infraestrutura necessaria
    5.3 - Seguro obrigatorio de responsabilidade civil profissional

    CLÁUSULA SEXTA - DA PROPRIEDADE INTELECTUAL E DIREITOS AUTORAIS
    Os direitos autorais pertencem exclusivamente a CONTRATANTE.

    6.1 - Codigo fonte e propriedade plena da CONTRATANTE
    6.2 - Licencas de terceiros conforme previamente acordado
    6.3 - Documentacao tecnica completa esta incluida

    CLÁUSULA SÉTIMA - DA CONFIDENCIALIDADE E SIGILO
    As informacoes sao estritamente confidenciais.

    7.1 - Sigilo permanente de informacoes comerciais estrategicas
    7.2 - Protecao rigorosa de dados pessoais conforme LGPD
    7.3 - Acordo de confidencialidade com vigencia permanente

    CLÁUSULA OITAVA - DAS PENALIDADES E SANÇÕES
    O descumprimento contratual acarreta penalidades previstas.

    8.1 - Multa compensatoria de 10 porcento sobre o valor mensal
    8.2 - Indenizacao por perdas, danos e lucros cessantes
    8.3 - Rescisao unilateral por justa causa comprovada

    CLÁUSULA NONA - DA RESCISÃO E SEUS EFEITOS
    O contrato podera ser rescindido nas hipoteses previstas.

    9.1 - Rescisao imotivada com aviso previo de 90 dias
    9.2 - Rescisao motivada sem necessidade de aviso
    9.3 - Efeitos juridicos e financeiros da rescisao

    CLÁUSULA DÉCIMA - DO FORO E JURISDIÇÃO
    Fica eleito o foro da comarca de Vitoria no Estado do Espirito Santo.

    10.1 - Renuncia expressa a qualquer outro foro por mais privilegiado
    10.2 - Mediacao previa e obrigatoria antes de processo judicial
    10.3 - Arbitragem como alternativa de resolucao de conflitos
    """


def get_test_tags() -> list[dict]:
    """Retorna lista de tags para testar (30 tags)."""
    return [
        {"conteudo": "CLÁUSULA PRIMEIRA - DO OBJETO"},
        {"conteudo": "Desenvolvimento de software sob demanda"},
        {"conteudo": "Consultoria técnica especializada"},
        {"conteudo": "Manutenção e suporte de sistemas"},
        {"conteudo": "CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DA CONTRATADA"},
        {"conteudo": "Alocar profissionais qualificados"},
        {"conteudo": "Fornecer relatórios periódicos"},
        {"conteudo": "Manter sigilo das informações"},
        {"conteudo": "CLÁUSULA TERCEIRA - DO PRAZO E VIGÊNCIA"},
        {"conteudo": "Início da vigência na data da assinatura"},
        {"conteudo": "Renovação automática por igual período"},
        {"conteudo": "Rescisão mediante aviso prévio de 90 dias"},
        {"conteudo": "CLÁUSULA QUARTA - DOS VALORES E PAGAMENTOS"},
        {"conteudo": "Valor mensal de R$ 50.000,00"},
        {"conteudo": "Pagamento até o 5º dia útil"},
        {"conteudo": "Reajuste anual pelo IPCA"},
        {"conteudo": "CLÁUSULA QUINTA - DAS RESPONSABILIDADES"},
        {"conteudo": "CONTRATADA responde por danos causados"},
        {"conteudo": "CONTRATANTE fornecerá infraestrutura"},
        {"conteudo": "Seguro obrigatório de responsabilidade civil"},
        {"conteudo": "CLÁUSULA SEXTA - DA PROPRIEDADE INTELECTUAL"},
        {"conteudo": "Código fonte é propriedade da CONTRATANTE"},
        {"conteudo": "Licenças de terceiros conforme acordado"},
        {"conteudo": "CLÁUSULA SÉTIMA - DA CONFIDENCIALIDADE"},
        {"conteudo": "Sigilo de informações comerciais"},
        {"conteudo": "Proteção de dados pessoais (LGPD)"},
        {"conteudo": "CLÁUSULA OITAVA - DAS PENALIDADES"},
        {"conteudo": "Multa de 10% sobre o valor mensal"},
        {"conteudo": "CLÁUSULA NONA - DA RESCISÃO"},
        {"conteudo": "CLÁUSULA DÉCIMA - DO FORO"},
    ]


class TestSuccessRate:
    """Testes de taxa de sucesso em cenário realista."""

    @pytest.mark.parametrize("matcher_name", ["difflib", "rapidfuzz"])
    def test_success_rate_above_90_percent(self, matcher_name):
        """
        Valida que a taxa de sucesso é superior a 90%.

        Simula cenário de produção onde documento foi modificado
        (acentos removidos, palavras alteradas, etc).
        """
        # Cria documentos
        modified = create_modified_document()

        # Normaliza espaços
        modified_norm = " ".join(modified.split())

        # Obtém matcher
        matcher = DifflibMatcher() if matcher_name == "difflib" else RapidFuzzMatcher()

        # Busca todas as tags
        tags = get_test_tags()
        found_count = 0
        not_found = []

        print(f"\n{'=' * 70}")
        print(f"🔍 Testando {matcher.name.upper()} - {len(tags)} tags")
        print(f"{'=' * 70}")

        for tag in tags:
            content = " ".join(tag["conteudo"].split())
            # Threshold 0.68 para aceitar até tags muito modificadas
            # (similares ao cenário de produção)
            result = matcher.find_best_match(content, modified_norm, threshold=0.68)

            if result.found:
                found_count += 1
                status = "✓"
            else:
                not_found.append(tag["conteudo"])
                status = "✗"

            print(
                f"{status} {tag['conteudo'][:50]:50} | "
                f"Sim: {result.similarity * 100:5.1f}% | "
                f"Found: {result.found}"
            )

        success_rate = (found_count / len(tags)) * 100

        print(f"\n{'=' * 70}")
        print(f"📊 RESULTADO: {found_count}/{len(tags)} tags encontradas")
        print(f"   Taxa de sucesso: {success_rate:.1f}%")
        print(f"{'=' * 70}")

        if not_found:
            print(f"\n❌ Tags não encontradas ({len(not_found)}):")
            for tag in not_found:
                print(f"   - {tag}")

        # Valida taxa de sucesso > 90%
        assert success_rate >= 90.0, (
            f"Taxa de sucesso {success_rate:.1f}% está abaixo de 90%! "
            f"Encontradas: {found_count}/{len(tags)}"
        )

        print(f"\n✅ PASSOU: Taxa de sucesso {success_rate:.1f}% >= 90%\n")


if __name__ == "__main__":
    # Executa teste diretamente
    test = TestSuccessRate()

    print("\n" + "=" * 70)
    print("🎯 TESTE DE TAXA DE SUCESSO - CENÁRIO REALISTA")
    print("=" * 70)

    print("\n1️⃣ Testando Difflib...")
    test.test_success_rate_above_90_percent("difflib")

    print("\n2️⃣ Testando RapidFuzz...")
    test.test_success_rate_above_90_percent("rapidfuzz")

    print("\n" + "=" * 70)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70 + "\n")
