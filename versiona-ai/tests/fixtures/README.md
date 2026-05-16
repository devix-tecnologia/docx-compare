# Fixtures para Teste A/B de Vinculação de Cláusulas

## Objetivo

Estrutura de fixtures para testar e comparar diferentes algoritmos de vinculação de modificações a cláusulas.

## Estrutura de uma Fixture

Cada fixture contém:

```python
{
    "id": "caso_01_insercao_simples",
    "descricao": "Inserção única dentro de uma cláusula",
    "nivel_complexidade": "simples",  # simples, medio, complexo

    # Entrada
    "documento": {
        "texto_completo": "...",  # Texto do documento (pode ser path)
        "tags": [
            {
                "id": "tag_1",
                "nome": "2",
                "posicao_inicio": 100,
                "posicao_fim": 200,
                "texto": "..."
            }
        ]
    },

    # Modificações detectadas (entrada para algoritmo)
    "modificacoes": [
        {
            "tipo": "INSERCAO",
            "conteudo": {"novo": "texto inserido"},
            # Posição pode estar None inicialmente
            "posicao_inicio": None,
            "posicao_fim": None
        }
    ],

    # Ground Truth (saída esperada)
    "vinculacoes_esperadas": [
        {
            "modificacao_index": 0,
            "tag_id": "tag_1",
            "confianca_minima": 0.8,
            "posicao_inicio_esperada": 150,
            "posicao_fim_esperada": 165
        }
    ],

    # Métricas de avaliação
    "metricas_objetivo": {
        "taxa_vinculacao_minima": 100.0,  # %
        "precisao_posicao_chars": 5  # Tolerância em caracteres
    }
}
```

## Casos de Teste

### Nível 1: Simples (validação básica)

- `caso_01_insercao_simples.json`: Uma inserção dentro de uma tag
- `caso_02_remocao_simples.json`: Uma remoção dentro de uma tag
- `caso_03_alteracao_simples.json`: Uma alteração dentro de uma tag
- `caso_04_fora_de_tags.json`: Modificação fora de qualquer tag (deve retornar null)

### Nível 2: Médio (casos reais comuns)

- `caso_05_multiplas_modificacoes.json`: 3-5 modificações em diferentes tags
- `caso_06_modificacoes_adjacentes.json`: Modificações próximas que afetam posições
- `caso_07_tags_sobrepostas.json`: Tags aninhadas ou sobrepostas

### Nível 3: Complexo (casos reais difíceis)

- `caso_08_versao_2573b998.json`: Caso real atual com 100 tags
- `caso_09_documento_longo.json`: Documento com 1000+ tags

## Framework de Comparação

```python
class AlgoritmoVinculacao(ABC):
    @abstractmethod
    def calcular_posicoes(self, modificacoes, texto) -> list[dict]:
        pass

    @abstractmethod
    def vincular_clausulas(self, modificacoes, tags, texto) -> list[dict]:
        pass

class ComparadorAlgoritmos:
    def avaliar(self, algoritmo, fixture) -> Metricas:
        """
        Métricas:
        - Taxa de vinculação: % de modificações vinculadas
        - Precisão: % de vinculações corretas
        - Recall: % de vinculações esperadas encontradas
        - F1-Score: Média harmônica de precisão e recall
        - Erro de posição: Média da diferença em caracteres
        """
        pass
```

## Uso

```bash
# Rodar todos os casos
uv run pytest tests/test_algoritmos_vinculacao.py -v

# Comparar algoritmos específicos
uv run python tests/comparar_algoritmos.py \
  --algoritmos ast_original,ast_melhorado,fuzzy_matching \
  --fixtures caso_01,caso_02,caso_08

# Gerar relatório
uv run python tests/comparar_algoritmos.py --report html
```
