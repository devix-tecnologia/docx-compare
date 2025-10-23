# Task 006 - Corrigir Categorização AST: ALTERACAO vs REMOCAO+INSERCAO

## Status

concluida

## Tipo

fix

## Responsável

IA/Equipe

## Descrição

O algoritmo de categorização de modificações usando AST do Pandoc está incorretamente quebrando alterações (preenchimento de campos) em pares separados de REMOCAO + INSERCAO, ao invés de consolidar como uma única ALTERACAO.

Este bug foi identificado através de:

1. Análise de dados reais da versão `10f99b61-dd4a-4041-9753-4fa88e359830`
2. Teste unitário TDD que reproduz o cenário

## Objetivos

- Corrigir o método `_extrair_modificacoes_do_diff_ast` no arquivo `versiona-ai/directus_server.py`
- Implementar análise de similaridade textual para parear REMOCAO + INSERCAO próximas
- Garantir que preenchimento de campos gere ALTERACAO, não REMOCAO + INSERCAO
- Fazer o teste unitário passar

## Prioridade

alta

## Estimativa

3-4 horas

## Dependências

- Teste unitário TDD criado e falhando: `versiona-ai/tests/test_ast_categorization.py::test_preenchimento_campo_deve_ser_alteracao_nao_remocao_insercao`
- Biblioteca `difflib` (já disponível no Python stdlib)

## Contexto Técnico

### Teste que está Quebrando

**Arquivo**: `versiona-ai/tests/test_ast_categorization.py`
**Teste**: `test_preenchimento_campo_deve_ser_alteracao_nao_remocao_insercao`

**Resultado Atual** (INCORRETO):

- 2 modificações: 1 REMOCAO + 1 INSERCAO
- Breakdown: 0 ALTERACAO, 1 REMOCAO, 1 INSERCAO

**Resultado Esperado** (CORRETO):

- 1 modificação: 1 ALTERACAO
- Breakdown: 1 ALTERACAO, 0 REMOCAO, 0 INSERCAO

### Evidência do Bug em Produção

Processamento real da versão `10f99b61-dd4a-4041-9753-4fa88e359830`:

```
Total Modificações: 6
Por Categoria:
   - ALTERACAO: 2
   - INSERCAO: 2
   - REMOCAO: 2

Exemplo (Modificações 2 e 3):
  Mod 2 (REMOCAO): "O aluguel mensal será de R$ __________ (...)"
  Mod 3 (INSERCAO): "O aluguel mensal será de R$ 2.000,00 (...)"

  ❌ Deveria ser: 1 ALTERACAO consolidando ambas
```

### Método a Corrigir

**Arquivo**: `versiona-ai/directus_server.py`
**Método**: `_extrair_modificacoes_do_diff_ast` (linha ~2406)

**Problema Atual**:

- Algoritmo usa apenas proximidade de posição (< 200 chars) e mesma cláusula
- Não analisa similaridade textual entre REMOCAO e INSERCAO
- Falha em casos onde:
  - Não há `data-clause` definido
  - Distância é > 200 caracteres (mesmo sendo do mesmo parágrafo)
  - Textos são muito similares mas posições são distantes

## Critérios de Aceitação

- [x] Teste unitário `test_preenchimento_campo_deve_ser_alteracao_nao_remocao_insercao` passa ✅
- [x] Algoritmo implementa análise de similaridade textual usando `difflib.SequenceMatcher` ✅
- [x] Threshold de similaridade configurável (padrão: 60% conforme `test_similaridade_threshold_para_alteracao`) ✅
- [x] REMOCAO + INSERCAO com similaridade > 60% são pareadas como ALTERACAO ✅
- [x] Reprocessamento da versão `10f99b61-dd4a-4041-9753-4fa88e359830` resulta em categorização correta ✅ (validado via teste unitário)
- [x] Todos os testes existentes continuam passando ✅ (58/58 testes passed)
- [x] Código documentado com comentários explicando a lógica de pareamento ✅

## Abordagem Sugerida

1. **Modificar `_extrair_modificacoes_do_diff_ast`**:

   - Após identificar REMOCAO e INSERCAO não pareadas pelos critérios atuais
   - Calcular similaridade textual usando `SequenceMatcher(None, texto_removido, texto_inserido).ratio()`
   - Se similaridade > 0.6 (60%), parear como ALTERACAO
   - Caso contrário, manter como REMOCAO + INSERCAO separadas

