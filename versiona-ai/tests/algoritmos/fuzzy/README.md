# Sistema de Comparação de Algoritmos de Fuzzy Matching

Sistema extensível para comparar diferentes implementações de algoritmos de vinculação de cláusulas.

## 📐 Arquitetura

### Interface Comum

Todos os algoritmos devem herdar de `AlgoritmoVinculacao` (em `framework_comparacao.py`):

```python
from framework_comparacao import AlgoritmoVinculacao

class MeuAlgoritmo(AlgoritmoVinculacao):
    @property
    def nome(self) -> str:
        return "meu_algo"

    @property
    def descricao(self) -> str:
        return "Descrição breve da estratégia"

    def calcular_posicoes(self, modificacoes, texto):
        # Calcula posicao_inicio/posicao_fim
        pass

    def vincular_clausulas(self, modificacoes, tags, texto):
        # Retorna lista de dicts com 'tag_vinculada'
        pass
```

### Sistema de Registro

Algoritmos são descobertos automaticamente via decorator `@register_algorithm`:

```python
# Em algoritmos/fuzzy/__init__.py
from algoritmos.registry import register_algorithm
from .meu_algoritmo import MeuAlgoritmo

# Registra automaticamente
MeuAlgoritmoRegistrado = register_algorithm(MeuAlgoritmo)
```

### Benchmark Runner

Executa todos os algoritmos registrados e compara métricas:

```bash
python versiona-ai/tests/benchmark_fuzzy_runner.py
```

**Métricas coletadas:**

- ⏱️ Tempo de execução
- 📊 Taxa de vinculação (% modificações vinculadas)
- 🔢 Número de comparações realizadas
- 💾 Cache hit rate (se disponível)
- 🚀 Early exits (se disponível)

## 🚀 Adicionando Novo Algoritmo

### Passo 1: Criar Arquivo

Crie `versiona-ai/tests/algoritmos/fuzzy/algoritmo_meu.py`:

```python
"""
Meu Algoritmo - Descrição da estratégia
"""

from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao

class MeuAlgoritmo(AlgoritmoVinculacao):
    @property
    def nome(self) -> str:
        return "meu_algo"  # Nome único

    @property
    def descricao(self) -> str:
        return "Estratégia X com otimização Y"

    def __init__(self, parametro1=10, parametro2=True):
        self.parametro1 = parametro1
        self.parametro2 = parametro2

        # Stats opcionais para benchmark
        self._stats = {
            "total_comparisons": 0,
            "cache_hits": 0,
            "early_exits": 0,
        }

    def calcular_posicoes(self, modificacoes, texto_completo):
        """Implementa lógica de cálculo de posições."""
        resultado = []

        for mod in modificacoes:
            # Sua lógica aqui
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)

            # Calcula posição
            pos_inicio = self._buscar_posicao(texto_busca, texto_completo)
            pos_fim = pos_inicio + len(texto_busca)

            resultado.append({
                **mod,
                "posicao_inicio": pos_inicio,
                "posicao_fim": pos_fim,
            })

        return resultado

    def vincular_clausulas(self, modificacoes, tags, texto_completo):
        """Implementa lógica de vinculação."""
        # Primeiro calcula posições
        mods_com_posicao = self.calcular_posicoes(modificacoes, texto_completo)

        resultado = []

        for mod in mods_com_posicao:
            # Busca melhor tag
            melhor_tag = self._buscar_melhor_tag(mod, tags)

            resultado.append({
                **mod,
                "tag_vinculada": melhor_tag,
            })

        return resultado

    def _buscar_posicao(self, texto, texto_completo):
        """Método auxiliar."""
        # Sua implementação
        return texto_completo.find(texto)

    def _buscar_melhor_tag(self, mod, tags):
        """Método auxiliar."""
        # Sua implementação
        pos_inicio = mod.get("posicao_inicio")

        if pos_inicio is None:
            return None

        # Usa utilit ário comum
        return UtilitariosVinculacao.buscar_tag_por_posicao(
            pos_inicio, mod.get("posicao_fim"), tags
        )
```

### Passo 2: Registrar Algoritmo

Atualize `versiona-ai/tests/algoritmos/fuzzy/__init__.py`:

```python
# Import e registro
from .meu_algoritmo import MeuAlgoritmo

# Registra automaticamente
MeuAlgoritmoRegistrado = register_algorithm(MeuAlgoritmo)
```

### Passo 3: Executar Benchmark

```bash
cd /Users/sidarta/repositorios/docx-compare

# Executa comparação
python versiona-ai/tests/benchmark_fuzzy_runner.py

# Ou com pytest
pytest versiona-ai/tests/test_task_019_comparacao.py -v -s
```

**Saída esperada:**

```
📦 Importando algoritmos...
   ✅ Algoritmos importados com sucesso

🔨 Criando dataset de teste...
   50 modificações
   200 tags
   Complexidade: 10,000 comparações

🏁 Executando 3 algoritmos...
   Dataset: 50 mods × 200 tags

⏱️  Testando 'fuzzy'... ✅ 12.34s | 38.0% vinculação
⏱️  Testando 'fuzzy_otimizado'... ✅ 2.15s | 42.0% vinculação
⏱️  Testando 'meu_algo'... ✅ 3.45s | 40.5% vinculação

====================================================================
📊 COMPARAÇÃO DE ALGORITMOS DE FUZZY MATCHING
====================================================================
Algoritmo            |  Tempo (s) | Taxa Vinc. |  Comparações | ...
--------------------------------------------------------------------
🥇 fuzzy_otimizado   |       2.15 |      42.0% |        1,340 | ...
🥈 meu_algo          |       3.45 |      40.5% |        3,200 | ...
🥉 fuzzy             |      12.34 |      38.0% |       10,000 | ...
====================================================================

🏆 Vencedor: fuzzy_otimizado
   Tempo: 2.15s
   Taxa de vinculação: 42.0%
   Vinculadas: 21/50
```

