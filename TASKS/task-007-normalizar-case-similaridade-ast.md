# Task 007: Normalizar Case na Comparação de Similaridade AST

Status: done

## Descrição

A comparação de similaridade textual no processamento AST está **case-sensitive**, fazendo com que textos idênticos (exceto por maiúsculas/minúsculas) não sejam pareados como ALTERACAO.

### Exemplo Real (Versão 95174b7a):

**Modificação 1:**

```
Original: "2.2. Se aplicável, a retroatividade dos efeitos do CONTRATO, não ocasionará..."
Novo: "--"
```

**Modificação 2:**

```
Original: "--"
Novo: "2.2. SE APLICÁVEL, A RETROATIVIDADE DOS EFEITOS DO CONTRATO NÃO OCASIONARÁ..."
```

**Resultado Esperado:** 1 ALTERACAO (similaridade ~95%)
**Resultado Atual:** 2 modificações separadas (não pareadas)

---

## 🎯 Solução

Adicionar normalização **case-insensitive** na comparação de similaridade textual:

1. Converter ambos os textos para **lowercase** antes do `SequenceMatcher`
2. Manter textos originais inalterados no resultado final
3. Normalizar também pontuação e espaços extras

---

## 🧪 Teste TDD

### Red (Teste que Falha)

```python
def test_alteracao_case_insensitive_deve_ser_pareada(mock_repositorio):
    """Textos idênticos exceto por case devem ser pareados como ALTERACAO"""

    # Arrange
    mock_repositorio.get_versao.return_value = {...}

    # Simular diff com textos case-different
    diff = [
        {"type": "removed", "text": "Se aplicável", "position": 100, "clause": "2.2"},
        {"type": "added", "text": "SE APLICÁVEL", "position": 105, "clause": "2.2"}
    ]

    processor = PandocASTProcessor(mock_repositorio)

    # Act
    result = processor._extrair_modificacoes_do_diff_ast(diff, tags=[])

    # Assert
    assert len(result) == 1, "Deve consolidar em 1 ALTERACAO"
    assert result[0]["tipo"] == "ALTERACAO"
    assert "se aplicável" in result[0]["original"].lower()
    assert "se aplicável" in result[0]["novo"].lower()
```

---

## 🔧 Implementação

### Arquivo: `versiona-ai/directus_server.py`

**Linha ~2487:** Adicionar normalização antes do `SequenceMatcher`

```python
# Critério 3: Alta similaridade textual (> 60%)
if not is_pair:
    # Decodificar HTML entities
    removed_text = self._unescape_html(removed["text"])
    added_text = self._unescape_html(added["text"])

    # NOVO: Normalizar para comparação case-insensitive
    removed_normalized = self._normalize_for_comparison(removed_text)
    added_normalized = self._normalize_for_comparison(added_text)

    # Calcular similaridade usando textos normalizados
    similarity = SequenceMatcher(None, removed_normalized, added_normalized).ratio()

    if similarity > SIMILARITY_THRESHOLD:
        is_pair = True
```

**Adicionar método auxiliar:**

```python
def _normalize_for_comparison(self, text: str) -> str:
    """Normaliza texto para comparação case-insensitive"""
    import unicodedata
    import re

    # Lowercase
    text = text.lower()

    # Normalizar Unicode (NFD -> NFC)
    text = unicodedata.normalize("NFC", text)

    # Normalizar espaços múltiplos
    text = re.sub(r'\s+', ' ', text)

    # Remover espaços no início/fim
    text = text.strip()

    # Normalizar pontuação comum (vírgula + espaço)
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'\s*\.\s*', '. ', text)

    return text
```

---

## ✅ Critérios de Aceitação

- [x] Teste TDD passa (Red → Green) ✅
- [x] Textos case-different são pareados como ALTERACAO ✅
- [x] Textos originais mantidos inalterados no resultado ✅
- [x] Similaridade calculada corretamente (>95% para case-only changes) ✅
- [x] Testes de categorização AST passando (4/4) ✅
- [x] Versão 95174b7a reprocessada corretamente (8→7 modificações) ✅

