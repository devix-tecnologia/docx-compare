# Task 019 — Otimizar Fuzzy Matching para Grandes Datasets

Status: open
Type: optimization
Priority: high
Assignee: Sistema de Otimização Contínua

**Data Criação:** 2026-06-03
**Relacionado a:** Task-018

---

## 📋 Problema

O **AlgoritmoFuzzyAvancado** possui **complexidade O(n² × m)** que causa timeouts em datasets grandes:

- `n` = número de modificações
- `m` = número de tags
- Cada comparação calcula múltiplas métricas de similaridade (ratio, partial_ratio, token_sort, token_set)

### Evidências

**Caso Real (Task-018):**

- Dataset: 67 modificações × 294 tags = **19,698 comparações**
- Tempo: **>60 segundos** (timeout)
- Solução atual: **Desabilitar fuzzy automaticamente** quando complexidade > 10,000

**Impacto:**

- Taxa de vinculação: **34.3%** (apenas overlap)
- Meta: **≥40%** (não atingida)
- **Perda de precisão:** Fuzzy não é usado em 65.7% das vinculações potenciais

### Limiar Atual

```python
AlgoritmoHibrido(
    usar_fuzzy=None,  # Auto-detecta
    limiar_complexidade_fuzzy=10000  # 10k comparações
)
```

**Casos que desabilitam fuzzy:**

- ✅ 100 mods × 100 tags = 10,000 (limite)
- ❌ 67 mods × 294 tags = 19,698 (desabilita)
- ❌ 50 mods × 300 tags = 15,000 (desabilita)

---

## 🎯 Objetivo

Permitir uso de fuzzy matching em datasets grandes sem degradação de performance.

### Metas

1. **Performance:** Reduzir tempo de O(n²) para O(n log n) ou melhor
2. **Taxa de vinculação:** Atingir ≥40% em datasets grandes (>10k comparações)
3. **Limiar:** Aumentar para ≥50,000 comparações sem timeout
4. **Compatibilidade:** Manter API existente do AlgoritmoHibrido

---

## 💡 Estratégias de Otimização

### 1. Batch Processing (Prioridade Alta)

**Ideia:** Dividir dataset em lotes pequenos e processar incrementalmente.

```python
def vincular_clausulas_batch(
    self,
    modificacoes: list[dict],
    tags: list[dict],
    batch_size: int = 100
) -> list[dict]:
    """
    Processa em lotes de 100 comparações por vez.

    Exemplo: 67 mods × 294 tags
    - Lote 1: mods 0-10 × todas tags (2,940 comparações)
    - Lote 2: mods 11-20 × todas tags (2,940 comparações)
    - ...
    - Total: 7 lotes executados sequencialmente
    """
```

**Vantagens:**

- ✅ Mantém algoritmo intacto
- ✅ Fácil implementar
- ✅ Permite progress feedback ao usuário

**Estimativa:**

- Complexidade: Mesma (O(n²)), mas com menor consumo de memória
- Ganho: 0-20% (apenas organização)

### 2. Cache de Similaridade (Prioridade Alta)

**Ideia:** Armazenar resultados de comparações para reutilizar.

```python
class FuzzyCacheado:
    def __init__(self):
        self._cache = {}  # {(texto1_hash, texto2_hash): score}

    def calcular_score(self, texto1: str, texto2: str) -> float:
        key = (hash(texto1), hash(texto2))
        if key not in self._cache:
            self._cache[key] = fuzz.ratio(texto1, texto2)
        return self._cache[key]
```

**Vantagens:**

- ✅ Evita cálculos redundantes
- ✅ Útil quando mesma modificação aparece múltiplas vezes
- ✅ Reutilizável entre execuções (persistir em disco)

**Estimativa:**

- Ganho: 30-50% se houver textos repetidos

### 3. Threshold Dinâmico Early Exit (Prioridade Média)

**Ideia:** Parar comparações assim que encontrar match bom o suficiente.

```python
def buscar_melhor_tag_early_exit(
    texto_busca: str,
    tags: list[dict],
    threshold: float = 85.0,
    early_exit_threshold: float = 95.0
) -> dict | None:
    """
    Para de buscar se encontrar score ≥95%.
    """
    melhor_tag = None
    melhor_score = 0.0

    for tag in tags:
        score = calcular_score(texto_busca, tag["texto"])

        if score >= early_exit_threshold:
            return tag  # Encontrou match excelente, para aqui

        if score > melhor_score and score >= threshold:
            melhor_score = score
            melhor_tag = tag

    return melhor_tag
```

**Vantagens:**

- ✅ Reduz comparações quando há match claro
- ✅ Não perde precisão (só para quando já achou)

**Estimativa:**

- Ganho: 20-40% em casos com bons matches

