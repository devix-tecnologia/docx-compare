"""
Fixture para teste de regressão - Contrato 86035523-977b-42cf-adda-6fd364170aa9
Baseado no teste A/B realizado em 2026-05-28 que identificou problema de detecção.

Problema identificado:
- Sistema detectou apenas 10 modificações (todas INSERCAO)
- IA detectou 44 modificações (mix de ALTERACAO + INSERCAO)
- Concordância: apenas 22.73%

Este contrato deve ser usado como baseline para validar melhorias na detecção
de modificações dentro de cláusulas existentes (não apenas inserções de blocos).

Relacionado à Task #016.
"""

# Metadados do contrato
CONTRATO_ID = "86035523-977b-42cf-adda-6fd364170aa9"
VERSAO_ID = "8d8e89a8-ba89-4e0e-846c-43e7ad058309"
MODELO_ID = "48b43d38-76b4-47a2-93a4-4216ad57defc"

CONTRATO_TITULO = "Teste - Esse vai!"
CONTRATO_NUMERO = "N0159"
MODELO_NOME = "Contrato de prestação de serviço - Rotina"
TOTAL_TAGS_MODELO = 294

# Métricas do sistema ANTES da correção (baseline)
METRICAS_SISTEMA_ANTES = {
    "total_modificacoes": 10,
    "por_categoria": {
        "INSERCAO": 10,  # 100%
        "ALTERACAO": 0,  # 0%
        "REMOCAO": 0,  # 0%
    },
    "vinculacoes_automaticas": 10,
    "vinculacoes_manuais": 0,
}

# Métricas da IA (ground truth aproximado)
METRICAS_IA_REFERENCIA = {
    "total_modificacoes": 44,
    "por_categoria": {
        "INSERCAO": 10,  # ~23%
        "ALTERACAO": 34,  # ~77%
        "REMOCAO": 0,  # 0%
    },
}

# Métricas esperadas APÓS correção
METRICAS_ESPERADAS_POS_CORRECAO = {
    "total_modificacoes_minimo": 40,  # Deve detectar pelo menos 40 (90% do que IA detectou)
    "alteracoes_minimo": 30,  # Pelo menos 30 alterações (não apenas inserções)
    "concordancia_com_ia_minimo": 80.0,  # Concordância > 80%
    "taxa_insercao_maximo": 30.0,  # No máximo 30% de INSERCAO (não 100%)
    "taxa_alteracao_minimo": 60.0,  # Pelo menos 60% de ALTERACAO
}

