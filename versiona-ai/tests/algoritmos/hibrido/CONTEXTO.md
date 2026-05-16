# Contexto: Algoritmo Híbrido (Combinação de Estratégias)

## 🎯 Objetivo

Implementar algoritmo que **combina** regex, fuzzy e ML para maximizar performance, cobertura e precisão.

**Meta**: Score ≥ 90 pontos | Taxa ≥ 95% | Precisão ≥ 95%

---

## 📋 Problema

Cada algoritmo individual tem pontos fortes e fracos:

| Algoritmo | Pontos Fortes                        | Limitações                         |
| --------- | ------------------------------------ | ---------------------------------- |
| **Regex** | Rápido (10ms), Preciso (95%+)        | Só para estruturados (~20% casos)  |
| **Fuzzy** | Versátil, Boa cobertura (80%+)       | Menos preciso (~85%), Médio (50ms) |
| **ML**    | Semântica, Sinônimos (90%+ precisão) | Lento (150ms), Memória             |

**Oportunidade**: Combinar os 3 para ter:

- ✅ Velocidade do regex (casos simples)
- ✅ Cobertura do fuzzy (maioria dos casos)
- ✅ Inteligência do ML (casos difíceis)

---

## 🔬 Abordagem: Cascata Hierárquica

### Estratégia em Camadas

```
┌─────────────────────────────────────┐
│ CAMADA 1: REGEX (padrões)          │
│ - R$ 10k → R$ 15k                  │
│ - 01/01/2024 → 15/02/2024          │
│ - CPF, CNPJ, IDs                   │
│ ✓ Rápido + Preciso                 │
│ ✗ Apenas ~20-30% dos casos         │
├─────────────────────────────────────┤
│ CAMADA 2: OVERLAP (posição)        │
│ - Modificação em [100-200]         │
│ - Tag em [90-210] → Match          │
│ ✓ Instantâneo + Confiável          │
│ ✗ Precisa posição conhecida        │
├─────────────────────────────────────┤
│ CAMADA 3: FUZZY (similaridade)     │
│ - Texto similar >85%               │
│ - Variações ortográficas           │
│ ✓ Boa cobertura (~80%)             │
│ ✗ Menos preciso que regex          │
├─────────────────────────────────────┤
│ CAMADA 4: ML (semântica) [OPCIONAL]│
│ - Sinônimos, paráfrases            │
│ - Cosine similarity >0.75          │
│ ✓ Alta precisão (~90%)             │
│ ✗ Lento, uso de memória            │
├─────────────────────────────────────┤
│ CAMADA 5: NONE                     │
│ - Nenhuma estratégia funcionou     │
│ - Retorna tag_vinculada: null      │
└─────────────────────────────────────┘
```

### Regras de Decisão

**Para calcular_posicoes():**

1. Detectou padrão regex? → Use regex
2. Não? → Use fuzzy
3. Fallback: Busca exata

**Para vincular_clausulas():**

1. Tem posição E overlap >50%? → Match por posição
2. Não? Detectou padrão? → Use regex structure search
3. Não? Fuzzy >85%? → Match fuzzy
4. Não? ML disponível E cosine >0.75? → Match ML
5. Senão → None

### Coleta de Estatísticas

```python
stats = {
    "regex": 15,      # 15% dos casos
    "overlap": 35,    # 35% dos casos
    "fuzzy": 40,      # 40% dos casos
    "ml": 5,          # 5% dos casos
    "none": 5,        # 5% falharam
}
```

---

## 🛠️ Interface a Implementar

