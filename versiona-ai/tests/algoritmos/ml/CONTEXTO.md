# Contexto: Algoritmo Machine Learning / Embeddings

## 🎯 Objetivo

Implementar algoritmo de vinculação baseado em **embeddings semânticos** que capture significado além da similaridade sintática.

**Meta**: Score ≥ 75 pontos | Taxa ≥ 85% | Precisão ≥ 90%

---

## 📋 Problema

Algoritmos baseados em similaridade textual (fuzzy) têm limitações:

- ❌ Não entendem sinônimos ("valor" vs "montante")
- ❌ Não capturam paráfrases ("R$ 10 mil" vs "dez mil reais")
- ❌ Dependem de palavras exatas
- ❌ Não lidam bem com ordem diferente de ideias

**Oportunidade**: Usar embeddings para capturar **semântica** do texto.

---

## 🔬 Abordagem: Embeddings Semânticos

### Estratégia

Use **Sentence Transformers** para gerar embeddings vetoriais:

1. **Modelo Pré-treinado**:
   - `paraphrase-MiniLM-L6-v2` (80MB, rápido, português OK)
   - Ou `paraphrase-multilingual-MiniLM-L12-v2` (420MB, melhor)

2. **Vetorização**:

   ```python
   from sentence_transformers import SentenceTransformer

   modelo = SentenceTransformer('paraphrase-MiniLM-L6-v2')
   embedding = modelo.encode("Texto aqui")  # → vetor [384]
   ```

3. **Similaridade Cosine**:

   ```python
   import numpy as np

   sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
   ```

4. **Cache**: Guardar embeddings já calculados para performance

5. **Fallback**: Se modelo falhar, usar fuzzy matching simples

### Vantagens

- ✅ Captura significado semântico
- ✅ Robusto a sinônimos e paráfrases
- ✅ Independente de ordem de palavras
- ✅ Modelos pré-treinados (não precisa treinar)

### Trade-offs

- ⚠️ Latência: ~50-150ms primeira execução (load modelo)
- ⚠️ Latência: ~5-20ms subsequentes (com cache)
- ⚠️ Memória: ~100-500MB (modelo carregado)
- ⚠️ CPU-bound: Inferência em CPU

---

## 🛠️ Interface a Implementar

```python
from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Optional

class AlgoritmoML(AlgoritmoVinculacao):
    """
    Algoritmo de vinculação usando embeddings semânticos.
    """

    def __init__(self):
        # Lazy loading: só carrega quando usar
        self._modelo = None
        self._cache_embeddings = {}
        self.threshold_cosine = 0.75  # Similaridade mínima

    @property
    def modelo(self):
        """Carrega modelo sob demanda"""
        if self._modelo is None:
            self._modelo = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        return self._modelo

    def calcular_posicoes(
        self,
        modificacoes: list[dict],
        texto_completo: str
    ) -> list[dict]:
        """
        Calcula posições usando busca semântica.

        Estratégia:
        1. Gerar embedding da modificação
        2. Deslizar janela pelo texto, gerando embeddings
        3. Calcular cosine similarity
        4. Retornar posição com maior similaridade
        """
        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            pos = self._buscar_semanticamente(texto_busca, texto_completo)

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
        Vincula modificações a tags usando similaridade semântica.
        """
        resultado = []

        # Gerar embeddings de todas as tags (batch para performance)
        tags_textos = [tag.get("texto", "") for tag in tags]
        tags_embeddings = self._obter_embeddings_batch(tags_textos)

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

            # 2. Similaridade semântica se não achou
            if tag is None:
                tag = self._buscar_melhor_tag_semantica(
                    texto_busca, tags, tags_embeddings
                )

            resultado.append({
                **mod,
                "tag_vinculada": tag.get("id") if tag else None
            })

        return resultado

    def _buscar_semanticamente(
        self,
        busca: str,
        texto: str
    ) -> Optional[tuple[int, int]]:
        """
        Busca posição usando similaridade semântica.
        """
        # Implementar busca com sliding window
        pass

    def _buscar_melhor_tag_semantica(
        self,
        texto_modificacao: str,
        tags: list[dict],
        tags_embeddings: list
    ) -> Optional[dict]:
        """
        Busca melhor tag usando cosine similarity.
        """
        emb_mod = self._obter_embedding(texto_modificacao)

        melhor_tag = None
        melhor_score = 0.0

        for tag, emb_tag in zip(tags, tags_embeddings):
            if emb_tag is None:
                continue

            # Cosine similarity
            sim = np.dot(emb_mod, emb_tag) / (
                np.linalg.norm(emb_mod) * np.linalg.norm(emb_tag)
            )

            if sim > melhor_score and sim >= self.threshold_cosine:
                melhor_tag = tag
                melhor_score = sim

        return melhor_tag

    def _obter_embedding(self, texto: str):
        """Obtém embedding com cache"""
        if texto not in self._cache_embeddings:
            self._cache_embeddings[texto] = self.modelo.encode(texto)
        return self._cache_embeddings[texto]

    def _obter_embeddings_batch(self, textos: list[str]) -> list:
        """Gera embeddings em batch (mais eficiente)"""
        embeddings = []
        for texto in textos:
            if texto:
                embeddings.append(self._obter_embedding(texto))
            else:
                embeddings.append(None)
        return embeddings
```

