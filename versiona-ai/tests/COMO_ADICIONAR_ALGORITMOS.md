# Como Adicionar Novos Algoritmos

## Estrutura

Para adicionar um novo algoritmo de vinculação, siga estes passos:

### 1. Criar a classe do algoritmo

Crie uma nova classe que herda de `AlgoritmoVinculacao`:

```python
# Em test_comparacao_algoritmos.py ou arquivo separado

from framework_comparacao import AlgoritmoVinculacao

class MeuNovoAlgoritmo(AlgoritmoVinculacao):
    @property
    def nome(self) -> str:
        return "meu_algoritmo"

    @property
    def descricao(self) -> str:
        return "Descrição da estratégia do meu algoritmo"

    def calcular_posicoes(
        self, modificacoes: list[dict], texto: str
    ) -> list[dict]:
        """
        Implementar lógica para calcular posicao_inicio e posicao_fim
        de cada modificação no texto.
        """
        # Sua implementação aqui
        return modificacoes

    def vincular_clausulas(
        self, modificacoes: list[dict], tags: list[dict], texto: str
    ) -> list[dict]:
        """
        Implementar lógica para vincular modificações às tags.
        Adicionar campo 'tag_vinculada' (dict ou None) em cada modificação.
        """
        # Sua implementação aqui
        return modificacoes
```

### 2. Registrar no CLI

Adicione o algoritmo em `comparar_algoritmos.py`:

```python
ALGORITMOS_DISPONIVEIS = {
    "naive_sequencial": AlgoritmoNaiveSequencial,
    "offset_acumulado": AlgoritmoComOffsetAcumulado,
    "meu_algoritmo": MeuNovoAlgoritmo,  # ← Adicionar aqui
}
```

### 3. Adicionar aos testes

Inclua em `test_comparacao_algoritmos.py`:

```python
@pytest.fixture
def algoritmos():
    return [
        AlgoritmoNaiveSequencial(),
        AlgoritmoComOffsetAcumulado(),
        MeuNovoAlgoritmo(),  # ← Adicionar aqui
    ]
```

### 4. Testar

```bash
# Testar apenas seu algoritmo
python comparar_algoritmos.py --algoritmos meu_algoritmo

# Comparar com outros
python comparar_algoritmos.py --algoritmos meu_algoritmo naive_sequencial

# Rodar testes automatizados
uv run pytest tests/test_comparacao_algoritmos.py -v
```

## Exemplos de Estratégias

### Estratégia 1: Fuzzy Matching com contexto

```python
from difflib import SequenceMatcher

class AlgoritmoFuzzyComContexto(AlgoritmoVinculacao):
    def calcular_posicoes(self, modificacoes, texto):
        for mod in modificacoes:
            texto_busca = self._extrair_texto_busca(mod)

            # Buscar com fuzzy matching
            melhor_pos, melhor_score = None, 0
            for i in range(len(texto) - len(texto_busca) + 1):
                trecho = texto[i:i + len(texto_busca)]
                score = SequenceMatcher(None, texto_busca, trecho).ratio()
                if score > melhor_score:
                    melhor_score = score
                    melhor_pos = i

            if melhor_score >= 0.8:  # Threshold
                mod["posicao_inicio"] = melhor_pos
                mod["posicao_fim"] = melhor_pos + len(texto_busca)

        return modificacoes
```

### Estratégia 2: Machine Learning

```python
class AlgoritmoML(AlgoritmoVinculacao):
    def __init__(self):
        self.model = self._carregar_modelo()

    def vincular_clausulas(self, modificacoes, tags, texto):
        for mod in modificacoes:
            # Extrair features
            features = self._extrair_features(mod, tags, texto)

            # Prever tag
            tag_id_previsto = self.model.predict([features])[0]

            # Encontrar tag
            mod["tag_vinculada"] = next(
                (t for t in tags if t["id"] == tag_id_previsto),
                None
            )

        return modificacoes
```

### Estratégia 3: Regex Patterns

```python
import re

class AlgoritmoRegexPatterns(AlgoritmoVinculacao):
    def calcular_posicoes(self, modificacoes, texto):
        for mod in modificacoes:
            texto_busca = self._extrair_texto_busca(mod)

            # Criar pattern flexível
            pattern = self._criar_pattern(texto_busca)

            # Buscar com regex
            match = re.search(pattern, texto, re.IGNORECASE)
            if match:
                mod["posicao_inicio"] = match.start()
                mod["posicao_fim"] = match.end()

        return modificacoes

    def _criar_pattern(self, texto):
        # Escapar e permitir variações
        escaped = re.escape(texto)
        # Permitir espaços extras
        flexible = escaped.replace(r"\ ", r"\s+")
        return flexible
```

## Dicas de Implementação

1. **Logging**: Use `print()` para debug durante desenvolvimento
2. **Validação**: Sempre verificar se posicoes são válidas (>= 0)
3. **Edge cases**: Testar com textos vazios, None, etc
4. **Performance**: Usar `time.time()` para medir tempo de execução
5. **Documentação**: Documentar estratégia no docstring

## Métricas de Sucesso

Um bom algoritmo deve ter:

- **Taxa de vinculação**: >90% (encontrar maioria das modificações)
- **Precisão**: >95% (não vincular errado)
- **Recall**: >90% (não perder vinculações esperadas)
- **F1-Score**: >90 (balanço entre precisão e recall)
- **Erro de posição**: <10 chars (posições precisas)
- **Tempo**: <100ms por fixture

## Próximos Passos

1. Implementar algoritmo
2. Testar em casos simples
3. Comparar com baseline (naive_sequencial)
4. Iterar e melhorar
5. Testar em casos complexos
6. Documentar estratégia e resultados
