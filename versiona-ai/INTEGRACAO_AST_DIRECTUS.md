# Integração AST com Directus

Este documento explica como processar versões usando a implementação AST e gravar os resultados no Directus.

## 📋 Visão Geral

A implementação AST oferece **59.3% de precisão** (vs 51.9% da implementação original) ao detectar modificações em documentos DOCX. Os principais benefícios incluem:

✅ Detecção correta de tipos: ALTERACAO, REMOCAO, INSERCAO
✅ Preservação da estrutura do documento
✅ Auto-detecção de números de cláusulas
✅ Melhor tratamento de formatação inconsistente

## ✅ INTEGRADO NO SERVIDOR PRINCIPAL

A implementação AST está **totalmente integrada** no `directus_server.py`! Não é necessário usar scripts separados.

### Como usar AST via API Flask:

```bash
# POST /api/process
curl -X POST "http://localhost:8001/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "versao_id": "sua_versao_id",
    "use_ast": true
  }'
```

### Parâmetros da API:

- `versao_id` (obrigatório): ID da versão no Directus
- `mock` (opcional, default: `false`): Usar dados mockados
- **`use_ast` (opcional, default: `false`)**: **Use `true` para AST (59.3% precisão)**

## 🚀 Exemplos de Uso

### 1. Via API Flask (Recomendado)

```bash
# Processamento com AST (melhor precisão)
curl -X POST "http://localhost:8001/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "versao_id": "322e56c0-4b38-4e62-b563-8f29a131889c",
    "use_ast": true
  }'

# Processamento tradicional (texto plano)
curl -X POST "http://localhost:8001/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "versao_id": "322e56c0-4b38-4e62-b563-8f29a131889c",
    "use_ast": false
  }'
```

### 2. Via Python (DirectusAPI)

```python
from directus_server import DirectusAPI

api = DirectusAPI()

# Com AST (59.3% precisão)
resultado = api.process_versao(
    versao_id="322e56c0-4b38-4e62-b563-8f29a131889c",
    use_ast=True
)

# Sem AST (51.9% precisão)
resultado = api.process_versao(
    versao_id="322e56c0-4b38-4e62-b563-8f29a131889c",
    use_ast=False  # default
)
```

### 3. Teste Comparativo via API

```bash
# Executar servidor (terminal 1)
uv run python versiona-ai/directus_server.py

# Executar teste comparativo (terminal 2)
uv run python versiona-ai/test_api_ast_vs_original.py
```

## � Fluxo de Processamento

### Com AST (use_ast=True):

1. **Busca dados do Directus**

   - Modelo: arquivo original
   - Versão: arquivo modificado

2. **Baixa arquivos DOCX**

   - Salva em arquivos temporários
   - Usa API de assets do Directus

3. **Processa com AST**

   - Converte DOCX para AST JSON usando Pandoc
   - Extrai parágrafos estruturados
   - Compara usando SequenceMatcher
   - Detecta tipos corretamente (ALTERACAO, REMOCAO, INSERCAO)

4. **Vincula às cláusulas**

   - Busca tags do modelo
   - Vincula modificações às cláusulas
   - Calcula blocos de modificações

5. **Grava resultados**

   - Salva no cache de diffs
   - Retorna URL para visualização
   - Inclui metadados (tipo, confiança, cláusulas, conteúdo)

6. **Limpa arquivos temporários**
   - Remove DOCXs baixados

## 📊 Exemplo de Saída (Servidor)

```
==================================================================================================
🚀 PROCESSAMENTO COM AST + GRAVAÇÃO NO DIRECTUS
==================================================================================================
Modelo ID: d2699a57-b0ff-472b-a130-626f5fc2852b
Versão ID: 322e56c0-4b38-4e62-b563-8f29a131889c

🔍 Buscando modelo d2699a57-b0ff-472b-a130-626f5fc2852b...
🔍 Buscando versão 322e56c0-4b38-4e62-b563-8f29a131889c...

📋 Modelo: Contrato de Vigência
📋 Versão: v1.2

📥 Baixando arquivo 8a7f3b2c...
✅ Arquivo salvo em: /tmp/tmp9x4k2l1m.docx
📥 Baixando arquivo 5d9e1a4f...
✅ Arquivo salvo em: /tmp/tmpj7n8m3p2.docx

==================================================================================================
🔬 PROCESSANDO COM IMPLEMENTAÇÃO AST
==================================================================================================
📥 Convertendo documento original para AST...
✅ AST do documento original extraído: 45 parágrafos
📥 Convertendo documento modificado para AST...
✅ AST do documento modificado extraído: 46 parágrafos

🔍 Gerando HTML de comparação...
✅ HTML de comparação gerado: 25847 caracteres

🔬 Extraindo modificações do HTML...
✅ Total de modificações extraídas: 8
  - ALTERACAO: 4
  - REMOCAO: 2
  - INSERCAO: 2

==================================================================================================
📊 RESULTADOS DA ANÁLISE AST
==================================================================================================
Total de modificações: 8
  - ALTERACAO: 4
  - REMOCAO: 2
  - INSERCAO: 2

📋 Detalhes das modificações:

  #1 - ALTERACAO
    Cláusula Original: 2.2
    Cláusula Modificada: 2.2
    Original: O prazo de vigência será de 12 (doze) meses...
    Novo: O prazo de vigência será de 24 (vinte e quatro) meses...

  #2 - ALTERACAO
    Cláusula Original: 3.1
    Cláusula Modificada: 3.1
    Original: O valor mensal será de R$ 5.000,00...
    Novo: O valor mensal será de R$ 7.500,00...

  #3 - REMOCAO
    Cláusula Original: 4.5
    Original: Todas as dúvidas sobre este contrato serão resolvidas...

  #4 - INSERCAO
    Cláusula Modificada: 4.6
    Novo: O foro competente para dirimir...

==================================================================================================
💾 GRAVANDO RESULTADOS NO DIRECTUS
==================================================================================================

📝 Gravando 8 modificações no Directus...
✅ Versão atualizada com métricas
  ✅ Modificação #1 (ALTERACAO) criada
  ✅ Modificação #2 (ALTERACAO) criada
  ✅ Modificação #3 (REMOCAO) criada
  ✅ Modificação #4 (INSERCAO) criada
  ✅ Modificação #5 (ALTERACAO) criada
  ✅ Modificação #6 (ALTERACAO) criada
  ✅ Modificação #7 (REMOCAO) criada
  ✅ Modificação #8 (INSERCAO) criada

✅ PROCESSAMENTO CONCLUÍDO!
  - Versão atualizada: True
  - Modificações gravadas: 8

🧹 Arquivos temporários removidos
```

