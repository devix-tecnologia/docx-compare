# Task: Corrigir Cálculo de Posições em Modificações AST

**Status:** 🔴 RED (Teste falhando)
**Prioridade:** Alta
**Criado em:** 2026-05-16

## 📋 Resumo

Modificações detectadas pelo processador AST não têm campos `posicao_inicio` e `posicao_fim` calculados, impedindo a vinculação automática com cláusulas.

## 🐛 Problema Identificado

### Versão Real Testada

- **ID:** `2573b998-63d0-4471-ad85-db6f860c3721`
- **Contrato:** `f7435867-8e6e-4798-a00f-f6edc23ae0f2`
- **Modelo:** `48b43d38-76b4-47a2-93a4-4216ad57defc` (271 cláusulas)
- **Arquivo:** `92f80aec-275c-4917-9d7c-4ba31a065561.docx`

### Estado Atual (🔴 RED)

**Processamento AST:**

```
✅ 2 modificações detectadas (INSERÇÃO)
✅ 85/100 tags mapeadas corretamente
✅ 271 cláusulas disponíveis no modelo
❌ posicao_inicio = NULL
❌ posicao_fim = NULL
❌ Taxa de vinculação: 0% (0/2)
```

**Dados no Banco:**

```sql
SELECT id, categoria, posicao_inicio, posicao_fim, clausula
FROM modificacao
WHERE versao = '2573b998-63d0-4471-ad85-db6f860c3721';

-- Resultado:
--   id        | categoria | posicao_inicio | posicao_fim | clausula
-- ------------|-----------|----------------|-------------|----------
--  439f412d   | INSERCAO  | NULL ❌        | NULL ❌     | NULL ❌
--  8e1e8dc2   | INSERCAO  | NULL ❌        | NULL ❌     | NULL ❌
```

### Logs do Processamento

```
🔗 Vinculando 2 modificações...
🔗 Vinculando tags às modificações por sobreposição
   Total de tags mapeadas: 85
   Total de modificações: 2

🏷️  Exemplo de tags mapeadas (primeiras 3):
   Tag 1: 2 [66805-66825] método=conteudo_apenas ✅
   Tag 2: 3 [68844-68878] método=conteudo_apenas ✅
   Tag 3: 4 [71225-71243] método=conteudo_apenas ✅

📝 Modificação 1: tipo=INSERCAO [0-0] ❌
   ❌ Modificação [0-0] tipo=INSERCAO: sem tag correspondente

📝 Modificação 2: tipo=INSERCAO [0-0] ❌
   ❌ Modificação [0-0] tipo=INSERCAO: sem tag correspondente

📊 Resultado da vinculação:
📎 Consolidação de vinculação: total=2, com_clausula=0, sem_clausula=2
Taxa de cobertura: 0.0%
```

**Causa Raiz:**

- Tags têm posições válidas: `[66805-66825]`, `[68844-68878]`
- Modificações têm posições inválidas: `[0-0]`
- Vinculação por sobreposição falha (sem sobreposição entre [0-0] e [66805-66825])

## ✅ Estado Esperado (🟢 GREEN)

```
✅ posicao_inicio calculado do texto
✅ posicao_fim calculado do texto
✅ Taxa de vinculação: >= 50% (pelo menos 1/2)
```

## 🧪 Teste Criado

**Arquivo:** `versiona-ai/tests/test_vinculacao_ast_versao_real.py`

**Comando para executar:**

```bash
cd versiona-ai
uv run pytest tests/test_vinculacao_ast_versao_real.py::test_vinculacao_clausulas_versao_real_ast -v -s
```

**Resultado atual (RED):**

```
FAILED tests/test_vinculacao_ast_versao_real.py::test_vinculacao_clausulas_versao_real_ast
AssertionError: ❌ 2/2 modificações SEM posição!
   Modificações sem posição: ['439f412d', '8e1e8dc2']
   PROBLEMA: Processamento AST não calculou posicoes_inicio/posicao_fim
```

### Asserções do Teste

1. **✅ Modificações criadas:** 2/2
2. **❌ Posições calculadas:** 0/2 (FALHANDO)
3. **❌ Vinculação >= 50%:** 0% (FALHANDO)

