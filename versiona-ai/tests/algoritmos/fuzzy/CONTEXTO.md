# Contexto: Algoritmo Fuzzy Matching Avançado

## 🎯 Objetivo

Implementar algoritmo de vinculação baseado em **fuzzy matching avançado** que supere o baseline (30.0 pontos) usando múltiplas métricas de similaridade textual.

**Meta**: Score ≥ 70 pontos | Taxa ≥ 80% | Precisão ≥ 85%

---

## 📋 Problema

O algoritmo baseline (produção) usa apenas:

- `str.find()` para busca exata
- `difflib.SequenceMatcher` com threshold fixo 85%
- Overlap de posições como fallback

**Limitações identificadas:**

- ❌ Threshold fixo não se adapta ao contexto
- ❌ SequenceMatcher sozinho é limitado
- ❌ Não lida bem com variações ortográficas
- ❌ Fraco para sinônimos parciais
- ❌ Taxa de vinculação: 0% nas fixtures de teste

**Oportunidade**: Usar múltiplas métricas de similaridade e threshold adaptativo.

---

## 🔬 Abordagem: Fuzzy Matching Avançado

### Estratégia

Use **múltiplas métricas de similaridade** e escolha a melhor:

1. **RapidFuzz** (mais rápido que difflib):
   - `fuzz.ratio()` - Similar ao SequenceMatcher
   - `fuzz.partial_ratio()` - Match de substring
   - `fuzz.token_sort_ratio()` - Ignora ordem de palavras
   - `fuzz.token_set_ratio()` - Ignora palavras duplicadas

2. **Normalização Avançada**:
   - Lowercase
   - Remover acentos (opcional)
   - Remover pontuação extra
   - Normalizar espaços
   - Normalizar números (R$ 10.000 → 10000)

3. **Threshold Dinâmico**:
   - Textos curtos (< 20 chars): threshold 90%
   - Textos médios (20-100 chars): threshold 85%
   - Textos longos (> 100 chars): threshold 80%

4. **Score Composto**:
   ```python
   score_final = max(
       fuzz.ratio(texto1, texto2),
       fuzz.partial_ratio(texto1, texto2),
       fuzz.token_set_ratio(texto1, texto2)
   )
   ```

### Vantagens

- ✅ Robusto a variações ortográficas
- ✅ Lida com ordem de palavras diferente
- ✅ Detecta substrings parciais
- ✅ Mais rápido que difflib (implementação em C)
- ✅ Threshold adaptativo ao contexto

### Casos de Uso Ideais

- Textos com pequenas variações
- Alterações de formato mantendo conteúdo
- Erros de digitação ou ortografia
- Ordem de palavras diferente

---

## 🛠️ Interface a Implementar

```python
from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao
from rapidfuzz import fuzz
from typing import Optional

class AlgoritmoFuzzyAvancado(AlgoritmoVinculacao):
    """
    Algoritmo de vinculação usando fuzzy matching avançado com RapidFuzz.
    """

    def __init__(self):
        # Configuração de thresholds dinâmicos
        self.thresholds = {
            "curto": 0.90,   # < 20 chars
            "medio": 0.85,   # 20-100 chars
            "longo": 0.80,   # > 100 chars
        }

    def calcular_posicoes(
        self,
        modificacoes: list[dict],
        texto_completo: str
    ) -> list[dict]:
        """
        Calcula posições usando busca fuzzy.

        Para cada modificação:
        1. Extrai texto a buscar
        2. Normaliza texto
        3. Busca melhor match no texto completo usando fuzzy
        4. Retorna posição do melhor match
        """
        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            pos = self._buscar_fuzzy_no_texto(texto_busca, texto_completo)

            if pos:
                resultado.append({
                    **mod,
                    "posicao_inicio": pos[0],
                    "posicao_fim": pos[1],
                })
            else:
                resultado.append({
                    **mod,
                    "posicao_inicio": None,
                    "posicao_fim": None,
                })

        return resultado

    def vincular_clausulas(
        self,
        modificacoes: list[dict],
        tags: list[dict],
        texto_completo: str
    ) -> list[dict]:
        """
        Vincula modificações a tags usando fuzzy matching.

        Para cada modificação:
        1. Se tem posição → tenta overlap primeiro
        2. Se não achou → fuzzy matching com texto da tag
        3. Usa threshold dinâmico baseado no tamanho do texto
        """
        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")

            tag = None

            # 1. Tentar overlap se tem posição
            if pos_inicio is not None:
                tag = UtilitariosVinculacao.buscar_tag_por_posicao(
                    pos_inicio, pos_fim, tags
                )

            # 2. Fuzzy matching se não achou
            if tag is None:
                tag = self._buscar_melhor_tag_fuzzy(texto_busca, tags)

            resultado.append({
                **mod,
                "tag_vinculada": tag.get("id") if tag else None
            })

        return resultado

    def _buscar_fuzzy_no_texto(
        self,
        busca: str,
        texto: str
    ) -> Optional[tuple[int, int]]:
        """
        Busca posição usando fuzzy matching no texto completo.
        Retorna (inicio, fim) ou None.
        """
        # Implementar busca fuzzy com sliding window
        pass

    def _buscar_melhor_tag_fuzzy(
        self,
        texto_modificacao: str,
        tags: list[dict]
    ) -> Optional[dict]:
        """
        Busca melhor tag usando múltiplas métricas fuzzy.
        Retorna tag com maior score ou None.
        """
        # Implementar busca com RapidFuzz
        pass

    def _obter_threshold(self, texto: str) -> float:
        """Retorna threshold adequado ao tamanho do texto"""
        tam = len(texto)
        if tam < 20:
            return self.thresholds["curto"]
        elif tam < 100:
            return self.thresholds["medio"]
        else:
            return self.thresholds["longo"]

    def _normalizar_para_fuzzy(self, texto: str) -> str:
        """Normalização avançada para fuzzy matching"""
        # Implementar normalização
        pass
```

