# Task 017 — Modo Semântico: Agrupamento de Modificações por Cláusula

Status: in-progress
Type: feature
Priority: high
Assignee: Sidarta Veloso

**Data Criação:** 2026-05-29
**Relacionado a:** Task-016

---

## 📋 Problema

Após a correção da Task-016, o sistema detecta **115 modificações** (42% alterações), mas a análise da IA detecta **44 modificações** (79% alterações). A diferença é explicada por:

1. **Granularidade diferente**: Sistema detecta mudanças token-level, IA detecta mudanças conceituais
2. **Modificações triviais**: 32% das modificações do sistema são < 10 chars (pontuação, palavras isoladas)
3. **Fragmentação**: Múltiplas modificações próximas na mesma cláusula são reportadas separadamente

### Exemplo Real

**Sistema** (5 modificações):

```json
[
  { "tipo": "ALTERACAO", "conteudo": "15", "original": "30" },
  { "tipo": "ALTERACAO", "conteudo": "quinze", "original": "trinta" },
  { "tipo": "INSERCAO", "conteudo": "," },
  { "tipo": "ALTERACAO", "conteudo": "RESUMO", "original": "ESTIMADO" },
  { "tipo": "ALTERACAO", "conteudo": "ou", "original": "DO" }
]
```

**IA** (1 modificação):

```json
{
  "tipo": "alteracao",
  "tag": "2.5",
  "conteudo": "O CONTRATO poderá ser suspenso... 15 (quinze) dias...",
  "contexto": "Reduz prazo de suspensão de 30 para 15 dias"
}
```

---

## 🎯 Objetivo

Criar **modo semântico** que agrupa modificações próximas dentro da mesma cláusula em uma única modificação conceitual.

### Critérios de Agrupamento

1. **Proximidade espacial**: Modificações com distância ≤ N caracteres (parametrizável)
2. **Mesma cláusula**: Todas pertencem à mesma tag/cláusula
3. **Mesmo tipo**: Preferencialmente mesmo tipo (ALTERACAO, INSERCAO, REMOCAO)
4. **Filtro de triviais**: Opcionalmente ignorar modificações < M caracteres

---

## 📐 Especificação

### Parâmetros Configuráveis

```python
@dataclass
class SemanticGroupingConfig:
    """Configuração do agrupamento semântico."""

    # Distância máxima entre modificações para agrupar (chars)
    max_distance: int = 100

    # Tamanho mínimo de modificação relevante (chars)
    min_modification_size: int = 10

    # Agrupar apenas modificações da mesma cláusula
    require_same_clause: bool = True

    # Agrupar apenas modificações do mesmo tipo
    require_same_type: bool = False

    # Estratégia de merge de conteúdo
    merge_strategy: str = "concat"  # "concat", "summary", "range"
```

### Algoritmo

```python
def group_modifications_semantically(
    modifications: list[dict],
    config: SemanticGroupingConfig
) -> list[dict]:
    """
    Agrupa modificações próximas em modificações semânticas.

    Passos:
    1. Filtrar triviais (< min_modification_size)
    2. Ordenar por posicao_inicio
    3. Identificar grupos:
       - Modificações consecutivas
       - Distância ≤ max_distance
       - Mesma cláusula (se require_same_clause)
       - Mesmo tipo (se require_same_type)
    4. Merge de cada grupo em modificação única
    5. Retornar modificações agrupadas
    """
    pass
```

### Estratégias de Merge

**1. concat (padrão)**: Concatena conteúdos separados por espaço

```python
{
    "tipo": "ALTERACAO",
    "conteudo": "15 quinze RESUMO ou",
    "conteudo_original": "30 trinta ESTIMADO DO",
    "posicao_inicio": 10000,
    "posicao_fim": 10150,
    "modificacoes_agrupadas": 5
}
```

**2. summary**: Resume mudanças em texto descritivo

```python
{
    "tipo": "ALTERACAO",
    "conteudo": "Parágrafo modificado com 5 alterações",
    "contexto": "15←30, quinze←trinta, RESUMO←ESTIMADO, ou←DO, vírgula adicionada",
    "posicao_inicio": 10000,
    "posicao_fim": 10150,
    "modificacoes_agrupadas": 5
}
```

**3. range**: Indica início e fim do bloco modificado

```python
{
    "tipo": "ALTERACAO_BLOCO",
    "conteudo": "Texto completo do bloco modificado",
    "conteudo_original": "Texto completo do bloco original",
    "posicao_inicio": 10000,
    "posicao_fim": 10150,
    "modificacoes_agrupadas": 5,
    "detalhes": [...]  # Lista de modificações individuais
}
```

---

## 🔧 Implementação

### Arquivos a Modificar

1. **`directus_server.py`**:
   - Adicionar `SemanticGroupingConfig` dataclass
   - Criar método `_group_modifications_semantically()`
   - Integrar no pipeline de `_extrair_modificacoes_do_diff_ast()`
   - Adicionar flag `use_semantic_grouping` no `process_versao()`

