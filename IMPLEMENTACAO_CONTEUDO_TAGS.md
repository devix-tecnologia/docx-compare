# Implementação de Preenchimento do Campo `conteudo` em `modelo_contrato_tag`

## 📋 Problema Identificado

O processador de modelo de contrato estava extraindo e salvando tags na coleção `modelo_contrato_tag`, mas **não estava preenchendo o campo `conteudo`** com o texto entre as tags de abertura e fechamento.

## 🔧 Solução Implementada

### 1. Nova Função: `extract_content_between_tags()`

Criada função para extrair conteúdo entre tags no formato:
- `{{TAG-nome}}...{{/TAG-nome}}`
- `{{nome}}...{{/nome}}`

```python
def extract_content_between_tags(text: str) -> dict[str, str]:
    """
    Extrai conteúdo entre tags de abertura e fechamento
    """
```

**Funcionalidades:**
- Suporta tanto formato `{{TAG-nome}}` quanto `{{nome}}`
- Extrai conteúdo completo entre as tags
- Valida se tags de abertura e fechamento coincidem
- Remove whitespace desnecessário
- Logging detalhado em modo verbose

### 2. Atualização dos Padrões Regex

Expandidos os padrões na função `extract_tags_from_differences()` para incluir:

```python
# Novos padrões adicionados:
r"(?<!\{)\{\{\s*TAG-([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",       # {{TAG-nome}}
r"(?<!\{)\{\{\s*TAG-([a-zA-Z_][a-zA-Z0-9_]*)\s*/\s*\}\}(?!\})",   # {{TAG-nome /}}
r"(?<!\{)\{\{\s*/\s*TAG-([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})",   # {{/TAG-nome}}
```

### 3. Integração no Fluxo Principal

Modificado `processar_modelo_contrato()` para:

1. **Extrair conteúdo** do arquivo `tagged_text`
2. **Enriquecer tags** com o conteúdo correspondente
3. **Incluir campo `conteudo`** nos dados enviados ao Directus

```python
# 4. Extrair conteúdo entre tags do arquivo com tags
content_map = extract_content_between_tags(tagged_text)

# 5. Extrair tags das diferenças
tags_encontradas = extract_tags_from_differences(modifications)

# 6. Enriquecer tags encontradas com conteúdo extraído
for tag_info in tags_encontradas:
    tag_nome = tag_info["nome"]
    if tag_nome in content_map:
        tag_info["conteudo"] = content_map[tag_nome]
```

### 4. Atualização do Salvamento

Modificado `salvar_tags_modelo_contrato()` para incluir o campo:

```python
tag_data = {
    "modelo_contrato": modelo_id,
    "tag_nome": tag_info["nome"],
    "caminho_tag_inicio": tag_info.get("caminho_tag_inicio", ""),
    "caminho_tag_fim": tag_info.get("caminho_tag_fim", ""),
    "conteudo": tag_info.get("conteudo", ""),  # ✅ CAMPO ADICIONADO
    "contexto": tag_info.get("contexto", "")[:500],
    # ... outros campos
}
```

### 5. Melhorias de Logging

Adicionado logging para mostrar:
- Conteúdo extraído para cada tag
- Preview do conteúdo sendo salvo
- Status de enriquecimento das tags

## 🧪 Testes Implementados

### 1. `test_extract_content_tags.py`
- Testa extração básica de conteúdo
- Valida diferentes formatos de tag
- Verifica casos especiais

### 2. `test_integration_content.py`
- Teste de integração completo
- Simula fluxo real do processador
- Verifica enriquecimento de tags com conteúdo

## 📊 Resultados dos Testes

```
✅ Todas as tags esperadas foram encontradas!
✅ Conteúdo da tag 'responsavel' está correto
📊 Resultado final: 2 tags processadas com conteúdo
```

## 🚀 Como Testar em Produção

1. **Modo Dry-Run:**
```bash
uv run python src/docx_compare/processors/processador_modelo_contrato.py --dry-run --verbose
```

2. **Processamento Real:**
```bash
uv run python src/docx_compare/processors/processador_modelo_contrato.py --single-run --verbose
```

3. **Via Orquestrador:**
```bash
make run-orquestrador-single-verbose
```

## 🔍 Verificação no Directus

Após o processamento, verificar na coleção `modelo_contrato_tag`:
- Campo `tag_nome`: Nome da tag extraída
- Campo `conteudo`: ✅ **Agora preenchido com o texto entre as tags**
- Campo `caminho_tag_inicio`: Posição de início
- Campo `caminho_tag_fim`: Posição de fim

## 📝 Exemplo Prático

**Arquivo com tags:**
```
{{TAG-responsavel}}
Nome: João Silva
E-mail: joao@empresa.com
Cargo: Gerente
{{/TAG-responsavel}}
```

**Resultado no banco:**
```json
{
  "tag_nome": "responsavel",
  "conteudo": "Nome: João Silva\nE-mail: joao@empresa.com\nCargo: Gerente",
  "caminho_tag_inicio": "modificacao_0_linha_1_pos_0",
  "caminho_tag_fim": "modificacao_0_linha_1_pos_120"
}
```

## ✅ Status Final

- ✅ Campo `conteudo` implementado
- ✅ Extração de conteúdo funcional
- ✅ Integração no fluxo principal
- ✅ Testes validados
- ✅ Logs informativos adicionados
- ✅ Compatibilidade mantida com padrões existentes
