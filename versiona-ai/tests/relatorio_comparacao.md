# Relatório Comparativo de Algoritmos

## 🏆 Ranking Geral

| Posição | Algoritmo | Score |
|---------|-----------|-------|
| 🥇 1 | offset_acumulado | 69.5 |
| 🥈 2 | naive_sequencial | 47.5 |

## 📊 Métricas Detalhadas

### caso_01_insercao_simples

| Algoritmo | Taxa Vinc | Precisão | Recall | F1 | Erro Pos | Tempo | Score |
|-----------|-----------|----------|--------|----|-----------|---------|----|
| offset_acumulado | 100.0% | 100.0% | 100.0% | 100.0 | 0.0 | 0.0ms | 100.0 |
| naive_sequencial | 100.0% | 100.0% | 100.0% | 100.0 | 0.0 | 0.0ms | 100.0 |

### caso_02_alteracao_simples

| Algoritmo | Taxa Vinc | Precisão | Recall | F1 | Erro Pos | Tempo | Score |
|-----------|-----------|----------|--------|----|-----------|---------|----|
| offset_acumulado | 100.0% | 100.0% | 100.0% | 100.0 | 0.0 | 0.0ms | 100.0 |
| naive_sequencial | 0.0% | 0.0% | 0.0% | 0.0 | 0.0 | 0.0ms | 30.0 |

### caso_03_fora_de_tags

| Algoritmo | Taxa Vinc | Precisão | Recall | F1 | Erro Pos | Tempo | Score |
|-----------|-----------|----------|--------|----|-----------|---------|----|
| offset_acumulado | 0.0% | 0.0% | 0.0% | 0.0 | 0.0 | 0.0ms | 30.0 |
| naive_sequencial | 0.0% | 0.0% | 0.0% | 0.0 | 0.0 | 0.0ms | 30.0 |

### caso_04_multiplas_modificacoes_interdependentes

| Algoritmo | Taxa Vinc | Precisão | Recall | F1 | Erro Pos | Tempo | Score |
|-----------|-----------|----------|--------|----|-----------|---------|----|
| offset_acumulado | 33.3% | 100.0% | 33.3% | 50.0 | 30.0 | 0.0ms | 48.0 |
| naive_sequencial | 0.0% | 0.0% | 0.0% | 0.0 | 0.0 | 0.0ms | 30.0 |