## 🔧 Estrutura de Dados Gravada

### Atualização da Versão

```json
{
  "total_modificacoes": 8,
  "alteracoes": 4,
  "remocoes": 2,
  "insercoes": 2,
  "metodo_deteccao": "AST_PANDOC",
  "status": "processada"
}
```

### Registro de Modificação

```json
{
  "versao": "322e56c0-4b38-4e62-b563-8f29a131889c",
  "tipo": "ALTERACAO",
  "confianca": 0.95,
  "clausula_original": "2.2",
  "clausula_modificada": "2.2",
  "conteudo_original": "O prazo de vigência será de 12 (doze) meses...",
  "conteudo_novo": "O prazo de vigência será de 24 (vinte e quatro) meses...",
  "posicao_linha": 15,
  "posicao_coluna": 0
}
```

## 🎯 Comparação: AST vs Original

| Métrica             | Original | AST       | Diferença     |
| ------------------- | -------- | --------- | ------------- |
| **Precisão Total**  | 51.9%    | **59.3%** | **+7.4%**     |
| ALTERACAO           | 6        | 4         | ✅ Correto    |
| REMOCAO             | 0        | 2         | ✅ Correto    |
| INSERCAO            | 0        | 2         | ✅ Correto    |
| **Total Detectado** | 6        | 8         | (esperado: 7) |

### Vantagens do AST

✅ **Detecção de tipos correta**: Identifica REMOCAO e INSERCAO (não apenas ALTERACAO)
✅ **Estrutura preservada**: Usa estrutura hierárquica do documento
✅ **Números de cláusulas**: Auto-detecta automaticamente
✅ **Formatação robusta**: Trata inconsistências melhor
✅ **Precisão superior**: +7.4% de acurácia

### Quando usar cada implementação

**Use AST quando:**

- Precisão é crítica
- Documentos têm estrutura clara (cláusulas numeradas)
- Detectar tipos específicos (REM/INS) é importante
- Documentos têm formatação inconsistente

**Use Original quando:**

- Velocidade é prioridade
- Documentos sem estrutura clara
- Precisão suficiente para caso de uso
- Modo fallback/backup

## 🔐 Configuração

### Variáveis de Ambiente

```bash
# Token de autenticação do Directus
export DIRECTUS_TOKEN="seu_token_directus"

# URL do Directus (opcional, padrão: https://contract.devix.co)
export DIRECTUS_URL="https://seu-servidor-directus.com"
```

### Dependências

```bash
# Instalar dependências
uv sync

# Verificar Pandoc instalado
pandoc --version
# Deve retornar versão >= 2.x
```

## 🧪 Testes

### Teste com fixture local

```bash
# Usar fixtures de teste (sem Directus)
uv run python versiona-ai/tests/comparar_ast_vs_original.py
```

### Teste com dados reais do Directus

```bash
# Processar versão real
export DIRECTUS_TOKEN="seu_token"
uv run python versiona-ai/test_ast_with_directus.py <modelo_id> <versao_id>
```

## 📝 Notas Importantes

1. **Arquivos DOCX necessários**: AST precisa dos arquivos originais, não apenas texto extraído
2. **Pandoc obrigatório**: Certifique-se de ter Pandoc 2.x ou superior instalado
3. **Token Directus**: Configure `DIRECTUS_TOKEN` para autenticação
4. **Arquivos temporários**: Script limpa automaticamente após processamento
5. **Metadados preservados**: Todas as informações (tags, vinculação, blocos) são mantidas

## 🚧 Próximos Passos

- [ ] Adicionar parâmetro `use_ast` ao endpoint Flask `/processar-versao`
- [ ] Integrar AST no `process_versao()` do `directus_server.py`
- [ ] Criar interface de administração para escolher implementação
- [ ] Adicionar métricas de performance (tempo de processamento)
- [ ] Implementar cache de AST para documentos já processados
- [ ] Adicionar testes de integração end-to-end

## 📚 Referências

- [Pandoc AST Format](https://pandoc.org/filters.html)
- [Comparação Detalhada](./COMPARACAO_AST_VS_ORIGINAL.md)
- [Documentação da API](../API_DOCUMENTATION.md)
- [Directus Server Original](./directus_server.py)
- [Directus Server com AST](./directus_server_ast.py)