# Modificações detectadas pelo SISTEMA (antes da correção)
# Todas categorizadas como INSERCAO
MODIFICACOES_SISTEMA_ANTES = [
    {
        "id": "09ebfea3-764b-4c5b-89de-70b9b7eec429",
        "categoria": "INSERCAO",
        "alteracao": "A subcontratação do OBJETO pela CONTRATADA, ou de parte dele, sem a prévia autorização ou sem a não objeção da CONTRATANTE será considerada inadimplemento contratual e permitirá à CONTRATANTE, a seu exclusivo critério: (i) solicitar a imediata paralisação do objeto; (ii) exigir a desmobilização imediata da(s) subcontratada(s); (iii) exigir a substituição da(s) subcontratada(s), sem prejuízo das penalidades cabíveis.",
        "clausula_id": "9f045cd2-d59e-4beb-bfbc-bda62e9efdfa",
        "posicao_inicio": 121881,
        "posicao_fim": 122300,
    },
    {
        "id": "0ad972ff-6482-449b-bb13-ced4030e5d0f",
        "categoria": "INSERCAO",
        "alteracao": "As estipulações e obrigações constantes da presente cláusula não serão aplicadas a qualquer informação que: (i) seja de domínio público; (ii) já esteja em poder da CONTRATADA como resultado de sua própria pesquisa ou desenvolvimento; (iii) tenha sido legitimamente recebida de terceiros sem violação de dever de confidencialidade; ou (iv) deva ser divulgada por ordem legal, regulatória, judicial ou arbitral, hipótese em que a outra PARTE deverá ser previamente comunicada, quando permitido.",
        "clausula_id": "802057b6-5411-4a40-b37c-1e384e2de600",
        "posicao_inicio": 125518,
        "posicao_fim": 126010,
    },
    {
        "id": "23a3f162-a1b2-4545-a23f-d213de6e4403",
        "categoria": "INSERCAO",
        "alteracao": "A CONTRATADA deverá providenciar para que não haja qualquer parada ou atraso injustificado na execução dos Serviços e, se ocorrer a indisponibilidade de qualquer Serviço ou recurso por motivo sob sua responsabilidade, compromete-se a buscar os meios necessários ao seu restabelecimento, sem ônus adicional à CONTRATANTE.",
        "clausula_id": "49c6db5b-e56e-41c6-b2e3-fc31f08c548a",
        "posicao_inicio": 113851,
        "posicao_fim": 114171,
    },
    {
        "id": "32c94a11-b48d-4cfd-aba7-586913973a70",
        "categoria": "INSERCAO",
        "alteracao": "As PARTES não poderão prestar informações a terceiros nem divulgar quaisquer dados, informações relacionadas ao CONTRATO, ou o CONTRATO em si, ANEXOS e eventuais aditivos, sem autorização prévia e por escrito da outra PARTE, exceto a seus consultores, auditores, seguradoras, financiadores e assessores profissionais, desde que sujeitos a deveres de confidencialidade compatíveis.",
        "clausula_id": "802057b6-5411-4a40-b37c-1e384e2de600",
        "posicao_inicio": 124777,
        "posicao_fim": 125157,
    },
    {
        "id": "3cc40510-3d64-4789-a82a-0f3451d566aa",
        "categoria": "INSERCAO",
        "alteracao": "Eventuais limitações de responsabilidade contidas neste CONTRATO não se aplicam a dolo, fraude, violação de confidencialidade, infrações anticorrupção, danos ambientais, danos à vida ou à integridade física, coberturas securitárias e/ou eventual direito de regresso da(s) seguradora(s) das PARTES.",
        "clausula_id": "49c6db5b-e56e-41c6-b2e3-fc31f08c548a",
        "posicao_inicio": 113654,
        "posicao_fim": 113951,
    },
    # Mais 5 inserções...
]

# Exemplos de modificações detectadas pela IA que o SISTEMA NÃO detectou
# Estas deveriam ser detectadas após a correção
MODIFICACOES_IA_NAO_DETECTADAS_SISTEMA = [
    {
        "id_sequencial": 1,
        "tipo": "ALTERACAO",
        "tag_relacionada_nome": "1.1",
        "conteudo_original": "A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no campo Serviços do QUADRO RESUMO, os quais serão prestados conforme disciplinado neste CONTRATO.",
        "conteudo": "A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no campo Serviços do QUADRO RESUMO, os quais serão prestados conforme disciplinado neste CONTRATO e nas ordens de serviço emitidas pela CONTRATANTE, admitindo-se ajustes operacionais de escopo por comunicação escrita do Gestor do Contrato, desde que não impliquem alteração substancial do objeto.",
        "contexto": "Adiciona flexibilidade para ajustes operacionais através de ordens de serviço",
        "nivel_impacto": "alto",
    },
    {
        "id_sequencial": 2,
        "tipo": "ALTERACAO",
        "tag_relacionada_nome": "1.2",
        "conteudo_original": "Este CONTRATO não implica em nenhum dever de exclusividade da CONTRATANTE, que poderá firmar contratos com outras empresas para os mesmos fins, de acordo com seus interesses.",
        "conteudo": "Este CONTRATO não implica dever de exclusividade da CONTRATANTE, ressalvado que, durante a vigência contratual, a CONTRATANTE deverá preferencialmente consultar a CONTRATADA antes de contratar terceiros para escopo idêntico no mesmo LOCAL DE PRESTAÇÃO DOS SERVIÇOS.",
        "contexto": "Adiciona obrigação de consulta prévia à CONTRATADA",
        "nivel_impacto": "alto",
    },
    {
        "id_sequencial": 4,
        "tipo": "ALTERACAO",
        "tag_relacionada_nome": "2.5",
        "conteudo_original": "O CONTRATO poderá ser suspenso total ou parcialmente, independente da anuência da CONTRATADA e/ou de procedimento judicial, mediante comunicação por escrito da CONTRATANTE à CONTRATADA enviada com antecedência mínima de 30 (trinta) DIAS, salvo se, por determinação do Poder Público ou Judiciário, for previsto menor prazo.",
        "conteudo": "O CONTRATO poderá ser suspenso total ou parcialmente, mediante comunicação por escrito da CONTRATANTE à CONTRATADA enviada com antecedência mínima de 15 (quinze) DIAS, salvo urgência operacional, determinação do Poder Público ou decisão judicial, hipótese em que a suspensão poderá produzir efeitos imediatos.",
        "contexto": "Reduz prazo de aviso de suspensão de 30 para 15 dias",
        "nivel_impacto": "alto",
    },
    # ... mais 31 alterações não detectadas
]