```python
from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao
from algoritmos.regex.algoritmo import AlgoritmoRegex
from algoritmos.fuzzy.algoritmo import AlgoritmoFuzzyAvancado
# from algoritmos.ml.algoritmo import AlgoritmoML  # Opcional

from typing import Optional, Dict

class AlgoritmoHibrido(AlgoritmoVinculacao):
    """
    Combina regex, overlap, fuzzy e ML em cascata.
    """

    def __init__(self):
        # Instanciar sub-algoritmos
        self.regex_alg = AlgoritmoRegex()
        self.fuzzy_alg = AlgoritmoFuzzyAvancado()
        # self.ml_alg = AlgoritmoML()  # Se disponível

        # Thresholds
        self.thresholds = {
            "overlap": 0.5,
            "fuzzy": 0.85,
            "ml": 0.75,
        }

        # Estatísticas de uso
        self.stats = {
            "regex": 0,
            "overlap": 0,
            "fuzzy": 0,
            "ml": 0,
            "none": 0,
        }

    def calcular_posicoes(
        self,
        modificacoes: list[dict],
        texto_completo: str
    ) -> list[dict]:
        """
        Cascata: Regex → Fuzzy → Exato
        """
        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            pos = None
            estrategia = None

            # 1. REGEX (se detectar padrão)
            tipo_padrao = self.regex_alg._detectar_tipo_padrao(texto_busca)
            if tipo_padrao:
                pos = self.regex_alg._buscar_com_regex(
                    texto_busca, texto_completo, tipo_padrao
                )
                if pos:
                    estrategia = "regex"

            # 2. FUZZY (se regex falhou)
            if pos is None:
                resultado_fuzzy = self.fuzzy_alg.calcular_posicoes(
                    [mod], texto_completo
                )
                if resultado_fuzzy and resultado_fuzzy[0].get("posicao_inicio"):
                    pos = (
                        resultado_fuzzy[0]["posicao_inicio"],
                        resultado_fuzzy[0]["posicao_fim"]
                    )
                    estrategia = "fuzzy"

            # 3. EXATO (fallback)
            if pos is None:
                idx = texto_completo.find(texto_busca)
                if idx >= 0:
                    pos = (idx, idx + len(texto_busca))
                    estrategia = "exact"

            # Registrar estatística
            if estrategia:
                self.stats[estrategia] = self.stats.get(estrategia, 0) + 1

            if pos:
                resultado.append({
                    **mod,
                    "posicao_inicio": pos[0],
                    "posicao_fim": pos[1],
                    "estrategia_posicao": estrategia,
                })
            else:
                resultado.append({
                    **mod,
                    "posicao_inicio": None,
                    "posicao_fim": None,
                    "estrategia_posicao": None,
                })

        return resultado

    def vincular_clausulas(
        self,
        modificacoes: list[dict],
        tags: list[dict],
        texto_completo: str
    ) -> list[dict]:
        """
        Cascata: Overlap → Regex → Fuzzy → ML → None
        """
        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")
            tipo_padrao = mod.get("tipo_padrao")

            tag = None
            estrategia = None
            score = 0.0

            # CAMADA 1: OVERLAP (se tem posição)
            if pos_inicio is not None:
                tag_overlap = UtilitariosVinculacao.buscar_tag_por_posicao(
                    pos_inicio, pos_fim, tags
                )
                if tag_overlap:
                    overlap_score = self._calcular_overlap_score(
                        pos_inicio, pos_fim, tag_overlap
                    )
                    if overlap_score >= self.thresholds["overlap"]:
                        tag = tag_overlap
                        estrategia = "overlap"
                        score = overlap_score

            # CAMADA 2: REGEX (se tem padrão estruturado)
            if tag is None and tipo_padrao:
                tag_regex = self.regex_alg._buscar_tag_por_estrutura(
                    texto_busca, tags, tipo_padrao
                )
                if tag_regex:
                    tag = tag_regex
                    estrategia = "regex"
                    score = 1.0

            # CAMADA 3: FUZZY (similaridade textual)
            if tag is None:
                resultado_fuzzy = self.fuzzy_alg.vincular_clausulas(
                    [mod], tags, texto_completo
                )
                if resultado_fuzzy and resultado_fuzzy[0].get("tag_vinculada"):
                    tag_id = resultado_fuzzy[0]["tag_vinculada"]
                    tag = next((t for t in tags if t.get("id") == tag_id), None)
                    if tag:
                        estrategia = "fuzzy"
                        score = 0.85  # Aproximado

            # CAMADA 4: ML (semântica) [OPCIONAL]
            # if tag is None and hasattr(self, 'ml_alg'):
            #     resultado_ml = self.ml_alg.vincular_clausulas(
            #         [mod], tags, texto_completo
            #     )
            #     if resultado_ml and resultado_ml[0].get("tag_vinculada"):
            #         tag_id = resultado_ml[0]["tag_vinculada"]
            #         tag = next((t for t in tags if t.get("id") == tag_id), None)
            #         if tag:
            #             estrategia = "ml"
            #             score = 0.80

            # Registrar estatística
            if estrategia:
                self.stats[estrategia] += 1
            else:
                self.stats["none"] += 1

            resultado.append({
                **mod,
                "tag_vinculada": tag.get("id") if tag else None,
                "estrategia_vinculacao": estrategia,
                "score_vinculacao": score,
            })

        return resultado

    def _calcular_overlap_score(
        self, pos_inicio: int, pos_fim: int, tag: dict
    ) -> float:
        """Calcula score de overlap"""
        tag_inicio = tag.get("posicao_inicio")
        tag_fim = tag.get("posicao_fim")

        if tag_inicio is None or tag_fim is None:
            return 0.0

        return UtilitariosVinculacao.calcular_overlap(
            pos_inicio, pos_fim, tag_inicio, tag_fim
        )

    def get_estatisticas(self) -> Dict[str, int]:
        """Retorna estatísticas de uso de cada estratégia"""
        return self.stats.copy()

    def reset_estatisticas(self):
        """Limpa estatísticas"""
        for key in self.stats:
            self.stats[key] = 0
```