## 📊 Métricas e Estatísticas

### Estatísticas Opcionais

Para métricas avançadas no benchmark, adicione atributo `_stats` ou método `get_stats()`:

```python
class MeuAlgoritmo(AlgoritmoVinculacao):
    def __init__(self):
        self._stats = {
            "total_comparisons": 0,      # Total de comparações fuzzy
            "comparisons_saved": 0,       # Economizadas por otimização
            "cache_hits": 0,              # Hits de cache
            "cache_misses": 0,            # Misses de cache
            "early_exits": 0,             # Saídas antecipadas
            "indexing_time": 0.0,         # Tempo de indexação
        }

    def vincular_clausulas(self, modificacoes, tags, texto):
        # Atualiza stats durante execução
        self._stats["total_comparisons"] += 1

        # ... sua lógica

        return resultado

    # OU implementar método
    def get_stats(self) -> dict:
        return {
            "total_comparisons": self.total_comparisons,
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) * 100,
        }
```

O benchmark runner extrai automaticamente essas métricas para o relatório.

## 🧪 Testes Automatizados

Todos os algoritmos registrados são testados automaticamente via `test_task_019_comparacao.py`:

```bash
pytest versiona-ai/tests/test_task_019_comparacao.py -v
```

**Testes incluem:**

- ✅ Execução sem erros
- ✅ Performance aceitável (<30s para 10k comparações)
- ✅ Taxa de vinculação > 0%
- ✅ Consistência entre algoritmos (±30%)
- ✅ Ordenação correta do ranking

## 🎯 Casos de Uso

### Comparação A/B de Otimizações

```python
# Teste: Cache ajuda?
# 1. Crie algoritmo_com_cache.py
# 2. Crie algoritmo_sem_cache.py
# 3. Execute benchmark
# 4. Compare cache_hit_rate e tempo
```

### Encontrar Melhor Threshold

```python
# Crie variantes com thresholds diferentes
class FuzzyThreshold70(AlgoritmoVinculacao):
    nome = "fuzzy_t70"
    threshold = 70.0

class FuzzyThreshold80(AlgoritmoVinculacao):
    nome = "fuzzy_t80"
    threshold = 80.0

# Benchmark compara automaticamente
```

### Validar Hipótese de Otimização

```python
# Hipótese: TF-IDF pré-filtering reduz tempo em 80%
# 1. Crie fuzzy_com_tfidf.py
# 2. Mantenha fuzzy.py (baseline)
# 3. Execute benchmark
# 4. Valide: tempo_otimizado < tempo_baseline * 0.2
```

## 📁 Estrutura de Arquivos

```
versiona-ai/tests/
├── algoritmos/
│   ├── base.py                    # Interface AlgoritmoVinculacao
│   ├── registry.py                # Sistema de registro
│   │
│   ├── fuzzy/                     # Algoritmos de fuzzy matching
│   │   ├── __init__.py            # Auto-registro
│   │   ├── README.md              # Esta documentação
│   │   ├── algoritmo.py           # Baseline
│   │   ├── algoritmo_otimizado.py # Com otimizações
│   │   └── ...                    # Seus algoritmos
│   │
│   ├── regex/                     # Algoritmos baseados em regex (futuro)
│   └── ml/                        # Algoritmos ML (futuro)
│
├── framework_comparacao.py        # Framework base
├── benchmark_fuzzy_runner.py      # Runner principal
├── test_task_019_comparacao.py    # Testes A/B
└── results/                       # JSONs exportados
    └── benchmark_results.json
```

## 💡 Dicas

### Performance

- ⏱️ Implemente métricas de tempo interno para identificar gargalos
- 📊 Use `_stats` para rastrear comparações economizadas
- 🔬 Profile com cProfile para otimizações micro

### Comparação Justa

- 📏 Use mesmos datasets para todos os algoritmos
- 🎲 Aleatorize ordem de execução para evitar viés de cache
- 🔄 Execute múltiplas iterações e calcule média

### Debug

- 🐛 Teste algoritmo isoladamente antes de registrar
- 📝 Adicione logging detalhado durante desenvolvimento
- ✅ Valide que retorna formato correto (lista de dicts com `tag_vinculada`)

## 🔗 Referências

- **Task 019**: [task-019-otimizar-fuzzy-matching-grandes-datasets.md](../../../TASKS/task-019-otimizar-fuzzy-matching-grandes-datasets.md)
- **Framework**: [framework_comparacao.py](../framework_comparacao.py)
- **Registry**: [registry.py](../registry.py)
- **Benchmark**: [benchmark_fuzzy_runner.py](../benchmark_fuzzy_runner.py)

---

**Última atualização**: 2026-06-03
**Autor**: Sistema de Otimização Contínua
