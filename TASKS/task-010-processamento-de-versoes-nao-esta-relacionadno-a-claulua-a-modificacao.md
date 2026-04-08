# Task 010 — processamento de versões não está relacionando cláusula à modificação

Status: pending
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

- [ ] Investigar fluxo atual de criação de modificações no `processador_automatico.py`
- [ ] Implementar lógica de vinculação modificação → cláusula via matching posicional/fuzzy
- [ ] Buscar cláusulas do modelo de contrato vinculado à versão
- [ ] Calcular melhor match entre modificação e cláusulas disponíveis
- [ ] Persistir ID da cláusula no campo `clausula` da modificação
- [ ] Adicionar testes para validar vinculação correta
- [ ] Registrar logs quando vinculação não for possível (threshold não atingido)