## 🔧 Onde Corrigir

### Arquivo Principal

`versiona-ai/directus_server.py`

### Método Responsável

`DirectusAPI._process_versao_com_ast()` (linha ~2164)

### Trecho Problemático

```python
def _process_versao_com_ast(self, versao_id, versao_data):
    # ...

    # 3. Processar com AST
    resultado_ast = self._compare_docx_ast(arquivo_orig_path, arquivo_novo_path)
    modificacoes = resultado_ast.get("modificacoes", [])

    # ❌ PROBLEMA: modificacoes não têm posicao_inicio/posicao_fim

    # 4. Vincular às cláusulas (usando texto modificado)
    if tags_modelo:
        arquivo_novo_id = # ...
        modified_text = self._download_and_extract_text(arquivo_novo_id)

        if modified_text:
            resultado_vinculacao = self._vincular_modificacoes_clausulas_novo(
                modificacoes=modificacoes,  # ❌ Sem posições!
                tags_modelo=tags_modelo,
                texto_com_tags=modified_text,
                texto_original=modified_text,
            )
```

### Método AST que Retorna Modificações

`DirectusAPI._compare_docx_ast()` (linha ~3000+)

```python
def _compare_docx_ast(self, arquivo_orig_path, arquivo_novo_path):
    # ...

    # Detecta modificações usando SequenceMatcher
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "insert":
            modificacoes.append({
                "tipo": "INSERCAO",
                "conteudo": {},
                "alteracao": paragrafos_novos[j1:j2],
                # ❌ FALTANDO: posicao_inicio, posicao_fim
            })
```

## 🎯 Solução Proposta

### Opção 1: Calcular Posições no Método AST (Recomendado)

Modificar `_compare_docx_ast()` para:

1. Extrair texto plano completo do documento modificado
2. Para cada parágrafo inserido, buscar sua posição no texto completo
3. Adicionar `posicao_inicio` e `posicao_fim` nas modificações

```python
def _compare_docx_ast(self, arquivo_orig_path, arquivo_novo_path):
    # ...

    # Extrair texto completo para calcular posições
    texto_completo_novo = self._extract_text_from_ast(ast_novo)

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "insert":
            paragrafo_texto = "\n".join(paragrafos_novos[j1:j2])

            # Buscar posição no texto completo
            pos_inicio = texto_completo_novo.find(paragrafo_texto)
            pos_fim = pos_inicio + len(paragrafo_texto) if pos_inicio >= 0 else None

            modificacoes.append({
                "tipo": "INSERCAO",
                "conteudo": {},
                "alteracao": paragrafo_texto,
                "posicao_inicio": pos_inicio,  # ✅ Calculado
                "posicao_fim": pos_fim,        # ✅ Calculado
            })
```

### Opção 2: Calcular Posições Antes da Vinculação

Adicionar um método `_calcular_posicoes_modificacoes()` que:

1. Recebe modificações sem posições
2. Baixa texto do arquivo modificado
3. Busca cada modificação no texto e calcula posições
4. Retorna modificações com posições

```python
def _process_versao_com_ast(self, versao_id, versao_data):
    # ...

    # 3. Processar com AST
    resultado_ast = self._compare_docx_ast(arquivo_orig_path, arquivo_novo_path)
    modificacoes = resultado_ast.get("modificacoes", [])

    # 3.5 Calcular posições
    if not modificacoes[0].get("posicao_inicio"):
        texto_modificado = self._download_and_extract_text(arquivo_novo_id)
        modificacoes = self._calcular_posicoes_modificacoes(
            modificacoes,
            texto_modificado
        )

    # 4. Vincular às cláusulas
    # ...
```

## 📝 Checklist de Implementação

- [ ] Escolher abordagem (Opção 1 ou 2)
- [ ] Implementar cálculo de posições
- [ ] Executar teste: `pytest tests/test_vinculacao_ast_versao_real.py -v -s`
- [ ] Verificar posições calculadas (não NULL)
- [ ] Verificar vinculação >= 50%
- [ ] Teste passar (🟢 GREEN)
- [ ] Commit com mensagem clara

