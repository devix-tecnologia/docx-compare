# Padronização de Status — `versao` e `modelo_contrato`

## Contexto

As coleções `versao` e `modelo_contrato` possuem um campo `status` que controla o ciclo de vida do registro e serve como **gatilho para o processamento pela máquina Python** (VersionaAI). Ao comparar os valores cadastrados nas duas coleções, foram identificadas inconsistências que dificultam a manutenção, a leitura por parte dos usuários e a rastreabilidade em queries e logs.

Este documento descreve o estado atual, os problemas encontrados e a proposta de padronização aprovada.

---

## Problemas identificados

| #   | Problema                                                                  | Exemplo                                                                      |
| --- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 1   | Mesmo significado, valores internos diferentes                            | `versao` usa `em_processamento`; `modelo_contrato` usa `processando`         |
| 2   | Status com nome de ação (verbo) ao invés de estado (substantivo/adjetivo) | Valor `processar` / Texto "Processar" — todos os demais são adjetivos        |
| 3   | Label verbose e focado na ação, não no objeto                             | Texto "Concluído processamento" em vez de "Processado"                       |
| 4   | Status existente no código mas ausente na interface                       | `cancelada` está implementado no hook mas não aparece como opção no Directus |

---

## Coleção: `versao`

### DE (situação atual)

| Texto                   | Valor              | Cor       |
| ----------------------- | ------------------ | --------- |
| Rascunho                | `draft`            | `#A2B5CD` |
| Processar               | `processar`        | `#6644FF` |
| Em processamento        | `em_processamento` | `#3399FF` |
| Concluído processamento | `concluido`        | `#2ECDA7` |
| Erro                    | `erro`             | `#E35100` |
| Fechada                 | `fechada`          | `#18222F` |
| _(ausente na UI)_       | `cancelada`        | —         |

### PARA (situação proposta)

| Texto                    | Valor              | Cor       | Mudança                 |
| ------------------------ | ------------------ | --------- | ----------------------- |
| Rascunho                 | `draft`            | `#A2B5CD` | — sem alteração         |
| Processamento solicitado | `solicitado`       | `#6644FF` | Texto e Valor alterados |
| Em processamento         | `em_processamento` | `#3399FF` | — sem alteração         |
| Processado               | `concluido`        | `#2ECDA7` | Texto alterado          |
| Erro                     | `erro`             | `#E35100` | — sem alteração         |
| Fechada                  | `fechada`          | `#18222F` | — sem alteração         |
| Cancelada                | `cancelada`        | `#E35169` | **Adicionado**          |

---

## Coleção: `modelo_contrato`

### DE (situação atual)

| Texto                   | Valor         | Cor       |
| ----------------------- | ------------- | --------- |
| Rascunho                | `draft`       | `#A2B5CD` |
| Processar               | `processar`   | `#6644FF` |
| Em processamento        | `processando` | `#3399FF` |
| Concluído processamento | `concluido`   | `#2ECDA7` |
| Erro                    | `erro`        | `#E35100` |
| Publicado               | `publicado`   | `#18D100` |

### PARA (situação proposta)

| Texto                    | Valor              | Cor       | Mudança                 |
| ------------------------ | ------------------ | --------- | ----------------------- |
| Rascunho                 | `draft`            | `#A2B5CD` | — sem alteração         |
| Processamento solicitado | `solicitado`       | `#6644FF` | Texto e Valor alterados |
| Em processamento         | `em_processamento` | `#3399FF` | Valor alterado          |
| Processado               | `concluido`        | `#2ECDA7` | Texto alterado          |
| Erro                     | `erro`             | `#E35100` | — sem alteração         |
| Publicado                | `publicado`        | `#18D100` | — sem alteração         |

---

## Fluxo de vida dos registros

### `versao`

```
draft → solicitado → em_processamento → concluido → fechada
                                     ↘ erro → solicitado (reprocessar)
  ↓ (a qualquer momento antes de concluir)
cancelada
```

| Status             | Quem aciona        | Significado                                                                  |
| ------------------ | ------------------ | ---------------------------------------------------------------------------- |
| `draft`            | Usuário            | Versão criada, ainda não enviada para análise                                |
| `solicitado`       | Usuário            | Processamento solicitado, aguardando a máquina Python iniciar                |
| `em_processamento` | Sistema (Python)   | Máquina Python iniciou a análise                                             |
| `concluido`        | Sistema (Python)   | Análise concluída, aguardando revisão do analista                            |
| `fechada`          | Usuário (analista) | Analista revisou e encaminhou considerações ao cliente — **estado terminal** |
| `cancelada`        | Usuário            | Análise interrompida antes da conclusão                                      |
| `erro`             | Sistema (Python)   | Falha durante o processamento                                                |

### `modelo_contrato`

```
draft → solicitado → em_processamento → concluido → publicado
                                     ↘ erro → solicitado (reprocessar)
```

