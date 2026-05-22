# Teste A/B: Análise de Contrato com IA vs Sistema Estruturado

## Contexto

Você é um sistema de análise jurídica que identifica modificações entre versões de contratos. Sua tarefa é comparar dois documentos e gerar uma lista estruturada de modificações, vinculando-as às cláusulas do modelo de contrato.

**IMPORTANTE**: O sistema estruturado já processou estes documentos e encontrou **7 modificações**. Sua análise será comparada com este resultado.

## Sua Tarefa

Analise as diferenças entre o documento do MODELO (template) e o documento da VERSÃO (modificado) e gere uma lista de modificações com a seguinte estrutura JSON:

```json
{
  "modificacoes": [
    {
      "id": "mod-001",
      "tipo": "adicao|remocao|alteracao",
      "conteudo_original": "texto do modelo que foi alterado/removido (null se adição)",
      "conteudo": "texto na versão (null se remoção)",
      "posicao_aprox": 150,
      "clausula_relacionada_id": "uuid ou null",
      "clausula_relacionada_nome": "nome da cláusula ou null",
      "contexto": "explicação da mudança",
      "nivel_impacto": "baixo|medio|alto",
      "confianca": "0-100%"
    }
  ],
  "resumo": {
    "total_adicoes": 0,
    "total_remocoes": 0,
    "total_alteracoes": 0,
    "clausulas_afetadas": [],
    "analise_qualitativa": "2-3 parágrafos sobre mudanças mais significativas"
  }
}
```

## Critérios de Qualidade

1. **Precisão**: Identifique TODAS as diferenças relevantes entre os textos
2. **Vinculação**: Use as posições das tags para associar modificações às cláusulas corretas
3. **Contexto**: Explique o significado jurídico/contratual de cada mudança
4. **Agrupamento**: Modificações próximas na mesma cláusula podem ser agrupadas
5. **Impacto**: Avalie se a mudança é cosmética (baixo), significativa (medio) ou crítica (alto)

## Regras Específicas

- Ignore diferenças de formatação pura (negrito, itálico, fonte)
- Ignore espaçamentos e quebras de linha se não mudarem o sentido
- Priorize mudanças em: valores monetários, datas, prazos, obrigações, responsabilidades
- Uma substituição de texto é uma "alteracao", não uma remoção + adição
- Compare os textos parágrafo por parágrafo usando os marcadores [P000], [P001], etc.

---

## DADOS DE ENTRADA

### 1. Modelo de Contrato - Informações

**ID do Modelo**: `d2699a57-b0ff-472b-a130-626f5fc2852b`
**Nome**: Contrato Devix
**Arquivo**: Contrato de teste - tag.docx

### 2. Tags/Cláusulas do Modelo

```json
[]
```

### 3. Documento do MODELO (Template Base)

