# Matching Strategies

Este diretorio concentra as estrategias de _matching_ usadas para localizar tags e clausulas da versao anterior que correspondem ao texto modificado na versao nova do documento. Cada implementacao parte da interface `MatchingStrategy` definida em `base.py`, que padroniza dois pontos de entrada:

- `find_best_match(needle, haystack, threshold)` para procurar um trecho diretamente.
- `find_with_context(needle, context_before, context_after, haystack, threshold)` para procurar usando o trecho e seu contexto anterior/posterior.

## Implementacoes atuais

- `DifflibMatcher` (`difflib_matcher.py`): usa apenas bibliotecas padrao (`difflib.SequenceMatcher`).
- `RapidFuzzMatcher` (`rapidfuzz_matcher.py`): usa a biblioteca opcional `rapidfuzz`, bem mais rapida em _fuzzy matching_.

Ambas retornam um `MatchResult` indicando se o texto foi encontrado, a posicao, a similaridade (0 a 1) e qual metodo interno chegou ao resultado (ex.: `*_exact`, `*_fuzzy`, `*_context_exact`).

## Como adicionar uma nova estrategia

1. Crie um novo arquivo `nome_matcher.py` nesta pasta.
2. Importe `MatchingStrategy` e `MatchResult` de `.base`.
3. Implemente uma classe que herde de `MatchingStrategy`, sobrescrevendo:
   - a propriedade `name` (string curta que identifica a estrategia),
   - o metodo `find_best_match`,
   - o metodo `find_with_context`.
4. Caso a estrategia dependa de pacotes extras, trate `ImportError` no inicio do arquivo e explique a instalacao.
5. Exporte a classe em `__init__.py` (e opcionalmente em qualquer fabrica que use estes matchers).
6. Atualize os testes em `tests/test_matching_strategies.py` para incluir a nova opcao na _fixture_ parametrizada.

## "Rinha" de matchers

Para comparar as estrategias existentes — a famosa rinha — execute os testes dedicados:

```sh
uv run pytest tests/test_matching_strategies.py -vv
```

O arquivo cobre casos exatos, _fuzzy_, com contexto e cenarios reais; adicione novos cenarios conforme evoluir a estrategia. Ao final da execucao o pytest imprime um placar similar a:

```
------------------- Rinha de Matching --------------------
rapidfuzz  | total     2.41 ms | chamadas  14 | media   0.17 ms
   best_match:  12 calls /     2.31 ms
   context   :   2 calls /     0.09 ms
difflib    | total     7.00 ms | chamadas  14 | media   0.50 ms
   best_match:  12 calls /     6.93 ms
   context   :   2 calls /     0.08 ms
Campea da rodada: rapidfuzz
```

Para rodar toda a suite (incluindo a rinha), use `uv run pytest tests/ -v`.