---

## 📦 Dependências

Depende dos algoritmos implementados:

- ✅ `algoritmos.regex` (obrigatório)
- ✅ `algoritmos.fuzzy` (obrigatório)
- 🔹 `algoritmos.ml` (opcional - melhoria incremental)

---

## 🧪 Fixtures Disponíveis

Use todas as 4 fixtures para validar cobertura completa:

1. **caso_01_insercao_simples.json**: Fuzzy deve resolver
2. **caso_02_alteracao_simples.json**: Regex deve detectar valor
3. **caso_03_fora_de_tags.json**: None esperado
4. **caso_04_multiplas_modificacoes_interdependentes.json**: Teste completo

---

## ✅ Critérios de Sucesso

### Métricas Mínimas

- **Score Geral**: ≥ 90 pontos
- **Taxa de Vinculação**: ≥ 95%
- **Precisão**: ≥ 95%
- **Recall**: ≥ 90%
- **F1-Score**: ≥ 0.92

### Distribuição Esperada

```python
stats = {
    "regex": 15-25%,    # Casos estruturados
    "overlap": 30-40%,  # Posições conhecidas
    "fuzzy": 30-45%,    # Maioria
    "ml": 5-10%,        # Casos difíceis
    "none": <5%,        # Falhas
}
```

### Validação Comparativa

```bash
cd versiona-ai

# Comparar todos
uv run python tests/comparar_algoritmos.py \
  --algoritmos producao regex fuzzy hibrido \
  --nivel completo

# Resultado esperado:
# hibrido: 90+ pontos (melhor)
# regex: 80 pontos
# fuzzy: 70 pontos
# producao: 30 pontos
```

---

## 💡 Dicas de Implementação

### 1. Priorização de Estratégias

```python
# Ordem importa! Mais rápido/preciso primeiro
prioridade = [
    "overlap",  # Instantâneo + confiável
    "regex",    # 10ms + 95% precisão
    "fuzzy",    # 50ms + 85% precisão
    "ml",       # 150ms + 90% precisão (opcional)
]
```

### 2. Short-Circuit: Parar na Primeira Match

```python
if tag and score >= threshold_minimo:
    break  # Não precisa testar outras estratégias
```

### 3. Ajuste de Thresholds

```python
# Experimentar diferentes valores
thresholds = {
    "overlap": 0.3,   # Mais permissivo (30%)
    "fuzzy": 0.85,    # Mantém alto
    "ml": 0.75,       # Mais permissivo (75%)
}
```

### 4. Coletar Métricas de Tempo