| Status             | Quem aciona      | Significado                                                                                   |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------------- |
| `draft`            | Usuário          | Modelo em elaboração, não disponível para uso                                                 |
| `solicitado`       | Usuário          | Processamento solicitado, aguardando a máquina Python iniciar                                 |
| `em_processamento` | Sistema (Python) | Máquina Python está processando o modelo                                                      |
| `concluido`        | Sistema (Python) | Processamento concluído, aguardando publicação                                                |
| `publicado`        | Usuário          | Modelo disponível para uso na criação de contratos (**estado terminal — não permite edição**) |
| `erro`             | Sistema (Python) | Falha durante o processamento                                                                 |

---

## Impacto técnico

### Directus (campo `status` de cada coleção)

- `versao`: atualizar choices conforme tabela PARA acima
- `modelo_contrato`: atualizar choices conforme tabela PARA acima

### Código — `src/versao-hook/index.ts`

- Constante `VERSAO_STATUS_CONFIG`: substituir chave `processar` por `solicitado` e label por "Processamento solicitado"
- Regras de transição (`statusTransitionRules`): substituir referências a `processar` por `solicitado`
- Validação (`validateVersaoData`, linha ~1157): substituir `"processar"` por `"solicitado"` na checagem de arquivo obrigatório
- Label "Concluído processamento" → "Processado"

### Scripts em `scripts/`

- Verificar se algum script filtra por `status = 'processar'` ou `status = 'processando'` e atualizar para os novos valores

---

## Condicionais de transição (estado → próximos estados permitidos)

As condições abaixo são as regras amarradas diretamente no campo `status` do Directus. Elas controlam quais opções ficam disponíveis no dropdown dependendo do estado atual do registro.

### `versao` — atual vs. proposto

| Estado atual       | Choices disponíveis HOJE                | Choices propostos                       | Ação necessária                                          |
| ------------------ | --------------------------------------- | --------------------------------------- | -------------------------------------------------------- |
| `draft`            | `draft`, `processar`                    | `draft`, `solicitado`, `cancelada`      | Trocar `processar` → `solicitado`; adicionar `cancelada` |
| `processar`        | `processar`, `em_processamento`         | _(condição removida)_                   | Deletar — substituída pela de `solicitado`               |
| `solicitado`       | _(não existe)_                          | `solicitado`, `em_processamento`        | Criar condição nova                                      |
| `em_processamento` | `em_processamento`, `concluido`, `erro` | `em_processamento`, `concluido`, `erro` | ✓ Sem alteração de choices                               |
| `concluido`        | `concluido`, `fechada`, `draft`         | `concluido`, `fechada`, `solicitado`    | Trocar `draft` → `solicitado`                            |
| `erro`             | `erro`, `draft`                         | `erro`, `solicitado`                    | Trocar `draft` → `solicitado`                            |
| `fechada`          | `fechada`, `draft`                      | `fechada` _(terminal)_                  | Remover `draft` dos choices                              |
| `cancelada`        | _(não existe)_                          | `cancelada` _(terminal)_                | Criar condição nova                                      |

> **`fechada` → `draft`:** hoje o Directus permite reverter uma versão fechada para rascunho. O código do hook define `fechada: []` (sem transições). Estão em conflito — a proposta resolve removendo essa opção do Directus, alinhando com o código.

> **`erro` e `concluido` → `draft`:** hoje reprocessar "reseta" o registro para rascunho. A proposta corrige: ambos devem ir para `solicitado`, mantendo o histórico e reenviando direto para a fila.

### `modelo_contrato` — atual vs. proposto

`modelo_contrato` **não tem máquina de estados configurada**. A única condição registrada é `processando → readonly` (e ainda assim `readonly: false`, o que indica que está quebrada). Toda a estrutura precisa ser criada do zero.

| Estado atual       | Choices disponíveis HOJE           | Choices propostos                                          | Ação necessária                            |
| ------------------ | ---------------------------------- | ---------------------------------------------------------- | ------------------------------------------ |
| `draft`            | _(sem restrição — qualquer valor)_ | `draft`, `solicitado`                                      | Criar condição                             |
| `processar`        | _(sem restrição)_                  | _(removido)_                                               | Deletar choice e condição                  |
| `solicitado`       | _(não existe)_                     | `solicitado`, `em_processamento`                           | Criar condição                             |
| `em_processamento` | campo readonly quebrado            | `em_processamento`, `concluido`, `erro` + `readonly: true` | Corrigir e complementar condição existente |
| `concluido`        | _(sem restrição)_                  | `concluido`, `publicado`, `solicitado`                     | Criar condição                             |
| `erro`             | _(sem restrição)_                  | `erro`, `solicitado`                                       | Criar condição                             |
| `publicado`        | _(sem restrição)_                  | `publicado` _(terminal + readonly)_                        | Criar condição de readonly                 |

---

## Resumo da contagem de status

| Coleção           | Antes                                | Depois    | Diferença                                   |
| ----------------- | ------------------------------------ | --------- | ------------------------------------------- |
| `versao`          | 6 choices (+ 1 no código sem choice) | 7 choices | **+1** (`cancelada` adicionado na UI)       |
| `modelo_contrato` | 6 choices                            | 6 choices | **=** (mesmo total; valores internalizados) |
