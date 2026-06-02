# Fixtures de Integração Completa: Modelo → Versão

Este diretório contém fixtures para testes de integração completos que simulam o fluxo real de processamento sem depender do Directus.

## Fluxo de Teste

```
┌─────────────────────────────────────────┐
│ ETAPA 1: Processar Modelo               │
│                                         │
│ Entrada:                                │
│  • arquivo_com_tags.docx               │
│  • clausulas_inicial.json              │
│                                         │
│ Saída:                                  │
│  • tags_processadas (com posições)     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ ETAPA 2: Processar Versão               │
│                                         │
│ Entrada:                                │
│  • arquivo_original.docx               │
│  • arquivo_modificado.docx             │
│  • tags_processadas (da etapa 1)       │
│                                         │
│ Saída:                                  │
│  • modificações vinculadas             │
└─────────────────────────────────────────┘
```

## Arquivos Necessários

### 1. `clausulas_inicial.json`
Lista de cláusulas existentes no sistema antes do processamento.

**Formato:**
```json
[
  {
    "id": "uuid-clausula-1",
    "numero": "1.1",
    "nome": "Objeto do Contrato",
    "objetivo": "Define o objeto do contrato",
    "modelo_contrato": "uuid-modelo"
  },
  ...
]
```

**Como capturar:**
```bash
# Buscar cláusulas do modelo antes do processamento
curl -H "Authorization: Bearer TOKEN" \
  "https://contract.devix.co/items/clausula?filter[modelo_contrato][_eq]=MODELO_ID&limit=-1" \
  > clausulas_inicial.json
```

### 2. `arquivo_com_tags.docx`
Arquivo DOCX do modelo com tags de marcação `{{TAG-1.1}}...{{/TAG-1.1}}`.

**Como capturar:**
- Baixar do Directus: campo `arquivo_com_tags` do modelo
- URL: `https://contract.devix.co/assets/UUID_ARQUIVO`

### 3. `arquivo_original.docx`
Arquivo DOCX original do modelo SEM tags (usado como base para comparação).

**Como capturar:**
- Baixar do Directus: campo `arquivo_original` do modelo
- URL: `https://contract.devix.co/assets/UUID_ARQUIVO`

### 4. `arquivo_modificado.docx`
Arquivo DOCX modificado da versão (com alterações feitas pelo usuário).

**Como capturar:**
- Baixar do Directus: campo `arquivo` da versão
- URL: `https://contract.devix.co/assets/UUID_ARQUIVO`

### 5. `tags_esperadas.json` (opcional)
Tags esperadas após processamento do modelo, para validação adicional.

**Formato:**
```json
[
  {
    "tag_nome": "1.1",
    "texto": "Conteúdo completo da cláusula...",
    "posicao_inicio": 1234,
    "posicao_fim": 5678,
    "clausula_id": "uuid-clausula-1"
  },
  ...
]
```

### 6. `metricas_esperadas.json` (opcional)
Métricas mínimas esperadas do processamento.

**Formato:**
```json
{
  "taxa_minima_vinculacao": 0.4,
  "total_tags_minimo": 10,
  "total_modificacoes_minimo": 5
}
```

## Script de Captura Automática

Para facilitar a captura das fixtures, use o script `capture_fixture.py` no diretório da fixture:

```bash
cd tests/sample/versao-8d8e89a8
uv run python capture_fixture.py
```

O script irá:
1. ✅ Baixar dados do Directus automaticamente
2. ✅ Salvar JSONs estruturados
3. ⚠️ Imprimir URLs dos arquivos DOCX para download manual

## Casos de Teste Existentes

### `versao-8d8e89a8/`
- **Modelo:** 48b43d38-76b4-47a2-93a4-4216ad57defc
- **Versão:** 8d8e89a8-ba89-4e0e-846c-43e7ad058309
- **Status:** Em construção
- **Objetivo:** Detectar bug de coordenadas incompatíveis (0% vinculação)

## Rodando os Testes

```bash
# Teste completo de integração
uv run pytest tests/test_integracao_modelo_versao.py -v -s

# Apenas teste de coordenadas
uv run pytest tests/test_integracao_modelo_versao.py::test_coordenadas_alinhadas -v -s

# Com debug detalhado
uv run pytest tests/test_integracao_modelo_versao.py -v -s --tb=short
```

## Por Que Este Teste É Importante?

1. ✅ **Independente do Directus**: Pode rodar offline, em CI/CD
2. ✅ **Reprodutível**: Mesmos inputs, mesmos outputs
3. ✅ **Rápido**: Não depende de API externa
4. ✅ **Detecta bugs de integração**: Problemas que só aparecem no fluxo completo
5. ✅ **Valida coordenadas**: Garante que tags e modificações estão no mesmo sistema

## Exemplo Real de Bug Detectado

Em 2 de junho de 2026, descobrimos que:
- Tags eram mapeadas em `texto_limpo` do `arquivo_com_tags`
- Modificações eram mapeadas em `texto_original` do diff
- **Resultado:** 0% vinculação (coordenadas incompatíveis)

Este teste teria detectado esse bug ANTES do deploy em produção! 🎯
