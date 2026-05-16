# Algoritmos de Vinculação de Cláusulas

Estrutura modular para desenvolvimento e comparação de diferentes estratégias de vinculação de modificações a cláusulas de contratos.

## 📁 Estrutura

```
algoritmos/
├── base.py                    # Interface comum + utilitários
│
├── producao/                  # ⭐ Baseline (código atual)
│   ├── CONTEXTO.md           # Documentação completa
│   ├── algoritmo.py          # Adapter do directus_server.py
│   └── test_producao.py      # Testes específicos
│
├── fuzzy/                     # Estratégia: Fuzzy Matching
│   ├── CONTEXTO.md
│   ├── algoritmo.py
│   └── test_fuzzy.py
│
├── ml/                        # Estratégia: Machine Learning
│   ├── CONTEXTO.md
│   ├── algoritmo.py
│   └── test_ml.py
│
├── regex/                     # Estratégia: Regex Patterns
│   ├── CONTEXTO.md
│   ├── algoritmo.py
│   └── test_regex.py
│
└── hibrido/                   # Estratégia: Híbrido
    ├── CONTEXTO.md
    ├── algoritmo.py
    └── test_hibrido.py
```

## 🎯 Interface Comum

Todos os algoritmos implementam `AlgoritmoVinculacao` (de `framework_comparacao.py`):

```python
from algoritmos.base import AlgoritmoVinculacao

class MeuAlgoritmo(AlgoritmoVinculacao):
    @property
    def nome(self) -> str:
        return "meu_algoritmo"

    @property
    def descricao(self) -> str:
        return "Descrição da estratégia"

    def calcular_posicoes(self, modificacoes: list[dict], texto: str) -> list[dict]:
        """Calcular posicao_inicio/posicao_fim de cada modificação"""
        # Implementação
        return modificacoes

    def vincular_clausulas(
        self, modificacoes: list[dict], tags: list[dict], texto: str
    ) -> list[dict]:
        """Vincular modificações às tags"""
        # Implementação
        return modificacoes
```

## 🛠️ Utilitários Disponíveis

De `base.py`:

```python
from algoritmos.base import UtilitariosVinculacao

# Extrair texto de modificação
texto = UtilitariosVinculacao.extrair_texto_busca(modificacao)

# Normalizar texto
texto_norm = UtilitariosVinculacao.normalizar_texto(texto)

# Calcular sobreposição entre intervalos
overlap = UtilitariosVinculacao.calcular_overlap(
    pos_inicio_a, pos_fim_a,
    pos_inicio_b, pos_fim_b
)  # Retorna 0.0 a 1.0

# Buscar tag por posição
tag = UtilitariosVinculacao.buscar_tag_por_posicao(
    posicao_inicio, posicao_fim, tags
)
```

## 📝 Estrutura de CONTEXTO.md

Cada pasta deve ter `CONTEXTO.md` com:

```markdown
# Algoritmo: [Nome da Estratégia]

## Problema

[Descrição do problema de vinculação de cláusulas]

## Abordagem

[Como esta estratégia resolve o problema]

## Interface

[Explicação dos métodos calcular_posicoes() e vincular_clausulas()]

## Fixtures Disponíveis

- caso_01_insercao_simples.json
- caso_02_alteracao_simples.json
- caso_03_fora_de_tags.json
- caso_04_multiplas_modificacoes_interdependentes.json

## Critérios de Sucesso

- Taxa de vinculação: ≥90%
- Precisão: ≥95%
- F1-Score: ≥90
- Score geral: ≥70

## Exemplos

[Exemplos de uso do algoritmo]

## Dependências

[Bibliotecas necessárias além das padrão]
```

## 🧪 Como Adicionar Nova Estratégia

1. **Criar pasta** em `algoritmos/minha_estrategia/`
2. **Criar `CONTEXTO.md`** seguindo template acima
3. **Criar `algoritmo.py`**:

   ```python
   from algoritmos.base import AlgoritmoVinculacao

   class AlgoritmoMinhaEstrategia(AlgoritmoVinculacao):
       @property
       def nome(self):
           return "minha_estrategia"

       # Implementar métodos...
   ```

4. **Criar `test_minha_estrategia.py`**:

   ```python
   import pytest
   from algoritmo import AlgoritmoMinhaEstrategia

   def test_caso_simples():
       alg = AlgoritmoMinhaEstrategia()
       # Testes...
   ```

5. **Registrar** em `comparar_algoritmos.py`:

   ```python
   from algoritmos.minha_estrategia.algoritmo import AlgoritmoMinhaEstrategia

   ALGORITMOS_DISPONIVEIS = {
       # ...
       "minha_estrategia": AlgoritmoMinhaEstrategia,
   }
   ```

6. **Testar**:

   ```bash
   # Testes unitários
   uv run pytest tests/algoritmos/minha_estrategia/test_*.py -v

   # Comparação A/B
   uv run python tests/comparar_algoritmos.py --algoritmos minha_estrategia
   ```

## 📊 Comparação de Algoritmos

```bash
# Comparar todos
cd versiona-ai
uv run python tests/comparar_algoritmos.py

# Comparar específicos
uv run python tests/comparar_algoritmos.py --algoritmos producao fuzzy regex

# Apenas casos simples
uv run python tests/comparar_algoritmos.py --nivel simples

# Gerar relatório HTML
uv run python tests/comparar_algoritmos.py --report html -o relatorio.html
```

## 🎯 Métricas de Avaliação

Cada algoritmo é avaliado em:

- **Taxa de vinculação**: % de modificações vinculadas
- **Precisão**: % de vinculações corretas
- **Recall**: % de vinculações esperadas encontradas
- **F1-Score**: Média harmônica de precisão/recall
- **Erro de posição**: Diferença média em caracteres
- **Tempo de execução**: Performance em ms
- **Score geral**: Combinação ponderada (0-100)

## 🏆 Melhores Práticas

1. **Isolamento**: Cada algoritmo em sua própria pasta
2. **CONTEXTO.md completo**: Permite execução em contextos zerados
3. **Testes específicos**: Validar comportamento da estratégia
4. **Baseline obrigatório**: `producao/` sempre disponível para comparação
5. **Documentar trade-offs**: Precisão vs velocidade, complexidade vs ROI

## 🔗 Referências

- [Framework de Comparação](../framework_comparacao.py)
- [CLI de Comparação](../comparar_algoritmos.py)
- [Fixtures](../fixtures/)
- [Guia Geral de Testes A/B](../README_TESTES_AB.md)