---

## 📦 Dependências

```toml
# Já disponível em pyproject.toml
dependencies = [
    "rapidfuzz>=3.14.1",
]
```

Instalar (se necessário):

```bash
cd versiona-ai
uv sync
```

---

## 🧪 Fixtures Disponíveis

Execute testes com estas fixtures (em `tests/fixtures/`):

### 1. caso_01_insercao_simples.json

- 1 INSERCAO de 50 caracteres
- 3 tags disponíveis
- Taxa esperada: 100%

### 2. caso_02_alteracao_simples.json

- 1 ALTERACAO de valor (R$ 10k → R$ 15k)
- 2 tags disponíveis
- Taxa esperada: 100%

### 3. caso_03_fora_de_tags.json

- 1 INSERCAO fora de qualquer tag
- Deve retornar None (caso negativo)
- Taxa esperada: 0%

### 4. caso_04_multiplas_modificacoes_interdependentes.json

- 3 modificações com offset acumulado
- Testa cálculo de posições complexo
- Taxa esperada: 100%

---

## ✅ Critérios de Sucesso

### Métricas Mínimas

- **Score Geral**: ≥ 70 pontos
- **Taxa de Vinculação**: ≥ 80%
- **Precisão**: ≥ 85%
- **Recall**: ≥ 75%
- **F1-Score**: ≥ 0.80
- **Tempo**: < 100ms por modificação

### Validação

```bash
# Executar testes
cd versiona-ai
uv run pytest tests/algoritmos/fuzzy/test_fuzzy.py -v

# Comparar com baseline
uv run python tests/comparar_algoritmos.py --algoritmos producao fuzzy --nivel simples
```

### Resultado Esperado

```
🏆 RANKING GERAL:
🥇 1. fuzzy: 70.0+ pontos
🥈 2. producao: 30.0 pontos

Melhoria: +40 pontos (+133%)
```

---

## 📚 Código de Referência

### Baseline (directus_server.py)

```python
# Linha ~2520 - Vinculação com fuzzy matching simples
from difflib import SequenceMatcher

def _vincular_modificacoes_clausulas_novo(
    modificacoes, tags_disponiveis, texto_modificado
):
    resultado = []
    for mod in modificacoes:
        texto_busca = mod.get("conteudo", {}).get("novo", "")
        melhor_tag = None
        melhor_score = 0.0

        for tag in tags_disponiveis:
            tag_texto = tag.get("texto", "")
            similarity = SequenceMatcher(None, texto_busca, tag_texto).ratio()

            if similarity > melhor_score and similarity >= 0.85:
                melhor_tag = tag
                melhor_score = similarity

        resultado.append({
            **mod,
            "tag_vinculada": melhor_tag.get("id") if melhor_tag else None
        })

    return resultado
```