---

## 📦 Dependências

Adicionar em `pyproject.toml`:

```toml
[dependency-groups]
ml = [
    "sentence-transformers>=2.5.0",
    "torch>=2.0.0",  # Backend para transformers
    "numpy>=1.24.0",
]
```

Instalar:

```bash
cd versiona-ai
uv sync --group ml

# Primeira execução baixa modelo (~80MB)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L6-v2')"
```

---

## 🧪 Fixtures Disponíveis

Mesmas fixtures do fuzzy (em `tests/fixtures/`):

1. **caso_01_insercao_simples.json**: 1 INSERCAO
2. **caso_02_alteracao_simples.json**: 1 ALTERACAO
3. **caso_03_fora_de_tags.json**: Caso negativo
4. **caso_04_multiplas_modificacoes_interdependentes.json**: 3 modificações

---

## ✅ Critérios de Sucesso

### Métricas Mínimas

- **Score Geral**: ≥ 75 pontos
- **Taxa de Vinculação**: ≥ 85%
- **Precisão**: ≥ 90% (ML deve ser mais preciso)
- **Recall**: ≥ 80%
- **F1-Score**: ≥ 0.85
- **Tempo**: < 200ms por modificação (incluindo embedding)

### Casos de Teste Específicos

```python
def test_sinonimos():
    """ML deve lidar melhor com sinônimos"""
    alg = AlgoritmoML()

    # "valor" e "montante" são sinônimos
    sim = alg._calcular_similaridade_semantica(
        "O valor do contrato é 10 mil",
        "O montante acordado foi 10 mil"
    )
    assert sim > 0.8  # Alta similaridade semântica

def test_parafrase():
    """ML deve detectar paráfrases"""
    alg = AlgoritmoML()

    sim = alg._calcular_similaridade_semantica(
        "R$ 15.000,00",
        "quinze mil reais"
    )
    assert sim > 0.7
```

### Validação

```bash
cd versiona-ai
uv run pytest tests/algoritmos/ml/test_ml.py -v
uv run python tests/comparar_algoritmos.py --algoritmos producao fuzzy ml
```

---

## 💡 Dicas de Implementação

### 1. Lazy Loading do Modelo

```python
@property
def modelo(self):
    if self._modelo is None:
        print("Carregando modelo... (primeira vez)")
        self._modelo = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    return self._modelo
```

### 2. Batch Processing

```python
# Mais eficiente que encode() individual
embeddings = modelo.encode([texto1, texto2, texto3], batch_size=32)
```

### 3. Fallback para Offline

```python
def vincular_clausulas(self, modificacoes, tags, texto_completo):
    try:
        return self._vincular_com_ml(modificacoes, tags, texto_completo)
    except Exception as e:
        logger.warning(f"ML falhou: {e}, usando fallback")
        # Fallback para fuzzy matching simples
        from algoritmos.fuzzy.algoritmo import AlgoritmoFuzzyAvancado
        return AlgoritmoFuzzyAvancado().vincular_clausulas(
            modificacoes, tags, texto_completo
        )
```

### 4. Threshold Adaptativo

```python
def _obter_threshold_ml(self, texto: str) -> float:
    """Threshold menor para textos curtos (mais difícil capturar semântica)"""
    if len(texto) < 10:
        return 0.70
    elif len(texto) < 30:
        return 0.75
    else:
        return 0.80
```

---

## 🐛 Debugging

### Verificar Modelo

```python
from sentence_transformers import SentenceTransformer

modelo = SentenceTransformer('paraphrase-MiniLM-L6-v2')
emb = modelo.encode("Teste")
print(f"Shape: {emb.shape}")  # (384,)
print(f"Type: {type(emb)}")   # numpy.ndarray
```

### Visualizar Similaridades

```python
import numpy as np

textos = [
    "O valor do contrato é R$ 10.000",
    "O montante acordado foi R$ 10 mil",
    "A data de vencimento é 31/12/2024"
]

embeddings = modelo.encode(textos)

# Matriz de similaridade
for i, texto1 in enumerate(textos):
    for j, texto2 in enumerate(textos):
        sim = np.dot(embeddings[i], embeddings[j]) / (
            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
        )
        print(f"{i}-{j}: {sim:.3f}")
```

### Performance

```python
import time

start = time.time()
emb = modelo.encode("Texto de teste" * 10)
elapsed = (time.time() - start) * 1000
print(f"Tempo: {elapsed:.1f}ms")
```

---

## 📈 Melhorias Propostas (Futuras)

1. **Fine-tuning**: Treinar modelo no domínio contratual
2. **Modelo Maior**: Usar `all-mpnet-base-v2` (melhor, mas 420MB)
3. **Pooling Strategies**: Testar mean/max/cls pooling
4. **TF-IDF Weighting**: Ponderar embeddings por importância
5. **Named Entity Recognition**: Extrair e comparar entidades

---

## 🔗 Referências

- **Sentence Transformers**: https://www.sbert.net/
- **Modelos Disponíveis**: https://www.sbert.net/docs/pretrained_models.html
- **Framework A/B**: `tests/framework_comparacao.py`
- **Algoritmo Fuzzy**: `tests/algoritmos/fuzzy/CONTEXTO.md`

---

**Boa implementação! 🚀**
