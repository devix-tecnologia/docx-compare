# 🐛 BUG REPORT: Taxa de Vinculação 30% (Esperado: ~100%)

## 📊 Sintomas

- **Observado**: 93/310 modificações vinculadas (30%)
- **Esperado**: ~100% baseado em testes unitários
- **Breakdown**: 
  - Modificações: 24/29 vinculadas (82.8%) ✅
  - Remoções: 69/281 vinculadas (24.6%) ❌

## 🔍 Análise Detalhada

### Caso de Teste: Modificação "4. CORREÇÃO MONETÁRIA"

```
ID: 9b53a892-4bec-4756-80c8-3e10b4a48cdd
Posição: 66655 → 66679 (24 chars)
Conteúdo: "4.  CORREÇÃO MONETÁRIA"
```

**Análise SQL:**
- Tag 1.5 (66226-66928): **overlap 100%** ✅
- Tag tem cláusula vinculada ✅
- Mas **NÃO foi vinculada** à modificação ❌

**Por que não vinculou?**

```
Overlap: 100.0% ✅
Fuzzy scores:
  - ratio:            35.9%
  - partial_ratio:    38.7%
  - token_sort_ratio: 33.5%
  - token_set_ratio:  34.7%
  - score_composto:   35.7% ❌

Threshold: Tier 1 (overlap ≥90% + fuzzy ≥40%)
Resultado: 35.7% < 40% → REJEITADO
```

**O overlap está perfeito, mas o fuzzy está baixo. Por quê?**

## 🎯 Causa Raiz: Desalinhamento de Coordenadas

### Problema

Os sistemas de coordenadas são **incompatíveis**:

1. **Tags** (`processador_tags_modelo.py`):
   - Posições calculadas no texto **COM marcações** `{{TAG-X}}`
   - Exemplo: `{{TAG-1.5}}conteúdo aqui{{/TAG-1.5}}`
   - `posicao_inicial_texto` = posição APÓS `{{TAG-1.5}}`

2. **Modificações** (`directus_server.py`):
   - Diff feito entre textos **SEM marcações**
   - Código: `re.sub(r"\{\{/?TAG-[^}]+\}\}", "", arquivo_com_tags_text)`
   - Posições baseadas no texto limpo

### Impacto

```python
# arquivo_com_tags.docx (texto COM tags)
Posição 66226: "{{TAG-1.5}}A CONTRATADA, em nenhuma hipótese..."
Tag 1.5 início: 66226 (após "{{TAG-1.5}}")

# arquivo_com_tags limpo (SEM tags) - usado para diff
Posição 66226: "4. CORREÇÃO MONETÁRIA..."  # ← TEXTO DIFERENTE!
Modificação: 66655-66679

# Overlap calculado: 100% (posições coincidem numericamente)
# MAS textos reais são COMPLETAMENTE DIFERENTES!
# Fuzzy score: 35.7% (textos não se parecem)
```

### Código Problemático

**`processador_tags_modelo.py` linha ~384:**
```python
def _extrair_conteudo_entre_tags(self, texto: str) -> dict[str, dict]:
    # texto = arquivo_com_tags COM marcações
    conteudo_inicio = open_pos  # Após {{TAG-X}}
    conteudo_fim = open_pos + close_match.start()
    
    conteudo_map[tag_nome] = {
        "posicao_inicial_texto": conteudo_inicio,  # ← Baseado no texto COM tags
        "posicao_final_texto": conteudo_fim,
    }
```

**`directus_server.py` linha ~568:**
```python
if arquivo_com_tags_text:
    # Remove tags ANTES do diff
    original_text_para_diff = re.sub(
        r"\{\{/?TAG-[^}]+\}\}", "", arquivo_com_tags_text
    )  # ← Posições das modificações baseadas NESTE texto
    
    diferenca = self._perform_diff(original_text_para_diff, modified_text)
```

## 💡 Solução

### Opção 1: Processar Tags no Texto Limpo (Recomendado)

Modificar `processador_tags_modelo.py` para:
1. Baixar `arquivo_com_tags.docx`
2. **Remover as marcações** antes de calcular posições
3. Usar o texto limpo como referência
4. Salvar posições baseadas no texto SEM tags

**Vantagem**: Compatível com o fluxo atual do `directus_server.py`

### Opção 2: Processar Modificações no Texto COM Tags

Modificar `directus_server.py` para:
1. NÃO remover tags antes do diff
2. Fazer diff entre:
   - Original: `arquivo_com_tags_text` (COM tags)
   - Modificado: `modified_text` (adicionar tags de volta)

**Desvantagem**: Modificações incluiriam as marcações `{{TAG-X}}` no conteúdo

### Opção 3: Mapear Coordenadas (Complexo)

Criar mapeamento entre sistemas de coordenadas:
1. Para cada posição no texto COM tags → posição no texto SEM tags
2. Converter posições das tags ao vincular

**Desvantagem**: Complexo, propenso a erros

## 📋 Impacto no Dataset

### Modificações Afetadas

Todas as modificações com:
- Overlap alto (>50%) baseado em posições
- Fuzzy baixo (<40%) devido a textos diferentes
- **Estimativa**: ~200 das 217 não vinculadas (92%)

### Categorias

- **Remoções vazias** (sem conteúdo): Não podem fazer fuzzy match → sempre rejeitadas
- **Títulos de cláusulas**: Pequenos, acabam em tags erradas
- **Modificações grandes**: Cruzam múltiplas tags devido a desalinhamento

## ✅ Próximos Passos

1. **Escolher solução** (Opção 1 recomendada)
2. **Reprocessar tags** com `processador_tags_modelo.py` corrigido
3. **Reprocessar versão** 2573b998 via API
4. **Validar** taxa de vinculação (esperado: >90%)
5. **Executar testes** para confirmar correção

## 🔬 Validação do Bug

Script de teste criado: `debug_vinculacao_falhada.py`

```bash
uv run python debug_vinculacao_falhada.py
```

Confirma:
- ✅ Overlap calculado: 100%
- ❌ Fuzzy score: 35.7% (< threshold 40%)
- ❌ Textos nas mesmas posições são DIFERENTES
