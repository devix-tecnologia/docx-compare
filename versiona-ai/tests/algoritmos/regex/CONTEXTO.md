# Contexto: Algoritmo Regex & Padrões Estruturados

## 🎯 Objetivo

Implementar algoritmo de vinculação baseado em **expressões regulares** para detectar padrões estruturados com alta precisão.

**Meta**: Score ≥ 80 pontos | Taxa ≥ 90% | Precisão ≥ 95%

---

## 📋 Problema

Dados estruturados (valores, datas, IDs) têm formato previsível, mas:

- ❌ Fuzzy matching é lento e menos preciso para padrões
- ❌ ML é overkill e tem latência
- ❌ Busca exata falha com variações de formato

**Oportunidade**: Regex é **ideal** para padrões estruturados:

- ✅ Extremamente rápido (< 10ms)
- ✅ 100% precisão quando padrão match
- ✅ Determinístico e previsível

---

## 🔬 Abordagem: Regex Patterns

### Estratégia

1. **Detectar Tipo de Padrão**: Identificar se texto tem estrutura conhecida
2. **Aplicar Regex Específico**: Usar pattern apropriado
3. **Normalizar para Comparação**: Tratar variações de formato
4. **Fallback**: Se não é estruturado, usar fuzzy

### Padrões a Implementar

```python
import re

PADROES = {
    # Valores monetários brasileiros
    "monetario_br": re.compile(
        r'R\$\s*(?:\d{1,3}(?:\.\d{3})*|\d+)(?:,\d{2})?'
    ),

    # Datas brasileiras
    "data_br": re.compile(
        r'\b\d{1,2}/\d{1,2}/\d{4}\b'
    ),

    # Percentuais
    "percentual": re.compile(
        r'\b\d+(?:,\d+)?%'
    ),

    # Prazos em dias
    "prazo_dias": re.compile(
        r'\b\d+\s+dias?\b',
        re.IGNORECASE
    ),

    # IDs de contrato/processo
    "contrato_id": re.compile(
        r'(?:contrato|processo)[\s#:]*(\d+)',
        re.IGNORECASE
    ),

    # CPF
    "cpf": re.compile(
        r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'
    ),

    # CNPJ
    "cnpj": re.compile(
        r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b'
    ),

    # CEP
    "cep": re.compile(
        r'\b\d{5}-\d{3}\b'
    ),
}
```

### Vantagens

- ✅ Performance: < 10ms por operação
- ✅ Precisão: 100% para padrões bem definidos
- ✅ Determinístico: Sem ambiguidade
- ✅ Zero dependências externas

### Casos de Uso Ideais

- Valores monetários: `R$ 10.000,00` → `R$ 15.000,00`
- Datas: `01/01/2024` → `15/02/2024`
- IDs: `Contrato #12345` → `Contrato #67890`
- Documentos: `CPF 123.456.789-00`

---

## 🛠️ Interface a Implementar