```python
import time

start = time.time()
# ... executar estratégia
elapsed_ms = (time.time() - start) * 1000

self.stats_tempo[estrategia] = elapsed_ms
```

---

## 📊 Análise de Resultados

### Interpretar Estatísticas

```python
alg = AlgoritmoHibrido()
# ... executar
stats = alg.get_estatisticas()

print(f"Regex: {stats['regex']/sum(stats.values())*100:.1f}%")
print(f"Overlap: {stats['overlap']/sum(stats.values())*100:.1f}%")
print(f"Fuzzy: {stats['fuzzy']/sum(stats.values())*100:.1f}%")
print(f"ML: {stats['ml']/sum(stats.values())*100:.1f}%")
print(f"None: {stats['none']/sum(stats.values())*100:.1f}%")
```

### Identificar Gargalos

| Estatística Alta | Interpretação        | Ação                    |
| ---------------- | -------------------- | ----------------------- |
| `regex` > 30%    | Muitos estruturados  | ✓ Ótimo!                |
| `fuzzy` > 60%    | Poucos estruturados  | Adicionar padrões regex |
| `ml` > 20%       | Casos muito difíceis | Revisar thresholds      |
| `none` > 10%     | Muitas falhas        | Diminuir thresholds     |

---

## 🧪 Testes Específicos

```python
import pytest
from algoritmos.hibrido.algoritmo import AlgoritmoHibrido

def test_estatisticas():
    alg = AlgoritmoHibrido()
    alg.reset_estatisticas()
    stats = alg.get_estatisticas()
    assert all(v == 0 for v in stats.values())

def test_prioriza_regex_para_valores():
    alg = AlgoritmoHibrido()
    # Modificação com valor monetário
    mods = [{
        "tipo": "ALTERACAO",
        "conteudo": {"novo": "R$ 15.000,00"}
    }]
    tags = [{
        "id": "tag1",
        "texto": "Valor do contrato: R$ 15.000,00",
        "posicao_inicio": 0,
        "posicao_fim": 100
    }]

    resultado = alg.vincular_clausulas(mods, tags, "")
    assert resultado[0]["estrategia_vinculacao"] == "regex"

def test_supera_todos_individuais():
    # Score híbrido deve ser maior que qualquer individual
    pass
```

---

## 📈 Melhorias Propostas (Futuras)

1. **Aprendizado de Pesos**: Ajustar thresholds baseado em histórico
2. **Voting Ensemble**: Combinar scores de múltiplas estratégias
3. **Adaptive Strategy**: Escolher estratégia baseado no contexto
4. **Cache Cross-Strategy**: Compartilhar computações entre estratégias
5. **Confidence Score**: Reportar confiança da vinculação

---

## 🔗 Referências

- **Algoritmo Regex**: `tests/algoritmos/regex/CONTEXTO.md`
- **Algoritmo Fuzzy**: `tests/algoritmos/fuzzy/CONTEXTO.md`
- **Algoritmo ML**: `tests/algoritmos/ml/CONTEXTO.md`
- **Framework A/B**: `tests/framework_comparacao.py`

---

## 📝 Relatório Esperado

Ao finalizar, gere relatório:

```markdown
## Resultado Híbrido

### Métricas Globais

- Score Geral: 92.0 pontos (+62 vs baseline)
- Taxa: 96%
- Precisão: 95%
- Recall: 91%
- F1: 0.93

### Distribuição de Estratégias

- Regex: 18% (15 casos)
- Overlap: 35% (29 casos)
- Fuzzy: 38% (32 casos)
- ML: 6% (5 casos)
- None: 3% (2 casos)

### Comparação

| Algoritmo | Score | Melhoria |
| --------- | ----- | -------- |
| Híbrido   | 92.0  | -        |
| Regex     | 80.0  | +12.0    |
| Fuzzy     | 72.0  | +20.0    |
| Baseline  | 30.0  | +62.0    |

### Conclusão

✅ Meta alcançada (≥90 pontos, ≥95% taxa)
✅ Combina pontos fortes de cada estratégia
✅ Tempo aceitável (~60ms médio)
```

---

**Boa implementação! 🚀**