### 4. Índice Invertido + Pre-filtering (Prioridade Média)

**Ideia:** Pré-filtrar tags candidatas usando trigrams ou tokens antes de fuzzy.

```python
from sklearn.feature_extraction.text import TfidfVectorizer

class FuzzyComIndice:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(3, 3))
        self.tags_vectors = None

    def indexar_tags(self, tags: list[dict]):
        """Cria índice TF-IDF de trigrams."""
        textos = [t["texto"] for t in tags]
        self.tags_vectors = self.vectorizer.fit_transform(textos)

    def buscar_candidatas(
        self,
        texto_busca: str,
        top_k: int = 10
    ) -> list[dict]:
        """
        Retorna apenas top 10 tags mais similares por TF-IDF.
        Depois aplica fuzzy apenas nessas 10.
        """
        busca_vector = self.vectorizer.transform([texto_busca])
        scores = (busca_vector * self.tags_vectors.T).toarray()[0]
        top_indices = scores.argsort()[-top_k:][::-1]
        return [self.tags[i] for i in top_indices]
```

**Vantagens:**

- ✅ Reduz de n comparações para top-k (ex: 10)
- ✅ TF-IDF é muito rápido (vetorização)
- ✅ Mantém precisão alta se top-k for suficiente

**Estimativa:**

- Complexidade: O(n × log k) onde k << n
- Ganho: **70-90%** se k = 10

### 5. Paralelização (Prioridade Baixa)

**Ideia:** Usar ThreadPoolExecutor para comparações paralelas.

```python
from concurrent.futures import ThreadPoolExecutor

def vincular_paralelo(
    self,
    modificacoes: list[dict],
    tags: list[dict]
) -> list[dict]:
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(self._vincular_uma, mod, tags)
            for mod in modificacoes
        ]
        return [f.result() for f in futures]
```

**Vantagens:**

- ✅ Usa múltiplos cores CPU
- ✅ Ganho linear com número de cores

**Desvantagens:**

- ⚠️ Overhead de threads
- ⚠️ GIL do Python limita ganho real

**Estimativa:**

- Ganho: 2-3x com 4 cores (depende de I/O vs CPU-bound)

### 6. Substituir RapidFuzz por Algoritmo Aproximado (Prioridade Baixa)

**Ideia:** Usar MinHash ou Locality-Sensitive Hashing (LSH) para similaridade aproximada.

```python
from datasketch import MinHash, MinHashLSH

class FuzzyAproximado:
    def __init__(self):
        self.lsh = MinHashLSH(threshold=0.85, num_perm=128)

    def indexar(self, tags: list[dict]):
        for i, tag in enumerate(tags):
            m = MinHash(num_perm=128)
            for word in tag["texto"].split():
                m.update(word.encode('utf8'))
            self.lsh.insert(f"tag_{i}", m)

    def buscar(self, texto: str) -> list[str]:
        """Retorna IDs de tags similares em O(1) amortizado."""
        m = MinHash(num_perm=128)
        for word in texto.split():
            m.update(word.encode('utf8'))
        return self.lsh.query(m)
```

**Vantagens:**

- ✅ O(1) lookup amortizado
- ✅ Escalável para milhões de documentos

**Desvantagens:**

- ⚠️ Aproximado: pode perder matches
- ⚠️ Requer tuning de threshold

**Estimativa:**

- Complexidade: O(n) (linear!)
- Ganho: **90-95%** mas com perda de precisão

---

## 📊 Plano de Implementação

### Sistema de Comparação Automática (NOVO)

**Infraestrutura criada para comparar múltiplos algoritmos:**

```
versiona-ai/tests/
├── algoritmos/
│   ├── registry.py                    # Sistema de registro automático
│   └── fuzzy/
│       ├── __init__.py                # Auto-registro de algoritmos
│       ├── algoritmo.py               # Baseline (fuzzy atual)
│       ├── algoritmo_otimizado.py     # Com cache + TF-IDF + early exit
│       ├── algoritmo_cache_only.py    # Variante: só cache (futuro)
│       └── algoritmo_tfidf_only.py    # Variante: só TF-IDF (futuro)
├── benchmark_fuzzy_runner.py          # Runner que executa todos e compara
└── test_task_019_comparacao.py        # Testes automatizados A/B
```

**Timeout e Notação de Status:**

Cada algoritmo tem **60 segundos** para completar. Algoritmos que excedem esse limite são marcados como **INVIÁVEIS** (⏱️).

Status possíveis:
- ✅ **OK**: Algoritmo completou com sucesso
- ⏱️ **TIMEOUT**: Excedeu 60s - INVIÁVEL para datasets grandes
- ❌ **ERROR**: Erro de execução (falha real)

