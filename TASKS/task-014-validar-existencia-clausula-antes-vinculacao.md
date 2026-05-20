# Task 014 - Validar Existência de Cláusula Antes da Vinculação

## Status

pendente

## Responsável

A definir

## Descrição

Durante o processamento de versões, o sistema está tentando vincular modificações a cláusulas que não existem no banco de dados do Directus, resultando em erro `INVALID_FOREIGN_KEY`.

### Erro Identificado

```
⚠️ Erro ao atualizar versão: HTTP 400: {"errors":[{
  "message":"Invalid foreign key \"59a034cc-e29d-4ed2-8989-4a945582d215\" for field \"clausula\" in collection \"modificacao\".",
  "extensions":{
    "collection":"modificacao",
    "field":"clausula",
    "value":"59a034cc-e29d-4ed2-8989-4a945582d215",
    "code":"INVALID_FOREIGN_KEY"
  }
}]}
```

### Contexto

- **ID da cláusula**: `59a034cc-e29d-4ed2-8989-4a945582d215`
- **Identificação**: Cláusula 3ª - 3.3
- **Situação**: O algoritmo de vinculação encontrou e vinculou 2 modificações a esta cláusula (taxa 100%)
- **Problema**: Esta cláusula NÃO existe na tabela de cláusulas do Directus

## Objetivos

- Implementar validação de existência de cláusula antes de tentar persistir vinculação
- Adicionar tratamento para casos onde a tag existe mas não tem cláusula associada
- Melhorar logs para identificar quando uma cláusula referenciada não existe
- Evitar falha completa do processamento quando uma cláusula é inválida

## Prioridade

alta

## Estimativa

4 horas

## Dependências

- Acesso ao schema do Directus (coleções `clausula`, `modificacao`, `tag`)
- Compreensão do fluxo de vinculação no processador

## Critérios de Aceitação

1. Sistema deve validar se a cláusula existe no Directus ANTES de tentar criar a modificação
2. Se a cláusula não existir:
   - Log de warning claro identificando o problema
   - Modificação deve ser criada SEM vinculação (campo `clausula` = null)
   - Taxa de vinculação deve refletir corretamente o problema
3. O processamento não deve falhar completamente por causa de uma cláusula inválida
4. Logs devem indicar:
   - Qual tag foi usada na tentativa de vinculação
   - ID da cláusula que não existe
   - Número da cláusula/tag
   - Quantas modificações foram afetadas

## Impacto

- **Alta criticidade**: Erro bloqueia a persistência de TODAS as modificações do processamento
- **Taxa de vinculação falsa**: Sistema reporta 100% mas falha ao persistir
- **Dados perdidos**: Modificações detectadas não são salvas no banco

## Investigação Necessária

1. Por que a tag `59a034cc-e29d-4ed2-8989-4a945582d215` está presente nos metadados mas a cláusula não existe?
   - Tag sem cláusula vinculada?
   - Cláusula deletada após criação da tag?
   - Problema na importação do modelo de contrato?

2. Quantas outras tags/cláusulas podem estar nesta situação?
   - Fazer query no Directus para identificar tags órfãs
   - Verificar consistência entre tags e cláusulas

## Arquivos Envolvidos

- `versiona-ai/processador_limpeza.py` - Lógica de processamento e persistência
- `versiona-ai/repositorio.py` - Interface com Directus
- Código de vinculação de modificações a cláusulas

## Próximos Passos

1. Adicionar método no repositório para validar existência de cláusula
2. Modificar fluxo de persistência para fazer validação antes do POST
3. Implementar fallback para modificações com cláusulas inválidas
4. Adicionar testes unitários para este cenário
5. Fazer auditoria completa das tags/cláusulas do modelo em produção

## Observações

Este erro pode estar relacionado à forma como o modelo de contrato foi importado ou a uma inconsistência no banco de dados. É importante não apenas corrigir o código, mas também investigar a causa raiz da inconsistência.

**Data de identificação**: 2026-05-20
**Versão afetada**: 2573b998-63d0-4471-ad85-db6f860c3721
**Modelo de contrato**: 48b43d38-76b4-47a2-93a4-4216ad57defc (Contrato de prestação de serviço - Rotina V.11jun2025)