2. **`docx_utils.py`**:
   - Mover lógica de agrupamento para módulo comum (se reutilizável)

3. **Testes**:
   - `tests/test_semantic_grouping.py`: Testes unitários
   - `tests/test_regressao_task_017.py`: Testes de regressão com contrato real

### Integração com Teste A/B

Modificar `teste_ab_orquestrador.py` para testar 3 modos:

1. Sistema estruturado (baseline)
2. Sistema estruturado + modo semântico
3. IA pura

---

## 📊 Métricas de Sucesso

| Métrica                 | Sistema Atual | Meta Semântico | IA Referência |
| ----------------------- | ------------- | -------------- | ------------- |
| **Total mods**          | 115           | 40-50          | 44            |
| **ALTERACAO**           | 42%           | ≥70%           | 79%           |
| **Triviais**            | 32%           | ≤5%            | 0%            |
| **Concordância com IA** | ?             | ≥80%           | 100%          |

### Critérios de Aceitação

- ✅ Reduzir modificações de 115 → ~45 (±10%)
- ✅ Aumentar taxa de ALTERACAO para ≥70%
- ✅ Eliminar ≥95% das modificações triviais
- ✅ Concordância com IA ≥80%
- ✅ Tempo de processamento ≤ 120% do baseline

---

## 🧪 Casos de Teste

### Caso 1: Modificações Próximas na Mesma Cláusula

**Entrada**:

```python
[
    {"tipo": "ALTERACAO", "pos": 100, "clausula": "2.5", "size": 2},
    {"tipo": "ALTERACAO", "pos": 110, "clausula": "2.5", "size": 5},
    {"tipo": "ALTERACAO", "pos": 120, "clausula": "2.5", "size": 3}
]
```

**Saída esperada** (config: max_distance=50, require_same_clause=True):

```python
[
    {
        "tipo": "ALTERACAO",
        "posicao_inicio": 100,
        "posicao_fim": 123,
        "clausula": "2.5",
        "modificacoes_agrupadas": 3
    }
]
```

### Caso 2: Modificações Distantes não Agrupam

**Entrada**:

```python
[
    {"tipo": "ALTERACAO", "pos": 100, "clausula": "2.5"},
    {"tipo": "ALTERACAO", "pos": 200, "clausula": "2.5"}  # 100 chars distante
]
```

**Saída esperada** (max_distance=50):

```python
[
    {"tipo": "ALTERACAO", "pos": 100, "clausula": "2.5"},
    {"tipo": "ALTERACAO", "pos": 200, "clausula": "2.5"}
]
```

### Caso 3: Filtro de Triviais

**Entrada**:

```python
[
    {"tipo": "INSERCAO", "pos": 100, "conteudo": ","},  # 1 char - trivial
    {"tipo": "ALTERACAO", "pos": 105, "conteudo": "palavra modificada"}  # 18 chars - relevante
]
```

**Saída esperada** (min_size=10):

```python
[
    {"tipo": "ALTERACAO", "pos": 105, "conteudo": "palavra modificada"}
]
```

---

## 📝 Notas de Implementação

### Performance

- Ordenar modificações por posição: O(n log n)
- Iterar e agrupar: O(n)
- Complexidade total: O(n log n)

### Retrocompatibilidade

- Modo semântico **opcional** (flag `use_semantic_grouping`)
- Default: **False** (manter comportamento atual)
- Adicionar ao endpoint: `/api/process?use_semantic_grouping=true`

### Validação

- Preservar total de caracteres modificados
- Validar que posicoes não se sobreponham
- Garantir que todas cláusulas sejam preservadas

---

## 🔗 Referências

- Task-016: Sistema não detecta alterações dentro de cláusulas
- Teste A/B: `teste_ab_output/teste_ab_completo_20260528_200703.json`
- IA resultado: `teste_ab_output/resultado_ia_8d8e89a8.json`
- Sistema resultado: `teste_ab_output/resultado_sistema_reprocessado_8d8e89a8.json`

---

## 📅 Timeline Estimado

- **Implementação**: 4-6 horas
- **Testes**: 2-3 horas
- **Integração A/B**: 1-2 horas
- **Total**: 7-11 horas

---

## ✅ Checklist de Implementação

- [ ] Criar `SemanticGroupingConfig` dataclass
- [ ] Implementar `_group_modifications_semantically()`
- [ ] Implementar estratégias de merge (concat, summary, range)
- [ ] Integrar no pipeline de processamento
- [ ] Adicionar flag `use_semantic_grouping` ao endpoint
- [ ] Criar testes unitários (`test_semantic_grouping.py`)
- [ ] Criar testes de regressão (`test_regressao_task_017.py`)
- [ ] Atualizar `teste_ab_orquestrador.py` para 3 modos
- [ ] Executar teste A/B completo
- [ ] Validar métricas de sucesso
- [ ] Documentar resultados
- [ ] Atualizar CHANGELOG.md
