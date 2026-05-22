# Teste A/B: Análise de Contrato com IA Pura

## Sua Missão

Você é um sistema de análise jurídica especializado. Sua tarefa é identificar **TODAS as modificações** entre o documento ANTERIOR e o documento VERSÃO ATUAL.

## Contexto do Teste

- **Contrato**: Demonstração de versionamento de documentos (#G9972)
- **Modelo**: Contrato Devix (11 tags/cláusulas mapeadas)
- **Baseline**: DOCUMENTO ORIGINAL (sem tags)
- **Versão Atual**: b93a6d72... (Status: concluido)

**IMPORTANTE**: Um sistema estruturado já processou estes documentos. Seu resultado será comparado para avaliar precisão, recall e qualidade da análise por IA pura.

---

## Tags/Cláusulas do Modelo (para referência)

As seguintes tags/cláusulas estão mapeadas no modelo de contrato. Use-as para vincular modificações às cláusulas correspondentes:

[
  {
    "id": "917457a1-7e62-49e0-a651-152488ca2e5a",
    "nome": "1.1",
    "posicao_inicio": 16,
    "posicao_fim": 223,
    "preview": "1 A CONTRATADA prestará à CONTRATANTE os serviços técnicos\nespecializados detalh..."
  },
  {
    "id": "56d73ee5-74a6-47d8-9b37-281e262e5d92",
    "nome": "2.1",
    "posicao_inicio": 1705,
    "posicao_fim": 2185,
    "preview": "1 O CONTRATO terá vigência a partir do INÍCIO DA VIGÊNCIA e encerrará\n(i) após o..."
  },
  {
    "id": "c0fee05e-cba6-497e-b2b2-4427fa21a0ea",
    "nome": "1",
    "posicao_inicio": 0,
    "posicao_fim": 19,
    "preview": "OBJETO\n\n\n\n\n\n1..."
  },
  {
    "id": "755be767-9cc7-4fb0-bf3a-0eafc96d01af",
    "nome": "1.2",
    "posicao_inicio": 207,
    "posicao_fim": 422,
    "preview": "2 Este CONTRATO não implica em nenhum dever de exclusividade da\nCONTRATANTE, que..."
  },
  {
    "id": "563ffc82-8e21-4fc8-ad98-c33078578e57",
    "nome": "1.4",
    "posicao_inicio": 739,
    "posicao_fim": 1068,
    "preview": "4 Os termos do QUADRO RESUMO prevalecem sobre os termos destas\nCondições Gerais ..."
  },
  {
    "id": "98423a70-ca16-47a3-adea-ab0514a4d0a1",
    "nome": "2",
    "posicao_inicio": 1675,
    "posicao_fim": 1794,
    "preview": "VIGÊNCIA E SUSPENSÃO\n\n\n\n\n\n2.1 O CONTRATO terá vigência a partir do INÍCIO DA VIG..."
  },
  {
    "id": "b22f1bb0-9a6f-4d7a-b78a-321eb058e478",
    "nome": "2.2",
    "posicao_inicio": 2083,
    "posicao_fim": 2459,
    "preview": "2. Se aplicável, a retroatividade dos efeitos do CONTRATO, não\nocasionará qualqu..."
  },
  {
    "id": "67953d59-ba26-4543-8dc9-b98212d35e06",
    "nome": "2.3",
    "posicao_inicio": 2342,
    "posicao_fim": 2665,
    "preview": "3 O PRAZO DE VIGÊNCIA já considera todos os dias necessários para as\nprovidência..."
  },
  {
    "id": "6cf261a9-eb70-4608-972d-2933d713f75a",
    "nome": "1.3",
    "posicao_inicio": 391,
    "posicao_fim": 785,
    "preview": "3 Os ANEXOS “Documentos Contratuais Gerais” ficam dispensados de\nrubrica ou vali..."
  },
  {
    "id": "015391a2-b986-4b9b-b544-d2bb7770382b",
    "nome": "1.5",
    "posicao_inicio": 1007,
    "posicao_fim": 1751,
    "preview": "5 A CONTRATADA, em nenhuma hipótese, poderá alegar, como justificativa\nou defesa..."
  },
  {
    "id": "983bc7fc-5246-4b22-834a-5680ae5da9c9",
    "nome": "2.4",
    "posicao_inicio": 2533,
    "posicao_fim": 3012,
    "preview": "4 O CONTRATO poderá ser suspenso total ou parcialmente, independente\nda anuência..."
  }
]

---

## DOCUMENTO ANTERIOR (DOCUMENTO ORIGINAL (sem tags))

```text
[P000] OBJETO
[P002] 1.1 A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no campo Serviços do QUADRO RESUMO, os quais serão prestados conforme disciplinado neste CONTRATO.
[P004] 1.2 Este CONTRATO não implica em nenhum dever de exclusividade da CONTRATANTE, que poderá firmar contratos com outras empresas para os mesmos fins, de acordo com seus interesses.
[P006] 1.3 Os ANEXOS “Documentos Contratuais Gerais” ficam dispensados de rubrica ou validação digital posterior. A CONTRATADA declara que já recebeu estes ANEXOS previamente em mídia eletrônica ou outra forma de acesso, que tem ciência do seu conteúdo e que concorda com os termos neles contidos, comprometendo-se a cumpri-los na sua integralidade.
[P008] 1.4 Os termos do QUADRO RESUMO prevalecem sobre os termos destas Condições Gerais os quais prevalecem sobre os termos dos ANEXOS. Na hipótese de conflitos entre os ANEXOS, prevalecerão uns sobre os outros na ordem em que se acham listados no QUADRO RESUMO acima.
[P010] 1.5 A CONTRATADA, em nenhuma hipótese, poderá alegar, como justificativa ou defesa, o desconhecimento, incompreensão, dúvida, no todo ou em parte, das disposições do presente CONTRATO e demais disposições de ordem geral ou particular nele estabelecidas, que são, desde já, consideradas necessárias e suficientes para definir os Serviços e os fornecimentos contidos no que foi contratado, e, ainda, permitir a sua execução de acordo com as normas vigentes no País, sendo vedado à CONTRATADA pleitear qualquer revisão de preços ou prorrogação de prazo, por erros ou omissões, que tenham sido cometidos na elaboração de sua(s) Proposta(s) que integra(m) o CONTRATO.
[P012] VIGÊNCIA E SUSPENSÃO
[P014] 2.1 O CONTRATO terá vigência a partir do INÍCIO DA VIGÊNCIA e encerrará (i) após o TÉRMINO DA VIGÊNCIA indicado no QUADRO RESUMO, (ii) após o cumprimento de todas as obrigações do CONTRATO e/ou dele decorrentes ou (iii) no caso de atingido o valor estabelecido neste instrumento, o que ocorrer primeiro, independentemente de qualquer notificação judicial ou extrajudicial.
[P016] 2.2. Se aplicável, a retroatividade dos efeitos do CONTRATO, não ocasionará qualquer prejuízo das obrigações da CONTRATADA sem acarretar quaisquer penalidades, compensação ou lucros cessantes para a CONTRATANTE, conforme prazo descrito no QUADRO RESUMO.
[P018] 2.3 O PRAZO DE VIGÊNCIA já considera todos os dias necessários para as providências prévias e finais, incluindo eventual mobilização, execução e desmobilização, por parte da CONTRATADA.
[P020] 2.4 O CONTRATO poderá ser suspenso total ou parcialmente, independente da anuência da CONTRATADA e/ou de procedimento judicial, mediante comunicação por escrito da CONTRATANTE à CONTRATADA enviada com antecedência mínima de 30 (trinta) DIAS, salvo se, por determinação do Poder Público ou Judiciário, for previsto menor prazo.
```

---

## DOCUMENTO VERSÃO ATUAL (Modificado)

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

## Sua Tarefa

Compare os dois documentos acima e gere um JSON com **TODAS as modificações** encontradas.

### Estrutura do JSON de Resposta

```json
{
  "versao_id": "b93a6d72-764b-4f86-b716-20c8373faa56",
  "modificacoes": [
    {
      "id_sequencial": 1,
      "tipo": "adicao|remocao|alteracao",
      "conteudo_original": "texto exato do documento anterior (null se adição)",
      "conteudo": "texto exato na versão atual (null se remoção)",
      "posicao_inicio": 150,
      "posicao_fim": 250,
      "paragrafo_inicio": "P042",
      "paragrafo_fim": "P045",
      "tag_relacionada_id": "uuid ou null",
      "tag_relacionada_nome": "nome da tag/cláusula ou null",
      "contexto": "explicação clara da mudança",
      "nivel_impacto": "baixo|medio|alto",
      "confianca": 85
    }
  ],
  "resumo": {
    "total_modificacoes": 10,
    "total_adicoes": 3,
    "total_remocoes": 2,
    "total_alteracoes": 5,
    "tags_afetadas": ["1.1", "2.3"],
    "tempo_analise_estimado": "2 minutos",
    "observacoes": "Principais mudanças concentradas em valores e prazos"
  },
  "metadata": {
    "metodo": "ia_pura",
    "modelo_usado": "GitHub Copilot / Claude",
    "timestamp": "2026-05-22T13:11:03.534459"
  }
}
```

### Critérios Importantes

1. **Precisão**: Identifique TODAS as diferenças de conteúdo
2. **Vinculação**: Use as posições das tags para associar modificações
3. **Tipo correto**:
   - `adicao`: texto que existe na versão atual mas não no documento anterior
   - `remocao`: texto que existe no documento anterior mas não na versão atual
   - `alteracao`: texto que mudou (substituição)
4. **Impacto**:
   - `baixo`: formatação, pontuação, correções ortográficas
   - `medio`: mudanças de valores, datas não críticas
   - `alto`: mudanças em obrigações, responsabilidades, valores críticos
5. **Ignore**: Diferenças de formatação pura (negrito, itálico, fonte) e tags de marcação (como {{1}}, {{/1}}, etc.)
6. **Posições**: Use os marcadores [P000], [P001], etc para identificar parágrafos

### Instruções Finais

- Compare parágrafo por parágrafo usando os marcadores [PXXX]
- Use as posições das tags para vincular modificações às cláusulas
- **IGNORE completamente tags de marcação** como {{tag}}, {{/tag}} - elas são apenas metadados estruturais
- Seja completo: não omita modificações pequenas de **conteúdo real**
- Retorne APENAS o JSON, sem texto adicional antes ou depois
- JSON deve ser válido e parseável

**COMECE SUA ANÁLISE AGORA!**
