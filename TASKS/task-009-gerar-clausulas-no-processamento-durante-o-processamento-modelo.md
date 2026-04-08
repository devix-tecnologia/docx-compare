# Task 009 — gerar clausulas no processamento durante o processamento modelo

Status: pending
Type: feat
Assignee: Sidarta Veloso

## Description

Durante o processamento automático de modelos de contrato (`processador_modelo_contrato.py`), criar automaticamente registros de cláusulas na coleção `clausula` do Directus.

**Campos preenchidos automaticamente:**

- `conteudo_original`: Texto extraído da cláusula no documento modelo
- `numero`: Número identificador da cláusula (ex: "12.6.1", "15.2")
- `nome`: Nome/título da cláusula extraído do documento

**Campos para preenchimento manual posterior:**

- `objetivo`: Finalidade/propósito da cláusula (será preenchido pelo usuário)
- `referencias`: Referências cruzadas com outras cláusulas (será preenchido pelo usuário)

**Contexto:**
Atualmente, as tags extraídas são vinculadas a cláusulas, mas as cláusulas precisam existir previamente no banco. Esta task automatiza a criação das cláusulas durante a extração de tags do modelo, eliminando trabalho manual e garantindo consistência entre tags e cláusulas.

## Tasks

- [ ] Implementar extração de número e nome da cláusula a partir do conteúdo do documento
- [ ] Criar endpoint/método no `DirectusRepository` para inserir cláusulas
- [ ] Integrar criação de cláusulas no fluxo do `processador_modelo_contrato.py`
- [ ] Adicionar validação para evitar duplicação de cláusulas (verificar por número)
- [ ] Registrar log das cláusulas criadas automaticamente
- [ ] Atualizar testes para validar criação automática de cláusulas