```text
[P000] {{1}}
[P001] OBJETO
[P002] {{/1}}
[P003] {{1.1}}
[P004] 1.1 A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no campo Serviços do QUADRO RESUMO, os quais serão prestados conforme disciplinado neste CONTRATO.
[P005] {{/1.1}}
[P006] {{1.2}}
[P007] 1.2 Este CONTRATO não implica em nenhum dever de exclusividade da CONTRATANTE, que poderá firmar contratos com outras empresas para os mesmos fins, de acordo com seus interesses.
[P008] {{/1.2}}
[P009] {{1.3}}
[P010] 1.3 Os ANEXOS “Documentos Contratuais Gerais” ficam dispensados de rubrica ou validação digital posterior. A CONTRATADA declara que já recebeu estes ANEXOS previamente em mídia eletrônica ou outra forma de acesso, que tem ciência do seu conteúdo e que concorda com os termos neles contidos, comprometendo-se a cumpri-los na sua integralidade.
[P011] {{/1.3}}
[P012] {{1.4}}
[P013] 1.4 Os termos do QUADRO RESUMO prevalecem sobre os termos destas Condições Gerais os quais prevalecem sobre os termos dos ANEXOS. Na hipótese de conflitos entre os ANEXOS, prevalecerão uns sobre os outros na ordem em que se acham listados no QUADRO RESUMO acima.
[P014] {{/1.4}}
[P015] {{1.5}}
[P016] 1.5 A CONTRATADA, em nenhuma hipótese, poderá alegar, como justificativa ou defesa, o desconhecimento, incompreensão, dúvida, no todo ou em parte, das disposições do presente CONTRATO e demais disposições de ordem geral ou particular nele estabelecidas, que são, desde já, consideradas necessárias e suficientes para definir os Serviços e os fornecimentos contidos no que foi contratado, e, ainda, permitir a sua execução de acordo com as normas vigentes no País, sendo vedado à CONTRATADA pleitear qualquer revisão de preços ou prorrogação de prazo, por erros ou omissões, que tenham sido cometidos na elaboração de sua(s) Proposta(s) que integra(m) o CONTRATO.
[P017] {{/1.5}}
[P018] {{2}}
[P019] VIGÊNCIA E SUSPENSÃO
[P020] {{/2}}
[P021] {{2.1}}
[P022] 2.1 O CONTRATO terá vigência a partir do INÍCIO DA VIGÊNCIA e encerrará (i) após o TÉRMINO DA VIGÊNCIA indicado no QUADRO RESUMO, (ii) após o cumprimento de todas as obrigações do CONTRATO e/ou dele decorrentes ou (iii) no caso de atingido o valor estabelecido neste instrumento, o que ocorrer primeiro, independentemente de qualquer notificação judicial ou extrajudicial.
[P023] {{/2.1}}
[P024] {{2.2}}
[P025] 2.2. Se aplicável, a retroatividade dos efeitos do CONTRATO, não ocasionará qualquer prejuízo das obrigações da CONTRATADA sem acarretar quaisquer penalidades, compensação ou lucros cessantes para a CONTRATANTE, conforme prazo descrito no QUADRO RESUMO.
[P026] {{/2.2}}
[P027] {{2.3}}
[P028] 2.3 O PRAZO DE VIGÊNCIA já considera todos os dias necessários para as providências prévias e finais, incluindo eventual mobilização, execução e desmobilização, por parte da CONTRATADA.
[P029] {{/2.3}}
[P030] {{2.4}}
[P031] 2.4 O CONTRATO poderá ser suspenso total ou parcialmente, independente da anuência da CONTRATADA e/ou de procedimento judicial, mediante comunicação por escrito da CONTRATANTE à CONTRATADA enviada com antecedência mínima de 30 (trinta) DIAS, salvo se, por determinação do Poder Público ou Judiciário, for previsto menor prazo.
[P032] {{/2.4}}
```

### 4. Documento da VERSÃO (Com Modificações)

**ID da Versão**: `b93a6d72-764b-4f86-b716-20c8373faa56`
**Status**: concluido
**Origem**: fornecedor