## 🚦 Como Saber que Está Funcionando

### 1. Teste Principal Verde

```bash
cd versiona-ai
uv run pytest tests/test_vinculacao_ast_versao_real.py::test_vinculacao_clausulas_versao_real_ast -v -s

# Saída esperada:
# ✅ 2/2 modificações COM posição
# ✅ Taxa de vinculação: >= 50%
# PASSED tests/test_vinculacao_ast_versao_real.py::test_vinculacao_clausulas_versao_real_ast
```

### 2. Verificar no Banco

```sql
SELECT
    id,
    categoria,
    posicao_inicio,
    posicao_fim,
    clausula
FROM modificacao
WHERE versao = '2573b998-63d0-4471-ad85-db6f860c3721';

-- Esperado:
--   id        | categoria | posicao_inicio | posicao_fim | clausula
-- ------------|-----------|----------------|-------------|----------
--  439f412d   | INSERCAO  | 123456 ✅     | 123642 ✅   | uuid ✅
--  8e1e8dc2   | INSERCAO  | 123700 ✅     | 123767 ✅   | uuid ✅
```

### 3. Logs de Processamento

```
🔗 Vinculando 2 modificações...
📝 Modificação 1: tipo=INSERCAO [123456-123642] ✅
   ✅ Modificação vinculada à Tag '5.2'
📝 Modificação 2: tipo=INSERCAO [123700-123767] ✅
   ✅ Modificação vinculada à Tag '5.3'

📊 Resultado da vinculação:
📎 Consolidação de vinculação: total=2, com_clausula=2, sem_clausula=0 ✅
Taxa de cobertura: 100.0% ✅
```

## 📚 Arquivos Relacionados

- **Teste:** `versiona-ai/tests/test_vinculacao_ast_versao_real.py`
- **Código Principal:** `versiona-ai/directus_server.py`
  - Método `_process_versao_com_ast()` (linha ~2164)
  - Método `_compare_docx_ast()` (linha ~3000+)
  - Método `_vincular_modificacoes_clausulas_novo()` (linha ~1599)

## 🔍 Debug Adicional

### Ver Modificações Atuais

```sql
SELECT
    m.id,
    m.categoria,
    m.posicao_inicio,
    m.posicao_fim,
    m.clausula,
    c.numero as clausula_numero,
    LENGTH(m.alteracao) as tam_alteracao
FROM modificacao m
LEFT JOIN clausula c ON m.clausula = c.id
WHERE m.versao = '2573b998-63d0-4471-ad85-db6f860c3721';
```

### Ver Tags Mapeadas

```sql
SELECT
    COUNT(*) as total_tags,
    COUNT(DISTINCT clausulas) as tags_com_clausulas
FROM tag
WHERE modelo_contrato = '48b43d38-76b4-47a2-93a4-4216ad57defc';
```

### Reprocessar Versão

```bash
curl -H "Authorization: Bearer pmUzcQ6EgMm9uqYcHIM-MYiZHz11rVfP" \
  "http://localhost:8011/api/versoes/2573b998-63d0-4471-ad85-db6f860c3721"
```

## 🎓 Contexto Adicional

### Por que Posições São Necessárias?

A vinculação de cláusulas funciona por **sobreposição de posições**:

1. **Tags têm posições** no texto tagueado: `Tag '5.2' [66805-66825]`
2. **Modificações precisam de posições** no texto: `Mod [66810-66820]`
3. **Vinculação por sobreposição:** Se `66810` está entre `[66805-66825]`, vincular à Tag '5.2'
4. **Tag '5.2' tem cláusulas:** Vincular modificação à cláusula da tag

Sem posições nas modificações (`[0-0]`), não há sobreposição possível!

### Métrica de Sucesso

- **Taxa mínima:** 50% de vinculação
- **Ideal:** >= 80% de vinculação
- **Tolerância:** Algumas modificações podem não ser vinculadas (texto fora de cláusulas conhecidas)

---

**Próximo passo:** Implementar cálculo de posições e executar teste até ficar 🟢 GREEN!
