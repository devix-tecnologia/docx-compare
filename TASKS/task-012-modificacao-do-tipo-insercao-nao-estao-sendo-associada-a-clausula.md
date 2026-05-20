# Task 012 — Modificações do tipo inserção não estão sendo associadas à cláusula

Status: done
Type: fix
Assignee: Sidarta Veloso

## Description

Modificações do tipo "inserção" não estão sendo vinculadas às suas respectivas cláusulas durante o processamento de documentos. O sistema deve identificar e associar corretamente cada inserção à cláusula correspondente.

**Problema**: Inserções permanecem sem vínculo com cláusulas, impedindo rastreamento adequado de alterações no documento.

**Escopo**: Processamento backend de modificações (não é problema de interface).

## Tasks

- [x] Investigar se modificações de inserção estão sendo detectadas corretamente
- [x] Verificar se existe teste unitário para vinculação de inserções a cláusulas
- [x] Reproduzir problema com documento de teste
- [x] Identificar causa raiz da falha de associação
- [x] Corrigir lógica de vinculação para modificações de inserção
- [x] Validar correção com testes automatizados

## Notes

- Verificar logs do processador para identificar erros durante associação
- Confirmar se problema ocorre apenas com inserções ou afeta outros tipos de modificação
- Documentar casos de teste que reproduzem o problema

## Root Cause

Dois bugs em `_vincular_por_sobreposicao_com_score` em `versiona-ai/directus_server.py`:

1. **TypeError**: `dict.get("posicao_inicio", 0)` retorna `None` quando a chave existe com valor `None` (comportamento Python). O `max(None, int)` gerava TypeError. Correção: remover default `0` e guardar o loop com `if mod_inicio is not None and mod_fim is not None`.

2. **Sem fallback para INSERCAO**: Inserções têm `posicao_inicio=None` (pois são conteúdo novo), então o overlap posicional sempre falha. A cláusula destino é identificada pelo campo `clausula_modificada` (extraído do atributo `data-clause` do HTML de diff). Correção: fallback que, quando `melhor_tag is None and mod_tipo == "INSERCAO"`, busca `clausula_modificada` em `tag.clausulas[*].numero` e atribui `melhor_score = 0.7`.

## Validation

- 9/9 testes unitários passando em `versiona-ai/tests/test_vinculacao_insercao.py`
- Validação com versão real `2573b998-63d0-4471-ad85-db6f860c3721`: ambas as inserções corretamente vinculadas à cláusula 2.5.2 (ID: 92eb8f9e)
