# Task 010 — processamento de versões não está relacionando cláusula à modificação

Status: done
Type: fix
Assignee: Sidarta Veloso

## Description

Durante o processamento automático de versões (`processador_automatico.py`), o sistema está criando registros na coleção `modificacao` do Directus, porém o campo `clausula` (chave estrangeira para a coleção `clausula`) não está sendo preenchido.

**Problema atual:**

- Modificações são detectadas e persistidas com sucesso
- Campo `clausula` permanece NULL/vazio
- Vinculação entre modificações e cláusulas não é estabelecida

**Impacto:**

- Impossibilita rastreamento de quais cláusulas foram modificadas
- Quebra relacionamento essencial para análise e auditoria de contratos
- Dashboard e relatórios não conseguem agrupar modificações por cláusula

**Causa provável:**
O processamento de versões precisa usar um algoritmo de matching para vincular cada modificação detectada à cláusula correspondente no modelo do contrato, baseando-se em:

- Posição no documento
- Similaridade de texto
- Tags relacionadas (quando disponíveis)

## Tasks

- [x] Investigar fluxo atual de criação de modificações no `processador_automatico.py`
- [x] Verificar implementação existente da lógica de vinculação modificação → cláusula via matching posicional/fuzzy
- [x] Buscar cláusulas do modelo de contrato vinculado à versão
- [x] Calcular melhor match entre modificação e cláusulas disponíveis
- [x] Persistir ID da cláusula no campo `clausula` da modificação
- [x] Adicionar testes para validar vinculação correta
- [x] Registrar logs quando vinculação não for possível (threshold não atingido)

## Plano de execução (realizado)

1. Reproduzir o problema com teste orientado a regressão para cenário de relação de cláusula aninhada no retorno do Directus.
2. Confirmar estado RED com falha explícita de ausência de `clausula_id` na consolidação.
3. Implementar correção mínima na consolidação para preencher `clausula_id` nos formatos de relacionamento observados no ambiente.
4. Confirmar estado GREEN no teste de regressão e nos testes focados de conversão/persistência.
5. Executar suíte principal para garantir ausência de regressão global.
6. Registrar evidências operacionais para auditoria da correção.

## Evidências de efetividade (sem código-fonte)

### Contexto de execução

- Data: 2026-04-29
- Branch: `feat/task-010`
- Commit de trabalho durante validação: `074e700129f9eb7bd8c02758aa9e86cd048e5c27`

### Evidência 1 - TDD RED → GREEN (regressão específica)

- Cenário: vinculação de modificação quando a cláusula vem em relação aninhada (formato de junção do Directus).
- Execução RED (antes da correção):
  - Comando: `uv run pytest versiona-ai/tests/test_vinculacao_clausulas.py -k "relacao_aninhada_directus" -v`
  - Resultado: FAILED
  - Erro observado: `clausula_id` retornando `None` em vez do ID esperado.
- Execução GREEN (após correção):
  - Mesmo comando acima
  - Resultado: PASSED (1 passed, 7 deselected)

### Evidência 2 - Testes focados da Task 010

- Comando: `uv run pytest versiona-ai/tests/test_vinculacao_clausulas.py -k "consolidacao or converter_modificacao or relacao_aninhada_directus" -v`
- Resultado: PASSED
- Contagem: 4 passed, 4 deselected
- Cobertura da validação focada:
  - preenchimento de `clausula_id` quando o valor prévio era `None`
  - mapeamento de relacionamento de cláusula em formato direto
  - mapeamento de relacionamento de cláusula em formato aninhado
  - persistência do campo FK `clausula` no payload final

### Evidência 3 - Observabilidade operacional

- Comando: `uv run pytest versiona-ai/tests/test_vinculacao_clausulas.py -k "consolidacao_preenche_clausula_id_quando_valor_previo_none" -v -s`
- Resultado: PASSED
- Log emitido durante a execução:
  - `Consolidação de vinculação: total=1, com_clausula=1, sem_clausula=0`
- Interpretação: o pipeline passou a contabilizar explicitamente vínculo com cláusula e ausência de vínculo.

### Evidência 4 - Regressão global

- Comando: `uv run pytest tests/ -v`
- Resultado: PASSED
- Contagem final: 84 passed
- Tempo de execução: 11.77s

### Conclusão auditável

- A falha foi reproduzida e comprovada antes da correção (RED).
- A correção resolveu o cenário de falha e manteve os cenários anteriores íntegros (GREEN).
- A suíte principal permaneceu estável após a mudança (84/84), reduzindo risco de regressão lateral.