**Como adicionar novo algoritmo:**

1. Crie arquivo `versiona-ai/tests/algoritmos/fuzzy/algoritmo_meu.py`
2. Herde de `AlgoritmoVinculacao` (interface comum)
3. Importe no `__init__.py` e registre com `@register_algorithm`
4. Execute: `python versiona-ai/tests/benchmark_fuzzy_runner.py`

**Saída do benchmark:**

```
🏁 Executando 3 algoritmos...
   Dataset: 67 mods × 294 tags

⏱️  Testando 'fuzzy'... ⏱️ TIMEOUT (>60s) - INVIÁVEL
⏱️  Testando 'fuzzy_cache'... ⏱️ TIMEOUT (>60s) - INVIÁVEL
⏱️  Testando 'fuzzy_otimizado'... ✅ 4.82s | 42.1% vinculação

===============================================================================
📊 COMPARAÇÃO DE ALGORITMOS DE FUZZY MATCHING
===============================================================================
Algoritmo            |   Status |  Tempo (s) | Taxa Vinc. |  Comparações | ...
-------------------------------------------------------------------------------
🥇 fuzzy_otimizado   |       ✅ |       4.82 |      42.1% |        1,340 | ...
⏱️ fuzzy             |       ⏱️ |    TIMEOUT |        N/A |          N/A | ...
⏱️ fuzzy_cache       |       ⏱️ |    TIMEOUT |        N/A |          N/A | ...
===============================================================================

🏆 Vencedor: fuzzy_otimizado
   Tempo: 4.82s
   Taxa de vinculação: 42.1%
   Vinculadas: 28/67

⏱️ Algoritmos INVIÁVEIS (timeout >60s):
   - fuzzy
   - fuzzy_cache
```

### Fase 1: Quick Wins (1-2 dias)

1. ✅ **Batch Processing** (commit separado)
   - Implementar `vincular_clausulas_batch()`
   - Testar com dataset real
   - Expectativa: Organização melhor, sem ganho significativo

2. ✅ **Cache de Similaridade** (commit separado)
   - Adicionar `_cache` dict em AlgoritmoFuzzyAvancado
   - Hash baseado em texto normalizado
   - Expectativa: 30-50% ganho se houver repetições

3. ✅ **Early Exit** (commit separado)
   - Adicionar `early_exit_threshold=95.0` em `vincular_clausulas()`
   - Parar loop quando score > 95%
   - Expectativa: 20-40% ganho em casos com bons matches

### Fase 2: Otimização Estrutural (3-5 dias)

4. ✅ **Índice Invertido + TF-IDF** (commit separado)
   - Criar `FuzzyComIndice` class
   - Pre-filtrar top-k=20 candidatas
   - Aplicar fuzzy apenas nas top-k
   - Testar com dataset real
   - Expectativa: **70-90% ganho**, sem perda de precisão
   - **Meta:** Atingir ≥40% taxa vinculação em datasets grandes

### Fase 3: Avançado (Opcional, 5+ dias)

5. ⏳ **Paralelização** (se Fase 2 não for suficiente)
6. ⏳ **MinHash/LSH** (se precisar escalar para 100k+ tags)

---

## ✅ Critérios de Aceitação

### Performance

- [ ] Dataset 67 mods × 294 tags (19,698 comp.) completa em **≤10 segundos**
- [ ] Dataset 100 mods × 500 tags (50,000 comp.) completa em **≤30 segundos**
- [ ] Limiar de auto-desabilitação aumentado para **≥50,000 comparações**

### Precisão

- [ ] Taxa de vinculação em dataset real: **≥40%** (com fuzzy habilitado)
- [ ] Não perder >5% de precisão vs fuzzy completo (baseline)

### Compatibilidade

- [ ] API do `AlgoritmoHibrido` mantida (backward compatible)
- [ ] Parametrização `usar_fuzzy` continua funcionando
- [ ] Estatísticas rastreiam estratégia usada

---

## 🧪 Validação

### Sistema de Testes A/B Automatizados

**Executar comparação:**

```bash
# Comparar todos os algoritmos registrados
python versiona-ai/tests/benchmark_fuzzy_runner.py

# Rodar testes automatizados
pytest versiona-ai/tests/test_task_019_comparacao.py -v

# Com dataset customizado
from benchmark_fuzzy_runner import AlgorithmBenchmarkRunner
runner = AlgorithmBenchmarkRunner()
resultados = runner.compare_all(modificacoes, tags, texto_completo)
runner.print_comparison_table()
```

**Testes incluídos:**