# Links úteis
LINKS = {
    "contrato_directus": f"https://contract.devix.co/admin/content/contrato/{CONTRATO_ID}",
    "versao_directus": f"https://contract.devix.co/admin/content/versao/{VERSAO_ID}",
    "modelo_directus": f"https://contract.devix.co/admin/content/modelo_contrato/{MODELO_ID}",
    "teste_ab_completo": "/versiona-ai/teste_ab_output/teste_ab_completo_20260528_164219.json",
    "resultado_ia": "/versiona-ai/teste_ab_output/resultado_ia_8d8e89a8.json",
}


def validar_metricas_pos_correcao(resultado_processamento: dict) -> dict:
    """
    Valida se o resultado do processamento atende às métricas esperadas
    após a correção do problema identificado na Task #016.

    Args:
        resultado_processamento: Resultado do processamento da versão

    Returns:
        Dict com validações e erros (se houver)
    """
    erros = []
    alertas = []

    total_mods = len(resultado_processamento.get("modificacoes", []))
    if total_mods < METRICAS_ESPERADAS_POS_CORRECAO["total_modificacoes_minimo"]:
        erros.append(
            f"Total de modificações ({total_mods}) abaixo do mínimo esperado "
            f"({METRICAS_ESPERADAS_POS_CORRECAO['total_modificacoes_minimo']})"
        )

    # Contar categorias
    categorias = {}
    for mod in resultado_processamento.get("modificacoes", []):
        cat = mod.get("categoria", "DESCONHECIDA")
        categorias[cat] = categorias.get(cat, 0) + 1

    total_alteracoes = categorias.get("ALTERACAO", 0)
    if total_alteracoes < METRICAS_ESPERADAS_POS_CORRECAO["alteracoes_minimo"]:
        erros.append(
            f"Total de ALTERACAO ({total_alteracoes}) abaixo do mínimo esperado "
            f"({METRICAS_ESPERADAS_POS_CORRECAO['alteracoes_minimo']})"
        )

    # Calcular percentuais
    if total_mods > 0:
        taxa_insercao = (categorias.get("INSERCAO", 0) / total_mods) * 100
        taxa_alteracao = (categorias.get("ALTERACAO", 0) / total_mods) * 100

        if taxa_insercao > METRICAS_ESPERADAS_POS_CORRECAO["taxa_insercao_maximo"]:
            alertas.append(
                f"Taxa de INSERCAO ({taxa_insercao:.1f}%) acima do máximo esperado "
                f"({METRICAS_ESPERADAS_POS_CORRECAO['taxa_insercao_maximo']}%)"
            )

        if taxa_alteracao < METRICAS_ESPERADAS_POS_CORRECAO["taxa_alteracao_minimo"]:
            erros.append(
                f"Taxa de ALTERACAO ({taxa_alteracao:.1f}%) abaixo do mínimo esperado "
                f"({METRICAS_ESPERADAS_POS_CORRECAO['taxa_alteracao_minimo']}%)"
            )

    return {
        "valido": len(erros) == 0,
        "erros": erros,
        "alertas": alertas,
        "metricas_obtidas": {
            "total_modificacoes": total_mods,
            "por_categoria": categorias,
            "taxa_alteracao": taxa_alteracao if total_mods > 0 else 0,
            "taxa_insercao": taxa_insercao if total_mods > 0 else 0,
        },
    }
