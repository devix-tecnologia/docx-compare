# Task 018 — Corrigir sistema de coordenadas incompatível entre processamento de modelo e versão

Status: in-progress
Type: fix
Priority: critical
Assignee: Sidarta Veloso

**Versão de Teste:** 8d8e89a8-ba89-4e0e-846c-43e7ad058309
**Modelo de Teste:** 48b43d38-76b4-47a2-93a4-4216ad57defc
**Data Criação:** 2026-06-02
**Última Atualização:** 2026-06-03

---

## 🎯 Progresso

### ✅ Completado

1. **Refatoração DRY** (commit c800f47):
   - Criadas funções core puras compartilhadas
   - `_analisar_diferencas_core()`, `_extrair_tags_core()`, `_remover_marcacoes_e_mapear_core()`, `_extrair_conteudo_tag_core()`
   - Eliminada duplicação entre `ProcessadorTagsModelo` e `processar_modelo_local()`
   - Ambos usam mesma lógica DIFF

2. **Correção de bug** (commit c800f47):
   - Corrigido processamento tag-por-tag (estava processando todas de uma vez)
   - Teste manual: 294 tags processadas com sucesso

3. **Formatação** (commit a9e2bbb):
   - Aplicado ruff format

### ⏳ Em Progresso

- **Problema identificado**: AlgoritmoHibrido trava ao vincular 294 tags com 67 modificações
- **Bloqueador**: Precisa investigar/otimizar algoritmo de vinculação antes de validar coordenadas

### ❌ Pendente

- Teste automatizado pytest ainda não passa (trava durante execução)
- Validação com dados reais (versão 8d8e89a8)
- Confirmar taxa de vinculação ≥40%

---

## 📋 Problema Original

O processamento de versões está resultando em **0% de vinculação** de modificações com cláusulas, mesmo usando o algoritmo híbrido otimizado que apresenta **98.8% de vinculação** nos testes isolados.

### Sintomas Observados

```
✅ 44 modificações detectadas
❌ 0/44 vinculadas (0.0%)
📝 Primeira modificação: Posições: None-None
```

### Causa Raiz Identificada

As **tags do modelo** e as **modificações da versão** estão mapeadas em **sistemas de coordenadas diferentes**:

1. **Tags do modelo** (`processador_tags_modelo.py`):
   - Extraídas de `arquivo_com_tags.docx`
   - Coordenadas calculadas após remover marcações `{{TAG-X}}`
   - Mapeadas em `texto_limpo` (texto sem tags)
   - Exemplo: tag em posição 85288-86642

2. **Modificações da versão** (`processar_versao_direta.py`):
   - Calculadas do diff entre `arquivo_original.docx` e `arquivo_modificado.docx`
   - Coordenadas calculadas em `texto_original` (convertido via pandoc)
   - Exemplo: modificação em posição 53853-54065

3. **Resultado**: Ranges nunca se sobrepõem → `buscar_tag_por_posicao()` retorna `None` → 0% vinculação

### Evidências

#### Teste Automatizado

```bash
# tests/test_integracao_modelo_versao.py::test_coordenadas_alinhadas
❌ ERRO DE COORDENADAS: 0% vinculação indica que posições estão em sistemas diferentes
```

#### Dados Reais

```python
# Processamento manual da versão 8d8e89a8:
Tags: 294
Modificações: 67
Vinculadas: 0/67 (0.0%)
```

#### Código Problemático

```python
# processador_tags_modelo.py linha 85:
texto_limpo, mapa_posicoes = self._remover_marcacoes_e_mapear(texto_tagged)
# Tags mapeadas no texto_limpo (159.151 caracteres)

# processar_versao_direta.py linha 109:
texto_original = re.sub(PATTERN_REMOVER_TAGS, "", texto_com_tags)
# Modificações calculadas neste texto_original (DIFERENTE do texto_limpo)
```

---

## 🎯 Objetivo

Alinhar os sistemas de coordenadas para que tags e modificações usem **o mesmo texto de referência**, permitindo que o algoritmo de vinculação funcione corretamente.

---

## ✅ Critérios de Aceitação

1. **Taxa mínima de vinculação**: ≥40% (preferencialmente ≥80% como nos testes)
2. **Teste automatizado passa**: `test_integracao_modelo_versao.py::test_coordenadas_alinhadas`
3. **Teste com dados reais**: Versão 8d8e89a8 apresenta vinculação significativa (>0%)
4. **Modificações com posições**: Todas as modificações devem ter `posicao_inicio` e `posicao_fim` válidos
5. **Coordenadas consistentes**: Tags e modificações no mesmo espaço de coordenadas

