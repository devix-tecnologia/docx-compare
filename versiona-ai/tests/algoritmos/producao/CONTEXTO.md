# Algoritmo: Produção (Baseline)

## Problema

Vincular modificações detectadas em contratos às suas respectivas cláusulas (tags) no modelo de contrato. O problema envolve:

1. **Calcular posições**: Encontrar onde cada modificação ocorre no texto (posicao_inicio, posicao_fim)
2. **Vincular a cláusulas**: Determinar qual tag (cláusula) cada modificação afeta

**Desafios:**

- Textos podem ter repetições
- Modificações podem cruzar fronteiras de cláusulas
- INSERCOES só existem no texto modificado
- REMOCOES só existem no texto original
- Modificações interdependentes alteram posições subsequentes (offset acumulado)

## Abordagem

Este é o algoritmo **atualmente em produção** (`directus_server.py`). Serve como **baseline** para comparação com novas estratégias.

### Estratégia Atual

**1. Cálculo de Posições** (`_calcular_posicoes_modificacoes`):

- Para INSERCAO/ALTERACAO: busca `conteudo.get("novo")` no texto modificado
- Para REMOCAO: retorna None (não está no texto modificado)
- Usa `str.find()` para busca simples
- Retorna primeira ocorrência encontrada

**2. Vinculação** (`_vincular_modificacoes_clausulas_novo`):

- Método baseado em **conteúdo** (não offset)
- Para cada modificação:
  - Extrai texto da modificação
  - Busca em cada tag usando fuzzy matching (difflib.SequenceMatcher)
  - Se similaridade ≥85%: vincula à tag
  - Se posição está dentro da tag: vincula
  - Senão: None

**Pontos Fortes:**

- Método de conteúdo é robusto a desalinhamentos
- Fuzzy matching lida com pequenas variações

**Pontos Fracos:**

- Busca simples com `str.find()` pode falhar em textos repetidos
- Não lida bem com modificações interdependentes (offset acumulado)
- Threshold fixo de 85% pode ser muito alto ou muito baixo dependendo do caso
- REMOCOES não são processadas

## Interface

```python
from algoritmos.producao.algoritmo import AlgoritmoProducao

alg = AlgoritmoProducao()

# 1. Calcular posições
modificacoes = [
    {
        "tipo": "INSERCAO",
        "conteudo": {"novo": "texto inserido"}
    }
]
modificacoes_com_pos = alg.calcular_posicoes(modificacoes, texto_completo)
# Resultado: posicao_inicio e posicao_fim preenchidos

# 2. Vincular a tags
tags = [
    {
        "id": "tag_1",
        "nome": "Cláusula 1",
        "posicao_inicio": 100,
        "posicao_fim": 500,
        "texto": "texto da cláusula..."
    }
]
modificacoes_vinculadas = alg.vincular_clausulas(
    modificacoes_com_pos, tags, texto_completo
)
# Resultado: campo "tag_vinculada" adicionado (dict ou None)
```

## Fixtures Disponíveis

### Caso 01: Inserção Simples

- **Arquivo**: `fixtures/caso_01_insercao_simples.json`
- **Descrição**: Uma única inserção dentro de uma tag
- **Expectativa**: Taxa 100%, Precisão 100%

### Caso 02: Alteração Simples

- **Arquivo**: `fixtures/caso_02_alteracao_simples.json`
- **Descrição**: Alteração de valor numérico
- **Expectativa**: Taxa 100%, Precisão 100%

### Caso 03: Fora de Tags

- **Arquivo**: `fixtures/caso_03_fora_de_tags.json`
- **Descrição**: Modificação em área sem tags (caso negativo)
- **Expectativa**: Taxa 0%, mas isso é correto (sem falsos positivos)

### Caso 04: Múltiplas Interdependentes

- **Arquivo**: `fixtures/caso_04_multiplas_modificacoes_interdependentes.json`
- **Descrição**: 3 modificações sequenciais com offset acumulado
- **Expectativa**: Algoritmo atual pode falhar aqui (busca simples)

## Critérios de Sucesso

Como este é o **baseline**, não há critério de "passar/falhar". Os critérios são:

- **Documentar desempenho atual**: Estabelecer linha de base
- **Identificar limitações**: Onde o algoritmo atual falha
- **Benchmark para novos algoritmos**: Score a superar

### Métricas Esperadas (estimativa)

- Taxa de vinculação: 60-80% (depende das fixtures)
- Precisão: 80-90% (pode vincular errado em casos ambíguos)
- F1-Score: 70-85
- Score geral: 65-75

**Novos algoritmos devem superar estes números!**

## Código de Produção

O algoritmo atual está implementado em:

**Arquivo**: `versiona-ai/directus_server.py`

**Métodos relevantes:**

- `_calcular_posicoes_modificacoes(modificacoes, texto_modificado)` - Linha ~2520
- `_vincular_modificacoes_clausulas_novo(modificacoes, tags, texto_com_tags, texto_original)` - Linha ~1678

**Dependências:**

- `difflib.SequenceMatcher` - Para fuzzy matching
- `repositorio.DirectusRepository` - Para acesso ao Directus

## Exemplo de Uso

```python
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from algoritmos.producao.algoritmo import AlgoritmoProducao
from framework_comparacao import ComparadorAlgoritmos

# Criar instância
alg = AlgoritmoProducao()

# Carregar fixtures
comparador = ComparadorAlgoritmos()
fixtures = comparador.carregar_fixtures(nivel="simples")

# Avaliar
for fixture in fixtures:
    metricas = comparador.avaliar(alg, fixture)
    print(f"{fixture.id}: {metricas}")
```

## Testes

```bash
# Rodar testes específicos
cd versiona-ai
uv run pytest tests/algoritmos/producao/test_producao.py -v

# Comparar com outros algoritmos
uv run python tests/comparar_algoritmos.py --algoritmos producao
```

## Melhorias Propostas

Baseado nas limitações identificadas, novos algoritmos podem tentar:

1. **Fuzzy matching mais sofisticado**: Usar embeddings (sentence-transformers) ao invés de difflib
2. **Regex patterns**: Para casos com padrões conhecidos (valores, datas)
3. **Offset acumulado**: Aplicar modificações sequencialmente ajustando posições
4. **Contexto ampliado**: Considerar parágrafo/seção ao redor da modificação
5. **Machine Learning**: Treinar modelo com features (overlap, distância, similaridade)
6. **Híbrido**: Combinar múltiplas estratégias com pesos ajustáveis

## Notas de Implementação

O adapter (`algoritmo.py`) traduz a interface do código de produção para a interface `AlgoritmoVinculacao`:

- `calcular_posicoes()` chama `_calcular_posicoes_modificacoes()` do código original
- `vincular_clausulas()` chama `_vincular_modificacoes_clausulas_novo()` do código original
- Necessário importar métodos de `directus_server.py` (pode ser via import relativo ou cópia)

## Status

✅ **Implementado** - Este é o código atual em produção
📊 **Métricas estabelecidas** - Baseline para comparação
🎯 **Objetivo**: Ser superado por novos algoritmos
