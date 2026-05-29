# Teste A/B: Análise de Contrato com IA Pura

## Sua Missão

Você é um sistema de análise jurídica especializado. Sua tarefa é identificar **TODAS as modificações** entre o documento ANTERIOR e o documento VERSÃO ATUAL.

## Contexto do Teste

- **Contrato**: Teste - Esse vai! (#N0159)
- **Modelo**: Contrato de prestação de serviço - Rotina (294 tags/cláusulas mapeadas)
- **Baseline**: DOCUMENTO ORIGINAL (sem tags)
- **Versão Atual**: 8d8e89a8... (Status: concluido)

**IMPORTANTE**: Um sistema estruturado já processou estes documentos. Seu resultado será comparado para avaliar precisão, recall e qualidade da análise por IA pura.

---

## Tags/Cláusulas do Modelo (para referência)

As seguintes tags/cláusulas estão mapeadas no modelo de contrato. Use-as para vincular modificações às cláusulas correspondentes:

[
  {
    "id": "a74d5625-2478-438c-9b99-7ae27acfd1eb",
    "nome": "2",
    "posicao_inicio": 66748,
    "posicao_fim": 66776,
    "preview": "VIGÊNCIA E SUSPENSÃO..."
  },
  {
    "id": "ba42cd57-fc4d-4a79-80ab-1dd23d83b3c9",
    "nome": "3",
    "posicao_inicio": 68763,
    "posicao_fim": 68805,
    "preview": "VALOR, PREÇOS E FORMA DE PAGAMENTO..."
  },
  {
    "id": "6129835f-2848-49f5-80ab-8412e2e53783",
    "nome": "4",
    "posicao_inicio": 70777,
    "posicao_fim": 70803,
    "preview": "CORREÇÃO MONETÁRIA..."
  },
  {
    "id": "52f2c87d-2892-4155-9784-df254e7f81d1",
    "nome": "5",
    "posicao_inicio": 73111,
    "posicao_fim": 73127,
    "preview": "TRIBUTOS..."
  },
  {
    "id": "1bb7e919-ae88-47c2-a934-2421d880ed0e",
    "nome": "10.7.1",
    "posicao_inicio": 101887,
    "posicao_fim": 102385,
    "preview": "Quanto à saúde, segurança, meio ambiente e comunidade:\n\n    1.  Designar como re..."
  },
  {
    "id": "0a1dc2f7-0e66-4bd9-8076-9bd3509b699c",
    "nome": "12.5.1",
    "posicao_inicio": 114394,
    "posicao_fim": 114814,
    "preview": "As atribuições do Gestor do Contrato incluem:\n\n    1.  Verificar o cumprimento d..."
  },
  {
    "id": "b67fa877-4c5f-472a-8f3d-cad60a92419c",
    "nome": "17.4",
    "posicao_inicio": 132404,
    "posicao_fim": 132582,
    "preview": "As penalidades previstas no CONTRATO e nos ANEXOS, caso aplicável,\n    não possu..."
  },
  {
    "id": "6fd55184-3e48-4edb-9dac-8110590e1c3f",
    "nome": "17.6",
    "posicao_inicio": 132982,
    "posicao_fim": 133293,
    "preview": "A cobrança das multas previstas nesta cláusula ocorrerá\n    cumulativamente, na ..."
  },
  {
    "id": "41a02f55-5919-4e9a-ba36-c3056feb6a10",
    "nome": "17.7",
    "posicao_inicio": 133312,
    "posicao_fim": 133472,
    "preview": "As multas acima previstas não reduzirão ou eliminarão outras\n    penalidades, ob..."
  },
  {
    "id": "0ae729dd-4575-409a-8595-fe55678859e0",
    "nome": "17.5",
    "posicao_inicio": 132601,
    "posicao_fim": 132963,
    "preview": "As multas serão descontadas do pagamento da primeira nota\n    fiscal/fatura apre..."
  },
  {
    "id": "bd4bb830-0538-4c78-97f6-a006f0640f19",
    "nome": "12.5.2",
    "posicao_inicio": 114837,
    "posicao_fim": 114879,
    "preview": "Aprovar as medições da CONTRATADA...."
  },
  {
    "id": "0b8e1476-5bd9-49de-88dc-6c2fe9f5e424",
    "nome": "12.5.3",
    "posicao_inicio": 114902,
    "posicao_fim": 115012,
    "preview": "Autorizar, se for o caso, previamente, a realização de despesas a\n    serem reem..."
  },
  {
    "id": "8dbb6015-8407-477a-a86a-20394274657f",
    "nome": "1.1",
    "posicao_inicio": 64062,
    "posicao_fim": 64259,
    "preview": "A CONTRATADA prestará à CONTRATANTE os serviços técnicos\n    especializados deta..."
  },
  {
    "id": "ac066ccd-dcec-4837-8d9a-2aee19a6f5a2",
    "nome": "24.1",
    "posicao_inicio": 153022,
    "posicao_fim": 153250,
    "preview": "As PARTES se comprometem a envidar seus melhores esforços para\n    resolver, ami..."
  },
  {
    "id": "6003ec81-446c-4721-bb4f-bb1226c7a27e",
    "nome": "17.1",
    "posicao_inicio": 127121,
    "posicao_fim": 127378,
    "preview": "Caso a CONTRATADA descumpra norma e/ou obrigação contratual\n    considerada saná..."
  },
  {
    "id": "49b10d84-b3f6-44be-ac19-2927878de850",
    "nome": "20.1",
    "posicao_inicio": 136563,
    "posicao_fim": 136835,
    "preview": "A CONTRATADA, ao aceitar este instrumento, confirma a ciência e se\n    compromet..."
  },
  {
    "id": "ede9f974-5b97-4cd2-8e81-1873f522d3b0",
    "nome": "9.1.7",
    "posicao_inicio": 93213,
    "posicao_fim": 93273,
    "preview": "Disponibilizar área de apoio para uso da CONTRATADA...."
  },
  {
    "id": "a6fc24cd-8650-42df-bf45-8b46903d75c3",
    "nome": "15.1",
    "posicao_inicio": 121343,
    "posicao_fim": 121661,
    "preview": "As PARTES não poderão prestar informações a terceiros nem divulgar\n    quaisquer..."
  },
  {
    "id": "9a78bbc1-906b-4970-8abe-ad8423c78e6d",
    "nome": "23.1",
    "posicao_inicio": 144676,
    "posicao_fim": 145000,
    "preview": "O presente CONTRATO será extinto na (i) DATA DE TÉRMINO, (ii) após a\n    consecu..."
  },
  {
    "id": "a0d4a97c-a256-4e77-8f27-3700e5c2a3c4",
    "nome": "13.1",
    "posicao_inicio": 118250,
    "posicao_fim": 118576,
    "preview": "A CONTRATADA não poderá transferir a terceiros nem subcontratar, no\n    todo ou ..."
  },
  {
    "id": "952067cf-9a63-49a2-bceb-d12309d842d1",
    "nome": "18.1",
    "posicao_inicio": 133520,
    "posicao_fim": 133847,
    "preview": "Todo objeto de propriedade intelectual obtido através das atividades\n    relacio..."
  },
  {
    "id": "2a891630-bb94-47f4-9d05-f1dbd10d8853",
    "nome": "5.1",
    "posicao_inicio": 73142,
    "posicao_fim": 73476,
    "preview": "Todas as obrigações tributárias principais e acessórias que incidam\n    ou venha..."
  },
  {
    "id": "9d2ec5ce-ade2-4e2a-921c-d37bc82902c1",
    "nome": "16.1",
    "posicao_inicio": 124325,
    "posicao_fim": 124675,
    "preview": "Conforme previsto no artigo 393 do Código Civil Brasileiro, nenhuma\n    PARTE se..."
  },
  {
    "id": "606bba69-6e03-41bc-82ed-56ee08a7d55d",
    "nome": "1.2",
    "posicao_inicio": 64276,
    "posicao_fim": 64466,
    "preview": "Este CONTRATO não implica em nenhum dever de exclusividade da\n    CONTRATANTE, q..."
  },
  {
    "id": "e89cfbc7-2f6e-4e42-9c99-fc16ce0284f4",
    "nome": "2.1",
    "posicao_inicio": 66791,
    "posicao_fim": 67187,
    "preview": "O CONTRATO terá vigência a partir do INÍCIO DA VIGÊNCIA e\n    encerrará (i) após..."
  },
  {
    "id": "15d163b0-0929-4937-be8d-1435dbb76cbe",
    "nome": "19.1",
    "posicao_inicio": 135792,
    "posicao_fim": 136196,
    "preview": "A CONTRATANTE incentiva e promove o desenvolvimento das regiões onde\n    possui ..."
  },
  {
    "id": "9f08c15b-6c29-49b2-b877-243e42d978d9",
    "nome": "14.1",
    "posicao_inicio": 119365,
    "posicao_fim": 119778,
    "preview": "A CONTRATADA e suas subcontratadas se obrigam a instituir, por sua\n    conta exc..."
  },
  {
    "id": "71316aff-50f1-4280-ab5d-581b7e1fd12e",
    "nome": "12.6",
    "posicao_inicio": 115033,
    "posicao_fim": 115256,
    "preview": "Quando as condições de execução impuserem a necessidade da\n    modificação em de..."
  },
  {
    "id": "9e54a004-e778-404f-8001-aba45f9f27e4",
    "nome": "25.1",
    "posicao_inicio": 158560,
    "posicao_fim": 159005,
    "preview": "A CONTRATADA reconhece que poderá haver outros contratos que\n    apresentam inte..."
  },
  {
    "id": "0f022909-58d4-400d-8245-acec10ceb757",
    "nome": "21.1",
    "posicao_inicio": 140328,
    "posicao_fim": 140777,
    "preview": "A CONTRATADA concorda em documentar de forma precisa e detalhada em\n    seus liv..."
  },
  {
    "id": "e5eacdc1-17f3-432e-be1d-cf0661981dd3",
    "nome": "3.1",
    "posicao_inicio": 68820,
    "posicao_fim": 69292,
    "preview": "Para fins legais e contratuais, inclusive para aplicação de multas e\n    penalid..."
  },
  {
    "id": "27d15788-7349-4eab-ad39-f4d1650f2684",
    "nome": "4.1",
    "posicao_inicio": 70818,
    "posicao_fim": 71327,
    "preview": "Se aplicável, a partir do 12º mês contado da data-base, a CONTRATADA\n    poderá ..."
  },
  {
    "id": "ba46f026-3356-4ad5-98cc-52b1398ccb8f",
    "nome": "13.2",
    "posicao_inicio": 118595,
    "posicao_fim": 118786,
    "preview": "A existência de cessionárias ou subcontratadas, autorizadas, ou não,\n    pela CO..."
  },
  {
    "id": "41086e7e-2f2d-4b84-aa3f-59377a588eb7",
    "nome": "17.1.1",
    "posicao_inicio": 127399,
    "posicao_fim": 127657,
    "preview": "Se a CONTRATADA se manter inerte em relação à notificação, recuse-se\n    a corri..."
  },
  {
    "id": "963061cf-60ce-46c5-a8cb-3e3d694e29b3",
    "nome": "23.2",
    "posicao_inicio": 145019,
    "posicao_fim": 145218,
    "preview": "Qualquer das PARTES poderá rescindir o presente CONTRATO, mediante\n    simples a..."
  },
  {
    "id": "de34bb77-38d0-41ad-8433-de280afcff93",
    "nome": "14.2",
    "posicao_inicio": 119797,
    "posicao_fim": 119972,
    "preview": "As apólices contratadas pela CONTRATADA deverão permanecer\n    suficientes para ..."
  },
  {
    "id": "9676b8e5-564b-453d-bd5e-0096d4e1127b",
    "nome": "24.2",
    "posicao_inicio": 153269,
    "posicao_fim": 153641,
    "preview": "Não sendo possível a solução, por meio de negociação direta, fica\n    desde já c..."
  },
  {
    "id": "739033a9-b6ae-48ed-8afb-91c725b49283",
    "nome": "18.2",
    "posicao_inicio": 133866,
    "posicao_fim": 134169,
    "preview": "Quando a invenção ou melhoria resultar de contribuição específica da\n    CONTRAT..."
  },
  {
    "id": "25e2f880-f1bf-4fd7-bf67-43b36fa32ab8",
    "nome": "25.2",
    "posicao_inicio": 159024,
    "posicao_fim": 159228,
    "preview": "O CONTRATO é aceito pelas PARTES como completo e suficiente para\n    definir o o..."
  },
  {
    "id": "3a7d57e3-7749-4170-b55e-e97511ad3913",
    "nome": "15.2",
    "posicao_inicio": 121680,
    "posicao_fim": 122022,
    "preview": "O acesso às informações confidenciais será restrito aos Funcionários\n    das PAR..."
  },
  {
    "id": "84b28d8f-bd40-449a-90b4-bd1f83bbbbcb",
    "nome": "3.2",
    "posicao_inicio": 69309,
    "posicao_fim": 69498,
    "preview": "Caso o dia do pagamento devido pela CONTRATANTE se dê em feriados\n    bancários ..."
  },
  {
    "id": "e6a86c06-e4a3-4664-9738-ab3d7979557b",
    "nome": "2.2",
    "posicao_inicio": 67204,
    "posicao_fim": 67472,
    "preview": "Se aplicável, a retroatividade dos efeitos do CONTRATO, não\n    ocasionará qualq..."
  },
  {
    "id": "c3e35950-f38d-4e3c-8bd8-f1c8bd0eddc7",
    "nome": "24.3",
    "posicao_inicio": 153660,
    "posicao_fim": 153742,
    "preview": "Para os fins da arbitragem, as PARTES ajustam, desde logo, o\n    seguinte:..."
  },
  {
    "id": "8463d78b-8d6b-47c3-a901-5c748bfc7d34",
    "nome": "19.2",
    "posicao_inicio": 136215,
    "posicao_fim": 136528,
    "preview": "Caso os Serviços sejam prestados no município de Anchieta/ES, a\n    CONTRATADA s..."
  },
  {
    "id": "86299bde-60bc-4ffb-8f53-985302219b30",
    "nome": "10.7.2.1",
    "posicao_inicio": 102956,
    "posicao_fim": 103131,
    "preview": "Após o envio de comunicação as PARTES deverão se reunir para avaliar\n    uma sol..."
  },
  {
    "id": "d48b75e0-2e79-4f78-8113-76499bd6b9e2",
    "nome": "16.2",
    "posicao_inicio": 124694,
    "posicao_fim": 125076,
    "preview": "Ante a ocorrência de qualquer circunstância que puder ser invocada\n    como caso..."
  },
  {
    "id": "4063a51b-867d-4ae3-9e58-6ebfc84ec328",
    "nome": "20.2",
    "posicao_inicio": 136854,
    "posicao_fim": 137319,
    "preview": "A CONTRATADA se obriga a apurar, com diligência, qualidade,\n    efetividade e de..."
  },
  {
    "id": "2f074b04-0c22-4e30-bccc-ae034464c726",
    "nome": "23.2.2",
    "posicao_inicio": 145394,
    "posicao_fim": 145446,
    "preview": "Uma das PARTES tiver sua falência decretada...."
  },
  {
    "id": "d8cdc1a5-c51d-4b34-a8b7-2da507f0e088",
    "nome": "12.6.1",
    "posicao_inicio": 115277,
    "posicao_fim": 115603,
    "preview": "Sustar o pagamento de quaisquer notas fiscais/faturas da CONTRATADA,\n    no caso..."
  },
  {
    "id": "2b2bce96-4442-4010-ae63-8e8da818db5c",
    "nome": "1.3",
    "posicao_inicio": 64483,
    "posicao_fim": 64849,
    "preview": "Os ANEXOS “Documentos Contratuais Gerais” ficam dispensados de\n    rubrica ou va..."
  },
  {
    "id": "e964c75b-272b-4805-8f48-8df6402eae57",
    "nome": "17.2",
    "posicao_inicio": 127678,
    "posicao_fim": 127921,
    "preview": "Se o referido descumprimento de norma e/ou obrigação pela CONTRATADA\n    for con..."
  },
  {
    "id": "ff034b57-fb97-4a50-b5e6-40b1eb462852",
    "nome": "4.1.1",
    "posicao_inicio": 71346,
    "posicao_fim": 71650,
    "preview": "Caso o reajuste seja solicitado em prazo superior a 90 (noventa)\n    dias após a..."
  },
  {
    "id": "eb36922f-8ac2-4773-aafb-c216db998cee",
    "nome": "22.1",
    "posicao_inicio": 142707,
    "posicao_fim": 143577,
    "preview": "As PARTES, ao tratarem dados pessoais no contexto de execução do\n    CONTRATO, a..."
  },
  {
    "id": "93a74f6c-8053-4b63-9e1e-59c0876afbf1",
    "nome": "5.1.1",
    "posicao_inicio": 73495,
    "posicao_fim": 74020,
    "preview": "A CONTRATADA declara estar ciente de que, no momento do pagamento, a\n    CONTRAT..."
  },
  {
    "id": "78cadfbb-df30-438d-9b82-4351945eacb6",
    "nome": "25.3",
    "posicao_inicio": 159247,
    "posicao_fim": 159459,
    "preview": "A CONTRATANTE reserva-se o direito de auditar qualquer das etapas do\n    objeto ..."
  },
  {
    "id": "d2ba0cc1-8b67-4859-92d2-63b50aca7ecd",
    "nome": "2.3",
    "posicao_inicio": 67489,
    "posicao_fim": 67686,
    "preview": "O PRAZO DE VIGÊNCIA já considera todos os dias necessários para as\n    providênc..."
  },
  {
    "id": "044fb1e3-7df3-4c6c-a8cf-10b34c6befba",
    "nome": "24.3.1",
    "posicao_inicio": 153763,
    "posicao_fim": 153970,
    "preview": "O presente CONTRATO, nos termos ora previstos, assim como os\n    direitos e obri..."
  },
  {
    "id": "9bf81630-5904-4218-b46f-0154af4e9617",
    "nome": "23.2.3",
    "posicao_inicio": 145469,
    "posicao_fim": 145639,
    "preview": "Imotivadamente, mediante aviso prévio escrito, com antecedência de\n    30 (trint..."
  },
  {
    "id": "a390b5c1-1de1-4d74-a98a-57d7f0db8241",
    "nome": "13.3",
    "posicao_inicio": 118805,
    "posicao_fim": 119242,
    "preview": "A subcontratação do OBJETO pela CONTRATADA, ou de parte dele, sem a\n    prévia a..."
  },
  {
    "id": "c1207d88-15f6-46a6-b506-af0936220431",
    "nome": "12.6.2",
    "posicao_inicio": 115626,
    "posicao_fim": 115823,
    "preview": "Solicitar, quando entenda necessário, ações referentes aos\n    Funcionários da C..."
  },
  {
    "id": "7d0c054c-0e06-4ad5-947b-bacc481885d2",
    "nome": "17.3",
    "posicao_inicio": 127940,
    "posicao_fim": 128124,
    "preview": "O valor de referência para cálculo das penalidades estabelecidas no\n    CONTRATO..."
  },
  {
    "id": "ddf04d1e-3ad4-4efc-afb3-f363b99da771",
    "nome": "10.7.3",
    "posicao_inicio": 103156,
    "posicao_fim": 103401,
    "preview": "Atingir os indicadores de desempenho em segurança, conforme\n    definição e cálc..."
  },
  {
    "id": "d608805c-4b5e-4920-aaee-718eb4ad9ba2",
    "nome": "16.3",
    "posicao_inicio": 125095,
    "posicao_fim": 125343,
    "preview": "A PARTE afetada pelo evento de força maior ou caso fortuito deverá\n    tomar e d..."
  },
  {
    "id": "44ef241d-e666-4ce3-9fdd-61ce66006658",
    "nome": "4.2",
    "posicao_inicio": 71669,
    "posicao_fim": 71835,
    "preview": "Uma vez reajustados, os valores permanecerão fixos por novo período\n    de 12 (d..."
  },
  {
    "id": "4c1296f1-a4ff-4624-a7d0-ebf336735340",
    "nome": "14.3",
    "posicao_inicio": 119991,
    "posicao_fim": 120393,
    "preview": "As responsabilidades da CONTRATADA são integrais, não se limitando\n    ao valor ..."
  },
  {
    "id": "2cf15b8c-229b-453c-afc7-cfedf7f5dad9",
    "nome": "18.3",
    "posicao_inicio": 134188,
    "posicao_fim": 134567,
    "preview": "A CONTRATADA se obriga a transferir à CONTRATANTE a propriedade\n    integral, li..."
  },
  {
    "id": "186ebe1f-5926-4bc7-864b-6f1ef934f130",
    "nome": "1.4",
    "posicao_inicio": 64866,
    "posicao_fim": 65144,
    "preview": "Os termos do QUADRO RESUMO prevalecem sobre os termos destas\n    Condições Gerai..."
  },
  {
    "id": "3d5ef0f4-aa28-4dd8-8f62-345880750449",
    "nome": "13.4",
    "posicao_inicio": 119261,
    "posicao_fim": 119333,
    "preview": "Fica vedado aos subcontratados realizarem novas subcontratações...."
  },
  {
    "id": "0939b2bf-cc62-42b3-ba9d-940608b7132b",
    "nome": "2.4",
    "posicao_inicio": 67703,
    "posicao_fim": 67869,
    "preview": "Havendo interesse entre as PARTES, este CONTRATO poderá ter sua\n    vigência pro..."
  },
  {
    "id": "86078830-fbdf-4c51-87e7-c82cade7dbed",
    "nome": "20.3",
    "posicao_inicio": 137338,
    "posicao_fim": 137707,
    "preview": "A apuração será conduzida de forma sigilosa e confidencial, sendo\n    vedado à C..."
  },
  {
    "id": "5fe33f15-e45b-4e3e-a321-ec43af4d06a9",
    "nome": "23.2.1",
    "posicao_inicio": 145239,
    "posicao_fim": 145371,
    "preview": "Ocorrendo caso fortuito ou de força maior, cujos efeitos persistirem\n    por pra..."
  },
  {
    "id": "9ac3ee49-cc6d-4455-9307-1c0ce091cbaa",
    "nome": "5.2",
    "posicao_inicio": 74039,
    "posicao_fim": 74301,
    "preview": "Eventuais alterações na legislação que impactem na tributação\n    relativa a est..."
  },
  {
    "id": "59a034cc-e29d-4ed2-8989-4a945582d215",
    "nome": "3.3",
    "posicao_inicio": 69515,
    "posicao_fim": 69991,
    "preview": "Os pagamentos serão efetuados pela CONTRATANTE mediante crédito em\n    conta cor..."
  },
  {
    "id": "f632bc49-878f-47f2-bcac-cfdb0ac85fc7",
    "nome": "10.7.4",
    "posicao_inicio": 103424,
    "posicao_fim": 103627,
    "preview": "Acatar as solicitações da(s) área(s) de SST da CONTRATANTE, o que\n    incluir di..."
  },
  {
    "id": "8a483127-d189-422b-ae7d-84b5f5a2dd0b",
    "nome": "21.2",
    "posicao_inicio": 140796,
    "posicao_fim": 141566,
    "preview": "Durante o prazo do presente CONTRATO e por 5 (cinco) anos após o seu\n    término..."
  },
  {
    "id": "b2a8ef45-9253-4fc6-b832-2a538403e5a8",
    "nome": "12.6.3",
    "posicao_inicio": 115846,
    "posicao_fim": 116090,
    "preview": "Mandar executar, por terceiros, debitando as despesas respectivas da\n    CONTRAT..."
  },
  {
    "id": "4806dfe6-f83b-4da3-911c-c4f1eb9d2524",
    "nome": "25.4",
    "posicao_inicio": 159478,
    "posicao_fim": 159846,
    "preview": "Quando aplicável, a CONTRATADA declara que tem ciência e cumprirá as\n    diretri..."
  },
  {
    "id": "940f00ef-d53a-40cc-af9e-20736dc266a7",
    "nome": "16.4",
    "posicao_inicio": 125362,
    "posicao_fim": 125612,
    "preview": "Cessado o caso fortuito ou o motivo de força maior, a PARTE que o\n    tiver invo..."
  },
  {
    "id": "2c7e80f6-411c-4b81-96cb-ba27d432d069",
    "nome": "22.2",
    "posicao_inicio": 143596,
    "posicao_fim": 144042,
    "preview": "A CONTRATADA declara que, na execução deste CONTRATO, caso ocorra o\n    tratamen..."
  },
  {
    "id": "92da8335-0fdf-499d-8e82-f0d88f8e2b67",
    "nome": "14.4",
    "posicao_inicio": 120412,
    "posicao_fim": 120746,
    "preview": "As PARTES, através da assinatura deste instrumento, autorizam, desde\n    já, o c..."
  },
  {
    "id": "c718c3ae-2f6a-4cd1-a8a3-2b02f5955225",
    "nome": "5.3",
    "posicao_inicio": 74318,
    "posicao_fim": 74523,
    "preview": "As despesas decorrentes de ações administrativas/judiciais visando\n    discutir ..."
  },
  {
    "id": "b860c61e-be1f-4b6b-80ec-a843df330e00",
    "nome": "20.4",
    "posicao_inicio": 137726,
    "posicao_fim": 137951,
    "preview": "É expressamente vedada qualquer forma de retaliação por parte da\n    CONTRATADA ..."
  },
  {
    "id": "c900edc1-db6c-47e8-842c-625a729edebb",
    "nome": "21.3",
    "posicao_inicio": 141585,
    "posicao_fim": 141727,
    "preview": "As análises e acesso aos documentos previstos nesta Cláusula estão\n    sujeitas ..."
  },
  {
    "id": "d2a5d33a-5907-4fac-97cb-309096bd8704",
    "nome": "12.6.4",
    "posicao_inicio": 116113,
    "posicao_fim": 116261,
    "preview": "Convocar e dirigir reuniões periódicas ou ocasionais com a\n    CONTRATADA, para ..."
  },
  {
    "id": "27b9595b-16d2-459a-9848-51ee052d8cbf",
    "nome": "2.5",
    "posicao_inicio": 67886,
    "posicao_fim": 68232,
    "preview": "O CONTRATO poderá ser suspenso total ou parcialmente, independente\n    da anuênc..."
  },
  {
    "id": "1ea4ff7c-e1f4-4114-8173-e4d3cd863317",
    "nome": "15.3",
    "posicao_inicio": 122041,
    "posicao_fim": 122794,
    "preview": "As estipulações e obrigações constantes da presente cláusula não\n    serão aplic..."
  },
  {
    "id": "b1802d8e-ee00-4b05-addd-68f5a7b47b06",
    "nome": "18.4",
    "posicao_inicio": 134586,
    "posicao_fim": 135029,
    "preview": "Todos os documentos, incluindo, mas não se limitando a relatórios,\n    gráficos,..."
  },
  {
    "id": "c36a53ba-2357-440d-8d0b-29eda533dccc",
    "nome": "23.4",
    "posicao_inicio": 145854,
    "posicao_fim": 146190,
    "preview": "O CONTRATO poderá ser resilido por qualquer uma das PARTES, a\n    qualquer momen..."
  },
  {
    "id": "d3e2565e-9099-4d94-ad32-6c8f46a06596",
    "nome": "25.5",
    "posicao_inicio": 159865,
    "posicao_fim": 160109,
    "preview": "Este instrumento, juntamente com seus ANEXOS, constitui o acordo\n    integral en..."
  },
  {
    "id": "fcfa32f1-8deb-4330-9051-02a54fd8acb2",
    "nome": "4.3",
    "posicao_inicio": 71852,
    "posicao_fim": 72380,
    "preview": "A aplicação do ÍNDICE DE CORREÇÃO MONETÁRIA ocorrerá apenas a partir\n    da prim..."
  },
  {
    "id": "45bd6ed2-c171-4fc0-a7f4-3f6e47539717",
    "nome": "16.5",
    "posicao_inicio": 125631,
    "posicao_fim": 125926,
    "preview": "Se o fato invocado como caso fortuito ou força maior impossibilitar\n    o cumpri..."
  },
  {
    "id": "90539eff-7a37-4bae-abaa-9dbdc0fc6304",
    "nome": "6.17.2",
    "posicao_inicio": 82684,
    "posicao_fim": 83037,
    "preview": "Caso haja atraso no pagamento de qualquer nota fiscal/fatura, por\n    motivos im..."
  },
  {
    "id": "9108434a-9076-49be-8537-00b0647ecee4",
    "nome": "24.3.2",
    "posicao_inicio": 153993,
    "posicao_fim": 154634,
    "preview": "Quaisquer questões, controvérsias, disputas ou reivindicações\n    decorrentes de..."
  },
  {
    "id": "34495166-5aaf-4e8f-ac42-a907cb0741c5",
    "nome": "3.4",
    "posicao_inicio": 70008,
    "posicao_fim": 70449,
    "preview": "A ausência de qualquer contestação por parte da CONTRATADA, no prazo\n    de 60 (..."
  },
  {
    "id": "bca1a4d3-7b88-418c-a8a9-294d7af6e456",
    "nome": "12.6.5",
    "posicao_inicio": 116284,
    "posicao_fim": 116484,
    "preview": "Comunicar à CONTRATADA, por escrito e com a devida antecedência,\n    qualquer in..."
  },
  {
    "id": "10dd8223-a719-4ecf-ae43-26072c9de2c6",
    "nome": "2.5.1",
    "posicao_inicio": 68251,
    "posicao_fim": 68451,
    "preview": "A CONTRATADA deverá reassumir a execução do CONTRATO em até 30\n    (trinta) DIAS..."
  },
  {
    "id": "93f3a624-d2fb-4146-a394-b86ffc1c2bbc",
    "nome": "14.5",
    "posicao_inicio": 120765,
    "posicao_fim": 121075,
    "preview": "Na ocorrência de sinistro, as PARTES deverão, no prazo de 05 (cinco)\n    dias út..."
  },
  {
    "id": "6f7d1a87-2dec-45c4-8795-10ccfdda4577",
    "nome": "15.4",
    "posicao_inicio": 122813,
    "posicao_fim": 123058,
    "preview": "A CONTRATADA declara antes do término deste CONTRATO, por qualquer\n    razão, de..."
  },
  {
    "id": "051bc3a1-45ea-4896-bbed-4ad79e2000b9",
    "nome": "20.5",
    "posicao_inicio": 137970,
    "posicao_fim": 138298,
    "preview": "A CONTRATADA autoriza expressamente a SAMARCO a requisitar\n    documentos, infor..."
  },
  {
    "id": "d4c86cae-18f9-46ea-b7a3-177207a35342",
    "nome": "18.5",
    "posicao_inicio": 135048,
    "posicao_fim": 135265,
    "preview": "A CONTRATADA é responsável pelo pagamento de qualquer taxa ou\n    royalty eventu..."
  },
  {
    "id": "0b1605a4-c5ac-40ed-9fdb-0544be160a80",
    "nome": "21.4",
    "posicao_inicio": 141746,
    "posicao_fim": 142074,
    "preview": "Durante o prazo do presente CONTRATO e por 5 (cinco) anos após o seu\n    término..."
  },
  {
    "id": "5037b47d-b9c0-46cf-a1e7-62ca7a9d77b2",
    "nome": "25.6",
    "posicao_inicio": 160128,
    "posicao_fim": 160332,
    "preview": "Nenhuma modificação do CONTRATO vinculará as PARTES, exceto quando\n    efetuada ..."
  },
  {
    "id": "ebf9ff3d-4dc5-4dfb-8dd5-7c502d6d353e",
    "nome": "1.5",
    "posicao_inicio": 65161,
    "posicao_fim": 65863,
    "preview": "A CONTRATADA, em nenhuma hipótese, poderá alegar, como justificativa\n    ou defe..."
  },
  {
    "id": "ca3a9028-a1ac-48fe-aec1-e57bfc620a06",
    "nome": "23.5",
    "posicao_inicio": 146209,
    "posicao_fim": 146508,
    "preview": "Adicionalmente, a CONTRATANTE poderá rescindir o CONTRATO de pleno\n    direito, ..."
  },
  {
    "id": "a384353d-f87a-40d4-a647-240f3761de41",
    "nome": "16.6.1",
    "posicao_inicio": 125947,
    "posicao_fim": 126235,
    "preview": "Em nenhuma hipótese será considerado como evento de caso fortuito ou\n    força m..."
  },
  {
    "id": "5fd6fe65-2ee3-4520-8620-0f49e1901a58",
    "nome": "7",
    "posicao_inicio": 83055,
    "posicao_fim": 83105,
    "preview": "DISPONIBILIZAÇÃO DE BEM IMÓVEL EM COMODATO..."
  },
  {
    "id": "cf9147b0-309e-4e68-96c6-ba36b0f57af1",
    "nome": "23.3",
    "posicao_inicio": 144061,
    "posicao_fim": 144627,
    "preview": "Caso a CONTRATANTE venha a ser responsabilizada, judicial ou\n    extrajudicialme..."
  },
  {
    "id": "d901b112-02af-40e4-8f24-ffcb620d8ba1",
    "nome": "14.6",
    "posicao_inicio": 121094,
    "posicao_fim": 121301,
    "preview": "A CONTRATADA deverá, sempre que solicitado, em até 10 (dez) DIAS\n    corridos, a..."
  },
  {
    "id": "f2972cd3-1638-4111-a262-e64df6bcc51d",
    "nome": "3.5",
    "posicao_inicio": 70466,
    "posicao_fim": 70762,
    "preview": "Se os pagamentos efetuados na forma deste item forem superiores aos\n    valores ..."
  },
  {
    "id": "0ac7501b-760f-4b79-bad1-e9a2a4e9cfee",
    "nome": "2.5.2",
    "posicao_inicio": 68472,
    "posicao_fim": 68746,
    "preview": "A CONTRATADA não terá direito de indenização de qualquer natureza em\n    razão d..."
  },
  {
    "id": "dd653004-7b9f-447f-ae87-bd356aa1ee5d",
    "nome": "4.4",
    "posicao_inicio": 72397,
    "posicao_fim": 72826,
    "preview": "A CORREÇÃO MONETÁRIA não incidirá sobre: (i) valores pagos em atraso\n    em razã..."
  },
  {
    "id": "015febed-31c8-4f90-87fb-05d88a6f0091",
    "nome": "10.7.5.1",
    "posicao_inicio": 104203,
    "posicao_fim": 104444,
    "preview": "Somente mediante autorização da CONTRATANTE e cumprimento da\n    legislação, em ..."
  },
  {
    "id": "4accd550-1757-47f5-9b8c-dc5a53703f35",
    "nome": "23.5.1",
    "posicao_inicio": 146529,
    "posicao_fim": 146735,
    "preview": "Descumprir quaisquer obrigações do CONTRATO não sanadas no prazo\n    mencionado ..."
  },
  {
    "id": "5a0de8cb-89dd-49be-a99f-6ee1fbcc9fc8",
    "nome": "16.6.2",
    "posicao_inicio": 126258,
    "posicao_fim": 126411,
    "preview": "Qualquer ação de qualquer autoridade pública que uma parte pudesse\n    ter evita..."
  },
  {
    "id": "2fea7592-b4ab-49be-ad55-fa098a1227f2",
    "nome": "12.7",
    "posicao_inicio": 116505,
    "posicao_fim": 116923,
    "preview": "No caso de inobservância, pela CONTRATADA, das exigências do Gestor\n    do Contr..."
  },
  {
    "id": "35521d1d-b9b9-4e2b-92ad-96f05b05ba1d",
    "nome": "15.5",
    "posicao_inicio": 123077,
    "posicao_fim": 123477,
    "preview": "Em caso de impossibilidade de devolução da documentação tendo em\n    vista o mei..."
  },
  {
    "id": "e612e332-aff8-4a17-9847-3a98cd385185",
    "nome": "16.6.3",
    "posicao_inicio": 126434,
    "posicao_fim": 126488,
    "preview": "Decretação de falência de qualquer das PARTES;..."
  },
  {
    "id": "ff86d77e-bf62-469f-bfc5-abcd96dd59b4",
    "nome": "20.6",
    "posicao_inicio": 138317,
    "posicao_fim": 138733,
    "preview": "O descumprimento, por parte da CONTRATADA, das obrigações previstas\n    nesta cl..."
  },
  {
    "id": "85129b49-680b-436e-86c7-1e2ed89c97f8",
    "nome": "18.6",
    "posicao_inicio": 135284,
    "posicao_fim": 135734,
    "preview": "A CONTRATADA é a única e exclusiva responsável por si e por seus\n    Funcionário..."
  },
  {
    "id": "f67e3f91-79e5-4aaf-965d-9ae8310f9d93",
    "nome": "5.4",
    "posicao_inicio": 74540,
    "posicao_fim": 75369,
    "preview": "Quando legalmente aplicável, e para todos os fins previdenciários, a\n    Matrícu..."
  },
  {
    "id": "56035e31-9d8d-4eb0-90ca-e80f34570ae1",
    "nome": "25.7",
    "posicao_inicio": 160351,
    "posicao_fim": 160795,
    "preview": "As Partes reconhecem a veracidade, autenticidade, integridade,\n    validade e ef..."
  },
  {
    "id": "c23329f8-472b-409f-bb96-3ea3a0f72810",
    "nome": "10.7.5.2",
    "posicao_inicio": 104471,
    "posicao_fim": 104637,
    "preview": "Cumprir todos os requisitos legais aplicáveis relacionados à SST,\n    bem como a..."
  },
  {
    "id": "4d208d91-fe3c-41f3-8754-7f9df1e90823",
    "nome": "16.6.4",
    "posicao_inicio": 126511,
    "posicao_fim": 126581,
    "preview": "Dificuldades econômicas ou financeiras de qualquer das PARTES;..."
  },
  {
    "id": "2545c66c-e8b6-4b1d-980d-7a593ee0b637",
    "nome": "23.5.2",
    "posicao_inicio": 146758,
    "posicao_fim": 146950,
    "preview": "Der causa à suspensão dos Serviços por determinação das autoridades\n    competen..."
  },
  {
    "id": "e62591a4-efdc-4c7c-af85-ca8d70095e72",
    "nome": "4.5",
    "posicao_inicio": 72843,
    "posicao_fim": 73096,
    "preview": "O ÍNDICE DE CORREÇÃO MONETÁRIA do CONTRATO será aplicado unicamente\n    pelas pr..."
  },
  {
    "id": "6dfbd7a1-aba9-4f1e-a7b6-d6f9ed742ba0",
    "nome": "12.8",
    "posicao_inicio": 116942,
    "posicao_fim": 117117,
    "preview": "As funções inerentes ao Gestor do Contrato não eximem, em nenhuma\n    hipótese, ..."
  },
  {
    "id": "d553d2c1-56a3-40b2-a35d-c3e5f2036a27",
    "nome": "6",
    "posicao_inicio": 75384,
    "posicao_fim": 75433,
    "preview": "MEDIÇÃO, FATURAMENTO E FORMA DE PAGAMENTO..."
  },
  {
    "id": "13a0d436-bddd-4528-b78e-9fa2f60ab7e5",
    "nome": "21.5",
    "posicao_inicio": 142093,
    "posicao_fim": 142651,
    "preview": "Qualquer violação das disposições desta cláusula durante o PRAZO DE\n    VIGÊNCIA..."
  },
  {
    "id": "c5d75070-e68a-44bf-ac36-447fd8a7e74d",
    "nome": "16.6.5",
    "posicao_inicio": 126604,
    "posicao_fim": 126691,
    "preview": "Os dias de chuvas não superiores às médias históricas e suas\n    consequências...."
  },
  {
    "id": "e8197ba6-1acc-443a-95ec-22a9eb70df53",
    "nome": "24.3.3",
    "posicao_inicio": 154657,
    "posicao_fim": 155397,
    "preview": "A arbitragem será conduzida por 3 (três) árbitros, cabendo a cada\n    uma das PA..."
  },
  {
    "id": "98cc361f-6761-4962-925f-de17455ea14e",
    "nome": "25.8",
    "posicao_inicio": 160814,
    "posicao_fim": 160974,
    "preview": "As PARTES de comum acordo estabelecem que o quanto negociado neste\n    CONTRATO ..."
  },
  {
    "id": "cf8f514c-e6ee-4062-bb43-43357184e1d9",
    "nome": "20.7",
    "posicao_inicio": 138752,
    "posicao_fim": 139003,
    "preview": "A CONTRATADA declara e garante que seus Funcionários que atuam nos\n    negócios ..."
  },
  {
    "id": "c2450c63-1439-4962-b164-1de2ae6a0f98",
    "nome": "10.8.1",
    "posicao_inicio": 104662,
    "posicao_fim": 104858,
    "preview": "Quanto aos Serviços como um todo:\n\n    1.  Credenciar, por escrito, junto à CONT..."
  },
  {
    "id": "c9cf3b00-cdce-4cd5-8227-f9e9dd57e17c",
    "nome": "15.6",
    "posicao_inicio": 123496,
    "posicao_fim": 123819,
    "preview": "A CONTRATADA reconhece e aceita que o uso para fim diverso da\n    execução dos S..."
  },
  {
    "id": "36e6d50a-e381-4bce-8e6d-c3bffe4d4ec1",
    "nome": "12.9",
    "posicao_inicio": 117136,
    "posicao_fim": 117311,
    "preview": "A ação/omissão, total ou parcial, do Gestor do Contrato, não exime a\n    CONTRAT..."
  },
  {
    "id": "250992f5-8b88-49ed-a2f7-9a57766382db",
    "nome": "6.1",
    "posicao_inicio": 75448,
    "posicao_fim": 75627,
    "preview": "Os pagamentos serão efetuados pela CONTRATANTE mediante crédito em\n    conta cor..."
  },
  {
    "id": "a9c73c8d-e456-4414-be60-f7b09218fb24",
    "nome": "24.3.4",
    "posicao_inicio": 155420,
    "posicao_fim": 155630,
    "preview": "Para controvérsias que possam envolver valores de até R$\n    1.000.000,00 (um mi..."
  },
  {
    "id": "d8c4d341-b154-4ef7-97ff-34e3017175d9",
    "nome": "23.5.3",
    "posicao_inicio": 146973,
    "posicao_fim": 147294,
    "preview": "Promover, supervenientemente, ações judiciais contra a CONTRATANTE,\n    suas con..."
  },
  {
    "id": "f02e809f-a2a0-4c56-9701-4892d7146133",
    "nome": "12.10",
    "posicao_inicio": 117331,
    "posicao_fim": 117442,
    "preview": "Sem prejuízo do cumprimento das demais obrigações previstas neste\n    CONTRATO, ..."
  },
  {
    "id": "aea4793c-b06b-4644-86e0-e0a0ee691319",
    "nome": "1.6",
    "posicao_inicio": 65880,
    "posicao_fim": 66733,
    "preview": "A CONTRATADA declara ter ciência das condições da região onde se\n    localizam a..."
  },
  {
    "id": "3f4122cb-0836-4cad-8f2c-8ea2cc3acbac",
    "nome": "20.8",
    "posicao_inicio": 139022,
    "posicao_fim": 139248,
    "preview": "A CONTRATADA deverá comunicar a CONTRATANTE imediatamente, através\n    de envio ..."
  },
  {
    "id": "02fd05e6-ad96-4ec8-85a7-54d7f220752d",
    "nome": "23.5.4",
    "posicao_inicio": 147317,
    "posicao_fim": 147380,
    "preview": "Reincidir no descumprimento de normas referentes à SST;..."
  },
  {
    "id": "076a06a5-a4da-408f-a295-01cf612590d5",
    "nome": "15.7",
    "posicao_inicio": 123838,
    "posicao_fim": 124050,
    "preview": "As obrigações acima mencionadas permanecerão em pleno e absoluto\n    vigor desde..."
  },
  {
    "id": "0113b784-f6c3-4de3-b38e-79642e36b13d",
    "nome": "10.8.2",
    "posicao_inicio": 104881,
    "posicao_fim": 105108,
    "preview": "Informar a CONTRATANTE a ocorrência de qualquer fato ou condição que\n    possa a..."
  },
  {
    "id": "c80f7c40-28c3-4215-8213-957433250f83",
    "nome": "24.3.5",
    "posicao_inicio": 155653,
    "posicao_fim": 155768,
    "preview": "Os procedimentos da arbitragem terão lugar na Cidade de Belo\n    Horizonte, Esta..."
  },
  {
    "id": "4b2ec9db-ae53-4b6f-a6a4-92201e257471",
    "nome": "16.7",
    "posicao_inicio": 126712,
    "posicao_fim": 127076,
    "preview": "As PARTES acordam, desde já, que os prazos previstos neste CONTRATO\n    poderão ..."
  },
  {
    "id": "089bff1e-c333-4816-9228-82c332deb086",
    "nome": "20.9",
    "posicao_inicio": 139267,
    "posicao_fim": 139352,
    "preview": "Qualquer violação real ou iminente da legislação anticorrupção\n    aplicável...."
  },
  {
    "id": "1217e473-42a9-45dc-b168-67a20474989e",
    "nome": "6.2",
    "posicao_inicio": 75644,
    "posicao_fim": 75960,
    "preview": "Independente da FORMA DE PAGAMENTO, a CONTRATADA deverá emitir o BMM\n    ou BM p..."
  },
  {
    "id": "fedf9ec3-8cef-44c8-be10-0d31f755da47",
    "nome": "10.8.3",
    "posicao_inicio": 105131,
    "posicao_fim": 105234,
    "preview": "Participar de forma efetiva e cooperativa dos processos de gestão\n    integrada ..."
  },
  {
    "id": "b3e3e0e1-8d5c-4a72-a68f-5a04624b9487",
    "nome": "23.5.5",
    "posicao_inicio": 147403,
    "posicao_fim": 147535,
    "preview": "Demonstrar incapacidade técnica, imperícia, imprudência ou\n    negligência da CO..."
  },
  {
    "id": "1f66b1cb-174e-4391-86c8-87e0f0d42425",
    "nome": "24.3.6",
    "posicao_inicio": 155791,
    "posicao_fim": 155917,
    "preview": "Os procedimentos de arbitragem serão conduzidos no idioma português\n    e o laud..."
  },
  {
    "id": "d92b9093-2d40-4224-a5a3-358d75fd2cb1",
    "nome": "15.8",
    "posicao_inicio": 124069,
    "posicao_fim": 124273,
    "preview": "A violação, pela CONTRATADA, do dever de confidencialidade previsto\n    nesta cl..."
  },
  {
    "id": "5fdbcf6a-c13f-4443-9dfc-2b017789d962",
    "nome": "12.10.1",
    "posicao_inicio": 117465,
    "posicao_fim": 117760,
    "preview": "Nomear o Gestor do Contrato, por escrito, com experiência comprovada\n    em ativ..."
  },
  {
    "id": "ce13b01c-5fb5-430d-8bf9-19d49ced1c91",
    "nome": "24.3.7",
    "posicao_inicio": 155940,
    "posicao_fim": 156045,
    "preview": "O Tribunal Arbitral não poderá arbitrar honorários sucumbenciais em\n    favor da..."
  },
  {
    "id": "51b1cb1b-2e6a-4731-bc59-66631f29c9cc",
    "nome": "10.8.4",
    "posicao_inicio": 105257,
    "posicao_fim": 105424,
    "preview": "Informar, quando solicitado, detalhadamente, os gastos incorridos\n    nos Serviç..."
  },
  {
    "id": "a013d65d-a53c-4bf0-94fd-b438234ac85f",
    "nome": "23.5.6",
    "posicao_inicio": 147558,
    "posicao_fim": 147719,
    "preview": "Praticar ato intencional, de natureza grave, assim entendido\n    conforme critér..."
  },
  {
    "id": "e75c02ad-1472-45de-ac7b-905de5c5eb6b",
    "nome": "12.10.2",
    "posicao_inicio": 117785,
    "posicao_fim": 117925,
    "preview": "Substituir o Gestor do Contrato no caso de falta, ausência ou\n    impedimento ev..."
  },
  {
    "id": "9cc6c1da-f4b8-4102-8f22-1b962499cfa9",
    "nome": "6.3",
    "posicao_inicio": 75977,
    "posicao_fim": 76289,
    "preview": "A CONTRATADA deverá apresentar o BMM ou o BM ao Gestor do Contrato\n    com a rel..."
  },
  {
    "id": "9a148b62-34c0-4191-8605-642d28dac07d",
    "nome": "23.5.7",
    "posicao_inicio": 147742,
    "posicao_fim": 147854,
    "preview": "Sofrer condenação em processos administrativos ou judiciais com\n    relação às L..."
  },
  {
    "id": "6b1b3f82-8bc0-4d62-baf8-f8d72a1b6e4d",
    "nome": "20.10",
    "posicao_inicio": 139372,
    "posicao_fim": 139822,
    "preview": "Existência ou possibilidade, seja no Brasil ou no exterior, de\n    qualquer inve..."
  },
  {
    "id": "a40b2868-9529-4e58-a2e0-f267ab4bc1f8",
    "nome": "23.5.8",
    "posicao_inicio": 147877,
    "posicao_fim": 147971,
    "preview": "Ficar impedida de executar o CONTRATO em razão de alteração na\n    legislação vi..."
  },
  {
    "id": "f35a6a30-d25c-484c-8645-670f91959e19",
    "nome": "12.10.3",
    "posicao_inicio": 117950,
    "posicao_fim": 118199,
    "preview": "Havendo alteração dos Gestor do Contrato pelas PARTES, comunicar\n    previamente..."
  },
  {
    "id": "f8ff2a55-5e66-46cd-a123-d7ac0f530bfe",
    "nome": "10.8.5",
    "posicao_inicio": 105447,
    "posicao_fim": 105833,
    "preview": "Caso aplicável, arcar com todos os custos e despesas decorrentes da\n    instalaç..."
  },
  {
    "id": "b06e2bf7-979d-4144-9b29-9b750f75e95c",
    "nome": "24.3.8",
    "posicao_inicio": 156068,
    "posicao_fim": 156614,
    "preview": "- Cada PARTE mantém o direito de buscar perante a jurisdição\n    competente as m..."
  },
  {
    "id": "195d9047-dfe9-4b55-87c6-88b285e3e536",
    "nome": "10.8.6",
    "posicao_inicio": 105856,
    "posicao_fim": 106043,
    "preview": "Quando aplicável, implantar SLA’s (níveis de serviço), acordados\n    entre as PA..."
  },
  {
    "id": "57574895-76a3-4149-a8fe-7431b97adc5b",
    "nome": "6.4",
    "posicao_inicio": 76306,
    "posicao_fim": 76845,
    "preview": "Em caso de não aceitação do BM ou BMM por parte da CONTRATANTE, as\n    medições ..."
  },
  {
    "id": "88ac14f8-a98c-45ce-ad8c-f29167ebb753",
    "nome": "20.11",
    "posicao_inicio": 139843,
    "posicao_fim": 140278,
    "preview": "Caso, na execução do objeto deste CONTRATO, os funcionários ou\n    representante..."
  },
  {
    "id": "b04e1de3-80ef-4dd6-aaeb-91d7c1da25e2",
    "nome": "24.4",
    "posicao_inicio": 156635,
    "posicao_fim": 156938,
    "preview": "A instauração e o procedimento arbitral não deverão influenciar a\n    execução d..."
  },
  {
    "id": "dbc702f2-eaa9-459b-b6a0-3d02d07b3c98",
    "nome": "6.5",
    "posicao_inicio": 76865,
    "posicao_fim": 77100,
    "preview": "Atrasos não justificados na liberação da medição, por motivos\n    imputáveis à C..."
  },
  {
    "id": "0748039e-519e-4d60-ba2c-31e84eb631a6",
    "nome": "10.8.7",
    "posicao_inicio": 106066,
    "posicao_fim": 106389,
    "preview": "Quando da demissão de seus FUNCIONÁRIOS, que venham a cumprir aviso\n    prévio t..."
  },
  {
    "id": "49803133-84e4-44c4-9bda-76b68e2cefae",
    "nome": "23.6",
    "posicao_inicio": 147992,
    "posicao_fim": 148698,
    "preview": "Nas hipóteses previstas na cláusula anterior, (i) a rescisão\n    operar-se-á de ..."
  },
  {
    "id": "c8b4cccf-4712-4ce9-9275-96e42dc462ba",
    "nome": "6.6",
    "posicao_inicio": 77117,
    "posicao_fim": 77215,
    "preview": "A elaboração, a entrega e a aprovação do BMM ou BM obedecerá ao\n    seguinte pro..."
  },
  {
    "id": "b7ba62ff-0b6b-4641-a319-d0f8e2ff4dd6",
    "nome": "10.8.8",
    "posicao_inicio": 106412,
    "posicao_fim": 106592,
    "preview": "Informar à CONTRATANTE acerca da ocorrência de qualquer fato,\n    incidente, aci..."
  },
  {
    "id": "075fd17f-278f-4bad-a63f-96ea6acd15f7",
    "nome": "24.5",
    "posicao_inicio": 156957,
    "posicao_fim": 157230,
    "preview": "A PARTE que violar a cláusula de arbitragem ou para prejudicar,\n    obstaculizar..."
  },
  {
    "id": "2cf104b5-385c-4289-8f73-6b90331a9cf1",
    "nome": "6.6.1",
    "posicao_inicio": 77234,
    "posicao_fim": 77461,
    "preview": "No último dia do PERÍODO DE MEDIÇÃO, a CONTRATADA emitirá o BM ou\n    BMM, que c..."
  },
  {
    "id": "402f0b4b-c5f5-4700-86fb-c99a07d22d1f",
    "nome": "10.8.9",
    "posicao_inicio": 106615,
    "posicao_fim": 106781,
    "preview": "Informar por escrito, para a CONTRATANTE, eventuais omissões,\n    contradições o..."
  },
  {
    "id": "d675f8a2-4b4c-4172-8ae2-51fd9702c3c0",
    "nome": "24.5.1",
    "posicao_inicio": 157251,
    "posicao_fim": 157559,
    "preview": "Entre outras, entendem-se como práticas violadoras da cláusula de\n    arbitragem..."
  },
  {
    "id": "16ba59dc-97ce-445f-be00-5b2fcd76d686",
    "nome": "23.7",
    "posicao_inicio": 148717,
    "posicao_fim": 149335,
    "preview": "Na hipótese de rescisão deste CONTRATO por culpa de uma das PARTES,\n    a PARTE ..."
  },
  {
    "id": "f6e9c1d3-c704-456f-b6eb-d10a00139315",
    "nome": "10.8.10",
    "posicao_inicio": 106805,
    "posicao_fim": 107067,
    "preview": "Realizar todos os treinamentos disponibilizados e/ou exigidos, a fim\n    de cump..."
  },
  {
    "id": "5e8ada09-3b63-4980-8fa5-e048f0eb1693",
    "nome": "6.6.2",
    "posicao_inicio": 77482,
    "posicao_fim": 77838,
    "preview": "O BMM ou BM será entregue pela CONTRATADA à CONTRATANTE, em via\n    física ou di..."
  },
  {
    "id": "97229734-f42c-4bac-b3b1-fdee926366ec",
    "nome": "24.5.2",
    "posicao_inicio": 157582,
    "posicao_fim": 157812,
    "preview": "A multa será exigida por meio de emissão de nota de débito ou\n    executada dire..."
  },
  {
    "id": "f8fad51d-ca31-4f31-90a7-6b0534aab372",
    "nome": "11.1",
    "posicao_inicio": 107126,
    "posicao_fim": 107348,
    "preview": "A CONTRATADA deverá isentar e defender a CONTRATANTE contra\n    quaisquer víncul..."
  },
  {
    "id": "450c9729-fb8b-45b5-996a-787bfe2571d5",
    "nome": "23.8",
    "posicao_inicio": 149354,
    "posicao_fim": 149665,
    "preview": "Antes da extinção do CONTRATO, a CONTRATADA deverá tomar todas as\n    providênci..."
  },
  {
    "id": "f93fcdea-4218-4630-91a6-3f05385d728c",
    "nome": "23.9",
    "posicao_inicio": 149684,
    "posicao_fim": 149876,
    "preview": "Uma vez distratado ou rescindido este CONTRATO, poderá a CONTRATANTE\n    entrega..."
  },
  {
    "id": "8efc94f6-4d52-444d-8c93-1c4180732f44",
    "nome": "24.6",
    "posicao_inicio": 157833,
    "posicao_fim": 158242,
    "preview": "A sentença arbitral será definitiva, irrecorrível (exceção feita à\n    hipótese ..."
  },
  {
    "id": "d9590a93-76a7-4e21-9ff3-a8ef9d8de750",
    "nome": "6.6.3",
    "posicao_inicio": 77859,
    "posicao_fim": 78379,
    "preview": "Caso a CONTRATANTE constate qualquer erro, imprecisão, falha no BM\n    ou BMM, i..."
  },
  {
    "id": "9cd08971-d5fd-467f-9e0f-166107d801bf",
    "nome": "24.7",
    "posicao_inicio": 158261,
    "posicao_fim": 158517,
    "preview": "Para a resolução de disputas que se refiram exclusivamente ao\n    COMODATO, , se..."
  },
  {
    "id": "b25b33a0-6500-432f-a4b6-69f8a8043424",
    "nome": "6.7",
    "posicao_inicio": 78398,
    "posicao_fim": 78656,
    "preview": "Para fechamento e aprovação do BM ou BMM, a CONTRATADA deverá\n    declarar a exi..."
  },
  {
    "id": "0f2a84f5-52a5-441a-a5cf-3a753f5fedec",
    "nome": "23.10",
    "posicao_inicio": 149896,
    "posicao_fim": 150204,
    "preview": "Ocorrendo uma ou mais das hipóteses de rescisão desta cláusula, e\n    não convin..."
  },
  {
    "id": "620c58d0-dc2d-441a-b962-e7118eb7f35b",
    "nome": "11.2",
    "posicao_inicio": 107367,
    "posicao_fim": 107998,
    "preview": "A CONTRATADA se obriga, ainda, a arcar com todas as despesas com\n    indenizaçõe..."
  },
  {
    "id": "361b4918-324a-4801-aca3-0037dd1a41f5",
    "nome": "6.8",
    "posicao_inicio": 78673,
    "posicao_fim": 78885,
    "preview": "O pleito deverá ser apresentado formalmente e por escrito junto à\n    CONTRATANT..."
  },
  {
    "id": "45d5922a-f5d5-4e0d-8e3f-3ab5214afc70",
    "nome": "6.8.1",
    "posicao_inicio": 78904,
    "posicao_fim": 79056,
    "preview": "A não apresentação do pleito até o mês seguinte à data da sua\n    ocorrência car..."
  },
  {
    "id": "64cef61b-e09a-4356-8d5b-725ff087a1dd",
    "nome": "6.9",
    "posicao_inicio": 79075,
    "posicao_fim": 79392,
    "preview": "A liberação do BM ou BMM não configura aceitação técnica, implícita\n    ou tácit..."
  },
  {
    "id": "a650e567-24d2-4fb2-b646-e8f8e510a500",
    "nome": "23.10.1",
    "posicao_inicio": 150227,
    "posicao_fim": 150964,
    "preview": "Quando aplicável, após o término dos Serviços, providenciar a\n    retirada, às s..."
  },
  {
    "id": "3deb337d-3583-486b-a644-0c9fe543b8d0",
    "nome": "11.2.1",
    "posicao_inicio": 108019,
    "posicao_fim": 108700,
    "preview": "Se, em decorrência da execução dos Serviços contratados, ocorrerem\n    incidente..."
  },
  {
    "id": "dc0b3c08-8bcd-4593-8dca-3ce862e2bef2",
    "nome": "6.10",
    "posicao_inicio": 79410,
    "posicao_fim": 79752,
    "preview": "Após aprovação do BM ou BMM, a CONTRATANTE autorizará a CONTRATADA a\n    emitir ..."
  },
  {
    "id": "08c131bc-6d2e-4afb-ba80-8aacf31061df",
    "nome": "11.2.2",
    "posicao_inicio": 108723,
    "posicao_fim": 109059,
    "preview": "A CONTRATADA será responsável por todas as ações ou omissões de seus\n    Funcion..."
  },
  {
    "id": "c700524a-17b9-4b6f-aa19-9cd389164f89",
    "nome": "23.11",
    "posicao_inicio": 150987,
    "posicao_fim": 151441,
    "preview": "A CONTRATANTE, após prévia notificação judicial, ou extrajudicial,\n    terá o di..."
  },
  {
    "id": "4e450b8f-adfb-4611-8bd3-fcf5458db5ad",
    "nome": "6.11",
    "posicao_inicio": 79771,
    "posicao_fim": 79952,
    "preview": "Os Serviços executados e aprovados serão medidos e liberados para\n    faturament..."
  },
  {
    "id": "39088172-7c48-4131-906c-007c5e7ed9de",
    "nome": "23.12",
    "posicao_inicio": 151462,
    "posicao_fim": 151587,
    "preview": "O Serviços executados até a data da extinção do CONTRATO serão\n    normalmente m..."
  },
  {
    "id": "8a971d91-b79e-4464-8d70-49f5235bc7e0",
    "nome": "6.12",
    "posicao_inicio": 79971,
    "posicao_fim": 80072,
    "preview": "As notas fiscais/faturas emitidas serão entregues pela CONTRATADA\n    conforme Q..."
  },
  {
    "id": "ebccdcb4-5961-45d0-b15d-2c309658c355",
    "nome": "23.13",
    "posicao_inicio": 151608,
    "posicao_fim": 151820,
    "preview": "Os direitos da CONTRATANTE relativos às consequências da extinção\n    antecipada..."
  },
  {
    "id": "227db34d-d36c-4a83-bc70-14562f0def6d",
    "nome": "11.3",
    "posicao_inicio": 109080,
    "posicao_fim": 109607,
    "preview": "Serão admitidas como exceções aos itens anteriores apenas as\n    ações/omissões ..."
  },
  {
    "id": "386c269f-66e8-4bee-a878-da623ab5eacc",
    "nome": "6.12.1",
    "posicao_inicio": 80093,
    "posicao_fim": 80379,
    "preview": "Obrigatoriamente, as notas fiscais/faturas deverão ser entregues ao\n    Gestor d..."
  },
  {
    "id": "5e5e9958-65f0-44d4-b6a7-8cf2fc249c6a",
    "nome": "6.12.2",
    "posicao_inicio": 80402,
    "posicao_fim": 80525,
    "preview": "Nenhuma nota fiscal/fatura poderá ser emitida anteriormente à\n    autorização ou..."
  },
  {
    "id": "5ea7a880-a07e-42a9-8d90-6aef1a91c134",
    "nome": "23.14",
    "posicao_inicio": 151841,
    "posicao_fim": 152271,
    "preview": "Na hipótese de extinção do CONTRATO, por qualquer motivo, as PARTES\n    se compr..."
  },
  {
    "id": "30ae564c-7c50-4f4a-a309-b0885722db28",
    "nome": "11.4",
    "posicao_inicio": 109626,
    "posicao_fim": 110210,
    "preview": "Fica expressamente convencionado que, se porventura, a CONTRATANTE\n    for conde..."
  },
  {
    "id": "574d00ca-3e19-4b77-9eae-c2856303c3c8",
    "nome": "6.13",
    "posicao_inicio": 80546,
    "posicao_fim": 80988,
    "preview": "Para estabelecimento do valor final a ser efetivamente pago pela\n    CONTRATANTE..."
  },
  {
    "id": "c0aba03f-09ab-4e28-9ccb-70e6864719a5",
    "nome": "6.14",
    "posicao_inicio": 81007,
    "posicao_fim": 81406,
    "preview": "É vedado à CONTRATADA, sob pena de rescisão, ceder total ou\n    parcialmente, of..."
  },
  {
    "id": "52b20a2a-09bc-4a13-885b-01eb520f9b31",
    "nome": "11.10",
    "posicao_inicio": 112109,
    "posicao_fim": 112407,
    "preview": "Caberá exclusivamente à CONTRATADA a reparação de eventuais danos ou\n    prejuíz..."
  },
  {
    "id": "2ddaf783-0ffe-4556-82ba-daf54192be34",
    "nome": "7.1",
    "posicao_inicio": 83120,
    "posicao_fim": 83357,
    "preview": "Se aplicável conforme assinalado no QUADRO RESUMO, o IMÓVEL e suas\n    benfeitor..."
  },
  {
    "id": "09dc3b1e-4a25-4e8c-a0a8-7e710b636cd1",
    "nome": "7.2",
    "posicao_inicio": 83374,
    "posicao_fim": 83634,
    "preview": "A CONTRATADA se obriga a manter e a devolver o IMÓVEL à CONTRATANTE,\n    quando ..."
  },
  {
    "id": "4ba6c238-a68e-430e-978e-0187cb640341",
    "nome": "11.11",
    "posicao_inicio": 112428,
    "posicao_fim": 112950,
    "preview": "A CONTRATADA é a única responsável pelas obrigações decorrentes dos\n    contrato..."
  },
  {
    "id": "a71802e5-b554-45c5-a8d9-91852173b4c8",
    "nome": "7.3",
    "posicao_inicio": 83651,
    "posicao_fim": 83976,
    "preview": "Havendo necessidade de expansão das instalações inerentes à execução\n    das ati..."
  },
  {
    "id": "5a8cf3b1-b66e-417c-88a5-7a73d8c966a9",
    "nome": "7.16",
    "posicao_inicio": 87638,
    "posicao_fim": 87819,
    "preview": "Responsabilizar-se pelos custos de toda e qualquer manutenção\n    corretiva caus..."
  },
  {
    "id": "b90e3597-47c6-4f12-8560-f3a7f8556659",
    "nome": "7.17",
    "posicao_inicio": 87838,
    "posicao_fim": 88036,
    "preview": "Adotar as especificações do Caderno de Especificações do Plano\n    Diretor de In..."
  },
  {
    "id": "4a147d10-2540-4cf2-af32-9e16503ffc93",
    "nome": "23.15",
    "posicao_inicio": 152292,
    "posicao_fim": 152979,
    "preview": "A CONTRATADA deverá desocupar inteiramente o LOCAL DE PRESTAÇÃO DOS\n    SERVIÇOS..."
  },
  {
    "id": "d40992a7-6c33-40b3-93f0-4d7df83c1097",
    "nome": "11.5",
    "posicao_inicio": 110229,
    "posicao_fim": 110918,
    "preview": "A CONTRATADA deverá se responsabilizar pelo estudo e avaliação das\n    especific..."
  },
  {
    "id": "4bf49726-ab62-4b3b-a580-15a0370bf73b",
    "nome": "6.15",
    "posicao_inicio": 81425,
    "posicao_fim": 81679,
    "preview": "Os pagamentos impugnados pela CONTRATANTE não estão sujeitos a\n    qualquer atua..."
  },
  {
    "id": "a0f1f99b-6146-4e40-9fb8-4442062a6bb9",
    "nome": "6.16",
    "posicao_inicio": 81698,
    "posicao_fim": 81800,
    "preview": "A CONTRATANTE não aceitará travamento bancário ou qualquer\n    instrumento finan..."
  },
  {
    "id": "a7b90583-68ae-4cf1-821c-deece084eb47",
    "nome": "11.6",
    "posicao_inicio": 110937,
    "posicao_fim": 111212,
    "preview": "Caso os Serviços devam ser sustados e/ou refeitos por estarem não\n    conformes ..."
  },
  {
    "id": "7d1e5cd9-08c6-4bad-8186-e8dc5a9f3174",
    "nome": "6.17",
    "posicao_inicio": 81819,
    "posicao_fim": 82268,
    "preview": "Caso ocorra comprovado descumprimento de quaisquer obrigações\n    contratuais, r..."
  },
  {
    "id": "77591f16-2735-4b25-9aeb-631035256482",
    "nome": "11.7",
    "posicao_inicio": 111231,
    "posicao_fim": 111543,
    "preview": "A CONTRATADA deverá promover a substituição, sempre que solicitado\n    justifica..."
  },
  {
    "id": "e514640b-e7ef-40fb-be37-e49b34669f89",
    "nome": "11.8",
    "posicao_inicio": 111562,
    "posicao_fim": 111749,
    "preview": "Eventuais limitações de responsabilidade contidas nesse CONTRATO não\n    se apli..."
  },
  {
    "id": "7b901ffe-2d2c-4991-8a78-b317523c1274",
    "nome": "6.17.1",
    "posicao_inicio": 82289,
    "posicao_fim": 82661,
    "preview": "As importâncias retidas na forma do item acima, acima, serão\n    liberadas à CON..."
  },
  {
    "id": "9df92416-728a-4c56-ae5c-7406be0b36d0",
    "nome": "11.9",
    "posicao_inicio": 111768,
    "posicao_fim": 112089,
    "preview": "A CONTRATADA deverá providenciar para que não haja qualquer parada\n    ou atraso..."
  },
  {
    "id": "3e59fb7f-d4fc-47aa-8248-0a932c815e05",
    "nome": "7.18",
    "posicao_inicio": 88055,
    "posicao_fim": 88184,
    "preview": "Apresentar à CONTRATANTE, sempre que solicitado, todas as\n    informações necess..."
  },
  {
    "id": "632824b9-64fc-48e2-b179-c17c9ba4df57",
    "nome": "12.1",
    "posicao_inicio": 113009,
    "posicao_fim": 113475,
    "preview": "A CONTRATANTE exercerá a fiscalização sobre a execução do CONTRATO\n    através d..."
  },
  {
    "id": "ef562751-4930-4d6d-82ce-d18b12768dab",
    "nome": "12.2",
    "posicao_inicio": 113494,
    "posicao_fim": 113679,
    "preview": "A CONTRATANTE acompanhará a execução do CONTRATO através de uma\n    equipe integ..."
  },
  {
    "id": "e10d47c9-2a7e-454d-a3fc-3867467cc72d",
    "nome": "7.4",
    "posicao_inicio": 83993,
    "posicao_fim": 84433,
    "preview": "Caso a CONTRATANTE solicite acréscimo de Funcionários ao Contrato e\n    as insta..."
  },
  {
    "id": "c67869c3-4fc8-4adb-8786-b1ccfe692f29",
    "nome": "12.2.1",
    "posicao_inicio": 113700,
    "posicao_fim": 113900,
    "preview": "Havendo alteração dos gestores, as PARTES deverão comunicar a outra\n    PARTE po..."
  },
  {
    "id": "25bd6e34-2c9e-4d9e-9b8b-f51c4bc914b4",
    "nome": "7.5",
    "posicao_inicio": 84450,
    "posicao_fim": 84841,
    "preview": "Quaisquer bens acessórios, melhorias e/ou benfeitorias porventura\n    realizadas..."
  },
  {
    "id": "5c66479e-7260-4bea-9823-627e336cc9db",
    "nome": "12.3",
    "posicao_inicio": 113921,
    "posicao_fim": 114102,
    "preview": "O Gestor do Contrato estará à disposição da CONTRATADA para fornecer\n    as info..."
  },
  {
    "id": "4b74d7bc-d5e2-40e3-8a9c-90c125273a09",
    "nome": "12.4",
    "posicao_inicio": 114121,
    "posicao_fim": 114373,
    "preview": "O Gestor do Contrato terá acesso a todos os locais onde os Serviços\n    se reali..."
  },
  {
    "id": "1e648d04-739d-4a1f-9218-87122dbd2de6",
    "nome": "7.6",
    "posicao_inicio": 84858,
    "posicao_fim": 85251,
    "preview": "Para a realização de qualquer intervenção no IMÓVEL, deverá a\n    CONTRATADA obs..."
  },
  {
    "id": "5ab0a2f7-c9f0-4f66-960a-4140a4de3f5d",
    "nome": "7.7",
    "posicao_inicio": 85268,
    "posicao_fim": 85577,
    "preview": "Antes de iniciar qualquer intervenção no IMÓVEL, como supressão de\n    vegetação..."
  },
  {
    "id": "e47d7e84-e787-4231-b583-cc40b624a7fb",
    "nome": "7.8",
    "posicao_inicio": 85594,
    "posicao_fim": 85814,
    "preview": "Em caso de danos diretos e/ou indiretos causados ao IMÓVEL e seus\n    bens acess..."
  },
  {
    "id": "dc09892e-6721-4257-8e81-8c01f9fddebd",
    "nome": "7.9",
    "posicao_inicio": 85831,
    "posicao_fim": 86344,
    "preview": "A CONTRATANTE poderá solicitar à CONTRATADA a extinção do COMODATO a\n    qualque..."
  },
  {
    "id": "ea41c866-4658-4da3-a260-174717a002ab",
    "nome": "7.10",
    "posicao_inicio": 86362,
    "posicao_fim": 86528,
    "preview": "O IMÓVEL não poderá ser objeto de cessão, transferência, sublocação\n    total ou..."
  },
  {
    "id": "8eafce3d-363a-4d4e-80b1-abd9f3ce4d92",
    "nome": "7.11",
    "posicao_inicio": 86547,
    "posicao_fim": 86726,
    "preview": "No caso de extinção do presente CONTRATO por quaisquer razões,\n    cumprirá à CO..."
  },
  {
    "id": "b1136197-7998-4574-93d6-234d7c8038b6",
    "nome": "7.12",
    "posicao_inicio": 86745,
    "posicao_fim": 86889,
    "preview": "Não caberá à CONTRATADA o direito a qualquer tipo de compensação,\n    ressarcime..."
  },
  {
    "id": "157eb781-aa36-4343-a544-5767f331d3e0",
    "nome": "7.13",
    "posicao_inicio": 86908,
    "posicao_fim": 86972,
    "preview": "Relativamente ao comodato, são obrigações da CONTRATADA:..."
  },
  {
    "id": "62606aa0-af7e-4a75-b46b-f286ca18000d",
    "nome": "7.14",
    "posicao_inicio": 86991,
    "posicao_fim": 87296,
    "preview": "Utilizar o IMÓVEL e seus bens acessórios, somente para a FINALIDADE\n    EXCLUSIV..."
  },
  {
    "id": "fa3261cb-3cb6-4cc6-8b8f-c18515cee0b3",
    "nome": "7.15",
    "posicao_inicio": 87315,
    "posicao_fim": 87619,
    "preview": "Arcar com todas e quaisquer despesas de mobiliário, incluindo, mas\n    não se li..."
  },
  {
    "id": "9436b2e3-7679-4f98-9822-2b16b20d1798",
    "nome": "7.19",
    "posicao_inicio": 88203,
    "posicao_fim": 88571,
    "preview": "Manter o IMÓVEL e seus bens acessórios em perfeito estado de guarda\n    e conser..."
  },
  {
    "id": "cafd69d6-a7af-487d-874a-eff7cce80951",
    "nome": "7.20",
    "posicao_inicio": 88590,
    "posicao_fim": 88786,
    "preview": "Informar por escrito e imediatamente à CONTRATANTE sobre qualquer\n    defeito ou..."
  },
  {
    "id": "27f89766-680f-42b0-be54-b5772f4fbf80",
    "nome": "7.21",
    "posicao_inicio": 88805,
    "posicao_fim": 88861,
    "preview": "Proteger o IMÓVEL contra turbações de terceiros...."
  },
  {
    "id": "1ead33be-fc1b-4869-b66a-46d535667c11",
    "nome": "7.22",
    "posicao_inicio": 88880,
    "posicao_fim": 89057,
    "preview": "Indenizar os prejuízos porventura causados em decorrência da\n    utilização do I..."
  },
  {
    "id": "847289ea-badf-4a97-8efb-ebd502ab09c7",
    "nome": "7.23",
    "posicao_inicio": 89076,
    "posicao_fim": 89259,
    "preview": "Permitir a inspeção do IMÓVEL pela CONTRATANTE, obrigando-se, para\n    tanto, a ..."
  },
  {
    "id": "f6c45137-b4b7-42e4-8315-8b0e84a502c4",
    "nome": "7.24",
    "posicao_inicio": 89278,
    "posicao_fim": 89422,
    "preview": "Promover todas as medidas necessárias para que suas atividades no\n    IMÓVEL não..."
  },
  {
    "id": "b32dff9e-8bd5-41ef-947d-bb03be8d0fdb",
    "nome": "7.25",
    "posicao_inicio": 89441,
    "posicao_fim": 89576,
    "preview": "Restringir sua ocupação à área delimitada pela Planta e Memorial\n    Descritivo ..."
  },
  {
    "id": "b342ade0-ced0-4098-9e6f-5b34cf7a8180",
    "nome": "7.26",
    "posicao_inicio": 89595,
    "posicao_fim": 89764,
    "preview": "Fornecer toda direção, supervisão técnica e administrativa e toda\n    força de t..."
  },
  {
    "id": "6cd677cd-e8c1-4f28-8478-45d1b0a69fd7",
    "nome": "7.27",
    "posicao_inicio": 89783,
    "posicao_fim": 90282,
    "preview": "Contratar seguro de incêndio para o IMÓVEL, bem como a manutenção,\n    em perfei..."
  },
  {
    "id": "eed6d5d3-18af-4f8d-917c-005f7c44142b",
    "nome": "8",
    "posicao_inicio": 90298,
    "posicao_fim": 90341,
    "preview": "DISPONIBILIZAÇÃO DE BENS E SERVIÇOS..."
  },
  {
    "id": "2b1430ff-5a36-4aa5-9354-262b1e84034b",
    "nome": "8.2",
    "posicao_inicio": 91099,
    "posicao_fim": 91505,
    "preview": "Quando aplicável, as instalações, mobiliário, equipamentos,\n    aparelhos e uten..."
  },
  {
    "id": "bec4c31a-4d7c-4f31-b10a-b6d52a0bc714",
    "nome": "8.2.1",
    "posicao_inicio": 91524,
    "posicao_fim": 91730,
    "preview": "O(s) bem(ns) cedido(s) em comodato será(ão) utilizado(s) pela\n    CONTRATADA exc..."
  },
  {
    "id": "aceaf455-5759-4f70-97c3-74a48303c306",
    "nome": "8.2.2",
    "posicao_inicio": 91751,
    "posicao_fim": 92189,
    "preview": "A CONTRATADA declara receber o (s) bem (ns) em perfeitas condições\n    de conser..."
  },
  {
    "id": "2befde22-1772-48b4-bec6-a16385b34f13",
    "nome": "9",
    "posicao_inicio": 92206,
    "posicao_fim": 92239,
    "preview": "OBRIGAÇÕES DA CONTRATANTE..."
  },
  {
    "id": "89e22284-31c8-4e78-9af7-d9f72e53d01f",
    "nome": "9.1",
    "posicao_inicio": 92254,
    "posicao_fim": 92346,
    "preview": "São obrigações da CONTRATANTE, sem prejuízo das demais previstas\n    neste CONTR..."
  },
  {
    "id": "6a045d76-89e5-4d9f-b5e1-44299a4b470c",
    "nome": "9.1.1",
    "posicao_inicio": 92365,
    "posicao_fim": 92458,
    "preview": "Efetuar as medições e remunerar a CONTRATADA na forma prevista neste\n    instrum..."
  },
  {
    "id": "eb54f2e1-70a9-484f-960b-07bcdd790ec9",
    "nome": "9.1.2",
    "posicao_inicio": 92479,
    "posicao_fim": 92644,
    "preview": "Fornecer à CONTRATADA as informações que guardem conexão com o\n    objeto deste ..."
  },
  {
    "id": "3414f9a8-f129-42cc-9a27-2cf519f2693b",
    "nome": "9.1.3",
    "posicao_inicio": 92665,
    "posicao_fim": 92739,
    "preview": "Estabelecer as diretrizes para a implantação do objeto contratado...."
  },
  {
    "id": "16955c16-a03c-4b63-b69e-4052f21aed75",
    "nome": "9.1.4",
    "posicao_inicio": 92760,
    "posicao_fim": 92850,
    "preview": "Instruir a CONTRATADA quanto a normas e procedimentos internos da\n    CONTRATANT..."
  },
  {
    "id": "2609e09c-f65c-412f-aea0-b1abab5a76ae",
    "nome": "9.1.5",
    "posicao_inicio": 92871,
    "posicao_fim": 93019,
    "preview": "Credenciar, por escrito, junto à CONTRATADA, um representante do seu\n    próprio..."
  },
  {
    "id": "284d3a0b-1240-448e-a201-a4fef03d1489",
    "nome": "9.1.6",
    "posicao_inicio": 93040,
    "posicao_fim": 93192,
    "preview": "Quando aplicável, providenciar em tempo hábil, todas as licenças e\n    autorizaç..."
  },
  {
    "id": "42988228-46dc-4210-b863-0a3cdeac25cb",
    "nome": "9.1.8",
    "posicao_inicio": 93294,
    "posicao_fim": 93741,
    "preview": "Fornecer alimentação (Desjejum, almoço, lanches e jantar) aos\n    Funcionários d..."
  },
  {
    "id": "3b96285c-4972-427c-a21b-3cdcb3026c8b",
    "nome": "10",
    "posicao_inicio": 93759,
    "posicao_fim": 93791,
    "preview": "OBRIGAÇÕES DA CONTRATADA..."
  },
  {
    "id": "a5e36fd9-d9f3-48cc-afbd-b0fb19eefaf1",
    "nome": "10.1",
    "posicao_inicio": 93808,
    "posicao_fim": 93899,
    "preview": "São obrigações da CONTRATADA, sem prejuízo das demais previstas\n    neste CONTRA..."
  },
  {
    "id": "1503e9e1-fb1d-402c-9208-cce13c73e2c8",
    "nome": "10.2",
    "posicao_inicio": 93918,
    "posicao_fim": 93957,
    "preview": "Quanto à força de trabalho~~:~~..."
  },
  {
    "id": "15ad9639-19e8-4cb3-9ffd-9609c8fe55ee",
    "nome": "10.2.1",
    "posicao_inicio": 93978,
    "posicao_fim": 94195,
    "preview": "Fornecer toda a direção, supervisão técnica e administrativa, e toda\n    a força..."
  },
  {
    "id": "fb03146a-9bc8-4f5c-9c03-1238b8dc58a9",
    "nome": "10.2.2",
    "posicao_inicio": 94218,
    "posicao_fim": 94473,
    "preview": "utilizar pessoal qualificado e em número suficiente para execução\n    dos Serviç..."
  },
  {
    "id": "65675162-4d91-4e9f-ae44-c785bf7a07d5",
    "nome": "10.2.3",
    "posicao_inicio": 94496,
    "posicao_fim": 94679,
    "preview": "Providenciar e custear, quando da desmobilização envolvendo\n    empregados de ou..."
  },
  {
    "id": "dbaf137b-9737-46b5-99f7-6db9ed0e1085",
    "nome": "10.3",
    "posicao_inicio": 94700,
    "posicao_fim": 94751,
    "preview": "Quanto à assistência aos seus Funcionários:..."
  },
  {
    "id": "29b79b52-4ab0-490e-8c5f-a65926242977",
    "nome": "10.3.1",
    "posicao_inicio": 94772,
    "posicao_fim": 94913,
    "preview": "Quando houver desligamento de Colaborador de outras localidades,\n    providencia..."
  },
  {
    "id": "95413954-425c-4ef7-ae93-b41b35f112a0",
    "nome": "10.3.2",
    "posicao_inicio": 94936,
    "posicao_fim": 95163,
    "preview": "Realizar o cadastro de seus empregados através de plataforma\n    disponibilizada..."
  },
  {
    "id": "d8f92d19-3432-4a40-85ae-caf55f076559",
    "nome": "10.4",
    "posicao_inicio": 95184,
    "posicao_fim": 95220,
    "preview": "Quanto a custeio e encargos:..."
  },
  {
    "id": "b690d5a3-bf3b-4e41-9624-dceaa65c0cd8",
    "nome": "10.4.1",
    "posicao_inicio": 95241,
    "posicao_fim": 95636,
    "preview": "Custear, como única empregadora - e fazer com que seus\n    subcontratados também..."
  },
  {
    "id": "11eb9a67-5e63-426f-a1c9-9bc832de2b50",
    "nome": "10.4.2",
    "posicao_inicio": 95659,
    "posicao_fim": 95973,
    "preview": "Disponibilizar, sempre que requisitado pela CONTRATANTE, toda\n    documentação r..."
  },
  {
    "id": "8c08bf86-84f8-440a-a7fb-71da98dfb456",
    "nome": "10.4.3",
    "posicao_inicio": 95996,
    "posicao_fim": 96293,
    "preview": "Apresentar, mensalmente, junto com o BM ou BMM e com a nota fiscal\n    de fatura..."
  },
  {
    "id": "813d5eb4-a60a-4c17-9459-929910638876",
    "nome": "10.4.4",
    "posicao_inicio": 96316,
    "posicao_fim": 96666,
    "preview": "Apresentar ao Gestor do Contrato, quando do início dos Serviços, os\n    comprova..."
  },
  {
    "id": "ff82b7ff-4825-4a87-9d66-9ab17d256b45",
    "nome": "10.5",
    "posicao_inicio": 96687,
    "posicao_fim": 96742,
    "preview": "Quanto às relações nas unidades da CONTRATANTE:..."
  },
  {
    "id": "dd0b2540-cc4c-4039-9f40-51f5542c7fb6",
    "nome": "10.5.1",
    "posicao_inicio": 96763,
    "posicao_fim": 97039,
    "preview": "Cumprir e fazer cumprir o Manual de Saúde e Segurança no Trabalho\n    (anexo), b..."
  },
  {
    "id": "f493bb26-3bf1-4a96-975c-aefa1029e2fd",
    "nome": "10.5.2",
    "posicao_inicio": 97062,
    "posicao_fim": 97666,
    "preview": "Quando aplicável, e nos casos em que houver necessidade dos\n    Funcionários da ..."
  },
  {
    "id": "cca77cc8-3a60-45bf-be6c-7cc124871375",
    "nome": "10.5.3",
    "posicao_inicio": 97689,
    "posicao_fim": 97975,
    "preview": "Fixar seus horários de trabalho de modo compatível com os adotados\n    pela CONT..."
  },
  {
    "id": "665d462e-c0a9-41c7-871c-1308294d811b",
    "nome": "10.5.4",
    "posicao_inicio": 97998,
    "posicao_fim": 98338,
    "preview": "Não permitir que o seus Funcionários, máquinas, veículos e\n    equipamentos a se..."
  },
  {
    "id": "f90371d0-7e2d-4b32-920d-ad460fce628f",
    "nome": "10.5.5",
    "posicao_inicio": 98361,
    "posicao_fim": 98649,
    "preview": "Não permitir que, fora dos horários de trabalho, seus Funcionários\n    circulem ..."
  },
  {
    "id": "4e1acb9f-2dd9-430a-b9cc-8fc7fa4299c7",
    "nome": "10.5.6",
    "posicao_inicio": 98672,
    "posicao_fim": 98852,
    "preview": "Providenciar a substituição ou retirada imediata de qualquer\n    Colaborador, cu..."
  },
  {
    "id": "bd72a3a5-6262-4493-9bcd-2226208506c9",
    "nome": "10.5.7",
    "posicao_inicio": 98875,
    "posicao_fim": 99390,
    "preview": "Providenciar os cadastros de todos os seus Funcionários que\n    adentrarem nas u..."
  },
  {
    "id": "366fcf55-6abb-44c4-8c99-33263a98d44f",
    "nome": "10.5.8",
    "posicao_inicio": 99413,
    "posicao_fim": 99788,
    "preview": "Responsabilizar-se pelos bens e pela segurança do LOCAL DE PRESTAÇÃO\n    DOS SER..."
  },
  {
    "id": "9a1ce9bb-79e7-4be8-8f69-7ecdfa2918d7",
    "nome": "10.5.9",
    "posicao_inicio": 99811,
    "posicao_fim": 100060,
    "preview": "Pedir autorização, prévia e por escrito, à segurança empresarial da\n    CONTRATA..."
  },
  {
    "id": "a79a8f7d-5c93-4a66-b09b-78304b7bd545",
    "nome": "10.5.10",
    "posicao_inicio": 100084,
    "posicao_fim": 100610,
    "preview": "Quando aplicável, envolver a área de segurança empresarial nas\n    reuniões de p..."
  },
  {
    "id": "5c44caf3-c379-407c-9293-2dcf24eb9d5b",
    "nome": "10.6.1",
    "posicao_inicio": 100634,
    "posicao_fim": 101003,
    "preview": "Quanto a registros e legalizações:\n\n    1.  Quando aplicável, promover o registr..."
  },
  {
    "id": "184244da-202e-451a-a417-afe1115bc65a",
    "nome": "10.6.2",
    "posicao_inicio": 101026,
    "posicao_fim": 101420,
    "preview": "Manter, até o término do CONTRATO, o arquivo completo da\n    documentação refere..."
  },
  {
    "id": "ff8c5acf-fef1-4d76-abed-fdbe1b9f264f",
    "nome": "10.6.3",
    "posicao_inicio": 101443,
    "posicao_fim": 101864,
    "preview": "No caso de serviço de engenharia e arquitetura a CONTRATADA deverá\n    apresenta..."
  }
]

---

## DOCUMENTO ANTERIOR (DOCUMENTO ORIGINAL (sem tags))

```text
[P001] CONTRATO DE PRESTAÇÃO DE SERVIÇOS
[P006] CONTRATANTE e CONTRATADA, doravante denominadas em conjunto “PARTES” e individualmente “PARTE”, ajustam entre si o presente CONTRATO DE PRESTAÇÃO DE SERVIÇOS (“CONTRATO”), que se regerá pelo QUADRO RESUMO e pelas Condições Gerais abaixo, modificadas, se cabível, pelas CONDIÇÕES ESPECIAIS.
[P008] CONDIÇÕES GERAIS
[P012] OBJETO
[P014] A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no campo Serviços do QUADRO RESUMO, os quais serão prestados conforme disciplinado neste CONTRATO.
[P016] Este CONTRATO não implica em nenhum dever de exclusividade da CONTRATANTE, que poderá firmar contratos com outras empresas para os mesmos fins, de acordo com seus interesses.
[P018] Os ANEXOS “Documentos Contratuais Gerais” ficam dispensados de rubrica ou validação digital posterior. A CONTRATADA declara que já recebeu estes ANEXOS previamente em mídia eletrônica ou outra forma de acesso, que tem ciência do seu conteúdo e que concorda com os termos neles contidos, comprometendo-se a cumpri-los na sua integralidade.
[P020] Os termos do QUADRO RESUMO prevalecem sobre os termos destas Condições Gerais os quais prevalecem sobre os termos dos ANEXOS. Na hipótese de conflitos entre os ANEXOS, prevalecerão uns sobre os outros na ordem em que se acham listados no QUADRO RESUMO acima.
[P022] A CONTRATADA, em nenhuma hipótese, poderá alegar, como justificativa ou defesa, o desconhecimento, incompreensão, dúvida, no todo ou em parte, das disposições do presente CONTRATO e demais disposições de ordem geral ou particular nele estabelecidas, que são, desde já, consideradas necessárias e suficientes para definir os Serviços e os fornecimentos contidos no que foi contratado, e, ainda, permitir a sua execução de acordo com as normas vigentes no País, sendo vedado à CONTRATADA pleitear qualquer revisão de preços ou prorrogação de prazo, por erros ou omissões, que tenham sido cometidos na elaboração de sua(s) Proposta(s) que integra(m) o CONTRATO.
[P024] A CONTRATADA declara ter ciência das condições da região onde se localizam as instalações da CONTRATANTE, assumindo exclusiva responsabilidade pelo perfeito conhecimento das diversas condicionantes que possam afetar os Serviços, entre as quais, mas sem limitação, se encontram: transporte, acesso, manuseio e armazenagem de materiais/equipamentos, disponibilidade e qualidade de força de trabalho, água e energia elétrica, disponibilidade e estado de estradas e vias de acesso, condições climáticas, hidrológicas, hidrometeorológicas, pluviométricas, físicas e ainda os regulamentos e normas vigentes no LOCAL DE PRESTAÇÃO DOS SERVIÇOS. Em função disto, a CONTRATADA renuncia a quaisquer reivindicações ou compensações adicionais sobre qualquer falha na avaliação adequada das dificuldades locais.
[P026] VIGÊNCIA E SUSPENSÃO
[P028] O CONTRATO terá vigência a partir do INÍCIO DA VIGÊNCIA e encerrará (i) após o TÉRMINO DA VIGÊNCIA indicado no QUADRO RESUMO, (ii) após o cumprimento de todas as obrigações do CONTRATO e/ou dele decorrentes ou (iii) no caso de atingido o valor estabelecido neste instrumento, o que ocorrer primeiro, independentemente de qualquer notificação judicial ou extrajudicial.
[P030] Se aplicável, a retroatividade dos efeitos do CONTRATO, não ocasionará qualquer prejuízo das obrigações da CONTRATADA sem acarretar quaisquer penalidades, compensação ou lucros cessantes para a CONTRATANTE, conforme prazo descrito no QUADRO RESUMO.
[P032] O PRAZO DE VIGÊNCIA já considera todos os dias necessários para as providências prévias e finais, incluindo eventual mobilização, execução e desmobilização, por parte da CONTRATADA.
[P034] Havendo interesse entre as PARTES, este CONTRATO poderá ter sua vigência prorrogada, mediante assinatura de Termo Aditivo formalizado entre as PARTES.
[P036] O CONTRATO poderá ser suspenso total ou parcialmente, independente da anuência da CONTRATADA e/ou de procedimento judicial, mediante comunicação por escrito da CONTRATANTE à CONTRATADA enviada com antecedência mínima de 30 (trinta) DIAS, salvo se, por determinação do Poder Público ou Judiciário, for previsto menor prazo.
[P038] A CONTRATADA deverá reassumir a execução do CONTRATO em até 30 (trinta) DIAS após recebimento de comunicação expressa pela CONTRATANTE, se outro prazo não for acordado entre as PARTES.
[P040] A CONTRATADA não terá direito de indenização de qualquer natureza em razão da suspensão dos Serviços, exceto em relação a valores justificados e comprovados pela CONTRATADA que sejam aprovados pela CONTRATANTE, conforme exclusivo critério da CONTRATANTE.
[P042] VALOR, PREÇOS E FORMA DE PAGAMENTO
[P044] Para fins legais e contratuais, inclusive para aplicação de multas e penalidades, deve ser considerado VALOR ESTIMADO DO CONTRATO. Sendo o valor estimado, a CONTRATADA não poderá (i) receber todo o VALOR ESTIMADO DO CONTRATO sem que tenha efetivamente prestado os Serviços correspondentes ou (ii) pretender atingir todo o VALOR ESTIMADO DO CONTRATO, sem que a CONTRATANTE tenha, a seu exclusivo critério, autorizado a prestação de Serviços.
[P046] Caso o dia do pagamento devido pela CONTRATANTE se dê em feriados bancários ou em finais de semana, será considerado como data de vencimento o primeiro dia útil subsequente.
[P048] Os pagamentos serão efetuados pela CONTRATANTE mediante crédito em conta corrente, sendo para todos os fins o comprovante bancário considerado prova de pagamento. No caso de mudança de estabelecimento bancário ou número da conta corrente, a CONTRATADA deverá comunicar ao Gestor do Contrato, com antecedência mínima de 30 (trinta) DIAS o novo estabelecimento ou a nova conta, sob pena de o depósito ser efetuado na conta anteriormente indicada.
[P050] A ausência de qualquer contestação por parte da CONTRATADA, no prazo de 60 (sessenta) DIAS, contados da data do depósito, deverá caracterizar a quitação plena, rasa, geral e irrevogável, conferida pela CONTRATADA à CONTRATANTE, relativamente ao pagamento dos materiais ou Serviços lançados na nota fiscal/fatura respectiva, não cabendo, nessa hipótese, à CONTRATADA, qualquer reivindicação, a qualquer título.
[P052] Se os pagamentos efetuados na forma deste item forem superiores aos valores efetivamente devidos, responderá a CONTRATADA pelas diferenças, que poderão ser descontadas de pagamentos futuros, inclusive relativos a outros créditos que a CONTRATADA tenha junto à CONTRATANTE.
[P054] CORREÇÃO MONETÁRIA
[P056] Se aplicável, a partir do 12º mês contado da data-base, a CONTRATADA poderá solicitar, anualmente, o reajuste dos preços praticados no CONTRATO mediante a aplicação do ÍNDICE DE REAJUSTE indicado no QUADRO RESUMO. A atualização com base no ÍNDICE DE REAJUSTE somente será aplicada sobre os preços unitários do CONTRATO e após negociação entre as PARTES, aprovação por escrito da CONTRATANTE, formalização de aditivo contratual e autorização de faturamento pela CONTRATANTE.
[P058] Caso o reajuste seja solicitado em prazo superior a 90 (noventa) dias após a data-base, os preços reajustados somente serão aplicados aos serviços/fornecimentos realizados após a data de solicitação do reajuste, não retroagindo aos serviços/fornecimentos realizados anteriormente.
[P060] Uma vez reajustados, os valores permanecerão fixos por novo período de 12 (doze) meses, quando então os valores remanescentes poderão ser reajustados.
[P062] A aplicação do ÍNDICE DE CORREÇÃO MONETÁRIA ocorrerá apenas a partir da primeira medição subsequente ao período da data-base, não sendo admitida a aplicação retroativa sobre a medição em curso. Fica expressamente vedada a utilização, em uma mesma medição, de valores distintos decorrentes de atualização parcial, de modo que os serviços/fornecimentos faturados em cada medição estarão integralmente sujeitos às condições vigentes (com ou sem atualização), conforme a sua competência temporal.
[P064] A CORREÇÃO MONETÁRIA não incidirá sobre: (i) valores pagos em atraso em razão de eventos de responsabilidade da CONTRATADA; (ii) valores eventualmente devidos pela CONTRATADA à CONTRATANTE, isto é, os itens (i) a (ii) serão deduzidos da base de cálculo para fins de CORREÇÃO MONETÁRIA, de modo que somente o saldo contratual remanescente estará sujeito à aplicação do  ÍNDICE DE CORREÇÃO MONETÁRIA.
[P066] O ÍNDICE DE CORREÇÃO MONETÁRIA do CONTRATO será aplicado unicamente pelas previsões contidas nesta cláusula, não devendo se vincular a qualquer tipo de previsões contidas em propostas, convenções coletivas, acordos coletivos e afins.
[P068] TRIBUTOS
[P070] Todas as obrigações tributárias principais e acessórias que incidam ou venham a incidir, direta ou indiretamente sobre os Serviços são de responsabilidade da CONTRATADA, que deverá, quando a legislação não exigir da CONTRATANTE a obrigação de retenção, comprovar o cumprimento de tais obrigações à CONTRATANTE.
[P072] A CONTRATADA declara estar ciente de que, no momento do pagamento, a CONTRATANTE observará a legislação vigente referente à retenção do Imposto Sobre Serviços de Qualquer Natureza (ISSQN), do Imposto sobre a Renda (IR), da Contribuição Social sobre o Lucro Líquido (CSLL), da Contribuição para o Programa de Integração Social (PIS) e da Contribuição para o Financiamento da Seguridade Social (COFINS), sendo que, na medida de sua aplicabilidade, procederá à retenção dos aludidos tributos.
[P074] Eventuais alterações na legislação que impactem na tributação relativa a este CONTRATO, para mais ou para menos, serão objeto de análise e negociação entre as PARTES, de modo a se determinar a sua influência final sobre os preços contratuais.
[P076] As despesas decorrentes de ações administrativas/judiciais visando discutir atos do Poder Público que alterem os encargos acima indicados, serão de exclusiva responsabilidade da CONTRATADA.
[P078] Quando legalmente aplicável, e para todos os fins previdenciários, a Matrícula CEI, a qual o objeto deste CONTRATO se refere, será comunicada formalmente à CONTRATADA, para que esta vincule seus recolhimentos previdenciários. A CONTRATADA deve zelar pelo correto e tempestivo lançamento e recolhimento da contribuição previdenciária vinculada a essa Matrícula CEI e o correto cumprimento de suas obrigações acessórias, estando, ainda, obrigada a proceder à imediata retificação nos casos em que forem identificados erros, omissões, incorreções, ou outras incongruências, inclusive aquelas apontadas pela CONTRATANTE. As consequências do descumprimento do disposto neste item serão atribuídas exclusivamente à CONTRATADA, cumulativamente às multas contratualmente previstas.
[P080] MEDIÇÃO, FATURAMENTO E FORMA DE PAGAMENTO
[P082] Os pagamentos serão efetuados pela CONTRATANTE mediante crédito em conta corrente fornecida pela CONTRATADA, servindo o comprovante bancário de prova de pagamento.
[P084] Independente da FORMA DE PAGAMENTO, a CONTRATADA deverá emitir o BMM ou BM para realizar a MEDIÇÃO MENSAL da parcela efetivamente executada no PERÍODO DE MEDIÇÃO, sendo que no caso de pagamento conforme os MARCOS CONTRATUAIS, a CONTRATADA deverá emitir o BM após o cumprimento de tais marcos.
[P086] A CONTRATADA deverá apresentar o BMM ou o BM ao Gestor do Contrato com a relação de todos os Serviços executados até o último dia do período de medição e sua respectiva valoração, com base nos preços contratuais, juntamente com os comprovantes de quitação legal contratualmente exigíveis.
[P088] Em caso de não aceitação do BM ou BMM por parte da CONTRATANTE, as medições serão recusadas e o pagamento correspondente ficará suspenso até que as obrigações pendentes, registradas em documento específico, sejam integralmente executados pela CONTRATADA e devidamente aceitos pela CONTRATANTE. A CONTRATANTE poderá, a seu exclusivo critério, realizar o pagamento do faturamento da parte incontroversa dos Serviços executados. Os itens controversos deverão ser informados pela CONTRATANTE por escrito.
[P089] Atrasos não justificados na liberação da medição, por motivos imputáveis à CONTRATADA, implicarão automaticamente na prorrogação do prazo de pagamento estabelecido no CONTRATO, sem quaisquer ônus para a CONTRATANTE.
[P091] A elaboração, a entrega e a aprovação do BMM ou BM obedecerá ao seguinte procedimento:
[P093] No último dia do PERÍODO DE MEDIÇÃO, a CONTRATADA emitirá o BM ou BMM, que conterá todos os Serviços executados até o último dia do PERÍODO DE MEDIÇÃO e respectiva valoração, com base nos preços contratuais.
[P095] O BMM ou BM será entregue pela CONTRATADA à CONTRATANTE, em via física ou digital. O BM ou BMM deverá ser entregue acompanhado de cópia dos documentos indicados no QUADRO RESUMO, bem como de qualquer documento adicional que a CONTRATANTE entender necessário para o cumprimento das obrigações legais ou contratuais da CONTRATADA.
[P097] Caso a CONTRATANTE constate qualquer erro, imprecisão, falha no BM ou BMM, incompletude ou deficiência de informação nos documentos mencionados no item anterior, o BM ou BMM será devolvido à CONTRATADA, contendo a justificativas para a sua rejeição, a fim de que a CONTRATADA efetue as devidas correções. Nessa hipótese, o prazo para a CONTRATANTE aprovar o BM ou BMM, se renovará, passando a contar apenas quando da reapresentação do BM ou BMM pela CONTRATADA, devidamente corrigido.
[P099] Para fechamento e aprovação do BM ou BMM, a CONTRATADA deverá declarar a existência, se houver, de eventuais pleitos até o fechamento, porquanto a CONTRATANTE não admitirá a abordagem de pleitos que não foram levantados na época oportuna.
[P101] O pleito deverá ser apresentado formalmente e por escrito junto à CONTRATANTE, fazendo expressa referência à ocorrência, apresentando os documentos e demais meios de sua comprovação e o seu valor.
[P103] A não apresentação do pleito até o mês seguinte à data da sua ocorrência caracteriza a renúncia e a decadência do direito da CONTRATADA.
[P105] A liberação do BM ou BMM não configura aceitação técnica, implícita ou tácita, dos Serviços executados, mas apenas reconhece condições para que os mesmos possam ser faturados, podendo o Gestor do Contrato rejeitá-los posteriormente e solicitar que tais Serviços sejam refeitos pela CONTRATADA.
[P107] Após aprovação do BM ou BMM, a CONTRATANTE autorizará a CONTRATADA a emitir a respectiva nota fiscal/fatura, indicando, obrigatoriamente, o número do CONTRATO e do respectivo BM ou BMM, cuja via original, juntamente com a dos comprovantes de quitação legal contratualmente exigíveis, será anexada à nota fiscal/fatura.
[P109] Os Serviços executados e aprovados serão medidos e liberados para faturamento mensal, obedecendo aos critérios do QUADRO RESUMO e dos ANEXOS que tratam sobre o tema.
[P111] As notas fiscais/faturas emitidas serão entregues pela CONTRATADA conforme QUADRO RESUMO.
[P113] Obrigatoriamente, as notas fiscais/faturas deverão ser entregues ao Gestor do Contrato da CONTRATANTE até o dia 25 (vinte e cinco) de cada mês. Após esta data, só poderão ser aceitas notas fiscais/faturas datadas a partir do primeiro dia útil do mês subsequente.
[P115] Nenhuma nota fiscal/fatura poderá ser emitida anteriormente à autorização ou entre os dias 26 a 31 de cada mês.
[P117] Para estabelecimento do valor final a ser efetivamente pago pela CONTRATANTE relativo a cada nota fiscal/fatura, deverão ser computados descontos aplicados com base nas disposições deste CONTRATO, inclusive decorrentes de penalidades, caso aplicadas, descontos estes constantes das Notas de Débito ou de Crédito que venham, conforme o caso, a ser emitidas, respectivamente, pela CONTRATANTE ou pela CONTRATADA.
[P119] É vedado à CONTRATADA, sob pena de rescisão, ceder total ou parcialmente, oferecer em garantia ou realizar qualquer operação comercial tendo por objeto crédito decorrente deste CONTRATO, bem como descontar em banco duplicatas emitidas sobre notas fiscais/faturas ou endossá-las a terceiros, salvo prévia e expressa concordância, por escrito, em cada caso, da CONTRATANTE.
[P121] Os pagamentos impugnados pela CONTRATANTE não estão sujeitos a qualquer atualização e incidências de ônus financeiros relativos ao período contestado até que a CONTRATADA atenda completamente às exigências formuladas pela CONTRATANTE.
[P123] A CONTRATANTE não aceitará travamento bancário ou qualquer instrumento financeiro similar.
[P125] Caso ocorra comprovado descumprimento de quaisquer obrigações contratuais, referentes, mas sem se limitar: a entrega de documentação de planejamento e controle (físico e financeiro), atrasos de Marcos Contratuais, descumprimento de legislação, fica desde já autorizada a CONTRATANTE a realizar a retenção de parte ou totalidade das medições mensais da CONTRATADA, até que se atinja o valor do referido descumprimento.
[P127] As importâncias retidas na forma do item acima, acima, serão liberadas à CONTRATADA, segundo o cronograma de faturamento, e desde que o fato gerador da retenção seja comprovadamente sanado, indenizado e/ou tenha a respectiva penalidade quitada pela CONTRATADA. Esses valores não sofrerão a incidência de quaisquer correções monetárias ou juros.
[P129] Caso haja atraso no pagamento de qualquer nota fiscal/fatura, por motivos imputáveis exclusivamente à CONTRATANTE, os valores em atraso serão acrescidos de juros de mora de 1% a.m., calculados com base no ÍNDICE DE CORREÇÃO indicado no QUADRO RESUMO, entre a data de vencimento da nota fiscal/fatura e a do seu efetivo pagamento.
[P131] DISPONIBILIZAÇÃO DE BEM IMÓVEL EM COMODATO
[P133] Se aplicável conforme assinalado no QUADRO RESUMO, o IMÓVEL e suas benfeitorias ficam disponibilizados à CONTRATADA no estado descrito no Termo de Vistoria, que é ANEXO e parte integrante e inseparável deste Contrato.
[P135] A CONTRATADA se obriga a manter e a devolver o IMÓVEL à CONTRATANTE, quando findo ou rescindido o CONTRATO ou o COMODATO, bem como a custear toda e qualquer manutenção corretiva que se faça necessária no IMÓVEL em virtude de seu uso e gozo.
[P137] Havendo necessidade de expansão das instalações inerentes à execução das atividades a CONTRATADA deverá solicitar prévia e escrita autorização à CONTRATANTE, sendo a CONTRATADA de toda forma responsável pela gestão, manutenção e conservação destas extensões durante o PRAZO DE VIGÊNCIA deste CONTRATO.
[P139] Caso a CONTRATANTE solicite acréscimo de Funcionários ao Contrato e as instalações do IMÓVEL não possuam capacidade de atendimento, será de reponsabilidade da CONTRATADA fornecer acréscimo de instalações conforme normas vigentes, inclusive manter em perfeitas condições de Saúde, Segurança e Meio Ambiente, devendo os custos serem de responsabilidade da CONTRATADA, sem qualquer repasse destes à CONTRATANTE.
[P141] Quaisquer bens acessórios, melhorias e/ou benfeitorias porventura realizadas pela CONTRATADA após o início do COMODATO serão incorporadas ao IMÓVEL e serão de propriedade da CONTRATANTE, não assistindo à CONTRATADA qualquer direito de retenção e/ou indenização em razão de benfeitorias e obras e melhorias de qualquer espécie realizadas no IMÓVEL pela CONTRATADA.
[P143] Para a realização de qualquer intervenção no IMÓVEL, deverá a CONTRATADA observar rigorosamente as exigências legais e administrativas das autoridades competentes relativas à aprovação dos projetos e execução dessas mesmas obras, especialmente no que concerne às autoridades encarregadas da saúde, bem como da administração, proteção e conservação do meio ambiente.
[P145] Antes de iniciar qualquer intervenção no IMÓVEL, como supressão de vegetação, obras civis, etc., a CONTRATADA deverá apresentar, previamente e de forma escrita, à CONTRATANTE toda e qualquer autorização emitida pelos órgãos competentes, sob pena de descumprimento do presente CONTRATO.
[P147] Em caso de danos diretos e/ou indiretos causados ao IMÓVEL e seus bens acessórios, a CONTRATANTE está autorizada a descontar dos valores devidos pela CONTRATADA, bem como cobrá-lo pelas vias cabíveis.
[P149] A CONTRATANTE poderá solicitar à CONTRATADA a extinção do COMODATO a qualquer tempo, bem como a desocupação do IMÓVEL e a retirada dos bens acessórios deste, devendo, para isso, enviar simples aviso escrito à CONTRATADA, que deverá desocupar a área no prazo descrito no QUADRO RESUMO, contados a partir da data do recebimento deste aviso, sendo dispensável qualquer procedimento judicial ou extrajudicial, e sem acarretar quaisquer penalidades, compensação ou lucros cessantes.
[P151] O IMÓVEL não poderá ser objeto de cessão, transferência, sublocação total ou parcial para terceiros, salvo prévia anuência por escrito da CONTRATANTE.
[P153] No caso de extinção do presente CONTRATO por quaisquer razões, cumprirá à CONTRATADA, restituir IMÓVEL, em perfeitas condições, no prazo indicado no QUADRO RESUMO.
[P155] Não caberá à CONTRATADA o direito a qualquer tipo de compensação, ressarcimento e/ou indenização na hipótese indicada no item acima.
[P157] Relativamente ao comodato, são obrigações da CONTRATADA:
[P159] Utilizar o IMÓVEL e seus bens acessórios, somente para a FINALIDADE EXCLUSIVA, respeitando as dimensões e diretrizes de ocupação dos espaços físicos determinadas pela Gerência de Infraestrutura, bem como as Diretrizes de Infraestrutura para Serviços Permanentes e Eventuais anexas.
[P161] Arcar com todas e quaisquer despesas de mobiliário, incluindo, mas não se limitando a mesas, cadeiras, armários, escaninhos, bebedouros, prateleiras, etc, devendo estes. estarem em conformidade com as normas de saúde, inclusive de ergonomia e estarem em bom estado de conservação.
[P163] Responsabilizar-se pelos custos de toda e qualquer manutenção corretiva causada por eventuais danos diretos e/ou indiretos causados ao IMÓVEL e seus bens acessórios.
[P165] Adotar as especificações do Caderno de Especificações do Plano Diretor de Infraestrutura da Samarco para realização de quaisquer benfeitorias, bem como para utilização de mobiliário.
[P167] Apresentar à CONTRATANTE, sempre que solicitado, todas as informações necessárias referentes às atividades no IMÓVEL.
[P169] Manter o IMÓVEL e seus bens acessórios em perfeito estado de guarda e conservação, procedendo todas as medidas necessárias ao funcionamento, limpeza, higiene e segurança do IMÓVEL, em conformidade com o estabelecido nas legislações pertinentes, assumindo todos os custos de qualquer natureza, sob pena de vir a responder por perdas e danos.
[P171] Informar por escrito e imediatamente à CONTRATANTE sobre qualquer defeito ou irregularidade no IMÓVEL ou danos a ele causado, ou sobre qualquer problema ocorrido na sua utilização.
[P173] Proteger o IMÓVEL contra turbações de terceiros.
[P175] Indenizar os prejuízos porventura causados em decorrência da utilização do IMÓVEL, mantendo a CONTRATANTE isenta de qualquer responsabilidade por tais prejuízos.
[P177] Permitir a inspeção do IMÓVEL pela CONTRATANTE, obrigando-se, para tanto, a franquear aos representantes da CONTRATANTE o acesso a qualquer das dependências do IMÓVEL.
[P179] Promover todas as medidas necessárias para que suas atividades no IMÓVEL não tragam qualquer embaraço aos interesses da CONTRATANTE.
[P181] Restringir sua ocupação à área delimitada pela Planta e Memorial Descritivo ou croqui de identificação da área do COMODATO.
[P183] Fornecer toda direção, supervisão técnica e administrativa e toda força de trabalho direta ou indireta, necessária à realização das atividades no IMÓVEL.
[P185] Contratar seguro de incêndio para o IMÓVEL, bem como a manutenção, em perfeitas condições, de todos os dispositivos de combate a incêndio, atendendo aos prazos de validade, inclusive conforme todas as normas vigentes. Caso o espaço não seja dotado de dispositivos de combate a incêndio e pânico, será de responsabilidade da CONTRATADA providenciar as adequações e aprovações necessárias, incluindo as obrigações relativas aos Autos de Vistorias do Corpo de Bombeiros.
[P187] DISPONIBILIZAÇÃO DE BENS E SERVIÇOS
[P189] A CONTRATANTE poderá fornecer os seguintes equipamentos, facilidades e serviços, nas quantidades que entender necessárias ao bom desenvolvimento dos Serviços, sem ônus para a CONTRATADA:
[P191] Alimentação para os profissionais alocados, durante o expediente, nos refeitórios da CONTRATANTE nas unidades de Germano e/ou Ponta de Ubu;
[P193] Atendimento médico ambulatorial de emergência nas unidades da CONTRATANTE.
[P195] Serviços de vigilância coorporativa da unidade em que os Serviços são prestados, não sendo fornecida vigilância específica para o objeto deste escopo ou, se aplicável, para o canteiro de obras da CONTRATADA.
[P197] Quando aplicável, as instalações, mobiliário, equipamentos, aparelhos e utensílios cedidos pela CONTRATANTE, para uso da CONTRATADA, inclusive em regime de Comodato, durante a prestação dos Serviços, permanecem de propriedade da CONTRATANTE, devendo a CONTRATADA zelar pelo seu bom uso e conservação, devolvendo-os ao término do CONTRATO em perfeito estado de conservação e uso.
[P199] O(s) bem(ns) cedido(s) em comodato será(ão) utilizado(s) pela CONTRATADA exclusivamente para fins da execução do objeto deste CONTRATO, sendo vedada a sua utilização para qualquer outro fim.
[P201] A CONTRATADA declara receber o (s) bem (ns) em perfeitas condições de conservação e funcionamento, obrigando-se a realizar, às suas custas, os consertos, reparos e substituições que forem necessárias, para que o(s) mesmo(s) seja(m) mantido(s) e venha(m) a ser restituído(s) nas mesmas condições recebidas, entendendo-se que a substituição de qualquer peça ou aparelho far-se-á por outra da mesma qualidade.
[P203] OBRIGAÇÕES DA CONTRATANTE
[P205] São obrigações da CONTRATANTE, sem prejuízo das demais previstas neste CONTRATO:
[P207] Efetuar as medições e remunerar a CONTRATADA na forma prevista neste instrumento.
[P209] Fornecer à CONTRATADA as informações que guardem conexão com o objeto deste instrumento e que se fizerem necessárias ao desenvolvimento dos Serviços.
[P211] Estabelecer as diretrizes para a implantação do objeto contratado.
[P213] Instruir a CONTRATADA quanto a normas e procedimentos internos da CONTRATANTE.
[P215] Credenciar, por escrito, junto à CONTRATADA, um representante do seu próprio quadro ou de terceiros, que atuará como Gestor do Contrato.
[P217] Quando aplicável, providenciar em tempo hábil, todas as licenças e autorizações ambientais relativas ao LOCAL DE PRESTAÇÃO DOS SERVIÇOS.
[P219] Disponibilizar área de apoio para uso da CONTRATADA.
[P221] Fornecer alimentação (Desjejum, almoço, lanches e jantar) aos Funcionários da CONTRATADA durante execução dos Serviços dentro das unidades de Germano e/ou Ponta de Ubu , respeitando as necessidades do regime de trabalho adotado, onde lanches e/ou jantar só serão fornecidos às equipes que trabalharem em regime de escala de revezamento ou após o horário administrativo, desde que sejam solicitados pela CONTRATANTE.
[P223] OBRIGAÇÕES DA CONTRATADA
[P225] São obrigações da CONTRATADA, sem prejuízo das demais previstas neste CONTRATO:
[P227] Quanto à força de trabalho:
[P229] Fornecer toda a direção, supervisão técnica e administrativa, e toda a força de trabalho necessária à execução dos Serviços, sendo para todos os efeitos, considerada como única e exclusiva empregadora.
[P231] utilizar pessoal qualificado e em número suficiente para execução dos Serviços, de modo a cumprir os prazos estabelecidos, bem como o padrão de qualidade técnica de segurança do trabalho e meio ambiente dos Serviços objeto do CONTRATO.
[P233] Providenciar e custear, quando da desmobilização envolvendo empregados de outras localidades, o retorno as suas origens imediatamente após o encerramento dos Serviços.
[P235] Quanto à assistência aos seus Funcionários:
[P237] Quando houver desligamento de Colaborador de outras localidades, providenciar seu imediato retorno ao respectivo local de origem.
[P239] Realizar o cadastro de seus empregados através de plataforma disponibilizada pela CONTRATANTE com informações atualizadas, bem como documentos comprobatórios, e em tempo hábil para as aprovações necessárias.
[P241] Quanto a custeio e encargos:
[P243] Custear, como única empregadora - e fazer com que seus subcontratados também o façam - as despesas decorrentes, direta ou indiretamente, dos Serviços, incluindo, mas não se limitando à remuneração de fornecedores, ao pagamento de encargos trabalhistas e previdenciários com relação a seus empregados e outros contratados, inclusive ao seguro de acidentes do trabalho;
[P245] Disponibilizar, sempre que requisitado pela CONTRATANTE, toda documentação referente ao pagamento e cumprimento das obrigações relativas a tributos, seguros, encargos sociais, trabalhistas e previdenciários, e qualquer obrigação que se referir à execução dos Serviços objeto deste CONTRATO.
[P247] Apresentar, mensalmente, junto com o BM ou BMM e com a nota fiscal de faturamento, as guias relacionadas abaixo, do mês anterior, como condição para recebimento do valor faturado: Guias de recolhimento de INSS; Guias de recolhimento de FGTS; Guias de recolhimento de ISSQN.
[P249] Apresentar ao Gestor do Contrato, quando do início dos Serviços, os comprovantes de recolhimento das contribuições relativas ao seguro dos envolvidos nos Serviços contra risco e acidentes de trabalho, nos termos da lei vigente, bem como manter atualizados tais recolhimentos, comprovando-os regularmente ao Gestor do Contrato.
[P251] Quanto às relações nas unidades da CONTRATANTE:
[P253] Cumprir e fazer cumprir o Manual de Saúde e Segurança no Trabalho (anexo), bem como outras normas administrativas e disciplinares vigentes ou a serem implantadas no LOCAL DA PRESTAÇÃO DOS SERVIÇOS, pela CONTRATANTE, respondendo, por si e seus Funcionários.
[P255] Quando aplicável, e nos casos em que houver necessidade dos Funcionários da CONTRATADA adentrarem nas unidades da CONTRATANTE, o pessoal sob sua responsabilidade deverá obedecer às Normas de Coordenação de Campo, Manual de Saúde e Segurança do Trabalho, bem como as Diretrizes para Meio Ambiente e Comunidade da CONTRATANTE – (ANEXO), além de utilizar todo o Equipamento de Proteção Individual (EPI), sendo obrigatório uniforme, botas com biqueira, capacete (identificado com a logomarca da CONTRATADA) e óculos de segurança é obrigatório para todos os empregados.
[P257] Fixar seus horários de trabalho de modo compatível com os adotados pela CONTRATANTE, informando qualquer alteração necessária no horário dos Serviços ao Gestor do Contrato, com a antecedência necessária, de modo a permitir a manutenção dos controles necessários.
[P259] Não permitir que o seus Funcionários, máquinas, veículos e equipamentos a seu serviço ingressem em propriedade de terceiros, sem antes se certificar de que a CONTRATANTE já está devidamente autorizada para tal, respondendo civilmente e criminalmente por todo e qualquer dano que tal irregularidade venha a dar causa.
[P261] Não permitir que, fora dos horários de trabalho, seus Funcionários circulem pelas áreas da CONTRATANTE, devendo manter, para isto, vigilância constante, responsabilizando-se, exclusivamente, por quaisquer problemas que decorrerem do descumprimento dessa obrigação.
[P263] Providenciar a substituição ou retirada imediata de qualquer Colaborador, cuja permanência na área seja considerada, justificadamente, indesejável pela CONTRATANTE.
[P265] Providenciar os cadastros de todos os seus Funcionários que adentrarem nas unidades da CONTRATANTE, bem como assegurar que os mesmos realizem os treinamentos (principalmente os obrigatórios) cursos disponibilizados na Plataforma da CONTRATANTE, dentro da jornada de trabalho, como requisito primordial para a efetiva execução dos Serviços, sendo responsabilidade da CONTRATADA a disponibilização dos recursos necessários para o acesso dos empregados ao Sistema de Acessibilidade.
[P267] Responsabilizar-se pelos bens e pela segurança do LOCAL DE PRESTAÇÃO DOS SERVIÇOS, bem como pelo armazenamento adequado e seguro de seus materiais, considerando as recomendações da segurança empresarial da CONTRATANTE, que deve ser envolvida para análise dos riscos em fase de planejamento do canteiro, caso os Serviços sejam relacionados a obras.
[P269] Pedir autorização, prévia e por escrito, à segurança empresarial da CONTRATANTE para realizar, às suas expensas, a instalação de sistema de câmeras, alarmes e demais recursos de proteção física no LOCAL DE PRESTAÇÃO DOS SERVIÇOS.
[P271] Quando aplicável, envolver a área de segurança empresarial nas reuniões de planejamentos para alteração ou mudanças no ambiente dos ativos, tais como, porém, não se limitando a paradas de equipamentos e instalações (programadas ou não), canteiros de obras, incluindo equipamentos com estruturas móveis, subestações de energia e instalações críticas para o processo produtivo, a fim de que seja realizado Diagnóstico de Segurança Empresarial e a adoção de medidas e controles em tempo hábil.
[P273] Quanto a registros e legalizações:
[P275] Quando aplicável, promover o registro deste CONTRATO e seus Termos Aditivos perante os órgãos competentes, de acordo com a legislação em vigor, arcando com todas as despesas daí decorrentes, comprovando essa obrigação em 20 (vinte) dias úteis, contados da assinatura deste instrumento.
[P277] Manter, até o término do CONTRATO, o arquivo completo da documentação referente aos Serviços, com registros precisos e atualizados de todos os custos, despesas, transações financeiras e obrigações relacionadas com este CONTRATO. Tais registros ficarão à disposição da CONTRATANTE, ou de quem esta designar, durante o horário comercial, nos escritórios da CONTRATADA.
[P279] No caso de serviço de engenharia e arquitetura a CONTRATADA deverá apresentar à CONTRATANTE as Anotações de Responsabilidade Técnica (ART) relativas aos Serviços em cumprimento à Lei n° 6.496/77. Caso não seja necessária a emissão da ART, será obrigação da contratada apresentar declaração emitida pelo CREA, informando que não há necessidade de emissão de ART para o objeto desta contratação.
[P281] Quanto à saúde, segurança, meio ambiente e comunidade:
[P283] Designar como representante para os assuntos de saúde de segurança do trabalho (“SST)” empregado da CONTRATADA com poder decisório, o qual deverá comparecer às reuniões dos Comitês de Saúde, Segurança e Meio Ambiente, às Auditorias Programadas, às reuniões para apresentação da Investigação de Acidentes e outros eventos programados pela Gerenciadora de SST ou pela CONTRATANTE.
[P285] Comunicar imediatamente à CONTRATANTE qualquer deficiência, infração ou violação de obrigações, qualquer acidente de trabalho, ou incidente que exponha alguma pessoa a risco, ou qualquer outro assunto relevante, relacionadas à SST e que possa impactar as relações de trabalho ou a prestação dos serviços, compreendendo, sem se limitar, iminência de greves, paralisações, acidentes de trabalho, situações de risco, violações de direitos humanos, dentre outras, durante a execução do presente CONTRATO.
[P287] Após o envio de comunicação as PARTES deverão se reunir para avaliar uma solução conjunta para os problemas e evitar qualquer impacto à prestação dos Serviços.
[P289] Atingir os indicadores de desempenho em segurança, conforme definição e cálculo constante na Gestão de Incidentes do Manual do Sistema de Saúde e Segurança (ANEXO), dentre os quais se destaca o indicador de Fatalidade – ZERO.
[P291] Acatar as solicitações da(s) área(s) de SST da CONTRATANTE, o que incluir direito de solicitar à CONTRATADA todo e qualquer equipamento ou medidas de controle que julgar necessário à SST.
[P293] Em observância aos padrões de qualidade das refeições e alojamentos disponibilizados aos seus Funcionários, fornecê-los somente em estabelecimentos que possuam alvará sanitário expedido e válido, em conformidade com a Secretaria de Estado de Saúde e o Código de Vigilância Sanitária do Município, sendo que, dentro das instalações industriais das unidades da CONTRATANTE, é obrigatória aos empregado/subcontratados da CONTRATADA, a utilização dos restaurantes da CONTRATANTE durante a jornada de trabalho.
[P295] Somente mediante autorização da CONTRATANTE e cumprimento da legislação, em especial das normas citadas na previsão 11.6.5, poderá haver transporte de alimentos para fornecimento de refeição de Funcionários da CONTRATADA.
[P297] Cumprir todos os requisitos legais aplicáveis relacionados à SST, bem como as diretrizes da CONTRATANTE estipuladas através do Manual de SST em anexo.
[P299] Quanto aos Serviços como um todo:
[P301] Credenciar, por escrito, junto à CONTRATANTE, seu representante com poderes para tomar qualquer providência relativa ao CONTRATO.
[P303] Informar a CONTRATANTE a ocorrência de qualquer fato ou condição que possa atrasar ou impedir a conclusão, no todo ou em parte, dos Serviços, indicando as medidas tomadas ou a tomar para corrigir a situação.
[P305] Participar de forma efetiva e cooperativa dos processos de gestão integrada da CONTRATANTE.
[P307] Informar, quando solicitado, detalhadamente, os gastos incorridos nos Serviços e pagos pela CONTRATADA nos Estados de Minas Gerais e/ou Espírito Santo.
[P309] Caso aplicável, arcar com todos os custos e despesas decorrentes da instalação, conexão e operação do canteiro de obras e de suas atividades no LOCAL DA PRESTAÇÃO DOS SERVIÇOS, restaurando-o, o que inclui o canteiro de obras e as áreas cedida em comodato e jazidas, de acordo com as exigências emanadas pela CONTRATANTE e determinações dos órgãos ambientais.
[P311] Quando aplicável, implantar SLA’s (níveis de serviço), acordados entre as PARTES para este CONTRATO, de avaliação periódica e regular da qualidade dos produtos e serviços.
[P313] Quando da demissão de seus FUNCIONÁRIOS, que venham a cumprir aviso prévio trabalhado, não permitir que os mesmos tenham acesso a qualquer local relacionado à execução do CONTRATO, bem como a programas e sistemas internos da CONTRATANTE, salvo exceção prévia e formalmente aprovada pela CONTRATANTE.
[P315] Informar à CONTRATANTE acerca da ocorrência de qualquer fato, incidente, acidente ou condição relevante que possa impactar na segurança e/ou andamento dos Serviços.
[P317] Informar por escrito, para a CONTRATANTE, eventuais omissões, contradições ou dúvidas encontradas no CONTRATO, ANEXOS e/ou orientações da CONTRATANTE.
[P319] Realizar todos os treinamentos disponibilizados e/ou exigidos, a fim de cumprir com as diretrizes internas da CONTRATANTE, incluindo, porém não se limitando, àqueles referentes a Código de Conduta, Saúde e Segurança e Segurança da Informação.
[P321] RESPONSABILIDADES DA CONTRATADA
[P323] A CONTRATADA deverá isentar e defender a CONTRATANTE contra quaisquer vínculos, liames ou reivindicações de subcontratados ou de terceiros, com ela relacionados, com fundamento no objeto deste CONTRATO.
[P325] A CONTRATADA se obriga, ainda, a arcar com todas as despesas com indenizações/reclamações decorrentes de prejuízos, perdas e danos físicos, materiais e morais, montante que pode ser superior inclusive ao da garantia oferecida pela CONTRATADA, que venham a ser causados a pessoas/coisas, da CONTRATANTE ou de terceiros, em decorrência de sua ação ou omissão, desídia, direta ou indireta, própria ou de seus empregados, auxiliares, prepostos ou subcontratados, incluindo os relacionados com o uso de materiais ou processos que requeiram técnicas especiais (protegidos por marcas/patentes).
[P327] Se, em decorrência da execução dos Serviços contratados, ocorrerem incidentes com potencial de gravidade maior que 3 (três) ou acidentes causando danos físicos ou materiais a pessoas/bens de propriedade da CONTRATANTE ou de terceiros, envolvendo seus Funcionários deverá a CONTRATADA, além das providências específicas que o evento requeira, apurar as causas que o determinaram e apresentar o relato preliminar do incidente/acidente num prazo máximo de 24 (vinte e quatro) horas, bem como o relatório detalhado de investigação ao Gestor do Contrato num prazo máximo de 5 (cinco) DIAS, ambos os prazos contados a partir da data do evento.
[P329] A CONTRATADA será responsável por todas as ações ou omissões de seus Funcionários, correndo por sua conta exclusiva a reparação e o ressarcimento de tais prejuízos, pelo custo atualizado, e quaisquer danos pessoais ou materiais, perda, lesão, irregularidade ou defeito que sofram os serviços por qualquer motivo.
[P331] Serão admitidas como exceções aos itens anteriores apenas as ações/omissões decorrentes dos "Riscos Excluídos", caso em que a reparação será custeada pela CONTRATANTE. São considerados "Riscos Excluídos" ato/utilização indevidos ou inadequados de bens, obras, serviços e materiais pela CONTRATANTE ou por quaisquer de seus prepostos, ou por outras contratadas que não sejam subcontratadas da CONTRATADA, desde que tal ato/utilização tenha se dado, contra recomendação expressa da CONTRATADA;
[P333] Fica expressamente convencionado que, se porventura, a CONTRATANTE for condenada em razão do não pagamento em época própria de qualquer obrigação atribuível à CONTRATADA ou suas subcontratadas, seja de natureza fiscal, trabalhista, previdenciária, civil, ou de qualquer outra espécie, mesmo após o término do CONTRATO, assistir-lhe-á o direito de reter os pagamentos devidos até o limite do valor da condenação, até que a CONTRATADA ou suas subcontratadas evidenciem a garantia ou realização do pagamento, liberando a CONTRATANTE da condenação.
[P335] A CONTRATADA deverá se responsabilizar pelo estudo e avaliação das especificações técnicas e eventuais documentos fornecidos pela CONTRATANTE, bem como pela execução e qualidade dos serviços contratados, utilizando-se de pessoal qualificado, equipamentos e procedimentos técnico-administrativos adequados, cabendo-lhe alertar a CONTRATANTE sobre falhas técnicas eventualmente encontradas e ainda suspender qualquer atividade em execução que comprovadamente não esteja sendo executada de acordo com o que foi acertado ou que ponha em risco a segurança dos profissionais das PARTES ou de terceiros, independentemente de solicitação da CONTRATANTE.
[P337] Caso os Serviços devam ser sustados e/ou refeitos por estarem não conformes com as normas técnicas e/ou com os padrões operacionais aplicáveis e/ou não tenham sido aceitos, justificadamente, pela CONTRATANTE, a CONTRATADA arcará com os custos decorrentes.
[P339] A CONTRATADA deverá promover a substituição, sempre que solicitado justificadamente pela CONTRATANTE, sem prejuízo do andamento dos Serviços, de qualquer Colaborador, e/ou mandatário que venha a apresentar, comportamento em desacordo com as normas ou regulamentos internos da CONTRATANTE.
[P341] Eventuais limitações de responsabilidade contidas nesse CONTRATO não se aplicam a coberturas securitárias e/ou eventual direito de regresso da(s) seguradora(s) das PARTES.
[P344] A CONTRATADA deverá providenciar para que não haja qualquer parada ou atraso na execução dos Serviços e, se por qualquer motivo, ocorrer a indisponibilidade de qualquer Serviço ou recurso, se compromete a buscar meios necessários ao seu restabelecimento, sem qualquer ônus adicional a CONTRATANTE.
[P346] Caberá exclusivamente à CONTRATADA a reparação de eventuais danos ou prejuízos causados ao meio ambiente por seus Funcionários ou prepostos durante a execução dos Serviços, bem como o pagamento de todas e quaisquer indenizações decorrentes e despesas oriundas de tais danos.
[P348] A CONTRATADA é a única responsável pelas obrigações decorrentes dos contratos de trabalho de seus Funcionários ou de prestação de serviços de seus subcontratados, inclusive por eventuais inadimplementos de obrigações trabalhistas ou previdenciárias, não podendo ser arguida solidariedade da CONTRATANTE por tais obrigações nem responsabilidade subsidiária, uma vez que a presente contratação não implica vinculação empregatícia entre seus empregados e/ou subcontratados e a CONTRATANTE;
[P350] FISCALIZAÇÃO E GESTÃO DO CONTRATO
[P352] A CONTRATANTE exercerá a fiscalização sobre a execução do CONTRATO através de uma equipe, denominada Fiscalização, integrada por pessoal pertencente ao seu quadro ou de terceiros, liderada pelo Gestor do Contrato e composta por fiscais do CONTRATO, sendo estes nominalmente definidos pela CONTRATANTE por meio de envio comunicação escrita para a CONTRATADA para quaisquer dos endereços físico ou eletrônico indicados no QUADRO RESUMO.
[P354] A CONTRATANTE acompanhará a execução do CONTRATO através de uma equipe integrada por pessoal pertencente ao seu quadro ou de terceiros, liderada pelo Gestor do Contrato.
[P356] Havendo alteração dos gestores, as PARTES deverão comunicar a outra PARTE por escrito, sob pena de serem consideradas válidas todas as comunicações aos gestores inicialmente indicados.
[P358] O Gestor do Contrato estará à disposição da CONTRATADA para fornecer as informações e documentação técnica que forem necessárias para o desenvolvimento dos Serviços.
[P360] O Gestor do Contrato terá acesso a todos os locais onde os Serviços se realizarem e plenos poderes para praticar atos, nos limites do presente CONTRATO, que se destinem a acautelar e preservar todo e qualquer direito da CONTRATANTE.
[P362] As atribuições do Gestor do Contrato incluem:
[P364] Verificar o cumprimento das obrigações da CONTRATADA, sendo-lhe lícito recusar Serviços que tenham sido executados em desacordo com as condições estabelecidas neste CONTRATO ou com as informações ou especificações fornecidas pela CONTRATANTE, determinando as correções ou retificações adequadas, a ônus da CONTRATADA.
[P366] Aprovar as medições da CONTRATADA.
[P368] Autorizar, se for o caso, previamente, a realização de despesas a serem reembolsadas à CONTRATADA.
[P370] Quando as condições de execução impuserem a necessidade da modificação em desenhos ou documentos de propriedade da CONTRATANTE, a CONTRATADA o fará mediante solicitação e aprovação do Gestor do Contrato.
[P372] Sustar o pagamento de quaisquer notas fiscais/faturas da CONTRATADA, no caso de inobservância de disposição contida neste CONTRATO, até a regularização da situação. Tal procedimento será comunicado por escrito à CONTRATADA, sem perda do direito de aplicação das demais sanções previstas neste CONTRATO.
[P374] Solicitar, quando entenda necessário, ações referentes aos Funcionários da CONTRATADA, ou de seus subcontratados, quando do descumprimento de algum requisito estipulado no CONTRATO.
[P376] Mandar executar, por terceiros, debitando as despesas respectivas da CONTRATADA, as providências necessárias para suprir ou corrigir deficiências da CONTRATADA por ela não sanadas no prazo estipulado pelo Gestor do Contrato.
[P378] Convocar e dirigir reuniões periódicas ou ocasionais com a CONTRATADA, para programação e coordenação geral/específica dos serviços.
[P380] Comunicar à CONTRATADA, por escrito e com a devida antecedência, qualquer instrução ou procedimento a adotar sobre assunto relacionado com este CONTRATO, inclusive aplicação de multas.
[P382] No caso de inobservância, pela CONTRATADA, das exigências do Gestor do Contrato, amparadas neste CONTRATO, terá a CONTRATANTE, além do direito de aplicação das sanções previstas no CONTRATO, também o de suspender a execução dos Serviços e de sustar o pagamento de quaisquer notas fiscais/faturas da CONTRATADA até a regularização da situação, do que dará ciência, por escrito, à CONTRATADA.
[P384] As funções inerentes ao Gestor do Contrato não eximem, em nenhuma hipótese, a exclusiva responsabilidade técnica da CONTRATADA durante a execução dos Serviços.
[P386] A ação/omissão, total ou parcial, do Gestor do Contrato, não exime a CONTRATADA da total responsabilidade pelo fiel cumprimento de suas obrigações contratuais.
[P388] Sem prejuízo do cumprimento das demais obrigações previstas neste CONTRATO, as PARTES se obrigam a:
[P390] Nomear o Gestor do Contrato, por escrito, com experiência comprovada em atividades inerentes ao objeto para receber demandas, resolver problemas e representá-las, com plenos poderes para tomar as providências que se fizerem necessárias para o bom cumprimento do CONTRATO.
[P392] Substituir o Gestor do Contrato no caso de falta, ausência ou impedimento eventual ou ocasional, por outro com iguais poderes; e
[P394] Havendo alteração dos Gestor do Contrato pelas PARTES, comunicar previamente a alteração à outra PARTE por escrito, sob pena de serem consideradas válidas todas as comunicações dirigidas aos representantes inicialmente indicados.
[P396] CESSÃO E SUBCONTRATAÇÃO
[P398] A CONTRATADA não poderá transferir a terceiros nem subcontratar, no todo ou em parte, os Serviços e/ou as obrigações deste CONTRATO, sem a prévia identificação do cessionário/subcontratado perante a CONTRATANTE e sem a prévia e expressa concordância desta, por escrito, na pessoa do Gestor do Contrato.
[P400] A existência de cessionárias ou subcontratadas, autorizadas, ou não, pela CONTRATANTE, não eximirá a CONTRATADA de sua exclusiva responsabilidade pelo cumprimento do CONTRATO.
[P402] A subcontratação do OBJETO pela CONTRATADA, ou de parte dele, sem a prévia autorização expressa da CONTRATANTE será considerada inadimplemento contratual e permitirá à CONTRATADA, a seu exclusivo critério: (i) solicitar a imediata paralisação do objeto (ii) exigir a desmobilização imediata da(s) subcontratada(s); (iii) exigir a substituição da(s) subcontratada(s), sem prejuízo das penalidades cabíveis.
[P404] Fica vedado aos subcontratados realizarem novas subcontratações.
[P406] SEGUROS
[P408] A CONTRATADA e suas subcontratadas se obrigam a instituir, por sua conta exclusiva, com empresa seguradora de idoneidade reconhecida, além dos seguros que julgar convenientes, os seguros previstos na legislação em vigor, inclusive seguro de responsabilidade civil geral, seguros de veículos, de vida e de acidentes para o seus Funcionários, utilizados/alocados na execução do CONTRATO.
[P410] As apólices contratadas pela CONTRATADA deverão permanecer suficientes para a cobertura dos riscos assumidos neste CONTRATO durante toda a vigência contratual.
[P412] As responsabilidades da CONTRATADA são integrais, não se limitando ao valor do seguro contratado. Independentemente do valor segurado, a CONTRATADA responde por perdas, danos, inclusive franquias e ações de ressarcimento por parte das seguradoras contratadas pela CONTRATANTE quando houver a responsabilidade pelos prejuízos causados e indenizados diretamente à CONTRATANTE.
[P414] As PARTES, através da assinatura deste instrumento, autorizam, desde já, o compartilhamento das disposições deste CONTRATO com seguradoras ou corretoras de seguro exclusivamente para fins de contratação ou renovação destes, sem que seja caracterizado descumprimento dos deveres de confidencialidades previstos.
[P416] Na ocorrência de sinistro, as PARTES deverão, no prazo de 05 (cinco) dias úteis, fornecer as informações solicitadas pela outra PARTE, bem como apoiá-la em eventuais discussões relacionadas ao sinistro, sob pena de responsabilização pelas consequências advindas de sua eventual omissão.
[P418] A CONTRATADA deverá, sempre que solicitado, em até 10 (dez) DIAS corridos, apresentar a cópia da(s) apólice(s) correspondente(s) e/ou comprovante de pagamento destas, a pedido da CONTRATANTE.
[P420] CONFIDENCIALIDADE
[P422] As PARTES não poderão prestar informações a terceiros nem divulgar quaisquer dados, informações relacionadas ao CONTRATO, ou o CONTRATO em si, ANEXOS e eventuais aditivos, sem autorização prévia e por escrito da outra PARTE, obrigação que abarca até mesmo a fase de concorrência da contratação.
[P424] O acesso às informações confidenciais será restrito aos Funcionários das PARTES que tiverem comprovada necessidade de conhecê-la, apenas na extensão necessária, e deverão assinar o modelo contido no anexo denominado “Termo de Confidencialidade”, que deve ser entregue aos cuidados do Gestor do Contrato da CONTRATANTE.
[P426] As estipulações e obrigações constantes da presente cláusula não serão aplicadas a qualquer informação que: (i) seja de domínio público; (ii) já esteja em poder da CONTRATADA como resultado de sua própria pesquisa ou desenvolvimento; (iii) tenha sido legitimamente recebida pela CONTRATADA de terceiros, sem que tenha havido violação de qualquer dever de confidencialidade; (iv) seja revelada em razão de uma ordem válida, administrativa ou judicial, somente até a extensão de tais ordens, contanto que a CONTRATADA tenha notificado a existência de tal ordem, previamente e por escrito, à CONTRATANTE, dando a esta, na medida do possível, tempo hábil para pleitear medidas de proteção que julgar cabíveis.
[P428] A CONTRATADA declara antes do término deste CONTRATO, por qualquer razão, deverá ser devolvida à CONTRATANTE toda e qualquer documentação, arquivada em qualquer meio, relativa ao CONTRATO, no prazo máximo de 15 (quinze) DIAS.
[P430] Em caso de impossibilidade de devolução da documentação tendo em vista o meio em que foi transmitida, incluindo, porém não se limitando a e-mails e/ou chats, a CONTRATADA declara que realizará a destruição completa dos arquivos confidenciais em sua posse, sob pena de ser caracterizado descumprimento contratual, desde que seja autorizada pela CONTRATANTE antecipadamente.
[P432] A CONTRATADA reconhece e aceita que o uso para fim diverso da execução dos Serviços, a exemplo da exploração comercial, a cópia, a produção de back-up, a divulgação, reprodução ou distribuição, total ou parcial, das informações confidenciais, configura violação da obrigação prevista desta cláusula.
[P434] As obrigações acima mencionadas permanecerão em pleno e absoluto vigor desde a data de envio pela CONTRATANTE da Solicitação de Proposta estendendo-se por 5 (cinco) anos após o término do CONTRATO
[P436] A violação, pela CONTRATADA, do dever de confidencialidade previsto nesta cláusula importará na aplicação de multa não compensatória de 20% (vinte por cento) do VALOR ESTIMADO DO CONTRATO.
[P438] CASO FORTUITO E FORÇA MAIOR
[P440] Conforme previsto no artigo 393 do Código Civil Brasileiro, nenhuma PARTE será responsabilizada por falhas no cumprimento de suas respectivas obrigações quando o cumprimento de tais obrigações tenha sido impedido ou atrasado em virtude da ocorrência de eventos comprovadamente caracterizados como caso fortuito ou força maior.
[P442] Ante a ocorrência de qualquer circunstância que puder ser invocada como caso fortuito ou força maior, a PARTE afetada enviará à outra, no prazo de até 24 horas, após ter tomado conhecimento, uma notificação, por escrito, por meio da qual comunicará a ocorrência do fato, as medidas que estiverem sendo tomadas e a previsão para regularização da situação.
[P444] A PARTE afetada pelo evento de força maior ou caso fortuito deverá tomar e demonstrar que tomou todas as medidas a seu alcance para cessar ou minimizar os efeitos dele decorrentes e impeditivos do cumprimento de suas obrigações.
[P446] Cessado o caso fortuito ou o motivo de força maior, a PARTE que o tiver invocado notificará a outra, por escrito, no prazo máximo de 05 (cinco) DIAS, a contar da referida cessação, informando-a acerca da regularização da situação.
[P448] Se o fato invocado como caso fortuito ou força maior impossibilitar o cumprimento integral deste CONTRATO e perdurar por prazo maior do que aquele previsto no QUADRO RESUMO, qualquer das PARTES poderá optar pela resolução deste instrumento, na forma prevista no CONTRATO.
[P450] Em nenhuma hipótese será considerado como evento de caso fortuito ou força maior a ocorrência de:
[P452] Greve e/ou interrupções trabalhistas, ou medidas tendo efeito semelhante, de Funcionários de uma das PARTES e/ou de suas contratadas e/ou subcontratadas;
[P454] Qualquer ação de qualquer autoridade pública que uma parte pudesse ter evitado se tivesse cumprido suas obrigações legais ou contratuais;
[P456] Decretação de falência de qualquer das PARTES;
[P458] Dificuldades econômicas ou financeiras de qualquer das PARTES;
[P460] Os dias de chuvas não superiores às médias históricas e suas consequências.
[P462] As PARTES acordam, desde já, que os prazos previstos neste CONTRATO poderão ser proporcionalmente prorrogados pelo mesmo número de dias relativos à eventual suspensão dos Serviços em razão da ocorrência de eventos caracterizados como caso fortuito ou força maior, a exclusivo critério da CONTRATANTE, mediante notificação nesse sentido.
[P464] MULTAS E PENALIDADES
[P466] Caso a CONTRATADA descumpra norma e/ou obrigação contratual considerada sanável pela CONTRATANTE, a CONTRATANTE poderá, a seu exclusivo critério, notificar a CONTRATADA para que esta sane a obrigação no prazo estipulado pela CONTRATANTE.
[P468] Se a CONTRATADA se manter inerte em relação à notificação, recuse-se a corrigir as inconformidades, insista em deslizes da mesma natureza ou apresente soluções incompatíveis com a situação, o Gestor do Contrato poderá aplicar penalidades.
[P470] Se o referido descumprimento de norma e/ou obrigação pela CONTRATADA for considerado insanável pela CONTRATANTE, esta poderá aplicar penalidades independente de prazo, apenas mediante envio de notificação para a CONTRATADA.
[P472] O valor de referência para cálculo das penalidades estabelecidas no CONTRATO será o VALOR ESTIMADO DO CONTRATO previsto no QUADRO RESUMO, conforme os parâmetros abaixo:
[P475] As penalidades previstas no CONTRATO e nos ANEXOS, caso aplicável, não possuem natureza compensatória, isto é, podem cumuladas com as perdas e danos relacionadas.
[P477] As multas serão descontadas do pagamento da primeira nota fiscal/fatura apresentada pela CONTRATADA após a sua aplicação e, não sendo estes suficientes, serão descontados dos montantes das notas fiscais/faturas sucessivas, podendo a CONTRATANTE, ainda, valer-se de qualquer outro meio juridicamente admitido para haver o valor devido.
[P479] A cobrança das multas previstas nesta cláusula ocorrerá cumulativamente, na medida em que cada obrigação deixar de ser cumprida, até o limite de 10% (dez por cento) do valor total estimado do CONTRATO. Caso este percentual seja atingido, será permitido à CONTRATANTE rescindir o CONTRATO
[P481] As multas acima previstas não reduzirão ou eliminarão outras penalidades, obrigações e responsabilidades da CONTRATADA previstas neste CONTRATO.
[P483] PROPRIEDADE INTELECTUAL
[P485] Todo objeto de propriedade intelectual obtido através das atividades relacionadas ao presente CONTRATO, que vierem a ocorrer durante a o PERÍODO DE VIGÊNCIA ou no prazo de um ano após a extinção do CONTRATO, decorrente da especificidade da atividade contratada, pertencerão exclusivamente à CONTRATANTE.
[P487] Quando a invenção ou melhoria resultar de contribuição específica da CONTRATADA, mas, que para tanto, forem utilizados recursos, dados, meios, materiais, instalações ou equipamentos da CONTRATANTE, a propriedade dessa invenção ou melhoria pertencerá exclusivamente à CONTRATANTE.
[P489] A CONTRATADA se obriga a transferir à CONTRATANTE a propriedade integral, livre de quaisquer ônus, responsabilidades e restrições legais por propriedade intelectual de todos os desenhos, projetos, equipamentos, materiais, PARTES e componentes, acessórios e pertenças, ferramentas e quaisquer outros bens empregados e produzidos no âmbito dos SERVIÇOS.
[P491] Todos os documentos, incluindo, mas não se limitando a relatórios, gráficos, planilhas, gerados pela CONTRATANTE em razão deste CONTRATO poderão ser utilizados livremente pela CONTRATANTE, que poderá repassá-los para terceiros que agem em seu interesse, como os seus fornecedores, independente de anuência prévia da CONTRATADA e sem quaisquer limitações e ônus/valores adicionais sejam devidos pela CONTRATANTE.
[P493] A CONTRATADA é responsável pelo pagamento de qualquer taxa ou royalty eventualmente exigível pelo uso de patentes, métodos, processos, materiais e equipamentos empregados na prestação dos Serviços.
[P495] A CONTRATADA é a única e exclusiva responsável por si e por seus Funcionários, pelo uso, nos Serviços de materiais e equipamentos, incluindo hardware e software, regularmente adquiridos e/ou licenciados e deve dispor de todos os documentos comprobatórios da aquisição e/ou licenciamento dos mesmos. A CONTRATADA responderá, isolada e exclusivamente, perante quaisquer terceiros, por qualquer irregularidade verificada.
[P497] PRIORIZAÇÃO DE RECURSOS REGIONAIS
[P499] A CONTRATANTE incentiva e promove o desenvolvimento das regiões onde possui instalações e, portanto, deverá ser priorizada pelas PARTES a contratação de pessoal e aquisição de serviços/materiais da região onde os Serviços serão prestados, sejam eles oriundos dos programas de qualificação, do pessoal já qualificado da região, de apoio, ou força de trabalho não especializada.
[P501] Caso os Serviços sejam prestados no município de Anchieta/ES, a CONTRATADA se obriga a cumprir o disposto na legislação municipal vigente (Lei 1.297/18 e/ou legislações que a sucederem), de forma a manter o percentual mínimo exigido pela legislação para a contratação de empregados locais.
[P503] COMPLIANCE
[P505] A CONTRATADA, ao aceitar este instrumento, confirma a ciência e se compromete ainda, no desempenho de qualquer ação ou negócio que envolva interesses da CONTRATANTE, a cumprir o Código de Conduta de Fornecedores disponibilizado no site www.samarco.com.
[P507] A CONTRATADA se obriga a apurar, com diligência, qualidade, efetividade e dentro do prazo solicitado, todas as denúncias encaminhadas pela SAMARCO que digam respeito exclusivamente à sua conduta, de seus empregados e representantes, devendo, caso constatada procedência, apresentar à SAMARCO plano de ação específico com medidas corretivas e mitigadoras, contendo prazos definidos para sua execução e comprovação de sua efetividade.
[P509] A apuração será conduzida de forma sigilosa e confidencial, sendo vedado à CONTRATADA compartilhar quaisquer informações relacionadas à denúncia – incluindo, mas não se limitando à identidade dos envolvidos – com qualquer pessoa que não integre sua área de Compliance, a qual deverá assegurar o tratamento restrito das informações recebidas.
[P511] É expressamente vedada qualquer forma de retaliação por parte da CONTRATADA a qualquer pessoa envolvida, direta ou indiretamente, na denúncia, sob pena de aplicação das sanções previstas neste instrumento.
[P513] A CONTRATADA autoriza expressamente a SAMARCO a requisitar documentos, informações, evidências e quaisquer registros necessários para o acompanhamento da apuração, comprometendo-se a fornecer os dados solicitados de forma tempestiva, adequada e com a devida classificação da informação como confidencial.
[P515] O descumprimento, por parte da CONTRATADA, das obrigações previstas nesta cláusula, inclusive, mas não se limitando, à prática de atos ilícitos, antiéticos, retaliatórios ou de omissão injustificada de resposta, ensejará a aplicação de sanções contratuais, sem prejuízo das demais medidas legais cabíveis, inclusive a rescisão contratual por justa causa e indenizações por perdas e danos.
[P517] A CONTRATADA declara e garante que seus Funcionários que atuam nos negócios relacionados ao CONTRATO que envolvam direta ou indiretamente a SAMARCO, não violaram e não violarão a legislação anticorrupção na execução deste CONTRATO.
[P519] A CONTRATADA deverá comunicar a CONTRATANTE imediatamente, através de envio de e-mail ao Gestor do Contrato, e em nenhuma hipótese em mais de 15 (quinze) DIAS após tomar conhecimento, dos seguintes eventos:
[P521] Qualquer violação real ou iminente da legislação anticorrupção aplicável.
[P523] Existência ou possibilidade, seja no Brasil ou no exterior, de qualquer investigação, processo administrativo ou judicial que esteja relacionado, direta ou indiretamente, às atividades da CONTRATADA (ou de qualquer um de seus Funcionários envolvidos nas atividades deste CONTRATO) que apure ou que inclua quaisquer alegações de fraude, corrupção, lavagem de dinheiro ou violações da legislação anticorrupção aplicável.
[P525] Caso, na execução do objeto deste CONTRATO, os funcionários ou representantes da CONTRATADA interajam ou tenham a expectativa de interação com Agente Público ou com a administração pública em nome da CONTRATANTE, suas empresas controladas e coligadas, estes deverão obrigatoriamente e previamente à execução dos serviços, realizar o treinamento disponibilizado para tal fim na plataforma da CONTRATANTE.
[P527] PRESTAÇÃO DE INFORMAÇÕES
[P529] A CONTRATADA concorda em documentar de forma precisa e detalhada em seus livros e registros, bem como nos documentos fornecidos à CONTRATANTE, todas as transações relacionadas, direta ou indiretamente, ao presente CONTRATO. Tais registros deverão ser mantidos de maneira organizada pela CONTRATADA durante a vigência do CONTRATO, e por um período adicional de 5 (cinco) anos após sua extinção, independente do motivo.
[P531] Durante o prazo do presente CONTRATO e por 5 (cinco) anos após o seu término, mediante comunicado por escrito com 15 (quinze) DIAS de antecedência, a CONTRATADA concorda em permitir que a CONTRATANTE, ou terceiros por ela autorizados, tenham acesso a todos os livros, registros, documentos e informações relacionados ao objeto do CONTRATO, podendo obter cópias, a fim de verificar a conformidade da CONTRATADA com este CONTRATO. A CONTRATANTE envidará seus melhores esforços para garantir que qualquer auditoria não interfira desarrazoadamente nas atividades normais da CONTRATADA. A CONTRATADA concorda em cooperar integralmente com a auditoria da CONTRATANTE, permitindo também que seus Funcionários sejam entrevistados.
[P533] As análises e acesso aos documentos previstos nesta Cláusula estão sujeitas aos deveres de Confidencialidade previsto no CONTRATO.
[P535] Durante o prazo do presente CONTRATO e por 5 (cinco) anos após o seu término, mediante comunicado por escrito com 15 (quinze) DIAS de antecedência, a CONTRATADA concorda em tomar todas as medidas necessárias para permitir que a CONTRATANTE tenha acesso a informações, documentos relacionados ao CONTRATO.
[P537] Qualquer violação das disposições desta cláusula durante o PRAZO DE VIGÊNCIA pela CONTRATADA autorizará a CONTRATANTE, a seu exclusivo critério, a rescindir o presente instrumento imediatamente mediante notificação por escrito e sem qualquer obrigação da CONTRATANTE de pagar indenização ou danos à CONTRATADA. A CONTRATADA deverá, ainda, indenizar e isentar a CONTRATANTE de quaisquer prejuízos ou danos incorridos pela CONTRATANTE como resultado da violação dos termos desta cláusula durante ou após o PRAZO DE VIGÊNCIA.
[P539] PRIVACIDADE E PROTEÇÃO DE DADOS
[P541] As PARTES, ao tratarem dados pessoais no contexto de execução do CONTRATO, ainda que de maneira pontual, observarão o disposto nas leis de proteção de dados aplicáveis, incluindo, sem limitação, a Lei nº 13.709, de 14 de agosto de 2018 (“LGPD”), em especial lastrearão tratamentos de dados em base legal e em observância aos princípios da LGPD. Fica também ajustado entre as PARTES que tratarão tais dados pessoais na medida do necessário para atingir a finalidade para qual eles foram fornecidos, para cumprimento das obrigações e prerrogativas previstas no CONTRATO e eventuais obrigações legais ou regulatórias, e em conformidade com as Políticas de Proteção de Dados e demais orientações da CONTRATANTE, obrigando-se a estender tais obrigações e conscientizar todos aqueles que engajar na cadeia de tratamento.
[P543] A CONTRATADA declara que, na execução deste CONTRATO, caso ocorra o tratamento de dados pessoais, cumprirá fielmente as diretrizes do Anexo XV – Termo LGPD, e concorda que será responsável perante a CONTRATANTE por qualquer violação à legislação de proteção de dados e privacidade aplicável que venha a ser cometida por seus Funcionários com relação a atividades direta ou indiretamente relacionadas à CONTRATANTE.
[P545] Caso a CONTRATANTE venha a ser responsabilizada, judicial ou extrajudicialmente, por danos causados pela CONTRATADA, esta se obriga a assumir a responsabilidade processual, assumindo o polo passivo da ação própria, se for o caso, e a ressarcir integralmente todos os custos e danos arcados pela CONTRATANTE, inclusive honorários advocatícios contratuais e sucumbenciais, além de qualquer quantia que seja obrigada a pagar em decorrência dos referidos danos, autorizando, desde logo, que a desconte da remuneração ora ajustada.
[P547] ENCERRAMENTO DO CONTRATO
[P549] O presente CONTRATO será extinto na (i) DATA DE TÉRMINO, (ii) após a consecução do seu objeto ou (iii) no caso de atingido o valor estabelecido neste instrumento, o que ocorrer primeiro, a critério exclusivo da CONTRATANTE, salvo se houver prorrogação destas condições, formalizado por termo aditivo.
[P551] Qualquer das PARTES poderá rescindir o presente CONTRATO, mediante simples aviso escrito à outra PARTE, sem necessidade de procedimento judicial ou extrajudicial, nos seguintes casos:
[P553] Ocorrendo caso fortuito ou de força maior, cujos efeitos persistirem por prazo maior do que o descrito no QUADRO RESUMO;
[P555] Uma das PARTES tiver sua falência decretada.
[P557] Imotivadamente, mediante aviso prévio escrito, com antecedência de 30 (trinta) dias, sem acarretar quaisquer penalidades, compensação ou lucros cessantes.
[P559] A rescisão operar-se-á de pleno direito na data de decretação da falência e, no caso da cláusula 23.2.1, no termo final do prazo indicado no QUADRO RESUMO.
[P561] O CONTRATO poderá ser resilido por qualquer uma das PARTES, a qualquer momento, mediante comunicação por escrito enviada com antecedência indicada no QUADRO-RESUMO, sem que sejam devidas penalidades, multas ou indenizações de uma PARTE a outra, operando-se a resilição, de pleno direito após decorrido tal prazo.
[P563] Adicionalmente, a CONTRATANTE poderá rescindir o CONTRATO de pleno direito, mediante simples aviso escrito à CONTRATADA, sem necessidade de procedimento judicial ou extrajudicial, e sem que caiba à CONTRATADA qualquer direito de indenização ou ressarcimento, se a CONTRATADA:
[P565] Descumprir quaisquer obrigações do CONTRATO não sanadas no prazo mencionado na cláusula de penalidades ou descumprir obrigação insanável, como por exemplo normas de anticorrupção/compliance.
[P567] Der causa à suspensão dos Serviços por determinação das autoridades competentes ou pela falta de cumprimento de prescrições técnicas, administrativas ou legais na sua execução;
[P569] Promover, supervenientemente, ações judiciais contra a CONTRATANTE, suas controladas, controladoras e empresas a ela coligadas, considerando não somente ações movidas pela CONTRATADA, mas também aquelas manejadas por seus acionistas, quotistas ou empresas que façam parte do mesmo grupo econômico;
[P571] Reincidir no descumprimento de normas referentes à SST;
[P573] Demonstrar incapacidade técnica, imperícia, imprudência ou negligência da CONTRATADA ou qualquer de seus subcontratados;
[P575] Praticar ato intencional, de natureza grave, assim entendido conforme critério exclusivo da CONTRATANTE, contrário às disposições deste CONTRATO.
[P577] Sofrer condenação em processos administrativos ou judiciais com relação às Legislação Anticorrupção;
[P579] Ficar impedida de executar o CONTRATO em razão de alteração na legislação vigente.
[P581] Nas hipóteses previstas na cláusula anterior, (i) a rescisão operar-se-á de pleno direito na data de envio da notificação pela CONTRATANTE à CONTRATADA e (ii) fica facultado à CONTRATANTE promover a rescisão do CONTRATO, ou, a seu exclusivo critério, mantê-lo e/ou promover a execução específica das obrigações inadimplidas, sem prejuízo de aplicar as penalidades previstas no CONTRATO e de ser ressarcida pelas perdas e danos sofridos; (iii) não convindo à CONTRATANTE a rescisão do CONTRATO, poderá a CONTRATANTE intervir no CONTRATO, de maneira que melhor satisfaça a seus interesses, correndo, por conta da CONTRATADA, os ônus decorrentes da intervenção.
[P583] Na hipótese de rescisão deste CONTRATO por culpa de uma das PARTES, a PARTE que der causa ao encerramento pagará à PARTE inocente a importância equivalente a 5% (cinco por cento) do saldo do VALOR ESTIMADO DO CONTRATO apurado no momento do encerramento, a título de multa rescisória. Caso a rescisão se dê por culpa da CONTRATANTE, esta pagará, ainda, os valores proporcionais às atividades da CONTRATADA, total ou parcialmente executada até então. Caso a rescisão se dê por culpa da CONTRATADA, esta pagará, ainda, os valores de perdas e danos suplementares que forem apurados.
[P585] Antes da extinção do CONTRATO, a CONTRATADA deverá tomar todas as providências necessárias para transmitir à CONTRATANTE todos os direitos, garantias, compensações, benefícios, titularidades, posse e participação da CONTRATADA relacionada aos Serviços até a data de extinção do CONTRATO.
[P587] Uma vez distratado ou rescindido este CONTRATO, poderá a CONTRATANTE entregar a conclusão dos Serviços a qualquer outra executante, independentemente da anuência da CONTRATADA.
[P589] Ocorrendo uma ou mais das hipóteses de rescisão desta cláusula, e não convindo à CONTRATANTE a rescisão do CONTRATO, poderá ela intervir nos Serviços contratados, de maneira que melhor satisfaça a seus interesses, correndo, por conta da CONTRATADA, os ônus decorrentes da intervenção.
[P591] Quando aplicável, após o término dos Serviços, providenciar a retirada, às suas custas, das máquinas, equipamentos, veículos, utensílios, acessórios, materiais e instalações provisórias de sua propriedade e de seus subcontratados, removendo-os dentro do prazo a ser acordado entre as PARTES, não superior a 15 (quinze) DIAS, a contar de solicitação escrita da CONTRATANTE. Caso este prazo não seja cumprido, a CONTRATANTE poderá, à sua conveniência, executar esta retirada, debitando as despesas respectivas da CONTRATADA, adicionadas dos custos eventualmente necessários para acautelar a ocorrência de danos, perdas, furtos ou extravios, inclusive os das coberturas de seguros aplicáveis.
[P593] A CONTRATANTE, após prévia notificação judicial, ou extrajudicial, terá o direito de reter, qualquer pagamento devido à CONTRATADA, oriundo deste CONTRATO ou outro instrumento celebrado com a CONTRATADA, a quantia correspondente ao custo de eventuais indenizações e reclamações, até a remoção, pela CONTRATADA, do aludido vínculo ou liame e liquidação da indenização, reclamação ou reivindicação porventura daí decorrente.
[P595] O Serviços executados até a data da extinção do CONTRATO serão normalmente medidos e pago nos termos do CONTRATO.
[P597] Os direitos da CONTRATANTE relativos às consequências da extinção antecipada do CONTRATO não eliminam ou restringem o direito desta em aplicar à CONTRATADA as penalidades previstas neste CONTRATO.
[P599] Na hipótese de extinção do CONTRATO, por qualquer motivo, as PARTES se comprometem a assinar um termo de encerramento do CONTRATO. As PARTES desde já ajustam que o CONTRATO será considerado plenamente encerrado e quitado se a CONTRATADA se mantiver silente e/ou inerte sobre a assinatura do termo de encerramento após o transcurso de 30 (trinta) DIAS do envio do termo de encerramento pela CONTRATANTE.
[P601] A CONTRATADA deverá desocupar inteiramente o LOCAL DE PRESTAÇÃO DOS SERVIÇOS, deixando-o livre de quaisquer materiais, equipamentos, profissionais, poluentes, lixos e entulhos, dando a estes últimos destinação adequada, bem como de equipamentos utilizados  e relacionados  aos Serviços, removendo-os dentro do prazo determinado pela CONTRATANTE. Caso este prazo não seja cumprido, a CONTRATANTE poderá, à sua conveniência, proceder à retirada, debitando as respectivas despesas, adicionadas dos custos eventualmente necessários para acautelar a ocorrência de danos, perdas, furtos ou extravios, inclusive os das coberturas de seguros aplicáveis.
[P603] ARBITRAGEM E FORO
[P605] As PARTES se comprometem a envidar seus melhores esforços para resolver, amigavelmente e de boa fé, quaisquer demandas, divergências e outras questões oriundas deste CONTRATO, por meio de negociações diretas.
[P607] Não sendo possível a solução, por meio de negociação direta, fica desde já convencionado, de forma irrenunciável, que, quaisquer controvérsias oriundas deste CONTRATO, serão definitivamente resolvidas por meio de arbitragem, nos termos da Lei nº 9.307, de 23/09/1996, de acordo com as regras da Câmara de Arbitragem Empresarial Brasil (CAMARB).
[P609] Para os fins da arbitragem, as PARTES ajustam, desde logo, o seguinte:
[P611] O presente CONTRATO, nos termos ora previstos, assim como os direitos e obrigações das PARTES dele decorrentes, serão interpretados e regidos pelas leis da República Federativa do Brasil;
[P613] Quaisquer questões, controvérsias, disputas ou reivindicações decorrentes de ou relacionadas à validade, interpretação, desempenho, implementação, rescisão ou violação deste Instrumento (incluindo a validade desta cláusula de ARBITRAGEM), bem como quaisquer relações jurídicas relativas a este CONTRATO, serão resolvidas, de maneira exclusiva e definitiva, por arbitragem, final e vinculante, a ser processada perante a Câmara de Arbitragem Empresarial – Brasil (CAMARB), de acordo com as suas regras e regimento (“Regulamento”) que estiver em vigor na data do pedido de instauração da arbitragem.
[P615] A arbitragem será conduzida por 3 (três) árbitros, cabendo a cada uma das PARTES a indicação de um árbitro. O arbitro deverá ser pessoa de reconhecida competência no assunto principal objeto do litígio, que não possua impedimento para atuação no procedimento, e deve fazer parte da lista de árbitros da CAMARB. O terceiro árbitro, que funcionará como o Presidente do Tribunal Arbitral, será nomeado de comum acordo pelos árbitros indicados pelas PARTES. Caso os 2 (dois) árbitros indicados pelas PARTES deixem de nomear o terceiro árbitro, no prazo regulamentar, ou não havendo consenso entre os árbitros a respeito da nomeação do terceiro árbitro, caberá à CAMARB indicar o terceiro árbitro.
[P617] Para controvérsias que possam envolver valores de até R$ 1.000.000,00 (um milhão de reais), as PARTES escolherão árbitro único. Não havendo consenso, caberá à CAMARB indicar o árbitro único.
[P619] Os procedimentos da arbitragem terão lugar na Cidade de Belo Horizonte, Estado de Minas Gerais, Brasil.
[P621] Os procedimentos de arbitragem serão conduzidos no idioma português e o laudo arbitral será redigido em português.
[P623] O Tribunal Arbitral não poderá arbitrar honorários sucumbenciais em favor da parte vencedora.
[P625] - Cada PARTE mantém o direito de buscar perante a jurisdição competente as medidas judiciais cautelares e/ou de urgência que entenderem necessárias para proteger e garantir direitos, antes da instauração do Tribunal Arbitral, cientes de que essas medidas judiciais não serão interpretadas como renúncia à arbitragem. Para o exercício desse direito, as PARTES elegem o foro da Comarca de Belo Horizonte, Estado de Minas Gerais, Brasil, com renúncia expressa a qualquer outro por mais privilegiado que possa ser.
[P627] A instauração e o procedimento arbitral não deverão influenciar a execução do CONTRATO, devendo as PARTES continuar cumprindo fielmente as obrigações contratuais que porventura não estejam diretamente impedidas pela arbitragem, sob pena de caracterizar descumprimento contratual.
[P629] A PARTE que violar a cláusula de arbitragem ou para prejudicar, obstaculizar ou impedir a solução da controvérsia por meio da arbitragem, ficará automaticamente sujeita ao pagamento de multa no valor correspondente a 10% sobre o VALOR ESTIMADO CONTRATO.
[P631] Entre outras, entendem-se como práticas violadoras da cláusula de arbitragem: (i) recusar ou se abster de participar atos no procedimento arbitral; (ii) descumprir prazos; (iii) prejudicar ou impedir o andamento do procedimento; (iv) adotar prática desleal, temerária ou protelatória.
[P633] A multa será exigida por meio de emissão de nota de débito ou executada diretamente, sem prejuízo da instauração e do processamento da arbitragem, de acordo com o procedimento previsto no Regulamento da CAMARB.
[P635] A sentença arbitral será definitiva, irrecorrível (exceção feita à hipótese do artigo 30 da Lei n.º 9.307/96) e obrigará plenamente as PARTES ligantes e seus sucessores, devendo ser imediatamente cumprida em todos os seus termos pelas PARTES, as quais se declaram, desde logo, cientes de que o não cumprimento da sentença arbitral autoriza a sua execução diretamente no Judiciário.
[P637] Para a resolução de disputas que se refiram exclusivamente ao COMODATO, , se aplicável, as partes elegem como foro contratual, a Comarca de Belo Horizonte, Estado de Minas Gerais, excluindo qualquer outro por mais privilegiado que seja.
[P639] DISPOSIÇÕES GERAIS
[P641] A CONTRATADA reconhece que poderá haver outros contratos que apresentam interfaces com o seu, e desde já se compromete a harmonizar/adequar as suas atividades com os respectivos contratados, a fim de não causar prejuízos diretos e/ou indiretos, de modo que qualquer entendimento entre a CONTRATADA e as demais empresas contratadas pela CONTRATANTE deverão ser aprovadas pela CONTRATANTE previamente e por escrito.
[P643] O CONTRATO é aceito pelas PARTES como completo e suficiente para definir o objeto dos Serviços, assim como sua extensão e intenção, dentro das leis e normas específicas vigentes no Brasil.
[P645] A CONTRATANTE reserva-se o direito de auditar qualquer das etapas do objeto do CONTRATO, a qualquer tempo, desde que no horário normal de trabalho da CONTRATADA e de seus subcontratados aprovados.
[P647] Quando aplicável, a CONTRATADA declara que tem ciência e cumprirá as diretrizes que integram, ANEXO - Termo de Compromisso Socioambiental nº 01/2011 - Plano Integrado de Ocupação da Rede Hoteleira (UBU), Anexo - NR 18 - Condições e Meio Ambiente de Trabalho na Indústria da Construção e Anexo - Relatório Mensal de Desempenho da CONTRATADA.
[P649] Este instrumento, juntamente com seus ANEXOS, constitui o acordo integral entre as PARTES. Ele substitui e cancela todas as demais comunicações, verbais ou escritas, propostas e declarações referentes ao objeto aqui versado.
[P651] Nenhuma modificação do CONTRATO vinculará as PARTES, exceto quando efetuada por escrito, assinada pelos representantes legais de cada PARTE, mediante o respectivo Termo Aditivo Contratual.
[P653] As Partes reconhecem a veracidade, autenticidade, integridade, validade e eficácia deste CONTRATO e seus termos, nos moldes do art. 219 do Código Civil, caso assinado digitalmente pelas PARTES, ainda que com utilização de meios diversos aos certificados eletrônicos emitidos pela ICP-Brasil, em observância aos ditames do art. 10, § 2º, da Medida Provisória nº 2.200-2, de 24 de agosto de 2001 (“MP nº 2.200-2”).
[P655] As PARTES de comum acordo estabelecem que o quanto negociado neste CONTRATO não representará um precedente para as próximas negociações futuras.
[P657] As Partes declaram e concordam que a assinatura do presente CONTRATO poderá ser efetuada em formato eletrônico. As Partes reconhecem a veracidade, autenticidade, integridade, validade e eficácia do presente instrumento e seus termos, incluindo seus ANEXOS, nos termos do art. 219 do Código Civil, em formato eletrônico e/ou assinado pelas Partes por meio de certificados eletrônicos, ainda que sejam certificados eletrônicos não emitidos pela ICP-Brasil, nos termos do art. 10, § 2º, da Medida Provisória nº 2.200-2, de 24 de agosto de 2001 (“MP nº 2.200-2”). Cada um dos indivíduos que assina em nome das Partes declara e garante que está autorizado a executar o presente instrumento em nome da respectiva Parte, bem como que o presente instrumento, quando executado, tornar-se-á válido e vinculante de acordo com seus termos.
[P659] Em caso de assinatura física, o presente CONTRATO será assinado na quantidade de vias correspondentes à quantidade de PARTES, e, em qualquer formato de assinatura, o CONTRATO segue assinado também por 2 (duas) testemunhas, todos de igual teor e forma, para um só efeito.
[P661] Belo Horizonte, _______________________________.
[P664] Samarco Mineração S.A.:
[P669] PREENCHER COM O NOME DA CONTRATADA:
[P675] TESTEMUNHAS:
```

---

## DOCUMENTO VERSÃO ATUAL (Modificado)

```text
[P001] CONTRATO DE PRESTAÇÃO DE SERVIÇOS
[P006] CONTRATANTE e CONTRATADA, doravante denominadas em conjunto “PARTES” e individualmente “PARTE”, ajustam entre si o presente CONTRATO DE PRESTAÇÃO DE SERVIÇOS (“CONTRATO”), que se regerá pelo QUADRO RESUMO e pelas Condições Gerais abaixo, modificadas, se cabível, pelas CONDIÇÕES ESPECIAIS.
[P008] CONDIÇÕES GERAIS
[P012] OBJETO
[P014] A CONTRATADA prestará à CONTRATANTE os serviços técnicos especializados detalhados no campo Serviços do QUADRO RESUMO, os quais serão prestados conforme disciplinado neste CONTRATO e nas ordens de serviço emitidas pela CONTRATANTE, admitindo-se ajustes operacionais de escopo por comunicação escrita do Gestor do Contrato, desde que não impliquem alteração substancial do objeto.
[P016] Este CONTRATO não implica dever de exclusividade da CONTRATANTE, ressalvado que, durante a vigência contratual, a CONTRATANTE deverá preferencialmente consultar a CONTRATADA antes de contratar terceiros para escopo idêntico no mesmo LOCAL DE PRESTAÇÃO DOS SERVIÇOS.
[P018] Os ANEXOS “Documentos Contratuais Gerais” ficam dispensados de rubrica ou validação digital posterior. A CONTRATADA declara que já recebeu estes ANEXOS previamente em mídia eletrônica ou outra forma de acesso, que tem ciência do seu conteúdo e que concorda com os termos neles contidos, comprometendo-se a cumpri-los na sua integralidade.
[P020] Os termos do QUADRO RESUMO prevalecem sobre os termos destas Condições Gerais, os quais prevalecem sobre os termos dos ANEXOS, exceto quando determinado ANEXO contiver condição técnica mais específica e expressamente aceita pelas PARTES. Na hipótese de conflitos entre os ANEXOS, prevalecerão uns sobre os outros na ordem em que se acham listados no QUADRO RESUMO acima.
[P022] A CONTRATADA, em nenhuma hipótese, poderá alegar, como justificativa ou defesa, o desconhecimento, incompreensão, dúvida, no todo ou em parte, das disposições do presente CONTRATO e demais disposições de ordem geral ou particular nele estabelecidas, que são, desde já, consideradas necessárias e suficientes para definir os Serviços e os fornecimentos contidos no que foi contratado, e, ainda, permitir a sua execução de acordo com as normas vigentes no País, sendo vedado à CONTRATADA pleitear qualquer revisão de preços ou prorrogação de prazo, por erros ou omissões, que tenham sido cometidos na elaboração de sua(s) Proposta(s) que integra(m) o CONTRATO.
[P024] A CONTRATADA declara ter ciência das condições da região onde se localizam as instalações da CONTRATANTE, assumindo exclusiva responsabilidade pelo perfeito conhecimento das diversas condicionantes que possam afetar os Serviços, entre as quais, mas sem limitação, se encontram: transporte, acesso, manuseio e armazenagem de materiais/equipamentos, disponibilidade e qualidade de força de trabalho, água e energia elétrica, disponibilidade e estado de estradas e vias de acesso, condições climáticas, hidrológicas, hidrometeorológicas, pluviométricas, físicas e ainda os regulamentos e normas vigentes no LOCAL DE PRESTAÇÃO DOS SERVIÇOS. Em função disto, a CONTRATADA renuncia a quaisquer reivindicações ou compensações adicionais sobre qualquer falha na avaliação adequada das dificuldades locais.
[P026] VIGÊNCIA E SUSPENSÃO
[P028] O CONTRATO terá vigência a partir do INÍCIO DA VIGÊNCIA e encerrará (i) após o TÉRMINO DA VIGÊNCIA indicado no QUADRO RESUMO, (ii) após o cumprimento de todas as obrigações do CONTRATO e/ou dele decorrentes ou (iii) no caso de atingido o valor estabelecido neste instrumento, o que ocorrer primeiro, independentemente de qualquer notificação judicial ou extrajudicial.
[P030] Se aplicável, a retroatividade dos efeitos do CONTRATO, não ocasionará qualquer prejuízo das obrigações da CONTRATADA sem acarretar quaisquer penalidades, compensação ou lucros cessantes para a CONTRATANTE, conforme prazo descrito no QUADRO RESUMO.
[P032] O PRAZO DE VIGÊNCIA já considera todos os dias necessários para as providências prévias e finais, incluindo eventual mobilização, execução e desmobilização, por parte da CONTRATADA.
[P034] Havendo interesse entre as PARTES, este CONTRATO poderá ter sua vigência prorrogada, mediante assinatura de Termo Aditivo formalizado entre as PARTES.
[P036] O CONTRATO poderá ser suspenso total ou parcialmente, mediante comunicação por escrito da CONTRATANTE à CONTRATADA enviada com antecedência mínima de 15 (quinze) DIAS, salvo urgência operacional, determinação do Poder Público ou decisão judicial, hipótese em que a suspensão poderá produzir efeitos imediatos.
[P038] A CONTRATADA deverá reassumir a execução do CONTRATO em até 30 (trinta) DIAS após recebimento de comunicação expressa pela CONTRATANTE, se outro prazo não for acordado entre as PARTES.
[P040] A CONTRATADA não terá direito de indenização de qualquer natureza em razão da suspensão dos Serviços, exceto em relação aos custos diretos, necessários e comprovadamente incorridos em razão da suspensão, desde que previamente aprovados pela CONTRATANTE e sem inclusão de margem, lucros cessantes ou custos indiretos.
[P042] VALOR, PREÇOS E FORMA DE PAGAMENTO
[P044] Para fins legais e contratuais, inclusive para aplicação de multas e penalidades, deve ser considerado o VALOR ESTIMADO DO CONTRATO. Sendo o valor estimado, a CONTRATADA não poderá receber valores sem que tenha efetivamente prestado os Serviços correspondentes, salvo hipóteses de mobilização, desmobilização ou disponibilidade mínima expressamente previstas no QUADRO RESUMO ou nos ANEXOS.
[P046] Caso o dia do pagamento devido pela CONTRATANTE se dê em feriados bancários ou em finais de semana, será considerado como data de vencimento o primeiro dia útil subsequente.
[P048] Os pagamentos serão efetuados pela CONTRATANTE mediante crédito em conta corrente, sendo para todos os fins o comprovante bancário considerado prova de pagamento. No caso de mudança de estabelecimento bancário ou número da conta corrente, a CONTRATADA deverá comunicar ao Gestor do Contrato, com antecedência mínima de 30 (trinta) DIAS o novo estabelecimento ou a nova conta, sob pena de o depósito ser efetuado na conta anteriormente indicada.
[P050] A ausência de qualquer contestação por parte da CONTRATADA, no prazo de 60 (sessenta) DIAS, contados da data do depósito, deverá caracterizar a quitação plena, rasa, geral e irrevogável, conferida pela CONTRATADA à CONTRATANTE, relativamente ao pagamento dos materiais ou Serviços lançados na nota fiscal/fatura respectiva, não cabendo, nessa hipótese, à CONTRATADA, qualquer reivindicação, a qualquer título.
[P052] Se os pagamentos efetuados na forma deste item forem superiores aos valores efetivamente devidos, responderá a CONTRATADA pelas diferenças, que poderão ser descontadas de pagamentos futuros, inclusive relativos a outros créditos que a CONTRATADA tenha junto à CONTRATANTE.
[P054] CORREÇÃO MONETÁRIA
[P056] Se aplicável, a partir do 12º mês contado da data-base, a CONTRATADA poderá solicitar, anualmente, o reajuste dos preços praticados no CONTRATO mediante a aplicação do ÍNDICE DE REAJUSTE indicado no QUADRO RESUMO. A atualização com base no ÍNDICE DE REAJUSTE será aplicada mediante solicitação formal da CONTRATADA e aprovação do Gestor do Contrato, dispensada a formalização de aditivo quando não houver alteração de escopo ou de valor global estimado.
[P058] Caso o reajuste seja solicitado em prazo superior a 120 (cento e vinte) dias após a data-base, os preços reajustados somente serão aplicados aos serviços/fornecimentos realizados após a data de solicitação do reajuste, não retroagindo aos serviços/fornecimentos realizados anteriormente.
[P060] Uma vez reajustados, os valores permanecerão fixos por novo período de 12 (doze) meses, quando então os valores remanescentes poderão ser reajustados.
[P062] A aplicação do ÍNDICE DE CORREÇÃO MONETÁRIA ocorrerá apenas a partir da primeira medição subsequente ao período da data-base, não sendo admitida a aplicação retroativa sobre a medição em curso. Fica expressamente vedada a utilização, em uma mesma medição, de valores distintos decorrentes de atualização parcial, de modo que os serviços/fornecimentos faturados em cada medição estarão integralmente sujeitos às condições vigentes (com ou sem atualização), conforme a sua competência temporal.
[P064] A CORREÇÃO MONETÁRIA não incidirá sobre: (i) valores pagos em atraso em razão de eventos de responsabilidade da CONTRATADA; (ii) valores eventualmente devidos pela CONTRATADA à CONTRATANTE, isto é, os itens (i) a (ii) serão deduzidos da base de cálculo para fins de CORREÇÃO MONETÁRIA, de modo que somente o saldo contratual remanescente estará sujeito à aplicação do  ÍNDICE DE CORREÇÃO MONETÁRIA.
[P066] O ÍNDICE DE CORREÇÃO MONETÁRIA do CONTRATO será aplicado unicamente pelas previsões contidas nesta cláusula, não devendo se vincular a qualquer tipo de previsões contidas em propostas, convenções coletivas, acordos coletivos e afins.
[P068] TRIBUTOS
[P070] Todas as obrigações tributárias principais e acessórias que incidam ou venham a incidir, direta ou indiretamente sobre os Serviços são de responsabilidade da CONTRATADA, que deverá, quando a legislação não exigir da CONTRATANTE a obrigação de retenção, comprovar o cumprimento de tais obrigações à CONTRATANTE.
[P072] A CONTRATADA declara estar ciente de que, no momento do pagamento, a CONTRATANTE observará a legislação vigente referente à retenção do Imposto Sobre Serviços de Qualquer Natureza (ISSQN), do Imposto sobre a Renda (IR), da Contribuição Social sobre o Lucro Líquido (CSLL), da Contribuição para o Programa de Integração Social (PIS) e da Contribuição para o Financiamento da Seguridade Social (COFINS), sendo que, na medida de sua aplicabilidade, procederá à retenção dos aludidos tributos.
[P074] Eventuais alterações na legislação que impactem na tributação relativa a este CONTRATO, para mais ou para menos, serão objeto de análise e negociação entre as PARTES, de modo a se determinar a sua influência final sobre os preços contratuais.
[P076] As despesas decorrentes de ações administrativas/judiciais visando discutir atos do Poder Público que alterem os encargos acima indicados, serão de exclusiva responsabilidade da CONTRATADA.
[P078] Quando legalmente aplicável, e para todos os fins previdenciários, a Matrícula CEI, a qual o objeto deste CONTRATO se refere, será comunicada formalmente à CONTRATADA, para que esta vincule seus recolhimentos previdenciários. A CONTRATADA deve zelar pelo correto e tempestivo lançamento e recolhimento da contribuição previdenciária vinculada a essa Matrícula CEI e o correto cumprimento de suas obrigações acessórias, estando, ainda, obrigada a proceder à imediata retificação nos casos em que forem identificados erros, omissões, incorreções, ou outras incongruências, inclusive aquelas apontadas pela CONTRATANTE. As consequências do descumprimento do disposto neste item serão atribuídas exclusivamente à CONTRATADA, cumulativamente às multas contratualmente previstas.
[P080] MEDIÇÃO, FATURAMENTO E FORMA DE PAGAMENTO
[P082] Os pagamentos serão efetuados pela CONTRATANTE mediante crédito em conta corrente fornecida pela CONTRATADA, servindo o comprovante bancário de prova de pagamento.
[P084] Independente da FORMA DE PAGAMENTO, a CONTRATADA deverá emitir o BMM ou BM para realizar a MEDIÇÃO MENSAL da parcela efetivamente executada no PERÍODO DE MEDIÇÃO, sendo que no caso de pagamento conforme os MARCOS CONTRATUAIS, a CONTRATADA deverá emitir o BM após o cumprimento de tais marcos.
[P086] A CONTRATADA deverá apresentar o BMM ou o BM ao Gestor do Contrato com a relação de todos os Serviços executados até o último dia do período de medição e sua respectiva valoração, com base nos preços contratuais, juntamente com os comprovantes de quitação legal contratualmente exigíveis.
[P088] Em caso de não aceitação do BM ou BMM por parte da CONTRATANTE, as medições serão recusadas e o pagamento correspondente ficará suspenso quanto aos itens efetivamente controvertidos, devendo a CONTRATANTE liberar o faturamento da parte incontroversa dos Serviços executados. Os itens controversos deverão ser informados pela CONTRATANTE por escrito e de forma fundamentada.
[P089] Atrasos não justificados na liberação da medição, por motivos imputáveis à CONTRATADA, implicarão automaticamente na prorrogação do prazo de pagamento estabelecido no CONTRATO, sem quaisquer ônus para a CONTRATANTE.
[P091] A elaboração, a entrega e a aprovação do BMM ou BM obedecerá ao seguinte procedimento:
[P093] No último dia do PERÍODO DE MEDIÇÃO, a CONTRATADA emitirá o BM ou BMM, que conterá todos os Serviços executados até o último dia do PERÍODO DE MEDIÇÃO e respectiva valoração, com base nos preços contratuais.
[P095] O BMM ou BM será entregue pela CONTRATADA à CONTRATANTE, em via física ou digital. O BM ou BMM deverá ser entregue acompanhado de cópia dos documentos indicados no QUADRO RESUMO, bem como de qualquer documento adicional que a CONTRATANTE entender necessário para o cumprimento das obrigações legais ou contratuais da CONTRATADA.
[P097] Caso a CONTRATANTE constate qualquer erro, imprecisão, falha no BM ou BMM, incompletude ou deficiência de informação nos documentos mencionados no item anterior, o BM ou BMM será devolvido à CONTRATADA, contendo as justificativas para a sua rejeição. Nessa hipótese, o prazo para a CONTRATANTE aprovar o BM ou BMM ficará suspenso até a reapresentação, não se renovando integralmente quando as correções forem meramente formais.
[P099] Para fechamento e aprovação do BM ou BMM, a CONTRATADA deverá declarar a existência, se houver, de eventuais pleitos até o fechamento, porquanto a CONTRATANTE não admitirá a abordagem de pleitos que não foram levantados na época oportuna.
[P101] O pleito deverá ser apresentado formalmente e por escrito junto à CONTRATANTE, fazendo expressa referência à ocorrência, apresentando os documentos e demais meios de sua comprovação e o seu valor.
[P103] A não apresentação do pleito até 30 (trinta) DIAS contados da data em que a CONTRATADA tiver ciência do evento poderá caracterizar renúncia ao direito, salvo se demonstrada impossibilidade justificada de apuração imediata do impacto financeiro ou de prazo.
[P105] A liberação do BM ou BMM não configura aceitação técnica definitiva dos Serviços executados, mas reconhece condições para faturamento. A rejeição posterior de Serviços já medidos deverá ser justificada tecnicamente pela CONTRATANTE e não poderá alcançar serviços que tenham sido expressamente aprovados sem ressalvas.
[P107] Após aprovação do BM ou BMM, a CONTRATANTE autorizará a CONTRATADA a emitir a respectiva nota fiscal/fatura, indicando, obrigatoriamente, o número do CONTRATO e do respectivo BM ou BMM, cuja via original, juntamente com a dos comprovantes de quitação legal contratualmente exigíveis, será anexada à nota fiscal/fatura.
[P109] Os Serviços executados e aprovados serão medidos e liberados para faturamento mensal, obedecendo aos critérios do QUADRO RESUMO e dos ANEXOS que tratam sobre o tema.
[P111] As notas fiscais/faturas emitidas serão entregues pela CONTRATADA conforme QUADRO RESUMO.
[P113] Obrigatoriamente, as notas fiscais/faturas deverão ser entregues ao Gestor do Contrato da CONTRATANTE até o dia 25 (vinte e cinco) de cada mês. Após esta data, só poderão ser aceitas notas fiscais/faturas datadas a partir do primeiro dia útil do mês subsequente.
[P115] Nenhuma nota fiscal/fatura poderá ser emitida anteriormente à autorização ou entre os dias 26 a 31 de cada mês.
[P117] Para estabelecimento do valor final a ser efetivamente pago pela CONTRATANTE relativo a cada nota fiscal/fatura, deverão ser computados descontos aplicados com base nas disposições deste CONTRATO, inclusive decorrentes de penalidades, caso aplicadas, descontos estes constantes das Notas de Débito ou de Crédito que venham, conforme o caso, a ser emitidas, respectivamente, pela CONTRATANTE ou pela CONTRATADA.
[P119] É vedado à CONTRATADA ceder total ou parcialmente, oferecer em garantia ou realizar qualquer operação comercial tendo por objeto crédito decorrente deste CONTRATO, salvo prévia comunicação à CONTRATANTE com antecedência mínima de 10 (dez) DIAS, ou prévia e expressa concordância da CONTRATANTE quando houver impacto operacional ou risco de travamento bancário.
[P121] Os pagamentos impugnados pela CONTRATANTE não estão sujeitos a atualização ou ônus financeiros durante o período contestado, desde que a impugnação seja fundamentada e enviada à CONTRATADA antes do vencimento da respectiva nota fiscal/fatura.
[P123] A CONTRATANTE não aceitará travamento bancário ou qualquer instrumento financeiro similar.
[P125] Caso ocorra comprovado descumprimento de obrigações contratuais, a CONTRATANTE poderá realizar a retenção proporcional de parte das medições mensais da CONTRATADA, limitada ao valor razoavelmente estimado do descumprimento, devendo liberar o saldo incontroverso e indicar por escrito a forma de regularização.
[P127] As importâncias retidas na forma do item acima, acima, serão liberadas à CONTRATADA, segundo o cronograma de faturamento, e desde que o fato gerador da retenção seja comprovadamente sanado, indenizado e/ou tenha a respectiva penalidade quitada pela CONTRATADA. Esses valores não sofrerão a incidência de quaisquer correções monetárias ou juros.
[P129] Caso haja atraso no pagamento de qualquer nota fiscal/fatura, por motivos imputáveis exclusivamente à CONTRATANTE, os valores em atraso serão acrescidos de juros de mora de 1% a.m., calculados com base no ÍNDICE DE CORREÇÃO indicado no QUADRO RESUMO, entre a data de vencimento da nota fiscal/fatura e a do seu efetivo pagamento.
[P131] DISPONIBILIZAÇÃO DE BEM IMÓVEL EM COMODATO
[P133] Se aplicável conforme assinalado no QUADRO RESUMO, o IMÓVEL e suas benfeitorias ficam disponibilizados à CONTRATADA no estado descrito no Termo de Vistoria, que é ANEXO e parte integrante e inseparável deste Contrato.
[P135] A CONTRATADA se obriga a manter e a devolver o IMÓVEL à CONTRATANTE, quando findo ou rescindido o CONTRATO ou o COMODATO, bem como a custear toda e qualquer manutenção corretiva que se faça necessária no IMÓVEL em virtude de seu uso e gozo.
[P137] Havendo necessidade de expansão das instalações inerentes à execução das atividades a CONTRATADA deverá solicitar prévia e escrita autorização à CONTRATANTE, sendo a CONTRATADA de toda forma responsável pela gestão, manutenção e conservação destas extensões durante o PRAZO DE VIGÊNCIA deste CONTRATO.
[P139] Caso a CONTRATANTE solicite acréscimo de Funcionários ao Contrato e as instalações do IMÓVEL não possuam capacidade de atendimento, será de reponsabilidade da CONTRATADA fornecer acréscimo de instalações conforme normas vigentes, inclusive manter em perfeitas condições de Saúde, Segurança e Meio Ambiente, devendo os custos serem de responsabilidade da CONTRATADA, sem qualquer repasse destes à CONTRATANTE.
[P141] Quaisquer bens acessórios, melhorias e/ou benfeitorias necessárias realizadas pela CONTRATADA após o início do COMODATO serão incorporadas ao IMÓVEL e serão de propriedade da CONTRATANTE, não assistindo à CONTRATADA direito de retenção, ressalvado eventual ressarcimento de benfeitorias previamente autorizadas por escrito pela CONTRATANTE.
[P143] Para a realização de qualquer intervenção no IMÓVEL, deverá a CONTRATADA observar rigorosamente as exigências legais e administrativas das autoridades competentes relativas à aprovação dos projetos e execução dessas mesmas obras, especialmente no que concerne às autoridades encarregadas da saúde, bem como da administração, proteção e conservação do meio ambiente.
[P145] Antes de iniciar qualquer intervenção no IMÓVEL, como supressão de vegetação, obras civis, etc., a CONTRATADA deverá apresentar, previamente e de forma escrita, à CONTRATANTE toda e qualquer autorização emitida pelos órgãos competentes, sob pena de descumprimento do presente CONTRATO.
[P147] Em caso de danos diretos e/ou indiretos causados ao IMÓVEL e seus bens acessórios, a CONTRATANTE está autorizada a descontar dos valores devidos pela CONTRATADA, bem como cobrá-lo pelas vias cabíveis.
[P149] A CONTRATANTE poderá solicitar à CONTRATADA a extinção do COMODATO a qualquer tempo, bem como a desocupação do IMÓVEL e a retirada dos bens acessórios deste, devendo, para isso, enviar simples aviso escrito à CONTRATADA, que deverá desocupar a área no prazo descrito no QUADRO RESUMO, contados a partir da data do recebimento deste aviso, sendo dispensável qualquer procedimento judicial ou extrajudicial, e sem acarretar quaisquer penalidades, compensação ou lucros cessantes.
[P151] O IMÓVEL não poderá ser objeto de cessão, transferência, sublocação total ou parcial para terceiros, salvo prévia anuência por escrito da CONTRATANTE.
[P153] No caso de extinção do presente CONTRATO por quaisquer razões, cumprirá à CONTRATADA, restituir IMÓVEL, em perfeitas condições, no prazo indicado no QUADRO RESUMO.
[P155] Não caberá à CONTRATADA o direito a qualquer tipo de compensação, ressarcimento e/ou indenização na hipótese indicada no item acima.
[P157] Relativamente ao comodato, são obrigações da CONTRATADA:
[P159] Utilizar o IMÓVEL e seus bens acessórios, somente para a FINALIDADE EXCLUSIVA, respeitando as dimensões e diretrizes de ocupação dos espaços físicos determinadas pela Gerência de Infraestrutura, bem como as Diretrizes de Infraestrutura para Serviços Permanentes e Eventuais anexas.
[P161] Arcar com todas e quaisquer despesas de mobiliário, incluindo, mas não se limitando a mesas, cadeiras, armários, escaninhos, bebedouros, prateleiras, etc, devendo estes. estarem em conformidade com as normas de saúde, inclusive de ergonomia e estarem em bom estado de conservação.
[P163] Responsabilizar-se pelos custos de toda e qualquer manutenção corretiva causada por eventuais danos diretos e/ou indiretos causados ao IMÓVEL e seus bens acessórios.
[P165] Adotar as especificações do Caderno de Especificações do Plano Diretor de Infraestrutura da Samarco para realização de quaisquer benfeitorias, bem como para utilização de mobiliário.
[P167] Apresentar à CONTRATANTE, sempre que solicitado, todas as informações necessárias referentes às atividades no IMÓVEL.
[P169] Manter o IMÓVEL e seus bens acessórios em perfeito estado de guarda e conservação, procedendo todas as medidas necessárias ao funcionamento, limpeza, higiene e segurança do IMÓVEL, em conformidade com o estabelecido nas legislações pertinentes, assumindo todos os custos de qualquer natureza, sob pena de vir a responder por perdas e danos.
[P171] Informar por escrito e imediatamente à CONTRATANTE sobre qualquer defeito ou irregularidade no IMÓVEL ou danos a ele causado, ou sobre qualquer problema ocorrido na sua utilização.
[P173] Proteger o IMÓVEL contra turbações de terceiros.
[P175] Indenizar os prejuízos porventura causados em decorrência da utilização do IMÓVEL, mantendo a CONTRATANTE isenta de qualquer responsabilidade por tais prejuízos.
[P177] Permitir a inspeção do IMÓVEL pela CONTRATANTE, obrigando-se, para tanto, a franquear aos representantes da CONTRATANTE o acesso a qualquer das dependências do IMÓVEL.
[P179] Promover todas as medidas necessárias para que suas atividades no IMÓVEL não tragam qualquer embaraço aos interesses da CONTRATANTE.
[P181] Restringir sua ocupação à área delimitada pela Planta e Memorial Descritivo ou croqui de identificação da área do COMODATO.
[P183] Fornecer toda direção, supervisão técnica e administrativa e toda força de trabalho direta ou indireta, necessária à realização das atividades no IMÓVEL.
[P185] Contratar seguro de incêndio para o IMÓVEL, bem como a manutenção, em perfeitas condições, de todos os dispositivos de combate a incêndio, atendendo aos prazos de validade, inclusive conforme todas as normas vigentes. Caso o espaço não seja dotado de dispositivos de combate a incêndio e pânico, será de responsabilidade da CONTRATADA providenciar as adequações e aprovações necessárias, incluindo as obrigações relativas aos Autos de Vistorias do Corpo de Bombeiros.
[P187] DISPONIBILIZAÇÃO DE BENS E SERVIÇOS
[P189] A CONTRATANTE poderá fornecer os seguintes equipamentos, facilidades e serviços, nas quantidades que entender necessárias ao bom desenvolvimento dos Serviços, sem ônus para a CONTRATADA:
[P191] Alimentação para os profissionais alocados, durante o expediente, nos refeitórios da CONTRATANTE nas unidades de Germano e/ou Ponta de Ubu;
[P193] Atendimento médico ambulatorial de emergência nas unidades da CONTRATANTE.
[P195] Serviços de vigilância coorporativa da unidade em que os Serviços são prestados, não sendo fornecida vigilância específica para o objeto deste escopo ou, se aplicável, para o canteiro de obras da CONTRATADA.
[P197] Quando aplicável, as instalações, mobiliário, equipamentos, aparelhos e utensílios cedidos pela CONTRATANTE, para uso da CONTRATADA, inclusive em regime de Comodato, durante a prestação dos Serviços, permanecem de propriedade da CONTRATANTE, devendo a CONTRATADA zelar pelo seu bom uso e conservação, devolvendo-os ao término do CONTRATO em perfeito estado de conservação e uso.
[P199] O(s) bem(ns) cedido(s) em comodato será(ão) utilizado(s) pela CONTRATADA exclusivamente para fins da execução do objeto deste CONTRATO, sendo vedada a sua utilização para qualquer outro fim.
[P201] A CONTRATADA declara receber o (s) bem (ns) em perfeitas condições de conservação e funcionamento, obrigando-se a realizar, às suas custas, os consertos, reparos e substituições que forem necessárias, para que o(s) mesmo(s) seja(m) mantido(s) e venha(m) a ser restituído(s) nas mesmas condições recebidas, entendendo-se que a substituição de qualquer peça ou aparelho far-se-á por outra da mesma qualidade.
[P203] OBRIGAÇÕES DA CONTRATANTE
[P205] São obrigações da CONTRATANTE, sem prejuízo das demais previstas neste CONTRATO:
[P207] Efetuar as medições e remunerar a CONTRATADA na forma prevista neste instrumento.
[P209] Fornecer à CONTRATADA as informações que guardem conexão com o objeto deste instrumento e que se fizerem necessárias ao desenvolvimento dos Serviços.
[P211] Estabelecer as diretrizes para a implantação do objeto contratado.
[P213] Instruir a CONTRATADA quanto a normas e procedimentos internos da CONTRATANTE.
[P215] Credenciar, por escrito, junto à CONTRATADA, um representante do seu próprio quadro ou de terceiros, que atuará como Gestor do Contrato.
[P217] Quando aplicável, providenciar em tempo hábil as licenças e autorizações ambientais relativas ao LOCAL DE PRESTAÇÃO DOS SERVIÇOS que sejam de sua responsabilidade legal, cabendo à CONTRATADA obter as licenças, cadastros e autorizações específicas relacionadas ao seu método executivo, equipamentos e atividades próprias.
[P219] Disponibilizar área de apoio para uso da CONTRATADA.
[P221] Fornecer alimentação (Desjejum, almoço, lanches e jantar) aos Funcionários da CONTRATADA durante execução dos Serviços dentro das unidades de Germano e/ou Ponta de Ubu , respeitando as necessidades do regime de trabalho adotado, onde lanches e/ou jantar só serão fornecidos às equipes que trabalharem em regime de escala de revezamento ou após o horário administrativo, desde que sejam solicitados pela CONTRATANTE.
[P223] OBRIGAÇÕES DA CONTRATADA
[P225] São obrigações da CONTRATADA, sem prejuízo das demais previstas neste CONTRATO:
[P227] Quanto à força de trabalho:
[P229] Fornecer toda a direção, supervisão técnica e administrativa, e toda a força de trabalho necessária à execução dos Serviços, sendo para todos os efeitos, considerada como única e exclusiva empregadora.
[P231] utilizar pessoal qualificado e em número suficiente para execução dos Serviços, de modo a cumprir os prazos estabelecidos, bem como o padrão de qualidade técnica de segurança do trabalho e meio ambiente dos Serviços objeto do CONTRATO.
[P233] Providenciar e custear, quando da desmobilização envolvendo empregados de outras localidades, o retorno as suas origens imediatamente após o encerramento dos Serviços.
[P235] Quanto à assistência aos seus Funcionários:
[P237] Quando houver desligamento de Colaborador de outras localidades, providenciar seu imediato retorno ao respectivo local de origem.
[P239] Realizar o cadastro de seus empregados através de plataforma disponibilizada pela CONTRATANTE com informações atualizadas, bem como documentos comprobatórios, e em tempo hábil para as aprovações necessárias.
[P241] Quanto a custeio e encargos:
[P243] Custear, como única empregadora - e fazer com que seus subcontratados também o façam - as despesas decorrentes, direta ou indiretamente, dos Serviços, incluindo remuneração de fornecedores e pagamento de encargos trabalhistas e previdenciários, sem prejuízo do direito de reequilíbrio econômico-financeiro em caso de alteração superveniente de escopo ou obrigação legal imposta pela CONTRATANTE.
[P245] Disponibilizar, sempre que requisitado pela CONTRATANTE, toda documentação referente ao pagamento e cumprimento das obrigações relativas a tributos, seguros, encargos sociais, trabalhistas e previdenciários, e qualquer obrigação que se referir à execução dos Serviços objeto deste CONTRATO.
[P247] Apresentar, mensalmente, junto com o BM ou BMM e com a nota fiscal de faturamento, as guias relacionadas abaixo, do mês anterior, como condição para recebimento do valor faturado, admitida a apresentação em até 5 (cinco) DIAS úteis após a entrega da medição quando houver indisponibilidade sistêmica comprovada: Guias de recolhimento de INSS; Guias de recolhimento de FGTS; Guias de recolhimento de ISSQN.
[P249] Apresentar ao Gestor do Contrato, quando do início dos Serviços, os comprovantes de recolhimento das contribuições relativas ao seguro dos envolvidos nos Serviços contra risco e acidentes de trabalho, nos termos da lei vigente, bem como manter atualizados tais recolhimentos, comprovando-os regularmente ao Gestor do Contrato.
[P251] Quanto às relações nas unidades da CONTRATANTE:
[P253] Cumprir e fazer cumprir o Manual de Saúde e Segurança no Trabalho (anexo), bem como outras normas administrativas e disciplinares vigentes ou a serem implantadas no LOCAL DA PRESTAÇÃO DOS SERVIÇOS, pela CONTRATANTE, respondendo, por si e seus Funcionários.
[P255] Quando aplicável, e nos casos em que houver necessidade dos Funcionários da CONTRATADA adentrarem nas unidades da CONTRATANTE, o pessoal sob sua responsabilidade deverá obedecer às Normas de Coordenação de Campo, Manual de Saúde e Segurança do Trabalho, bem como as Diretrizes para Meio Ambiente e Comunidade da CONTRATANTE – (ANEXO), além de utilizar todo o Equipamento de Proteção Individual (EPI), sendo obrigatório uniforme, botas com biqueira, capacete (identificado com a logomarca da CONTRATADA) e óculos de segurança é obrigatório para todos os empregados.
[P257] Fixar seus horários de trabalho de modo compatível com os adotados pela CONTRATANTE, informando qualquer alteração necessária no horário dos Serviços ao Gestor do Contrato, com a antecedência necessária, de modo a permitir a manutenção dos controles necessários.
[P259] Não permitir que o seus Funcionários, máquinas, veículos e equipamentos a seu serviço ingressem em propriedade de terceiros, sem antes se certificar de que a CONTRATANTE já está devidamente autorizada para tal, respondendo civilmente e criminalmente por todo e qualquer dano que tal irregularidade venha a dar causa.
[P261] Não permitir que, fora dos horários de trabalho, seus Funcionários circulem pelas áreas da CONTRATANTE, devendo manter, para isto, vigilância constante, responsabilizando-se, exclusivamente, por quaisquer problemas que decorrerem do descumprimento dessa obrigação.
[P263] Providenciar a substituição ou retirada de qualquer Colaborador cuja permanência na área seja considerada, justificadamente, indesejável pela CONTRATANTE, no prazo de até 48 (quarenta e oito) horas, salvo em caso de risco à segurança, hipótese em que a retirada deverá ser imediata.
[P265] Providenciar os cadastros de todos os seus Funcionários que adentrarem nas unidades da CONTRATANTE, bem como assegurar que os mesmos realizem os treinamentos (principalmente os obrigatórios) cursos disponibilizados na Plataforma da CONTRATANTE, dentro da jornada de trabalho, como requisito primordial para a efetiva execução dos Serviços, sendo responsabilidade da CONTRATADA a disponibilização dos recursos necessários para o acesso dos empregados ao Sistema de Acessibilidade.
[P267] Responsabilizar-se pelos bens e pela segurança do LOCAL DE PRESTAÇÃO DOS SERVIÇOS, bem como pelo armazenamento adequado e seguro de seus materiais, considerando as recomendações da segurança empresarial da CONTRATANTE, que deve ser envolvida para análise dos riscos em fase de planejamento do canteiro, caso os Serviços sejam relacionados a obras.
[P269] Pedir autorização, prévia e por escrito, à segurança empresarial da CONTRATANTE para realizar, às suas expensas, a instalação de sistema de câmeras, alarmes e demais recursos de proteção física no LOCAL DE PRESTAÇÃO DOS SERVIÇOS.
[P271] Quando aplicável, envolver a área de segurança empresarial nas reuniões de planejamentos para alteração ou mudanças no ambiente dos ativos, tais como, porém, não se limitando a paradas de equipamentos e instalações (programadas ou não), canteiros de obras, incluindo equipamentos com estruturas móveis, subestações de energia e instalações críticas para o processo produtivo, a fim de que seja realizado Diagnóstico de Segurança Empresarial e a adoção de medidas e controles em tempo hábil.
[P273] Quanto a registros e legalizações:
[P275] Quando aplicável, promover o registro deste CONTRATO e seus Termos Aditivos perante os órgãos competentes, de acordo com a legislação em vigor, arcando com todas as despesas daí decorrentes, comprovando essa obrigação em 20 (vinte) dias úteis, contados da assinatura deste instrumento.
[P277] Manter, até o término do CONTRATO, o arquivo completo da documentação referente aos Serviços, com registros precisos e atualizados de todos os custos, despesas, transações financeiras e obrigações relacionadas com este CONTRATO. Tais registros ficarão à disposição da CONTRATANTE, ou de quem esta designar, durante o horário comercial, nos escritórios da CONTRATADA.
[P279] No caso de serviço de engenharia e arquitetura a CONTRATADA deverá apresentar à CONTRATANTE as Anotações de Responsabilidade Técnica (ART) relativas aos Serviços em cumprimento à Lei n° 6.496/77. Caso não seja necessária a emissão da ART, será obrigação da contratada apresentar declaração emitida pelo CREA, informando que não há necessidade de emissão de ART para o objeto desta contratação.
[P281] Quanto à saúde, segurança, meio ambiente e comunidade:
[P283] Designar como representante para os assuntos de saúde de segurança do trabalho (“SST)” empregado da CONTRATADA com poder decisório, o qual deverá comparecer às reuniões dos Comitês de Saúde, Segurança e Meio Ambiente, às Auditorias Programadas, às reuniões para apresentação da Investigação de Acidentes e outros eventos programados pela Gerenciadora de SST ou pela CONTRATANTE.
[P285] Comunicar imediatamente à CONTRATANTE qualquer deficiência, infração ou violação de obrigações, qualquer acidente de trabalho, ou incidente que exponha alguma pessoa a risco, ou qualquer outro assunto relevante, relacionadas à SST e que possa impactar as relações de trabalho ou a prestação dos serviços, compreendendo, sem se limitar, iminência de greves, paralisações, acidentes de trabalho, situações de risco, violações de direitos humanos, dentre outras, durante a execução do presente CONTRATO.
[P287] Após o envio de comunicação as PARTES deverão se reunir para avaliar uma solução conjunta para os problemas e evitar qualquer impacto à prestação dos Serviços.
[P289] Atingir os indicadores de desempenho em segurança, conforme definição e cálculo constante na Gestão de Incidentes do Manual do Sistema de Saúde e Segurança (ANEXO), dentre os quais se destaca o indicador de Fatalidade – ZERO.
[P291] Acatar as solicitações da(s) área(s) de SST da CONTRATANTE, o que incluir direito de solicitar à CONTRATADA todo e qualquer equipamento ou medidas de controle que julgar necessário à SST.
[P293] Em observância aos padrões de qualidade das refeições e alojamentos disponibilizados aos seus Funcionários, fornecê-los somente em estabelecimentos que possuam alvará sanitário expedido e válido, em conformidade com a Secretaria de Estado de Saúde e o Código de Vigilância Sanitária do Município, sendo que, dentro das instalações industriais das unidades da CONTRATANTE, é obrigatória aos empregado/subcontratados da CONTRATADA, a utilização dos restaurantes da CONTRATANTE durante a jornada de trabalho.
[P295] Somente mediante autorização da CONTRATANTE e cumprimento da legislação, em especial das normas citadas na previsão 11.6.5, poderá haver transporte de alimentos para fornecimento de refeição de Funcionários da CONTRATADA.
[P297] Cumprir todos os requisitos legais aplicáveis relacionados à SST, bem como as diretrizes da CONTRATANTE estipuladas através do Manual de SST em anexo.
[P299] Quanto aos Serviços como um todo:
[P301] Credenciar, por escrito, junto à CONTRATANTE, seu representante com poderes para tomar qualquer providência relativa ao CONTRATO.
[P303] Informar a CONTRATANTE a ocorrência de qualquer fato ou condição que possa atrasar ou impedir a conclusão, no todo ou em parte, dos Serviços, indicando as medidas tomadas ou a tomar para corrigir a situação.
[P305] Participar de forma efetiva e cooperativa dos processos de gestão integrada da CONTRATANTE.
[P307] Informar, quando solicitado, detalhadamente, os gastos incorridos nos Serviços e pagos pela CONTRATADA nos Estados de Minas Gerais e/ou Espírito Santo.
[P309] Caso aplicável, arcar com todos os custos e despesas decorrentes da instalação, conexão e operação do canteiro de obras e de suas atividades no LOCAL DA PRESTAÇÃO DOS SERVIÇOS, restaurando-o, o que inclui o canteiro de obras e as áreas cedida em comodato e jazidas, de acordo com as exigências emanadas pela CONTRATANTE e determinações dos órgãos ambientais.
[P311] Quando aplicável, implantar SLA’s (níveis de serviço), acordados entre as PARTES para este CONTRATO, de avaliação periódica e regular da qualidade dos produtos e serviços.
[P313] Quando da demissão de seus FUNCIONÁRIOS, que venham a cumprir aviso prévio trabalhado, não permitir que os mesmos tenham acesso a qualquer local relacionado à execução do CONTRATO, bem como a programas e sistemas internos da CONTRATANTE, salvo exceção prévia e formalmente aprovada pela CONTRATANTE.
[P315] Informar à CONTRATANTE acerca da ocorrência de qualquer fato, incidente, acidente ou condição relevante que possa impactar na segurança e/ou andamento dos Serviços.
[P317] Informar por escrito, para a CONTRATANTE, eventuais omissões, contradições ou dúvidas encontradas no CONTRATO, ANEXOS e/ou orientações da CONTRATANTE.
[P319] Realizar todos os treinamentos disponibilizados e/ou exigidos, a fim de cumprir com as diretrizes internas da CONTRATANTE, incluindo, porém não se limitando, àqueles referentes a Código de Conduta, Saúde e Segurança e Segurança da Informação.
[P321] RESPONSABILIDADES DA CONTRATADA
[P323] A CONTRATADA deverá isentar e defender a CONTRATANTE contra quaisquer vínculos, liames ou reivindicações de subcontratados ou de terceiros, com ela relacionados, com fundamento no objeto deste CONTRATO.
[P325] A CONTRATADA se obriga, ainda, a arcar com todas as despesas com indenizações/reclamações decorrentes de prejuízos, perdas e danos físicos, materiais e morais, montante que pode ser superior inclusive ao da garantia oferecida pela CONTRATADA, que venham a ser causados a pessoas/coisas, da CONTRATANTE ou de terceiros, em decorrência de sua ação ou omissão, desídia, direta ou indireta, própria ou de seus empregados, auxiliares, prepostos ou subcontratados, incluindo os relacionados com o uso de materiais ou processos que requeiram técnicas especiais (protegidos por marcas/patentes).
[P327] Se, em decorrência da execução dos Serviços contratados, ocorrerem incidentes com potencial de gravidade maior que 3 (três) ou acidentes causando danos físicos ou materiais a pessoas/bens de propriedade da CONTRATANTE ou de terceiros, envolvendo seus Funcionários deverá a CONTRATADA, além das providências específicas que o evento requeira, apurar as causas que o determinaram e apresentar o relato preliminar do incidente/acidente num prazo máximo de 24 (vinte e quatro) horas, bem como o relatório detalhado de investigação ao Gestor do Contrato num prazo máximo de 5 (cinco) DIAS, ambos os prazos contados a partir da data do evento.
[P329] A CONTRATADA será responsável por todas as ações ou omissões de seus Funcionários, correndo por sua conta exclusiva a reparação e o ressarcimento de tais prejuízos, pelo custo atualizado, e quaisquer danos pessoais ou materiais, perda, lesão, irregularidade ou defeito que sofram os serviços por qualquer motivo.
[P331] Serão admitidas como exceções aos itens anteriores apenas as ações/omissões decorrentes dos "Riscos Excluídos", caso em que a reparação será custeada pela CONTRATANTE. São considerados "Riscos Excluídos" ato/utilização indevidos ou inadequados de bens, obras, serviços e materiais pela CONTRATANTE ou por quaisquer de seus prepostos, ou por outras contratadas que não sejam subcontratadas da CONTRATADA, desde que tal ato/utilização tenha se dado, contra recomendação expressa da CONTRATADA;
[P333] Fica expressamente convencionado que, se porventura, a CONTRATANTE for condenada em razão do não pagamento em época própria de qualquer obrigação atribuível à CONTRATADA ou suas subcontratadas, seja de natureza fiscal, trabalhista, previdenciária, civil, ou de qualquer outra espécie, mesmo após o término do CONTRATO, assistir-lhe-á o direito de reter os pagamentos devidos até o limite do valor da condenação, até que a CONTRATADA ou suas subcontratadas evidenciem a garantia ou realização do pagamento, liberando a CONTRATANTE da condenação.
[P335] A CONTRATADA deverá se responsabilizar pelo estudo e avaliação das especificações técnicas e eventuais documentos fornecidos pela CONTRATANTE, bem como pela execução e qualidade dos serviços contratados, utilizando-se de pessoal qualificado, equipamentos e procedimentos técnico-administrativos adequados, cabendo-lhe alertar a CONTRATANTE sobre falhas técnicas eventualmente encontradas e ainda suspender qualquer atividade em execução que comprovadamente não esteja sendo executada de acordo com o que foi acertado ou que ponha em risco a segurança dos profissionais das PARTES ou de terceiros, independentemente de solicitação da CONTRATANTE.
[P337] A CONTRATADA deverá isentar e defender a CONTRATANTE contra quaisquer vínculos, liames ou reivindicações de subcontratados ou de terceiros com ela relacionados, com fundamento no objeto deste CONTRATO, desde que tais reivindicações não decorram de ato, omissão ou instrução direta da CONTRATANTE.
[P339] A CONTRATADA se obriga a arcar com despesas com indenizações/reclamações decorrentes de prejuízos, perdas e danos físicos, materiais e morais que venham a ser causados por sua ação ou omissão comprovada, direta ou indireta, própria ou de seus empregados, auxiliares, prepostos ou subcontratados, incluindo os relacionados com o uso de materiais ou processos que requeiram técnicas especiais.
[P341] Eventuais limitações de responsabilidade contidas nesse CONTRATO não se aplicam a coberturas securitárias e/ou eventual direito de regresso da(s) seguradora(s) das PARTES.
[P344] A CONTRATADA deverá providenciar para que não haja qualquer parada ou atraso na execução dos Serviços e, se por qualquer motivo, ocorrer a indisponibilidade de qualquer Serviço ou recurso, se compromete a buscar meios necessários ao seu restabelecimento, sem qualquer ônus adicional a CONTRATANTE.
[P346] Caberá exclusivamente à CONTRATADA a reparação de eventuais danos ou prejuízos causados ao meio ambiente por seus Funcionários ou prepostos durante a execução dos Serviços, bem como o pagamento de todas e quaisquer indenizações decorrentes e despesas oriundas de tais danos.
[P348] A CONTRATADA é a única responsável pelas obrigações decorrentes dos contratos de trabalho de seus Funcionários ou de prestação de serviços de seus subcontratados, inclusive por eventuais inadimplementos de obrigações trabalhistas ou previdenciárias, não podendo ser arguida solidariedade da CONTRATANTE por tais obrigações nem responsabilidade subsidiária, uma vez que a presente contratação não implica vinculação empregatícia entre seus empregados e/ou subcontratados e a CONTRATANTE;
[P349] Eventuais limitações de responsabilidade contidas neste CONTRATO não se aplicam a dolo, fraude, violação de confidencialidade, infrações anticorrupção, danos ambientais, danos à vida ou à integridade física, coberturas securitárias e/ou eventual direito de regresso da(s) seguradora(s) das PARTES.
[P350] FISCALIZAÇÃO E GESTÃO DO CONTRATO
[P351] A CONTRATADA deverá providenciar para que não haja qualquer parada ou atraso injustificado na execução dos Serviços e, se ocorrer a indisponibilidade de qualquer Serviço ou recurso por motivo sob sua responsabilidade, compromete-se a buscar os meios necessários ao seu restabelecimento, sem ônus adicional à CONTRATANTE.
[P352] A CONTRATANTE exercerá a fiscalização sobre a execução do CONTRATO através de uma equipe, denominada Fiscalização, integrada por pessoal pertencente ao seu quadro ou de terceiros, liderada pelo Gestor do Contrato e composta por fiscais do CONTRATO, sendo estes nominalmente definidos pela CONTRATANTE por meio de envio comunicação escrita para a CONTRATADA para quaisquer dos endereços físico ou eletrônico indicados no QUADRO RESUMO.
[P354] A CONTRATANTE acompanhará a execução do CONTRATO através de uma equipe integrada por pessoal pertencente ao seu quadro ou de terceiros, liderada pelo Gestor do Contrato.
[P356] Havendo alteração dos gestores, as PARTES deverão comunicar a outra PARTE por escrito, sob pena de serem consideradas válidas todas as comunicações aos gestores inicialmente indicados.
[P358] O Gestor do Contrato estará à disposição da CONTRATADA para fornecer as informações e documentação técnica que forem necessárias para o desenvolvimento dos Serviços.
[P359] A CONTRATANTE exercerá a fiscalização sobre a execução do CONTRATO através de uma equipe, denominada Fiscalização, integrada por pessoal pertencente ao seu quadro ou de terceiros. A indicação ou substituição de fiscais produzirá efeitos perante a CONTRATADA a partir da comunicação escrita para qualquer dos endereços físico ou eletrônico indicados no QUADRO RESUMO.
[P360] O Gestor do Contrato terá acesso a todos os locais onde os Serviços se realizarem e plenos poderes para praticar atos, nos limites do presente CONTRATO, que se destinem a acautelar e preservar todo e qualquer direito da CONTRATANTE.
[P362] As atribuições do Gestor do Contrato incluem:
[P364] Verificar o cumprimento das obrigações da CONTRATADA, sendo-lhe lícito recusar Serviços que tenham sido executados em desacordo com as condições estabelecidas neste CONTRATO ou com as informações ou especificações fornecidas pela CONTRATANTE, determinando as correções ou retificações adequadas, a ônus da CONTRATADA.
[P366] Aprovar as medições da CONTRATADA.
[P368] Autorizar, se for o caso, previamente, a realização de despesas a serem reembolsadas à CONTRATADA.
[P370] Quando as condições de execução impuserem a necessidade da modificação em desenhos ou documentos de propriedade da CONTRATANTE, a CONTRATADA o fará mediante solicitação e aprovação do Gestor do Contrato.
[P372] Sustar o pagamento de quaisquer notas fiscais/faturas da CONTRATADA, no caso de inobservância de disposição contida neste CONTRATO, até a regularização da situação. Tal procedimento será comunicado por escrito à CONTRATADA, sem perda do direito de aplicação das demais sanções previstas neste CONTRATO.
[P374] Solicitar, quando entenda necessário, ações referentes aos Funcionários da CONTRATADA, ou de seus subcontratados, quando do descumprimento de algum requisito estipulado no CONTRATO.
[P376] Mandar executar, por terceiros, debitando as despesas respectivas da CONTRATADA, as providências necessárias para suprir ou corrigir deficiências da CONTRATADA por ela não sanadas no prazo estipulado pelo Gestor do Contrato.
[P378] Convocar e dirigir reuniões periódicas ou ocasionais com a CONTRATADA, para programação e coordenação geral/específica dos serviços.
[P380] Comunicar à CONTRATADA, por escrito e com a devida antecedência, qualquer instrução ou procedimento a adotar sobre assunto relacionado com este CONTRATO, inclusive aplicação de multas.
[P382] No caso de inobservância, pela CONTRATADA, das exigências do Gestor do Contrato, amparadas neste CONTRATO, terá a CONTRATANTE, além do direito de aplicação das sanções previstas no CONTRATO, também o de suspender a execução dos Serviços e de sustar o pagamento de quaisquer notas fiscais/faturas da CONTRATADA até a regularização da situação, do que dará ciência, por escrito, à CONTRATADA.
[P384] As funções inerentes ao Gestor do Contrato não eximem, em nenhuma hipótese, a exclusiva responsabilidade técnica da CONTRATADA durante a execução dos Serviços.
[P386] A ação/omissão, total ou parcial, do Gestor do Contrato, não exime a CONTRATADA da total responsabilidade pelo fiel cumprimento de suas obrigações contratuais.
[P388] Sem prejuízo do cumprimento das demais obrigações previstas neste CONTRATO, as PARTES se obrigam a:
[P390] Nomear o Gestor do Contrato, por escrito, com experiência comprovada em atividades inerentes ao objeto para receber demandas, resolver problemas e representá-las, com plenos poderes para tomar as providências que se fizerem necessárias para o bom cumprimento do CONTRATO.
[P392] Substituir o Gestor do Contrato no caso de falta, ausência ou impedimento eventual ou ocasional, por outro com iguais poderes; e
[P394] Havendo alteração dos Gestor do Contrato pelas PARTES, comunicar previamente a alteração à outra PARTE por escrito, sob pena de serem consideradas válidas todas as comunicações dirigidas aos representantes inicialmente indicados.
[P396] CESSÃO E SUBCONTRATAÇÃO
[P397] A CONTRATADA não poderá transferir a terceiros nem subcontratar, no todo ou em parte, os Serviços e/ou as obrigações deste CONTRATO, sem prévia identificação do cessionário/subcontratado perante a CONTRATANTE. A ausência de manifestação da CONTRATANTE no prazo de 10 (dez) DIAS úteis, contado do recebimento das informações completas, será interpretada como não objeção à subcontratação indicada.
[P398] A CONTRATADA não poderá transferir a terceiros nem subcontratar, no todo ou em parte, os Serviços e/ou as obrigações deste CONTRATO, sem a prévia identificação do cessionário/subcontratado perante a CONTRATANTE e sem a prévia e expressa concordância desta, por escrito, na pessoa do Gestor do Contrato.
[P400] A existência de cessionárias ou subcontratadas, autorizadas, ou não, pela CONTRATANTE, não eximirá a CONTRATADA de sua exclusiva responsabilidade pelo cumprimento do CONTRATO.
[P401] A subcontratação do OBJETO pela CONTRATADA, ou de parte dele, sem a prévia autorização ou sem a não objeção da CONTRATANTE será considerada inadimplemento contratual e permitirá à CONTRATANTE, a seu exclusivo critério: (i) solicitar a imediata paralisação do objeto; (ii) exigir a desmobilização imediata da(s) subcontratada(s); (iii) exigir a substituição da(s) subcontratada(s), sem prejuízo das penalidades cabíveis.
[P402] A subcontratação do OBJETO pela CONTRATADA, ou de parte dele, sem a prévia autorização expressa da CONTRATANTE será considerada inadimplemento contratual e permitirá à CONTRATADA, a seu exclusivo critério: (i) solicitar a imediata paralisação do objeto (ii) exigir a desmobilização imediata da(s) subcontratada(s); (iii) exigir a substituição da(s) subcontratada(s), sem prejuízo das penalidades cabíveis.
[P404] Fica vedado aos subcontratados realizarem novas subcontratações.
[P406] SEGUROS
[P408] A CONTRATADA e suas subcontratadas se obrigam a instituir, por sua conta exclusiva, com empresa seguradora de idoneidade reconhecida, além dos seguros que julgar convenientes, os seguros previstos na legislação em vigor, inclusive seguro de responsabilidade civil geral, seguros de veículos, de vida e de acidentes para o seus Funcionários, utilizados/alocados na execução do CONTRATO.
[P410] As apólices contratadas pela CONTRATADA deverão permanecer suficientes para a cobertura dos riscos assumidos neste CONTRATO durante toda a vigência contratual.
[P412] As responsabilidades da CONTRATADA são integrais, não se limitando ao valor do seguro contratado. Independentemente do valor segurado, a CONTRATADA responde por perdas, danos, inclusive franquias e ações de ressarcimento por parte das seguradoras contratadas pela CONTRATANTE quando houver a responsabilidade pelos prejuízos causados e indenizados diretamente à CONTRATANTE.
[P414] As PARTES, através da assinatura deste instrumento, autorizam, desde já, o compartilhamento das disposições deste CONTRATO com seguradoras ou corretoras de seguro exclusivamente para fins de contratação ou renovação destes, sem que seja caracterizado descumprimento dos deveres de confidencialidades previstos.
[P416] Na ocorrência de sinistro, as PARTES deverão, no prazo de 05 (cinco) dias úteis, fornecer as informações solicitadas pela outra PARTE, bem como apoiá-la em eventuais discussões relacionadas ao sinistro, sob pena de responsabilização pelas consequências advindas de sua eventual omissão.
[P418] A CONTRATADA deverá, sempre que solicitado, em até 10 (dez) DIAS corridos, apresentar a cópia da(s) apólice(s) correspondente(s) e/ou comprovante de pagamento destas, a pedido da CONTRATANTE.
[P419] As PARTES não poderão prestar informações a terceiros nem divulgar quaisquer dados, informações relacionadas ao CONTRATO, ou o CONTRATO em si, ANEXOS e eventuais aditivos, sem autorização prévia e por escrito da outra PARTE, exceto a seus consultores, auditores, seguradoras, financiadores e assessores profissionais, desde que sujeitos a deveres de confidencialidade compatíveis.
[P420] CONFIDENCIALIDADE
[P422] As PARTES não poderão prestar informações a terceiros nem divulgar quaisquer dados, informações relacionadas ao CONTRATO, ou o CONTRATO em si, ANEXOS e eventuais aditivos, sem autorização prévia e por escrito da outra PARTE, obrigação que abarca até mesmo a fase de concorrência da contratação.
[P423] As estipulações e obrigações constantes da presente cláusula não serão aplicadas a qualquer informação que: (i) seja de domínio público; (ii) já esteja em poder da CONTRATADA como resultado de sua própria pesquisa ou desenvolvimento; (iii) tenha sido legitimamente recebida de terceiros sem violação de dever de confidencialidade; ou (iv) deva ser divulgada por ordem legal, regulatória, judicial ou arbitral, hipótese em que a outra PARTE deverá ser previamente comunicada, quando permitido.
[P424] O acesso às informações confidenciais será restrito aos Funcionários das PARTES que tiverem comprovada necessidade de conhecê-la, apenas na extensão necessária, e deverão assinar o modelo contido no anexo denominado “Termo de Confidencialidade”, que deve ser entregue aos cuidados do Gestor do Contrato da CONTRATANTE.
[P426] As estipulações e obrigações constantes da presente cláusula não serão aplicadas a qualquer informação que: (i) seja de domínio público; (ii) já esteja em poder da CONTRATADA como resultado de sua própria pesquisa ou desenvolvimento; (iii) tenha sido legitimamente recebida pela CONTRATADA de terceiros, sem que tenha havido violação de qualquer dever de confidencialidade; (iv) seja revelada em razão de uma ordem válida, administrativa ou judicial, somente até a extensão de tais ordens, contanto que a CONTRATADA tenha notificado a existência de tal ordem, previamente e por escrito, à CONTRATANTE, dando a esta, na medida do possível, tempo hábil para pleitear medidas de proteção que julgar cabíveis.
[P428] A CONTRATADA declara antes do término deste CONTRATO, por qualquer razão, deverá ser devolvida à CONTRATANTE toda e qualquer documentação, arquivada em qualquer meio, relativa ao CONTRATO, no prazo máximo de 15 (quinze) DIAS.
[P430] Em caso de impossibilidade de devolução da documentação tendo em vista o meio em que foi transmitida, incluindo, porém não se limitando a e-mails e/ou chats, a CONTRATADA declara que realizará a destruição completa dos arquivos confidenciais em sua posse, sob pena de ser caracterizado descumprimento contratual, desde que seja autorizada pela CONTRATANTE antecipadamente.
[P432] A CONTRATADA reconhece e aceita que o uso para fim diverso da execução dos Serviços, a exemplo da exploração comercial, a cópia, a produção de back-up, a divulgação, reprodução ou distribuição, total ou parcial, das informações confidenciais, configura violação da obrigação prevista desta cláusula.
[P434] As obrigações acima mencionadas permanecerão em pleno e absoluto vigor desde a data de envio pela CONTRATANTE da Solicitação de Proposta estendendo-se por 5 (cinco) anos após o término do CONTRATO
[P436] A violação, pela CONTRATADA, do dever de confidencialidade previsto nesta cláusula importará na aplicação de multa não compensatória de 20% (vinte por cento) do VALOR ESTIMADO DO CONTRATO.
[P438] CASO FORTUITO E FORÇA MAIOR
[P440] Conforme previsto no artigo 393 do Código Civil Brasileiro, nenhuma PARTE será responsabilizada por falhas no cumprimento de suas respectivas obrigações quando o cumprimento de tais obrigações tenha sido impedido ou atrasado em virtude da ocorrência de eventos comprovadamente caracterizados como caso fortuito ou força maior.
[P442] Ante a ocorrência de qualquer circunstância que puder ser invocada como caso fortuito ou força maior, a PARTE afetada enviará à outra, no prazo de até 24 horas, após ter tomado conhecimento, uma notificação, por escrito, por meio da qual comunicará a ocorrência do fato, as medidas que estiverem sendo tomadas e a previsão para regularização da situação.
[P443] Salvo se expressamente previsto em sentido diverso no QUADRO RESUMO ou em instrumento específico, a titularidade das criações intelectuais, documentos, relatórios, desenhos, bases de dados, métodos, melhorias e demais resultados desenvolvidos especificamente no âmbito dos Serviços pertencerá à CONTRATANTE, assegurada à CONTRATADA licença interna, não exclusiva e sem direito de sublicenciamento para fins de arquivo, defesa técnica e comprovação de experiência.
[P444] A PARTE afetada pelo evento de força maior ou caso fortuito deverá tomar e demonstrar que tomou todas as medidas a seu alcance para cessar ou minimizar os efeitos dele decorrentes e impeditivos do cumprimento de suas obrigações.
[P446] Cessado o caso fortuito ou o motivo de força maior, a PARTE que o tiver invocado notificará a outra, por escrito, no prazo máximo de 05 (cinco) DIAS, a contar da referida cessação, informando-a acerca da regularização da situação.
[P448] Se o fato invocado como caso fortuito ou força maior impossibilitar o cumprimento integral deste CONTRATO e perdurar por prazo maior do que aquele previsto no QUADRO RESUMO, qualquer das PARTES poderá optar pela resolução deste instrumento, na forma prevista no CONTRATO.
[P450] Em nenhuma hipótese será considerado como evento de caso fortuito ou força maior a ocorrência de:
[P451] Os direitos de propriedade intelectual pré-existentes de cada PARTE permanecerão de sua respectiva titularidade. O simples uso de ferramentas, metodologias, templates, know-how, softwares ou materiais previamente desenvolvidos pela CONTRATADA não transferirá tais direitos à CONTRATANTE, salvo previsão expressa em contrário.
[P452] Greve e/ou interrupções trabalhistas, ou medidas tendo efeito semelhante, de Funcionários de uma das PARTES e/ou de suas contratadas e/ou subcontratadas;
[P454] Qualquer ação de qualquer autoridade pública que uma parte pudesse ter evitado se tivesse cumprido suas obrigações legais ou contratuais;
[P456] Decretação de falência de qualquer das PARTES;
[P458] Dificuldades econômicas ou financeiras de qualquer das PARTES;
[P460] Os dias de chuvas não superiores às médias históricas e suas consequências.
[P462] As PARTES acordam, desde já, que os prazos previstos neste CONTRATO poderão ser proporcionalmente prorrogados pelo mesmo número de dias relativos à eventual suspensão dos Serviços em razão da ocorrência de eventos caracterizados como caso fortuito ou força maior, a exclusivo critério da CONTRATANTE, mediante notificação nesse sentido.
[P464] MULTAS E PENALIDADES
[P466] Caso a CONTRATADA descumpra norma e/ou obrigação contratual considerada sanável pela CONTRATANTE, a CONTRATANTE poderá, a seu exclusivo critério, notificar a CONTRATADA para que esta sane a obrigação no prazo estipulado pela CONTRATANTE.
[P468] Se a CONTRATADA se manter inerte em relação à notificação, recuse-se a corrigir as inconformidades, insista em deslizes da mesma natureza ou apresente soluções incompatíveis com a situação, o Gestor do Contrato poderá aplicar penalidades.
[P470] Se o referido descumprimento de norma e/ou obrigação pela CONTRATADA for considerado insanável pela CONTRATANTE, esta poderá aplicar penalidades independente de prazo, apenas mediante envio de notificação para a CONTRATADA.
[P471] A CONTRATADA não poderá usar o nome, marcas, logotipos ou sinais distintivos da CONTRATANTE em materiais publicitários, portfólios, propostas comerciais, redes sociais ou comunicações públicas sem autorização prévia e por escrito da CONTRATANTE.
[P472] O valor de referência para cálculo das penalidades estabelecidas no CONTRATO será o VALOR ESTIMADO DO CONTRATO previsto no QUADRO RESUMO, conforme os parâmetros abaixo:
[P475] As penalidades previstas no CONTRATO e nos ANEXOS, caso aplicável, não possuem natureza compensatória, isto é, podem cumuladas com as perdas e danos relacionadas.
[P477] As multas serão descontadas do pagamento da primeira nota fiscal/fatura apresentada pela CONTRATADA após a sua aplicação e, não sendo estes suficientes, serão descontados dos montantes das notas fiscais/faturas sucessivas, podendo a CONTRATANTE, ainda, valer-se de qualquer outro meio juridicamente admitido para haver o valor devido.
[P479] A cobrança das multas previstas nesta cláusula ocorrerá cumulativamente, na medida em que cada obrigação deixar de ser cumprida, até o limite de 10% (dez por cento) do valor total estimado do CONTRATO. Caso este percentual seja atingido, será permitido à CONTRATANTE rescindir o CONTRATO
[P481] As multas acima previstas não reduzirão ou eliminarão outras penalidades, obrigações e responsabilidades da CONTRATADA previstas neste CONTRATO.
[P483] PROPRIEDADE INTELECTUAL
[P485] Todo objeto de propriedade intelectual obtido através das atividades relacionadas ao presente CONTRATO, que vierem a ocorrer durante a o PERÍODO DE VIGÊNCIA ou no prazo de um ano após a extinção do CONTRATO, decorrente da especificidade da atividade contratada, pertencerão exclusivamente à CONTRATANTE.
[P487] Quando a invenção ou melhoria resultar de contribuição específica da CONTRATADA, mas, que para tanto, forem utilizados recursos, dados, meios, materiais, instalações ou equipamentos da CONTRATANTE, a propriedade dessa invenção ou melhoria pertencerá exclusivamente à CONTRATANTE.
[P489] A CONTRATADA se obriga a transferir à CONTRATANTE a propriedade integral, livre de quaisquer ônus, responsabilidades e restrições legais por propriedade intelectual de todos os desenhos, projetos, equipamentos, materiais, PARTES e componentes, acessórios e pertenças, ferramentas e quaisquer outros bens empregados e produzidos no âmbito dos SERVIÇOS.
[P491] Todos os documentos, incluindo, mas não se limitando a relatórios, gráficos, planilhas, gerados pela CONTRATANTE em razão deste CONTRATO poderão ser utilizados livremente pela CONTRATANTE, que poderá repassá-los para terceiros que agem em seu interesse, como os seus fornecedores, independente de anuência prévia da CONTRATADA e sem quaisquer limitações e ônus/valores adicionais sejam devidos pela CONTRATANTE.
[P493] A CONTRATADA é responsável pelo pagamento de qualquer taxa ou royalty eventualmente exigível pelo uso de patentes, métodos, processos, materiais e equipamentos empregados na prestação dos Serviços.
[P495] A CONTRATADA é a única e exclusiva responsável por si e por seus Funcionários, pelo uso, nos Serviços de materiais e equipamentos, incluindo hardware e software, regularmente adquiridos e/ou licenciados e deve dispor de todos os documentos comprobatórios da aquisição e/ou licenciamento dos mesmos. A CONTRATADA responderá, isolada e exclusivamente, perante quaisquer terceiros, por qualquer irregularidade verificada.
[P497] PRIORIZAÇÃO DE RECURSOS REGIONAIS
[P499] A CONTRATANTE incentiva e promove o desenvolvimento das regiões onde possui instalações e, portanto, deverá ser priorizada pelas PARTES a contratação de pessoal e aquisição de serviços/materiais da região onde os Serviços serão prestados, sejam eles oriundos dos programas de qualificação, do pessoal já qualificado da região, de apoio, ou força de trabalho não especializada.
[P501] Caso os Serviços sejam prestados no município de Anchieta/ES, a CONTRATADA se obriga a cumprir o disposto na legislação municipal vigente (Lei 1.297/18 e/ou legislações que a sucederem), de forma a manter o percentual mínimo exigido pela legislação para a contratação de empregados locais.
[P503] COMPLIANCE
[P505] A CONTRATADA, ao aceitar este instrumento, confirma a ciência e se compromete ainda, no desempenho de qualquer ação ou negócio que envolva interesses da CONTRATANTE, a cumprir o Código de Conduta de Fornecedores disponibilizado no site www.samarco.com.
[P507] A CONTRATADA se obriga a apurar, com diligência, qualidade, efetividade e dentro do prazo solicitado, todas as denúncias encaminhadas pela SAMARCO que digam respeito exclusivamente à sua conduta, de seus empregados e representantes, devendo, caso constatada procedência, apresentar à SAMARCO plano de ação específico com medidas corretivas e mitigadoras, contendo prazos definidos para sua execução e comprovação de sua efetividade.
[P509] A apuração será conduzida de forma sigilosa e confidencial, sendo vedado à CONTRATADA compartilhar quaisquer informações relacionadas à denúncia – incluindo, mas não se limitando à identidade dos envolvidos – com qualquer pessoa que não integre sua área de Compliance, a qual deverá assegurar o tratamento restrito das informações recebidas.
[P511] É expressamente vedada qualquer forma de retaliação por parte da CONTRATADA a qualquer pessoa envolvida, direta ou indiretamente, na denúncia, sob pena de aplicação das sanções previstas neste instrumento.
[P513] A CONTRATADA autoriza expressamente a SAMARCO a requisitar documentos, informações, evidências e quaisquer registros necessários para o acompanhamento da apuração, comprometendo-se a fornecer os dados solicitados de forma tempestiva, adequada e com a devida classificação da informação como confidencial.
[P515] O descumprimento, por parte da CONTRATADA, das obrigações previstas nesta cláusula, inclusive, mas não se limitando, à prática de atos ilícitos, antiéticos, retaliatórios ou de omissão injustificada de resposta, ensejará a aplicação de sanções contratuais, sem prejuízo das demais medidas legais cabíveis, inclusive a rescisão contratual por justa causa e indenizações por perdas e danos.
[P517] A CONTRATADA declara e garante que seus Funcionários que atuam nos negócios relacionados ao CONTRATO que envolvam direta ou indiretamente a SAMARCO, não violaram e não violarão a legislação anticorrupção na execução deste CONTRATO.
[P519] A CONTRATADA deverá comunicar a CONTRATANTE imediatamente, através de envio de e-mail ao Gestor do Contrato, e em nenhuma hipótese em mais de 5 (cinco) DIAS úteis após tomar conhecimento, dos seguintes eventos:
[P521] Qualquer violação real ou iminente da legislação anticorrupção aplicável.
[P523] Existência ou possibilidade, seja no Brasil ou no exterior, de qualquer investigação, processo administrativo ou judicial que esteja relacionado, direta ou indiretamente, às atividades da CONTRATADA (ou de qualquer um de seus Funcionários envolvidos nas atividades deste CONTRATO) que apure ou que inclua quaisquer alegações de fraude, corrupção, lavagem de dinheiro ou violações da legislação anticorrupção aplicável.
[P525] Caso, na execução do objeto deste CONTRATO, os funcionários ou representantes da CONTRATADA interajam ou tenham a expectativa de interação com Agente Público ou com a administração pública em nome da CONTRATANTE, suas empresas controladas e coligadas, estes deverão obrigatoriamente e previamente à execução dos serviços, realizar o treinamento disponibilizado para tal fim na plataforma da CONTRATANTE.
[P527] PRESTAÇÃO DE INFORMAÇÕES
[P529] A CONTRATADA concorda em documentar de forma precisa e detalhada em seus livros e registros, bem como nos documentos fornecidos à CONTRATANTE, todas as transações relacionadas, direta ou indiretamente, ao presente CONTRATO. Tais registros deverão ser mantidos de maneira organizada pela CONTRATADA durante a vigência do CONTRATO, e por um período adicional de 5 (cinco) anos após sua extinção, independente do motivo.
[P531] Durante o prazo do presente CONTRATO e por 5 (cinco) anos após o seu término, mediante comunicado por escrito com 10 (dez) DIAS de antecedência, a CONTRATADA concorda em permitir que a CONTRATANTE, ou terceiros por ela autorizados, tenham acesso a livros, registros, documentos e informações diretamente relacionados ao objeto do CONTRATO, podendo obter cópias, a fim de verificar a conformidade da CONTRATADA com este CONTRATO. A auditoria deverá ocorrer em horário comercial e de modo a não interferir desarrazoadamente nas atividades normais da CONTRATADA.
[P533] As análises e acesso aos documentos previstos nesta Cláusula estão sujeitas aos deveres de Confidencialidade previsto no CONTRATO.
[P535] Durante o prazo do presente CONTRATO e por 5 (cinco) anos após o seu término, mediante comunicado por escrito com 15 (quinze) DIAS de antecedência, a CONTRATADA concorda em tomar todas as medidas necessárias para permitir que a CONTRATANTE tenha acesso a informações, documentos relacionados ao CONTRATO.
[P537] Qualquer violação das disposições desta cláusula durante o PRAZO DE VIGÊNCIA pela CONTRATADA autorizará a CONTRATANTE, a seu exclusivo critério, a rescindir o presente instrumento imediatamente mediante notificação por escrito e sem qualquer obrigação da CONTRATANTE de pagar indenização ou danos à CONTRATADA. A CONTRATADA deverá, ainda, indenizar e isentar a CONTRATANTE de quaisquer prejuízos ou danos incorridos pela CONTRATANTE como resultado da violação dos termos desta cláusula durante ou após o PRAZO DE VIGÊNCIA.
[P539] PRIVACIDADE E PROTEÇÃO DE DADOS
[P541] As PARTES, ao tratarem dados pessoais no contexto de execução do CONTRATO, ainda que de maneira pontual, observarão o disposto nas leis de proteção de dados aplicáveis, incluindo, sem limitação, a Lei nº 13.709, de 14 de agosto de 2018 (“LGPD”), em especial lastrearão tratamentos de dados em base legal e em observância aos princípios da LGPD. Fica também ajustado entre as PARTES que tratarão tais dados pessoais na medida do necessário para atingir a finalidade para qual eles foram fornecidos, para cumprimento das obrigações e prerrogativas previstas no CONTRATO e eventuais obrigações legais ou regulatórias, e em conformidade com as Políticas de Proteção de Dados e demais orientações da CONTRATANTE, obrigando-se a estender tais obrigações e conscientizar todos aqueles que engajar na cadeia de tratamento.
[P543] A CONTRATADA declara que, na execução deste CONTRATO, caso ocorra o tratamento de dados pessoais, cumprirá fielmente as diretrizes do Anexo XV – Termo LGPD, e concorda que será responsável perante a CONTRATANTE por violações à legislação de proteção de dados e privacidade aplicável que sejam comprovadamente cometidas por seus Funcionários com relação a atividades direta ou indiretamente relacionadas à CONTRATANTE.
[P545] Caso a CONTRATANTE venha a ser responsabilizada, judicial ou extrajudicialmente, por danos causados pela CONTRATADA, esta se obriga a assumir a responsabilidade processual, assumindo o polo passivo da ação própria, se for o caso, e a ressarcir integralmente todos os custos e danos arcados pela CONTRATANTE, inclusive honorários advocatícios contratuais e sucumbenciais, além de qualquer quantia que seja obrigada a pagar em decorrência dos referidos danos, autorizando, desde logo, que a desconte da remuneração ora ajustada.
[P547] ENCERRAMENTO DO CONTRATO
[P549] O presente CONTRATO será extinto na (i) DATA DE TÉRMINO, (ii) após a consecução do seu objeto ou (iii) no caso de atingido o valor estabelecido neste instrumento, o que ocorrer primeiro, a critério exclusivo da CONTRATANTE, salvo se houver prorrogação destas condições, formalizado por termo aditivo.
[P551] Qualquer das PARTES poderá rescindir o presente CONTRATO, mediante simples aviso escrito à outra PARTE, sem necessidade de procedimento judicial ou extrajudicial, nos seguintes casos:
[P553] Ocorrendo caso fortuito ou de força maior, cujos efeitos persistirem por prazo maior do que o descrito no QUADRO RESUMO;
[P555] Uma das PARTES tiver sua falência decretada.
[P557] Imotivadamente, mediante aviso prévio escrito, com antecedência de 60 (sessenta) dias, sem acarretar quaisquer penalidades, compensação ou lucros cessantes, ressalvado o pagamento dos Serviços efetivamente prestados e dos custos de desmobilização previamente aprovados.
[P559] A rescisão operar-se-á de pleno direito na data de decretação da falência e, no caso da cláusula 23.2.1, no termo final do prazo indicado no QUADRO RESUMO.
[P561] O CONTRATO poderá ser resilido por qualquer uma das PARTES, a qualquer momento, mediante comunicação por escrito enviada com antecedência indicada no QUADRO-RESUMO, sem que sejam devidas penalidades, multas ou indenizações de uma PARTE a outra, operando-se a resilição, de pleno direito após decorrido tal prazo.
[P563] Adicionalmente, a CONTRATANTE poderá rescindir o CONTRATO de pleno direito, mediante simples aviso escrito à CONTRATADA, sem necessidade de procedimento judicial ou extrajudicial, e sem que caiba à CONTRATADA qualquer direito de indenização ou ressarcimento, se a CONTRATADA:
[P565] Descumprir quaisquer obrigações materiais do CONTRATO não sanadas no prazo mencionado na cláusula de penalidades ou descumprir obrigação insanável, como normas de anticorrupção/compliance, confidencialidade, proteção de dados, saúde e segurança ou meio ambiente.
[P567] Der causa à suspensão dos Serviços por determinação das autoridades competentes ou pela falta de cumprimento de prescrições técnicas, administrativas ou legais na sua execução;
[P569] Promover, supervenientemente, ações judiciais contra a CONTRATANTE, suas controladas, controladoras e empresas a ela coligadas, considerando não somente ações movidas pela CONTRATADA, mas também aquelas manejadas por seus acionistas, quotistas ou empresas que façam parte do mesmo grupo econômico;
[P571] Reincidir no descumprimento de normas referentes à SST;
[P573] Demonstrar incapacidade técnica, imperícia, imprudência ou negligência da CONTRATADA ou qualquer de seus subcontratados;
[P575] Praticar ato intencional, de natureza grave, assim entendido conforme critério exclusivo da CONTRATANTE, contrário às disposições deste CONTRATO.
[P577] Sofrer condenação em processos administrativos ou judiciais com relação às Legislação Anticorrupção;
[P579] Ficar impedida de executar o CONTRATO em razão de alteração na legislação vigente.
[P581] Nas hipóteses previstas na cláusula anterior, (i) a rescisão operar-se-á de pleno direito na data de envio da notificação pela CONTRATANTE à CONTRATADA e (ii) fica facultado à CONTRATANTE promover a rescisão do CONTRATO, ou, a seu exclusivo critério, mantê-lo e/ou promover a execução específica das obrigações inadimplidas, sem prejuízo de aplicar as penalidades previstas no CONTRATO e de ser ressarcida pelas perdas e danos sofridos; (iii) não convindo à CONTRATANTE a rescisão do CONTRATO, poderá a CONTRATANTE intervir no CONTRATO, de maneira que melhor satisfaça a seus interesses, correndo, por conta da CONTRATADA, os ônus decorrentes da intervenção.
[P583] Na hipótese de rescisão deste CONTRATO por culpa de uma das PARTES, a PARTE que der causa ao encerramento pagará à PARTE inocente a importância equivalente a 10% (dez por cento) do saldo do VALOR ESTIMADO DO CONTRATO apurado no momento do encerramento, a título de multa rescisória. Caso a rescisão se dê por culpa da CONTRATANTE, esta pagará, ainda, os valores proporcionais às atividades da CONTRATADA, total ou parcialmente executadas até então. Caso a rescisão se dê por culpa da CONTRATADA, esta pagará, ainda, os valores de perdas e danos suplementares que forem apurados.
[P585] Antes da extinção do CONTRATO, a CONTRATADA deverá tomar todas as providências necessárias para transmitir à CONTRATANTE todos os direitos, garantias, compensações, benefícios, titularidades, posse e participação da CONTRATADA relacionada aos Serviços até a data de extinção do CONTRATO.
[P587] Uma vez distratado ou rescindido este CONTRATO, poderá a CONTRATANTE entregar a conclusão dos Serviços a qualquer outra executante, independentemente da anuência da CONTRATADA.
[P589] Ocorrendo uma ou mais das hipóteses de rescisão desta cláusula, e não convindo à CONTRATANTE a rescisão do CONTRATO, poderá ela intervir nos Serviços contratados, de maneira que melhor satisfaça a seus interesses, correndo, por conta da CONTRATADA, os ônus decorrentes da intervenção.
[P591] Quando aplicável, após o término dos Serviços, providenciar a retirada, às suas custas, das máquinas, equipamentos, veículos, utensílios, acessórios, materiais e instalações provisórias de sua propriedade e de seus subcontratados, removendo-os dentro do prazo a ser acordado entre as PARTES, não superior a 15 (quinze) DIAS, a contar de solicitação escrita da CONTRATANTE. Caso este prazo não seja cumprido, a CONTRATANTE poderá, à sua conveniência, executar esta retirada, debitando as despesas respectivas da CONTRATADA, adicionadas dos custos eventualmente necessários para acautelar a ocorrência de danos, perdas, furtos ou extravios, inclusive os das coberturas de seguros aplicáveis.
[P593] A CONTRATANTE, após prévia notificação judicial, ou extrajudicial, terá o direito de reter, qualquer pagamento devido à CONTRATADA, oriundo deste CONTRATO ou outro instrumento celebrado com a CONTRATADA, a quantia correspondente ao custo de eventuais indenizações e reclamações, até a remoção, pela CONTRATADA, do aludido vínculo ou liame e liquidação da indenização, reclamação ou reivindicação porventura daí decorrente.
[P595] O Serviços executados até a data da extinção do CONTRATO serão normalmente medidos e pago nos termos do CONTRATO.
[P597] Os direitos da CONTRATANTE relativos às consequências da extinção antecipada do CONTRATO não eliminam ou restringem o direito desta em aplicar à CONTRATADA as penalidades previstas neste CONTRATO.
[P599] Na hipótese de extinção do CONTRATO, por qualquer motivo, as PARTES se comprometem a assinar um termo de encerramento do CONTRATO. As PARTES desde já ajustam que o CONTRATO será considerado encerrado quanto às obrigações operacionais se a CONTRATADA se mantiver silente e/ou inerte sobre a assinatura do termo de encerramento após o transcurso de 30 (trinta) DIAS do envio do termo pela CONTRATANTE, sem prejuízo de obrigações de confidencialidade, garantia, indenização, auditoria, propriedade intelectual e proteção de dados.
[P601] A CONTRATADA deverá desocupar inteiramente o LOCAL DE PRESTAÇÃO DOS SERVIÇOS, deixando-o livre de quaisquer materiais, equipamentos, profissionais, poluentes, lixos e entulhos, dando a estes últimos destinação adequada, bem como de equipamentos utilizados  e relacionados  aos Serviços, removendo-os dentro do prazo determinado pela CONTRATANTE. Caso este prazo não seja cumprido, a CONTRATANTE poderá, à sua conveniência, proceder à retirada, debitando as respectivas despesas, adicionadas dos custos eventualmente necessários para acautelar a ocorrência de danos, perdas, furtos ou extravios, inclusive os das coberturas de seguros aplicáveis.
[P603] ARBITRAGEM E FORO
[P605] As PARTES se comprometem a envidar seus melhores esforços para resolver, amigavelmente e de boa fé, quaisquer demandas, divergências e outras questões oriundas deste CONTRATO, por meio de negociações diretas.
[P607] Não sendo possível a solução por meio de negociação direta no prazo de 30 (trinta) DIAS contado da notificação da controvérsia, fica desde já convencionado que quaisquer controvérsias oriundas deste CONTRATO serão definitivamente resolvidas por meio de arbitragem, nos termos da Lei nº 9.307, de 23/09/1996, de acordo com as regras da Câmara de Arbitragem Empresarial Brasil (CAMARB).
[P609] Para os fins da arbitragem, as PARTES ajustam, desde logo, o seguinte:
[P611] O presente CONTRATO, nos termos ora previstos, assim como os direitos e obrigações das PARTES dele decorrentes, serão interpretados e regidos pelas leis da República Federativa do Brasil;
[P613] Quaisquer questões, controvérsias, disputas ou reivindicações decorrentes de ou relacionadas à validade, interpretação, desempenho, implementação, rescisão ou violação deste Instrumento (incluindo a validade desta cláusula de ARBITRAGEM), bem como quaisquer relações jurídicas relativas a este CONTRATO, serão resolvidas, de maneira exclusiva e definitiva, por arbitragem, final e vinculante, a ser processada perante a Câmara de Arbitragem Empresarial – Brasil (CAMARB), de acordo com as suas regras e regimento (“Regulamento”) que estiver em vigor na data do pedido de instauração da arbitragem.
[P615] A arbitragem será conduzida por 3 (três) árbitros, cabendo a cada uma das PARTES a indicação de um árbitro. O arbitro deverá ser pessoa de reconhecida competência no assunto principal objeto do litígio, que não possua impedimento para atuação no procedimento, e deve fazer parte da lista de árbitros da CAMARB. O terceiro árbitro, que funcionará como o Presidente do Tribunal Arbitral, será nomeado de comum acordo pelos árbitros indicados pelas PARTES. Caso os 2 (dois) árbitros indicados pelas PARTES deixem de nomear o terceiro árbitro, no prazo regulamentar, ou não havendo consenso entre os árbitros a respeito da nomeação do terceiro árbitro, caberá à CAMARB indicar o terceiro árbitro.
[P617] Para controvérsias que possam envolver valores de até R$ 1.000.000,00 (um milhão de reais), as PARTES escolherão árbitro único. Não havendo consenso, caberá à CAMARB indicar o árbitro único.
[P619] Os procedimentos da arbitragem terão lugar na Cidade de Belo Horizonte, Estado de Minas Gerais, Brasil.
[P621] Os procedimentos de arbitragem serão conduzidos no idioma português e o laudo arbitral será redigido em português.
[P623] O Tribunal Arbitral poderá arbitrar honorários sucumbenciais em favor da parte vencedora, observados os limites da legislação aplicável e o Regulamento da CAMARB.
[P625] - Cada PARTE mantém o direito de buscar perante a jurisdição competente as medidas judiciais cautelares e/ou de urgência que entenderem necessárias para proteger e garantir direitos, antes da instauração do Tribunal Arbitral, cientes de que essas medidas judiciais não serão interpretadas como renúncia à arbitragem. Para o exercício desse direito, as PARTES elegem o foro da Comarca de Belo Horizonte, Estado de Minas Gerais, Brasil, com renúncia expressa a qualquer outro por mais privilegiado que possa ser.
[P627] A instauração e o procedimento arbitral não deverão influenciar a execução do CONTRATO, devendo as PARTES continuar cumprindo fielmente as obrigações contratuais que porventura não estejam diretamente impedidas pela arbitragem, sob pena de caracterizar descumprimento contratual.
[P629] A PARTE que violar a cláusula de arbitragem ou praticar ato destinado a prejudicar, obstaculizar ou impedir a solução da controvérsia por meio da arbitragem ficará sujeita ao pagamento de multa no valor correspondente a 5% sobre o VALOR ESTIMADO DO CONTRATO, sem prejuízo de perdas e danos comprovados.
[P631] Entre outras, entendem-se como práticas violadoras da cláusula de arbitragem: (i) recusar ou se abster de participar atos no procedimento arbitral; (ii) descumprir prazos; (iii) prejudicar ou impedir o andamento do procedimento; (iv) adotar prática desleal, temerária ou protelatória.
[P633] A multa será exigida por meio de emissão de nota de débito ou executada diretamente, sem prejuízo da instauração e do processamento da arbitragem, de acordo com o procedimento previsto no Regulamento da CAMARB.
[P635] A sentença arbitral será definitiva, irrecorrível (exceção feita à hipótese do artigo 30 da Lei n.º 9.307/96) e obrigará plenamente as PARTES ligantes e seus sucessores, devendo ser imediatamente cumprida em todos os seus termos pelas PARTES, as quais se declaram, desde logo, cientes de que o não cumprimento da sentença arbitral autoriza a sua execução diretamente no Judiciário.
[P637] Para a resolução de disputas que se refiram exclusivamente ao COMODATO, , se aplicável, as partes elegem como foro contratual, a Comarca de Belo Horizonte, Estado de Minas Gerais, excluindo qualquer outro por mais privilegiado que seja.
[P639] DISPOSIÇÕES GERAIS
[P641] A CONTRATADA reconhece que poderá haver outros contratos que apresentam interfaces com o seu, e desde já se compromete a harmonizar/adequar as suas atividades com os respectivos contratados, a fim de não causar prejuízos diretos e/ou indiretos, de modo que qualquer entendimento entre a CONTRATADA e as demais empresas contratadas pela CONTRATANTE deverão ser aprovadas pela CONTRATANTE previamente e por escrito.
[P643] O CONTRATO é aceito pelas PARTES como completo e suficiente para definir o objeto dos Serviços, assim como sua extensão e intenção, dentro das leis e normas específicas vigentes no Brasil.
[P645] A CONTRATANTE reserva-se o direito de auditar qualquer das etapas do objeto do CONTRATO, a qualquer tempo, desde que no horário normal de trabalho da CONTRATADA e de seus subcontratados aprovados, mediante aviso prévio mínimo de 5 (cinco) DIAS úteis, salvo hipótese de urgência, investigação de compliance ou risco à saúde, segurança, meio ambiente ou continuidade operacional.
[P647] Quando aplicável, a CONTRATADA declara que tem ciência e cumprirá as diretrizes que integram, ANEXO - Termo de Compromisso Socioambiental nº 01/2011 - Plano Integrado de Ocupação da Rede Hoteleira (UBU), Anexo - NR 18 - Condições e Meio Ambiente de Trabalho na Indústria da Construção e Anexo - Relatório Mensal de Desempenho da CONTRATADA.
[P649] Este instrumento, juntamente com seus ANEXOS, constitui o acordo integral entre as PARTES. Ele substitui e cancela todas as demais comunicações, verbais ou escritas, propostas e declarações referentes ao objeto aqui versado.
[P651] Nenhuma modificação do CONTRATO vinculará as PARTES, exceto quando efetuada por escrito, assinada pelos representantes legais de cada PARTE, mediante o respectivo Termo Aditivo Contratual, admitindo-se que ajustes operacionais de rotina, sem impacto financeiro ou alteração de risco, sejam formalizados por ordem de serviço ou e-mail dos Gestores do Contrato.
[P653] As Partes reconhecem a veracidade, autenticidade, integridade, validade e eficácia deste CONTRATO e seus termos, nos moldes do art. 219 do Código Civil, caso assinado digitalmente pelas PARTES, ainda que com utilização de meios diversos aos certificados eletrônicos emitidos pela ICP-Brasil, em observância aos ditames do art. 10, § 2º, da Medida Provisória nº 2.200-2, de 24 de agosto de 2001 (“MP nº 2.200-2”).
[P655] As PARTES de comum acordo estabelecem que o quanto negociado neste CONTRATO não representará um precedente para as próximas negociações futuras.
[P657] As Partes declaram e concordam que a assinatura do presente CONTRATO poderá ser efetuada em formato eletrônico. As Partes reconhecem a veracidade, autenticidade, integridade, validade e eficácia do presente instrumento e seus termos, incluindo seus ANEXOS, nos termos do art. 219 do Código Civil, em formato eletrônico e/ou assinado pelas Partes por meio de certificados eletrônicos, ainda que sejam certificados eletrônicos não emitidos pela ICP-Brasil, nos termos do art. 10, § 2º, da Medida Provisória nº 2.200-2, de 24 de agosto de 2001 (“MP nº 2.200-2”). Cada um dos indivíduos que assina em nome das Partes declara e garante que está autorizado a executar o presente instrumento em nome da respectiva Parte, bem como que o presente instrumento, quando executado, tornar-se-á válido e vinculante de acordo com seus termos.
[P659] Em caso de assinatura física, o presente CONTRATO será assinado na quantidade de vias correspondentes à quantidade de PARTES, e, em qualquer formato de assinatura, o CONTRATO segue assinado também por 2 (duas) testemunhas, todos de igual teor e forma, para um só efeito.
[P661] Belo Horizonte, _______________________________.
[P664] Samarco Mineração S.A.:
[P669] PREENCHER COM O NOME DA CONTRATADA:
[P675] TESTEMUNHAS:
```

---

## Sua Tarefa

Compare os dois documentos acima e gere um JSON com **TODAS as modificações** encontradas.

### Estrutura do JSON de Resposta

```json
{
  "versao_id": "8d8e89a8-ba89-4e0e-846c-43e7ad058309",
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
    "timestamp": "2026-05-28T20:06:39.178244"
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
