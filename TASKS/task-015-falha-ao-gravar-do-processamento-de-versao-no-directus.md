# Task 015 — Falha silenciosa ao gravar resultado do processamento no Directus

Status: pending
Type: fix
Assignee: Sidarta Veloso

## Descrição

Ao concluir o processamento de uma versão, o sistema falha ao tentar persistir as modificações no Directus com erro `INVALID_FOREIGN_KEY`, mas ainda assim reporta o processamento como bem-sucedido (`✅ Processamento AST concluído!`). O resultado é que o processamento aparenta ter funcionado, porém nenhuma modificação é de fato salva no banco de dados.

### Comportamento observado

1. O processamento ocorre normalmente: modificações são detectadas e vinculadas às cláusulas.
2. Na etapa de gravação, o Directus rejeita a operação com erro HTTP 400 — a cláusula referenciada não existe na coleção `clausula`.
3. O erro é logado como `⚠️ warning`, mas o fluxo continua e termina com status de sucesso.
4. A versão fica com status "processado" no Directus, porém sem nenhuma modificação associada.

### Log observado

```
...
2026-05-20T18:31:43.306510323Z 🔄 Registrando resultado do processamento da versão 2573b998-63d0-4471-ad85-db6f860c3721...
2026-05-20T18:31:43.306519642Z    📊 Total de modificações: 2
2026-05-20T18:31:43.376872037Z ⚠️ Erro ao atualizar versão: HTTP 400: {"errors":[{"message":"Invalid foreign key \"59a034cc-e29d-4ed2-8989-4a945582d215\" for field \"clausula\" in collection \"modificacao\".","extensions":{"collection":"modificacao","field":"clausula","value":"59a034cc-e29d-4ed2-8989-4a945582d215","code":"INVALID_FOREIGN_KEY"}}]}
2026-05-20T18:31:43.376915879Z ⚠️ Erro ao persistir modificações: HTTP 400: {"errors":[{"message":"Invalid foreign key \"59a034cc-e29d-4ed2-8989-4a945582d215\" for field \"clausula\" in collection \"modificacao\".","extensions":{"collection":"modificacao","field":"clausula","value":"59a034cc-e29d-4ed2-8989-4a945582d215","code":"INVALID_FOREIGN_KEY"}}]}
2026-05-20T18:31:43.377725112Z ✅ Processamento AST concluído!
...
```

Dados completos do log: [2026-05-20-task-015.log](./assets/2026-05-20-task-015.log)

### Causa raiz provável

A cláusula `59a034cc-e29d-4ed2-8989-4a945582d215` é referenciada por uma tag do modelo, mas não existe na coleção `clausula` do Directus. O algoritmo de vinculação retorna este ID sem verificar se ele de fato existe antes de tentar criar o registro de `modificacao`. A task [014](./task-014-validar-existencia-clausula-antes-vinculacao.md) cobre a correção preventiva deste caso.

O problema desta task é complementar: **mesmo quando a gravação falha, o sistema não atualiza o status da versão para refletir a falha**, tornando o erro invisível para o operador.

### Impacto

- Modificações detectadas pelo processamento são descartadas silenciosamente.
- A versão aparece como "processada" na interface, mas está incompleta.
- Não há nenhum sinal de erro visível para o usuário ou operador sem inspecionar os logs.
- O reprocessamento manual torna-se necessário, mas o operador não sabe que precisa fazê-lo.

## Tarefas

- [ ] Verificar qual status a versão recebe quando a persistência de modificações falha
- [ ] Garantir que falha na gravação das modificações resulte em status de erro na versão (não "processado")
- [ ] Avaliar se o erro deve interromper o fluxo ou apenas marcar as modificações afetadas como não persistidas
- [ ] Revisar o tratamento de exceção na etapa de registro de resultado para não mascarar falhas
- [ ] Adicionar log de nível `error` (não apenas `warning`) quando modificações não puderem ser salvas
- [ ] Validar comportamento corrigido com teste reproduzindo a falha de FK

## Dependências

- Task [014](./task-014-validar-existencia-clausula-antes-vinculacao.md) — validação de existência de cláusula antes da vinculação (endereça a causa raiz do FK inválido)

## Critérios de Aceitação

1. Quando a gravação de qualquer modificação falhar, a versão deve ter seu status atualizado para um estado que indique falha ou processamento parcial.
2. O log deve distinguir claramente entre "processamento concluído" e "resultado gravado com sucesso".
3. O operador deve conseguir identificar, sem inspecionar logs brutos, que o processamento de uma versão resultou em erro de persistência.
4. O comportamento deve ser testável via teste automatizado que simule a rejeição do Directus.