```python
from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao
import re
from typing import Optional, Pattern

class AlgoritmoRegex(AlgoritmoVinculacao):
    """
    Algoritmo de vinculação usando regex para padrões estruturados.
    """

    def __init__(self):
        self.padroes = self._inicializar_padroes()
        self._cache_deteccao = {}

    def _inicializar_padroes(self) -> dict[str, Pattern]:
        """Define todos os padrões regex suportados"""
        return {
            "monetario_br": re.compile(r'R\$\s*(?:\d{1,3}(?:\.\d{3})*|\d+)(?:,\d{2})?'),
            "data_br": re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b'),
            "percentual": re.compile(r'\b\d+(?:,\d+)?%'),
            "prazo_dias": re.compile(r'\b\d+\s+dias?\b', re.IGNORECASE),
            "contrato_id": re.compile(r'(?:contrato|processo)[\s#:]*(\d+)', re.IGNORECASE),
            "cpf": re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'),
            "cnpj": re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b'),
            "cep": re.compile(r'\b\d{5}-\d{3}\b'),
        }

    def calcular_posicoes(
        self,
        modificacoes: list[dict],
        texto_completo: str
    ) -> list[dict]:
        """
        Calcula posições usando regex quando possível, senão fallback.
        """
        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)

            # Detectar tipo de padrão
            tipo_padrao = self._detectar_tipo_padrao(texto_busca)

            if tipo_padrao:
                # Usar regex
                pos = self._buscar_com_regex(
                    texto_busca, texto_completo, tipo_padrao
                )
            else:
                # Fallback: busca exata
                idx = texto_completo.find(texto_busca)
                pos = (idx, idx + len(texto_busca)) if idx >= 0 else None

            if pos:
                resultado.append({
                    **mod,
                    "posicao_inicio": pos[0],
                    "posicao_fim": pos[1],
                    "tipo_padrao": tipo_padrao,
                })
            else:
                resultado.append({
                    **mod,
                    "posicao_inicio": None,
                    "posicao_fim": None,
                    "tipo_padrao": None,
                })

        return resultado

    def vincular_clausulas(
        self,
        modificacoes: list[dict],
        tags: list[dict],
        texto_completo: str
    ) -> list[dict]:
        """
        Vincula usando regex para estruturados, fallback para resto.
        """
        resultado = []

        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")
            tipo_padrao = mod.get("tipo_padrao")

            tag = None

            # 1. Overlap se tem posição
            if pos_inicio is not None:
                tag = UtilitariosVinculacao.buscar_tag_por_posicao(
                    pos_inicio, pos_fim, tags
                )

            # 2. Busca por estrutura se não achou
            if tag is None and tipo_padrao:
                tag = self._buscar_tag_por_estrutura(
                    texto_busca, tags, tipo_padrao
                )

            resultado.append({
                **mod,
                "tag_vinculada": tag.get("id") if tag else None
            })

        return resultado

    def _detectar_tipo_padrao(self, texto: str) -> Optional[str]:
        """
        Detecta qual padrão estruturado o texto match.
        Retorna nome do padrão ou None.
        """
        # Cache para performance
        if texto in self._cache_deteccao:
            return self._cache_deteccao[texto]

        for nome, padrao in self.padroes.items():
            if padrao.search(texto):
                self._cache_deteccao[texto] = nome
                return nome

        self._cache_deteccao[texto] = None
        return None

    def _buscar_com_regex(
        self,
        texto_busca: str,
        texto_completo: str,
        tipo_padrao: str
    ) -> Optional[tuple[int, int]]:
        """
        Busca usando regex do tipo detectado.
        """
        padrao = self.padroes[tipo_padrao]

        # Extrair valor estruturado do texto de busca
        match_busca = padrao.search(texto_busca)
        if not match_busca:
            return None

        valor_busca = match_busca.group(0)

        # Buscar no texto completo
        for match in padrao.finditer(texto_completo):
            valor_encontrado = match.group(0)

            # Normalizar e comparar
            if self._valores_equivalentes(
                valor_busca, valor_encontrado, tipo_padrao
            ):
                return (match.start(), match.end())

        return None

    def _valores_equivalentes(
        self, val1: str, val2: str, tipo: str
    ) -> bool:
        """
        Verifica se dois valores do mesmo tipo são equivalentes.
        """
        # Normalizar
        v1 = val1.strip().lower()
        v2 = val2.strip().lower()

        # Comparação exata primeiro
        if v1 == v2:
            return True

        # Comparações específicas por tipo
        if tipo == "monetario_br":
            return self._comparar_valores_monetarios(v1, v2)
        elif tipo in ["prazo_dias", "percentual"]:
            return self._comparar_numeros(v1, v2)
        elif tipo in ["cpf", "cnpj", "cep"]:
            # Documentos: apenas dígitos
            d1 = re.sub(r'\D', '', v1)
            d2 = re.sub(r'\D', '', v2)
            return d1 == d2

        return False

    def _comparar_valores_monetarios(self, v1: str, v2: str) -> bool:
        """Compara valores monetários normalizando formato"""
        def extrair_numero(v):
            # Remove R$, espaços, pontos de milhar
            v = re.sub(r'r\$|\.(?=\d{3})', '', v)
            # Troca vírgula por ponto
            v = v.replace(',', '.')
            return float(re.sub(r'[^\d.]', '', v))

        try:
            return abs(extrair_numero(v1) - extrair_numero(v2)) < 0.01
        except:
            return False

    def _comparar_numeros(self, v1: str, v2: str) -> bool:
        """Extrai e compara apenas números"""
        try:
            n1 = float(re.sub(r'[^\d,.]', '', v1).replace(',', '.'))
            n2 = float(re.sub(r'[^\d,.]', '', v2).replace(',', '.'))
            return abs(n1 - n2) < 0.01
        except:
            return False

    def _buscar_tag_por_estrutura(
        self,
        texto_busca: str,
        tags: list[dict],
        tipo_padrao: str
    ) -> Optional[dict]:
        """
        Busca tag que contenha estrutura similar.
        """
        padrao = self.padroes[tipo_padrao]

        # Extrair valor da busca
        match_busca = padrao.search(texto_busca)
        if not match_busca:
            return None

        valor_busca = match_busca.group(0)

        # Procurar em tags
        for tag in tags:
            tag_texto = tag.get("texto", "")

            for match_tag in padrao.finditer(tag_texto):
                valor_tag = match_tag.group(0)

                if self._valores_equivalentes(
                    valor_busca, valor_tag, tipo_padrao
                ):
                    return tag

        return None
```