### Utilitários Disponíveis (base.py)

```python
from algoritmos.base import UtilitariosVinculacao

# Extrair texto de modificação
texto = UtilitariosVinculacao.extrair_texto_busca(mod)

# Normalizar texto
texto_norm = UtilitariosVinculacao.normalizar_texto(texto)

# Calcular overlap entre intervalos
overlap = UtilitariosVinculacao.calcular_overlap(
    pos_inicio1, pos_fim1, pos_inicio2, pos_fim2
)

# Buscar tag por posição
tag = UtilitariosVinculacao.buscar_tag_por_posicao(
    pos_inicio, pos_fim, tags
)
```

---

## 💡 Dicas de Implementação

### 1. Sliding Window para Busca

```python
def _buscar_fuzzy_no_texto(self, busca: str, texto: str):
    tamanho_busca = len(busca)
    tamanho_janela = tamanho_busca + 50  # Margem
    threshold = self._obter_threshold(busca)

    melhor_pos = None
    melhor_score = 0.0

    # Deslizar janela pelo texto
    for i in range(0, len(texto) - tamanho_janela + 1, 10):  # Passo 10
        janela = texto[i:i + tamanho_janela]
        score = fuzz.partial_ratio(busca, janela)

        if score > melhor_score and score >= threshold * 100:
            melhor_score = score
            # Refinar posição exata dentro da janela
            melhor_pos = self._refinar_posicao(busca, janela, i)

    return melhor_pos
```

### 2. Múltiplas Métricas

```python
def _calcular_score_composto(self, texto1: str, texto2: str) -> float:
    """Usa múltiplas métricas e retorna a melhor"""
    scores = [
        fuzz.ratio(texto1, texto2),
        fuzz.partial_ratio(texto1, texto2),
        fuzz.token_sort_ratio(texto1, texto2),
        fuzz.token_set_ratio(texto1, texto2),
    ]
    return max(scores) / 100.0  # Normalizar para 0-1
```

### 3. Normalização

```python
import re
import unicodedata

def _normalizar_para_fuzzy(self, texto: str) -> str:
    # Lowercase
    texto = texto.lower()

    # Remover acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')

    # Normalizar espaços
    texto = re.sub(r'\s+', ' ', texto).strip()

    # Normalizar valores monetários
    texto = re.sub(r'R\$\s*', '', texto)
    texto = re.sub(r'\.(?=\d{3})', '', texto)  # Remove separador de milhar

    return texto
```

---

## 🐛 Debugging

### Verificar Scores

```python
from rapidfuzz import fuzz

texto1 = "O valor do contrato é R$ 10.000,00"
texto2 = "valor contrato R$ 10000"

print(f"ratio: {fuzz.ratio(texto1, texto2)}")
print(f"partial: {fuzz.partial_ratio(texto1, texto2)}")
print(f"token_sort: {fuzz.token_sort_ratio(texto1, texto2)}")
print(f"token_set: {fuzz.token_set_ratio(texto1, texto2)}")
```

### Testar Threshold

```python
alg = AlgoritmoFuzzyAvancado()

# Curto
print(alg._obter_threshold("Teste"))  # 0.90

# Médio
print(alg._obter_threshold("Este é um texto médio de teste"))  # 0.85

# Longo
print(alg._obter_threshold("A" * 150))  # 0.80
```

---

## 📈 Melhorias Propostas (Futuras)

1. **Cache de Scores**: Guardar scores já calculados
2. **N-grams**: Comparar trigramas/4-gramas
3. **TF-IDF**: Ponderar palavras importantes
4. **Phonetic Matching**: Para nomes próprios (Soundex, Metaphone)
5. **Aprendizado de Threshold**: Ajustar baseado em casos passados

---

## 🔗 Referências

- **RapidFuzz Docs**: https://github.com/maxbachmann/RapidFuzz
- **Algoritmo Baseline**: `tests/algoritmos/producao/CONTEXTO.md`
- **Framework A/B**: `tests/framework_comparacao.py`
- **Fixtures**: `tests/fixtures/*.json`

---

## 📞 Para Ajuda

Se encontrar problemas:

1. Ler `tests/algoritmos/README.md` para estrutura geral
2. Ver `tests/algoritmos/producao/algoritmo.py` como exemplo
3. Executar testes individuais com `-v` para detalhes
4. Comparar com baseline para validar melhoria

**Boa implementação! 🚀**
