# Parametrização do Fuzzy Matching

**Data:** 2026-06-03  
**Autor:** Sistema de Otimização Contínua

## 📋 Visão Geral

O `AlgoritmoHibrido` agora suporta **parametrização inteligente do fuzzy matching** para evitar timeouts em datasets grandes.

## 🎯 Problema

Fuzzy matching com `RapidFuzz` é **O(n² × m)** onde:
- `n` = número de modificações
- `m` = número de tags
- Cada comparação calcula múltiplas métricas de similaridade

**Exemplo real:**
- 67 modificações × 294 tags = **19,698 comparações**
- Tempo estimado: **>60 segundos** (timeout)

## ✅ Solução

### Auto-Detecção de Complexidade

```python
from tests.algoritmos.hibrido.algoritmo import AlgoritmoHibrido

# Padrão: auto-detecta baseado em complexidade
algoritmo = AlgoritmoHibrido(usar_fuzzy=None, limiar_complexidade_fuzzy=10000)

# Fuzzy SEMPRE habilitado
algoritmo_com_fuzzy = AlgoritmoHibrido(usar_fuzzy=True)

# Fuzzy SEMPRE desabilitado
algoritmo_sem_fuzzy = AlgoritmoHibrido(usar_fuzzy=False)
```

### Lógica de Decisão

```python
complexidade = num_modificacoes × num_tags

if usar_fuzzy is None:
    if complexidade > limiar_complexidade_fuzzy:
        # Desabilita automaticamente
        usar_fuzzy = False
    else:
        # Habilita automaticamente
        usar_fuzzy = True
```

## 📊 Performance Validada

### Antes da Parametrização

| Dataset | Complexidade | Tempo | Status |
|---------|-------------|-------|--------|
| 67 mods × 294 tags | 19,698 | >60s | ⚠️ Timeout |

### Depois da Parametrização

| Dataset | Complexidade | Fuzzy | Tempo | Taxa | Status |
|---------|-------------|-------|-------|------|--------|
| 67 mods × 294 tags | 19,698 | ❌ Auto-desabilitado | <30s | 34.3% | ✅ OK |
| 5 mods × 10 tags | 50 | ✅ Auto-habilitado | <1s | 80%+ | ✅ OK |

## 🎛️ Configuração Recomendada

### Produção

```python
# Padrão conservador: desabilita fuzzy para datasets médios/grandes
algoritmo = AlgoritmoHibrido(
    usar_fuzzy=None,  # Auto-detecta
    limiar_complexidade_fuzzy=5000  # 5k comparações
)
```

**Exemplos:**
- ✅ 20 mods × 200 tags = 4,000 ← fuzzy habilitado
- ❌ 30 mods × 200 tags = 6,000 ← fuzzy desabilitado

### Desenvolvimento/Testes

```python
# Mais agressivo: permite fuzzy em datasets maiores
algoritmo = AlgoritmoHibrido(
    usar_fuzzy=None,
    limiar_complexidade_fuzzy=10000  # 10k comparações
)
```

### Casos Especiais

```python
# Contratos simples com poucas cláusulas: sempre habilitar
if num_tags < 50:
    algoritmo = AlgoritmoHibrido(usar_fuzzy=True)

# Contratos complexos com muitas cláusulas: sempre desabilitar
if num_tags > 500:
    algoritmo = AlgoritmoHibrido(usar_fuzzy=False)
```

## 📈 Estatísticas

O algoritmo rastreia quantas vezes fuzzy foi usado ou desabilitado:

```python
stats = algoritmo.obter_estatisticas()
# {
#   "overlap": {"count": 23, "percentage": 20.72},
#   "regex": {"count": 0, "percentage": 0.0},
#   "fuzzy": {"count": 0, "percentage": 0.0},
#   "fuzzy_desabilitado": {"count": 44, "percentage": 39.64},
#   "ml": {"count": 0, "percentage": 0.0},
#   "nao_vinculada": {"count": 44, "percentage": 39.64}
# }
```

## ⚙️ Estratégias de Vinculação (Ordem)

1. **Overlap** (mais rápido)
   - Se modificação tem `posicao_inicio/posicao_fim`
   - Busca tag com maior sobreposição geométrica

2. **Regex** (rápido, preciso)
   - Padrões estruturados: valores monetários, datas, IDs, CPF/CNPJ
   - Named groups para extração

3. **Fuzzy** (lento, flexível) - *parametrizável*
   - Texto livre com variações ortográficas
   - Múltiplas métricas: ratio, partial_ratio, token_sort, token_set
   - **Desabilitado automaticamente** se complexidade > limiar

4. **ML** (futuro)
   - Semântica, paráfrases, sinônimos

## 🔍 Diagnóstico

Se a vinculação estiver lenta:

1. **Verificar complexidade:**
   ```python
   complexidade = len(modificacoes) * len(tags)
   print(f"Complexidade: {complexidade:,}")
   # > 10,000 → considerar desabilitar fuzzy
   ```

2. **Analisar estatísticas:**
   ```python
   stats = algoritmo.obter_estatisticas()
   if stats["fuzzy"]["count"] > 1000:
       print("⚠️ Fuzzy sendo usado demais, considerar desabilitar")
   ```

3. **Ajustar limiar:**
   ```python
   # Se vinculação está lenta mas não está desabilitando
   algoritmo = AlgoritmoHibrido(limiar_complexidade_fuzzy=5000)  # Mais restritivo
   ```

## 💡 Otimizações Futuras

1. **Fuzzy incremental:** Processar em batches de 100 tags por vez
2. **Cache de similaridade:** Reutilizar cálculos entre execuções
3. **Threshold dinâmico:** Ajustar baseado em tamanho médio do texto
4. **Paralelização:** ThreadPoolExecutor para comparações independentes

## 📚 Referências

- **Código:** `versiona-ai/tests/algoritmos/hibrido/algoritmo.py`
- **Commit:** 3e4674b
- **Issue:** Fuzzy O(n²) para datasets grandes (task-018)