```text
[P000] OBJETO
[P002] 1.1 A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no campo Serviços do ESCOPO INICIAL PREVISTO, os quais serão prestados conforme disciplinado neste CONTRATO.
[P004] 1.3 Os ANEXOS “Documentos Contratuais Gerais” ficam dispensados de rubrica ou validação digital posterior. A CONTRATADA declara que já recebeu estes ANEXOS previamente em mídia eletrônica ou outra forma de acesso, que tem ciência do seu conteúdo e que concorda com os termos neles contidos, comprometendo-se a cumpri-los na sua integralidade.
[P006] 1.4 Os termos do QUADRO RESUMO prevalecem sobre os termos destas Condições Gerais os quais prevalecem sobre os termos dos ANEXOS. Se houver conflito entre os ANEXOS, valerá o que estiver indicado primeiro no QUADRO RESUMO.
[P008] 1.5 A CONTRATADA, em nenhuma hipótese, poderá alegar, como justificativa ou defesa, o desconhecimento, incompreensão, dúvida, no todo ou em parte, das disposições do presente CONTRATO e demais disposições de ordem geral ou particular nele estabelecidas, que são, desde já, consideradas necessárias e suficientes para definir os Serviços e os fornecimentos contidos no que foi contratado, e, ainda, permitir a sua execução de acordo com as normas vigentes no País, sendo vedado à CONTRATADA pleitear qualquer revisão de preços ou prorrogação de prazo, por erros ou omissões, que tenham sido cometidos na elaboração de sua(s) Proposta(s) que integra(m) o CONTRATO. Na hipótese de conflitos entre os ANEXOS, prevalecerão uns sobre os outros na ordem em que se acham listados no QUADRO RESUMO acima.
[P010] VIGÊNCIA E SUSPENSÃO
[P012] 2.1 O CONTRATO terá vigência a partir do INÍCIO DA VIGÊNCIA e encerrará (i) após o TÉRMINO DA VIGÊNCIA indicado no QUADRO RESUMO, (ii) após o cumprimento de todas as obrigações do CONTRATO e/ou dele decorrentes ou (iii) no caso de atingido o valor estabelecido neste instrumento, o que ocorrer primeiro, independentemente de qualquer notificação judicial ou extrajudicial.
[P014] 2.2. SE APLICÁVEL, A RETROATIVIDADE DOS EFEITOS DO CONTRATO NÃO OCASIONARÁ QUALQUER PREJUÍZO DAS OBRIGAÇÕES DA CONTRATADA, SEM ACARRETAR QUAISQUER PENALIDADES, COMPENSAÇÃO OU LUCROS CESSANTES PARA A CONTRATANTE, CONFORME PRAZO DESCRITO NO QUADRO RESUMO.
[P016] 2.3 O PRAZO DE VIGÊNCIA já considera todos os dias necessários para as providências prévias e finais, incluindo eventual mobilização, execução e desmobilização, por parte da EMPRESA CONTRATADA.
[P018] 2.4 O CONTRATO poderá ser suspenso total ou parcialmente, independente da anuência da CONTRATADA e/ou de procedimento judicial, mediante comunicação por escrito da CONTRATANTE à CONTRATADA enviada com antecedência mínima de 30 (trinta) DIAS, salvo se, por determinação do Poder Público ou Judiciário, for previsto menor prazo.
[P020] 2.5Todas as obrigações tributárias principais e acessórias que incidam ou venham a incidir, direta ou indiretamente sobre os Serviços são de responsabilidade da CONTRATADA, que deverá, quando a legislação não exigir da CONTRATANTE a obrigação de retenção, comprovar o cumprimento de tais obrigações à CONTRATANTE.
```

---

## RESULTADO DO SISTEMA ESTRUTURADO (Para Comparação)

O sistema estruturado identificou **7 modificações**.

Resumo das modificações do sistema:
```json
[
  {
    "id": "0a36633c-4c55-441a-904f-90e56c913b91",
    "tipo": null,
    "posicao_inicio": 2001,
    "posicao_fim": 2101,
    "tem_conteudo": true,
    "tem_original": false
  },
  {
    "id": "317307e5-656a-4a0c-b789-78bf7076d3a1",
    "tipo": null,
    "posicao_inicio": 1974,
    "posicao_fim": 2227,
    "tem_conteudo": true,
    "tem_original": false
  },
  {
    "id": "9f70a58f-50c2-46ae-be60-bce5f3f6f3f6",
    "tipo": null,
    "posicao_inicio": 777,
    "posicao_fim": 1572,
    "tem_conteudo": true,
    "tem_original": false
  },
  {
    "id": "cce9a74d-d20b-4281-8293-b0cc85df242b",
    "tipo": null,
    "posicao_inicio": 12,
    "posicao_fim": 207,
    "tem_conteudo": true,
    "tem_original": false
  },
  {
    "id": "f020e135-b3a0-4be4-b3b9-b30e544de4fc",
    "tipo": null,
    "posicao_inicio": 2752,
    "posicao_fim": 3065,
    "tem_conteudo": false,
    "tem_original": false
  },
  {
    "id": "f13a907b-c50b-4ece-bba5-aae3b01b24c5",
    "tipo": null,
    "posicao_inicio": 2229,
    "posicao_fim": 2422,
    "tem_conteudo": true,
    "tem_original": false
  },
  {
    "id": "fd3b654c-0678-4949-bfb7-e2154fe9a189",
    "tipo": null,
    "posicao_inicio": 553,
    "posicao_fim": 775,
    "tem_conteudo": true,
    "tem_original": false
  }
]
```

---

## INSTRUÇÕES FINAIS

1. Analise cuidadosamente os dois documentos
2. Identifique TODAS as diferenças
3. Para cada diferença, determine qual cláusula (tag) ela pertence usando as posições
4. Gere o JSON completo conforme o schema acima
5. Adicione a análise qualitativa no campo `resumo.analise_qualitativa`

**Comece sua análise agora!**