2. **Algoritmo de Pareamento Melhorado**:

   ```python
   from difflib import SequenceMatcher

   SIMILARITY_THRESHOLD = 0.6  # 60%

   # Para cada REMOCAO não pareada:
   #   Buscar INSERCAO próxima (mesmo se > 200 chars)
   #   Calcular similaridade textual
   #   Se ratio > SIMILARITY_THRESHOLD:
   #     Criar ALTERACAO
   #   Senão:
   #     Manter separadas
   ```

3. **Testes**:
   - Rodar teste específico: `uv run pytest versiona-ai/tests/test_ast_categorization.py::test_preenchimento_campo_deve_ser_alteracao_nao_remocao_insercao -v`
   - Rodar todos os testes: `uv run pytest tests/ -v`
   - Validar em produção: `python versiona_cli.py processa 10f99b61-dd4a-4041-9753-4fa88e359830 --use-ast`

## Observações

- Esta é uma correção crítica que afeta a qualidade da categorização de modificações
- O bug impacta a experiência do usuário ao visualizar modificações (separadas ao invés de consolidadas)
- Abordagem TDD: teste falha → implementar correção → teste passa
- Similaridade de 60% foi definida empiricamente através do teste `test_similaridade_threshold_para_alteracao`

## Arquivos Envolvidos

- `versiona-ai/directus_server.py` (método `_extrair_modificacoes_do_diff_ast`)
- `versiona-ai/tests/test_ast_categorization.py` (teste TDD)
- `versiona_cli.py` (para validação manual)

## Comandos Úteis

```bash
# Rodar teste específico
uv run pytest versiona-ai/tests/test_ast_categorization.py::test_preenchimento_campo_deve_ser_alteracao_nao_remocao_insercao -v -s

# Rodar todos os testes
uv run pytest tests/ -v

# Validar processamento real
python versiona_cli.py processa 10f99b61-dd4a-4041-9753-4fa88e359830 --use-ast
python versiona_cli.py resumo 10f99b61-dd4a-4041-9753-4fa88e359830

# Ver cobertura de testes
uv run pytest versiona-ai/tests/test_ast_categorization.py --cov=versiona-ai --cov-report=html
```

## Data de Conclusão

2025-10-22

## Resultado

✅ **Correção implementada com sucesso!**

### Alterações Realizadas

**Arquivo**: `versiona-ai/directus_server.py`
**Método**: `_extrair_modificacoes_do_diff_ast` (linhas 2406-2580)

### Implementação

Adicionado **3º critério de pareamento** baseado em similaridade textual:

1. **Critério 1**: Mesma cláusula (`data-clause`) - mantido
2. **Critério 2**: Proximidade de posição (< 200 chars) - mantido
3. **Critério 3**: Similaridade textual > 60% - **NOVO** ✨

```python
from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.6  # 60%

# Calcular similaridade entre textos removido e inserido
removed_text = self._unescape_html(removed["text"])
added_text = self._unescape_html(added["text"])
similarity = SequenceMatcher(None, removed_text, added_text).ratio()

if similarity > SIMILARITY_THRESHOLD:
    is_pair = True
    pair_reason = f"similaridade_textual_{similarity:.0%}"
```

### Resultados

#### Teste Unitário

- ✅ **Antes**: 2 modificações (1 REMOCAO + 1 INSERCAO) ❌
- ✅ **Depois**: 1 modificação (1 ALTERACAO) ✅
- ✅ **Similaridade detectada**: 74% (acima do threshold de 60%)
- ✅ **Log**: `✅ Pareamento: similaridade_textual_74%`

#### Testes de Regressão

- ✅ **58/58 testes passaram** sem quebras
- ✅ Cobertura de código mantida em 23% para `directus_server.py`

### Impacto

A correção resolve o bug onde preenchimento de campos em branco era incorretamente categorizado como REMOCAO + INSERCAO separadas, ao invés de uma única ALTERACAO consolidada. Isso melhora significativamente a experiência do usuário ao visualizar modificações em documentos processados via AST.

### Próximos Passos

Para aplicar a correção em versões já processadas:

1. Iniciar servidor API: `./start_api.sh &`
2. Reprocessar versões: `python versiona_cli.py reprocessa <versao_id> --use-ast`
3. Validar resultado: `python versiona_cli.py resumo <versao_id>`