---

## 📊 Resultado Esperado

**Versão 95174b7a:**

- **Antes:** 8 modificações (4 ALTERACAO + 2 REMOCAO + 2 INSERCAO)
- **Depois:** 7 modificações (5 ALTERACAO + 1 REMOCAO + 1 INSERCAO)
  - Par "2.2. Se aplicável" / "2.2. SE APLICÁVEL" → 1 ALTERACAO

---

## 🔄 Próximos Passos

1. ✅ Criar teste TDD (Red)
2. ✅ Implementar `_normalize_for_comparison`
3. ✅ Validar com versão 95174b7a (reprocessar localmente)
4. ✅ Deploy em produção (https://ignai-contract-ia.paas.node10.de.vix.br)
5. ⏳ Reprocessar versões antigas em produção (opcional)

---

## 📝 Resumo da Implementação

### Teste TDD (Red → Green)

**Red Phase:** Teste falhou como esperado

```
✅ Total de modificações extraídas: 2
  - REMOCAO: 1
  - INSERCAO: 1
```

**Green Phase:** Teste passou após implementação

```
✅ Total de modificações extraídas: 1
  - ALTERACAO: 1
```

### Código Implementado

**Método auxiliar** (`_normalize_for_comparison`):

- Converte para lowercase
- Normaliza Unicode (NFC)
- Remove espaços múltiplos
- Normaliza pontuação (vírgulas e pontos)

**Critério 3 atualizado** (linha ~2487):

- Aplica normalização antes do `SequenceMatcher`
- Calcula similaridade com textos normalizados
- Mantém textos originais no resultado final

### Resultados

- ✅ 4/4 testes de categorização AST passando
- ✅ Textos case-different agora são pareados
- ✅ Case original preservado no resultado
- ✅ Nenhuma regressão detectada

### Validação em Produção (Local)

**Versão 95174b7a reprocessada:**

**Antes da correção:**

- 8 modificações: 4 ALTERACAO + 2 REMOCAO + 2 INSERCAO
- Par "Se aplicável"/"SE APLICÁVEL" separado (similaridade case-sensitive: 8.30%)

**Depois da correção:**

- 7 modificações: 5 ALTERACAO + 1 REMOCAO + 1 INSERCAO ✅
- Par consolidado como ALTERACAO (similaridade case-insensitive: 99.60%) ✅
- Modificação #5: case original preservado

**Evidência:**

```
🎉 MODIFICAÇÃO #5 - ALTERACAO (PAREADA COM SUCESSO!)
   📄 Original: "2.2. Se aplicável, a retroatividade..."
   📝 Novo: "2.2. SE APLICÁVEL, A RETROATIVIDADE..."
   📊 Similaridade case-insensitive: 99.60% ✅
```

**⚠️ Importante:** Necessário limpar cache Python completamente antes do reprocessamento:

- `pkill -f directus_server.py`
- `find . -name "*.pyc" -delete`
- `find . -type d -name "__pycache__" -exec rm -rf {} +`
- Rodar servidor com `PYTHONDONTWRITEBYTECODE=1 python3 directus_server.py`

### Deploy em Produção ✅

**Data:** 2025-10-23
**URL:** https://ignai-contract-ia.paas.node10.de.vix.br

**Validação:**

```
📊 Versão 95174b7a em produção:
   Total modificações: 7 ✅
   ALTERACAO: 5 (incluindo par case-insensitive)

🎉 Task 007 ATIVA EM PRODUÇÃO!
   Modificação #5 - ALTERACAO pareada com case-insensitive
   Similaridade: 99.60%
```

**Status:** Correção deployada e funcionando corretamente em produção! 🚀

---

## 📚 Referências

- Task 006: Correção de pareamento por similaridade
- difflib.SequenceMatcher: https://docs.python.org/3/library/difflib.html
- unicodedata.normalize: https://docs.python.org/3/library/unicodedata.html