- ✅ `test_todos_algoritmos_executam_sem_erro`: Valida que nenhum algoritmo lança exceção
- ✅ `test_performance_dataset_medio`: Valida critérios de tempo (<30s para 10k comp.)
- ✅ `test_taxa_vinculacao_aceitavel`: Valida taxa de vinculação mínima
- ✅ `test_resultados_consistentes`: Valida que algoritmos não divergem drasticamente (±30%)
- ✅ `test_benchmark_gera_ranking`: Valida ordenação por performance

### Teste de Regressão

```python
# versiona-ai/tests/test_task_019_otimizacao_fuzzy.py

def test_performance_dataset_grande():
    """Valida que fuzzy funciona em datasets grandes."""
    algoritmo = AlgoritmoHibrido(usar_fuzzy=True)

    # Dataset: 100 mods × 500 tags = 50k comparações
    modificacoes = gerar_modificacoes(100)
    tags = gerar_tags(500)

    inicio = time.time()
    resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto_completo)
    tempo = time.time() - inicio

    # Critério 1: Performance
    assert tempo <= 30, f"Tempo {tempo:.1f}s excedeu 30s"

    # Critério 2: Taxa vinculação
    vinculadas = sum(1 for r in resultado if r.get("tag_vinculada"))
    taxa = vinculadas / len(modificacoes) * 100
    assert taxa >= 40, f"Taxa {taxa:.1f}% abaixo de 40%"

def test_precisao_nao_degradou():
    """Valida que otimização não perdeu precisão."""
    algoritmo_completo = AlgoritmoHibrido(usar_fuzzy=True, otimizar=False)
    algoritmo_otimizado = AlgoritmoHibrido(usar_fuzzy=True, otimizar=True)

    # Comparar resultados
    resultado_baseline = algoritmo_completo.vincular_clausulas(...)
    resultado_otimizado = algoritmo_otimizado.vincular_clausulas(...)

    # Aceita até 5% de diferença
    diff = calcular_diferenca_vinculacao(resultado_baseline, resultado_otimizado)
    assert diff <= 5.0, f"Perda de {diff:.1f}% na precisão (limite: 5%)"
```

### Métricas

```python
# Gerar relatório de performance
python versiona-ai/benchmark_fuzzy_otimizado.py

# Saída esperada:
# ================================================================================
# BENCHMARK: Fuzzy Matching Otimizado
# ================================================================================
#
# Dataset Pequeno (10 mods × 50 tags = 500 comp.)
#   Tempo baseline: 1.2s
#   Tempo otimizado: 0.3s
#   Ganho: 75% ✅
#
# Dataset Médio (50 mods × 200 tags = 10k comp.)
#   Tempo baseline: 28.5s
#   Tempo otimizado: 3.2s
#   Ganho: 88% ✅
#
# Dataset Grande (67 mods × 294 tags = 19,698 comp.)
#   Tempo baseline: >60s (timeout)
#   Tempo otimizado: 5.8s
#   Ganho: >90% ✅
#   Taxa vinculação: 42.3% (meta: ≥40%) ✅
```

---

## 📚 Referências

- **Issue:** Task-018 - Taxa vinculação 34.3% (sem fuzzy)
- **Commit:** 3e4674b - Parametrização fuzzy com auto-detecção
- **Doc:** `docs/FUZZY_PARAMETRIZACAO.md`
- **Código:** `versiona-ai/tests/algoritmos/fuzzy/algoritmo.py`

### Bibliotecas Úteis

- **RapidFuzz:** Fuzzy matching atual (CPU-bound)
- **scikit-learn:** TF-IDF vectorization
- **datasketch:** MinHash, LSH para similaridade aproximada
- **faiss:** Similarity search em vetores (Facebook AI)
- **annoy:** Approximate Nearest Neighbors (Spotify)

---

## 💭 Notas

### Trade-offs

**Exatidão vs Performance:**

- Índice TF-IDF: 70-90% ganho, ~0% perda precisão ✅ **Recomendado**
- MinHash/LSH: 90-95% ganho, ~5-10% perda precisão ⚠️ Último recurso

**Complexidade de Implementação:**

- Cache: Trivial (1h) ✅
- Early Exit: Fácil (2h) ✅
- Batch: Fácil (4h) ✅
- TF-IDF: Médio (1-2 dias) ✅ **Melhor custo-benefício**
- Paralelização: Médio (2-3 dias)
- MinHash: Difícil (5+ dias)

### Decisão Recomendada

**Implementar primeiro:**

1. Cache (quick win)
2. Early Exit (quick win)
3. TF-IDF Pre-filtering (maior impacto)

**Expectativa realista:**

- Ganho combinado: **80-90%** redução de tempo
- Dataset 19,698 comp.: 60s → **6-12s** ✅
- Taxa vinculação: 34.3% → **≥40%** ✅

Se isso não for suficiente, considerar paralelização ou MinHash na Fase 3.