---

## 🔧 Soluções Propostas

### Opção 1: Usar arquivo_com_tags como base (Recomendada)

**Vantagens:**

- Tags já mapeadas neste arquivo
- Menor mudança no código do modelo
- Arquivo com tags é sempre disponível

**Implementação:**

1. Em `processar_versao_direta.py`, usar `arquivo_com_tags` do modelo como base
2. Fazer diff: `arquivo_com_tags` (limpo) vs `arquivo_modificado`
3. Tags e modificações estarão no mesmo `texto_limpo`

```python
# processar_versao_direta.py
# Buscar arquivo_com_tags do modelo
arquivo_com_tags_id = modelo_data.get("arquivo_com_tags")
texto_com_tags = baixar_e_converter_para_texto(arquivo_com_tags_id)

# Usar MESMA função de limpeza do processador
texto_original_limpo = re.sub(PATTERN_REMOVER_TAGS, "", texto_com_tags)

# Fazer diff com arquivo modificado
modificacoes = fazer_diff(texto_original_limpo, texto_modificado)
```

### Opção 2: Recalcular tags no texto original

**Vantagens:**

- Mantém lógica atual do processamento de versão
- Tags recalculadas para cada versão

**Desvantagens:**

- Mais complexo
- Tags já foram processadas uma vez
- Risco de divergência

### Opção 3: Criar mapeamento entre coordenadas

**Vantagens:**

- Não modifica fluxo existente
- Solução "ponte"

**Desvantagens:**

- Mais complexo
- Propenso a erros
- Não resolve problema na raiz

---

## 📊 Impacto

### Componentes Afetados

- ✅ `processar_versao_direta.py` (modificar busca de arquivo base)
- ✅ `repositorio.py` (garantir que arquivo_com_tags está disponível)
- ⚠️ `processador_tags_modelo.py` (possivelmente exportar função de limpeza)

### Testes Necessários

- ✅ `tests/test_integracao_modelo_versao.py` (já existe, deve passar)
- ✅ Teste manual com versão 8d8e89a8
- ✅ Regressão: versões já processadas não devem quebrar

---

## 📝 Notas de Implementação

### Fixtures Disponíveis

```
tests/sample/integracao-completa/
├── arquivo_com_tags.docx      495K (modelo)
├── arquivo_original.docx      128K (modelo sem tags)
├── arquivo_modificado.docx    121K (versão)
├── clausulas_inicial.json     1.4M (859 cláusulas)
└── tags_modelo.json           2.5M (294 tags)
```

### Constante Compartilhada

```python
# processador_tags_modelo.py linha 24-26:
PATTERN_REMOVER_TAGS = r"\{\{/?TAG-[^}]+\}\}|\{\{/?[a-zA-Z_][a-zA-Z0-9_]*\}\}|\{\{/?\d+(?:\.\d+)*\}\}"
```

Esta constante JÁ está sendo importada corretamente em `processar_versao_direta.py`.

---

## 🚦 Validação

### Comando de Teste

```bash
# Teste automatizado
cd versiona-ai
uv run pytest tests/test_integracao_modelo_versao.py -v -s

# Teste com dados reais
uv run python processar_versao_direta.py \
  --versao 8d8e89a8-ba89-4e0e-846c-43e7ad058309 \
  --directus-url https://contract.devix.co \
  --directus-token TOKEN
```

### Resultados Esperados

```
✅ 44 modificações encontradas
✅ Vinculadas: ≥18/44 (≥40%)  # Meta mínima
🎯 Vinculadas: ≥35/44 (≥80%)  # Meta ideal (como testes)
```

---

## 🔍 Investigação Adicional

### Por que os testes unitários não pegaram?

✅ **Respondido**: Testes unitários usam dados sintéticos/fixtures isolados. O problema só aparece no **fluxo de integração completo** Modelo → Versão.

### Teste de integração criado

✅ `tests/test_integracao_modelo_versao.py` detecta o problema automaticamente e garante que a correção funciona.

---

## 📚 Referências

- Algoritmo Híbrido: `tests/algoritmos/hibrido/algoritmo.py`
- Commit 42e2939 (2026-05-16): Implementação dos algoritmos avançados
- Issue descoberta em: 2026-06-02
- Teste de regressão: `tests/test_integracao_modelo_versao.py`