---

## 📦 Dependências

Nenhuma! Usa apenas biblioteca padrão `re`.

---

## 🧪 Fixtures Disponíveis

**Fixture específica para regex**: `caso_02_alteracao_simples.json`

- ALTERACAO de valor: R$ 10.000,00 → R$ 15.000,00
- Ideal para testar detecção de padrões monetários

---

## ✅ Critérios de Sucesso

### Métricas Mínimas

- **Score Geral**: ≥ 80 pontos
- **Taxa de Vinculação**: ≥ 90% (casos estruturados)
- **Precisão**: ≥ 95% (regex não deve dar falsos positivos)
- **Recall**: ≥ 85%
- **Tempo**: < 10ms (extremamente rápido)

### Casos de Teste Específicos

```python
def test_detectar_valor_monetario():
    alg = AlgoritmoRegex()
    assert alg._detectar_tipo_padrao("R$ 10.000,00") == "monetario_br"
    assert alg._detectar_tipo_padrao("R$15000") == "monetario_br"

def test_valores_equivalentes():
    alg = AlgoritmoRegex()
    # Formatos diferentes, mesmo valor
    assert alg._valores_equivalentes(
        "R$ 10.000,00", "R$ 10000,00", "monetario_br"
    )
    assert alg._valores_equivalentes(
        "R$ 10.000", "R$ 10.000,00", "monetario_br"
    )

def test_buscar_valor():
    alg = AlgoritmoRegex()
    texto = "O valor acordado é R$ 15.000,00 conforme cláusula."
    pos = alg._buscar_com_regex("R$ 15.000,00", texto, "monetario_br")
    assert pos is not None
    assert texto[pos[0]:pos[1]] == "R$ 15.000,00"
```

### Validação

```bash
cd versiona-ai
uv run pytest tests/algoritmos/regex/test_regex.py -v
uv run python tests/comparar_algoritmos.py --algoritmos producao regex
```

---

## 💡 Dicas de Implementação

### 1. Teste Regex Isoladamente

```python
import re

padrao = re.compile(r'R\$\s*(?:\d{1,3}(?:\.\d{3})*|\d+)(?:,\d{2})?')

textos = [
    "R$ 10.000,00",
    "R$15000",
    "R$ 1.500,50",
    "valor de R$ 100,00"
]

for texto in textos:
    match = padrao.search(texto)
    if match:
        print(f"{texto} → {match.group(0)}")
```

### 2. Named Groups para Captura

```python
# Capturar partes específicas
padrao = re.compile(
    r'(?P<moeda>R\$)\s*(?P<valor>[\d.,]+)'
)

match = padrao.search("R$ 10.000,00")
print(match.group("moeda"))  # R$
print(match.group("valor"))  # 10.000,00
```

### 3. Adicionar Novo Padrão

```python
# Em _inicializar_padroes()
"telefone": re.compile(
    r'\(?\d{2}\)?\s*\d{4,5}-?\d{4}'
),
```

---

## 📈 Melhorias Propostas (Futuras)

1. **Mais Padrões**: Telefone, Email, URLs
2. **Variações de Formato**: Aceitar mais formatos de data
3. **Localização**: Suporte a outros idiomas
4. **Validação**: Verificar se CPF/CNPJ são válidos (dígito verificador)
5. **Extração de Entidades**: NER combinado com regex

---

## 🐛 Debugging

### Testar Regex Online

Use https://regex101.com/ para validar patterns.

### Ver Todos os Matches

```python
import re

texto = "Valores: R$ 10.000, R$ 15.000,00 e R$20000"
padrao = re.compile(r'R\$\s*[\d.,]+')

for match in padrao.finditer(texto):
    print(f"Pos {match.start()}-{match.end()}: {match.group(0)}")
```

---

## 🔗 Referências

- **Python re docs**: https://docs.python.org/3/library/re.html
- **Regex101**: https://regex101.com/
- **Framework A/B**: `tests/framework_comparacao.py`

---

**Boa implementação! 🚀**
