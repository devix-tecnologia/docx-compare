# Configuração de Webhooks no Directus

Este documento explica como configurar webhooks no Directus para processar automaticamente modelos e versões quando o status mudar para "processar".

## 📋 Visão Geral

O sistema possui dois endpoints que podem ser acionados via webhook:

1. **Processar Modelo** - `/api/process-modelo` - Processa modelo completo com todas versões
2. **Processar Versão** - `/api/process` - Processa versão individual

## 🔧 Configuração no Directus

### 1. Webhook para Processar Modelo

**Quando:** Status do modelo_contrato mudar para "processar"

**Configuração:**

1. Acesse o Directus Admin
2. Vá em **Settings** → **Webhooks**
3. Clique em **Create Webhook**
4. Configure:

```yaml
Nome: Processar Modelo de Contrato
Método: POST
URL: https://ignai-contract-ia.paas.node10.de.vix.br/api/process-modelo
Status: Ativo
Coleção: modelo_contrato
Ação: items.update
Filtros:
  - Campo: status
  - Operador: igual a
  - Valor: processar
```

**Body (JSON):**

```json
{
  "modelo_id": "{{$trigger.key}}",
  "use_ast": true,
  "process_tags": true,
  "process_versions": true,
  "dry_run": false
}
```

**Headers:**

```
Content-Type: application/json
```

### 2. Webhook para Processar Versão

**Quando:** Status da versão mudar para "processar"

**Configuração:**

1. Acesse o Directus Admin
2. Vá em **Settings** → **Webhooks**
3. Clique em **Create Webhook**
4. Configure:

```yaml
Nome: Processar Versão
Método: POST
URL: https://ignai-contract-ia.paas.node10.de.vix.br/api/process
Status: Ativo
Coleção: versao
Ação: items.update
Filtros:
  - Campo: status
  - Operador: igual a
  - Valor: processar
```

**Body (JSON):**

```json
{
  "versao_id": "{{$trigger.key}}",
  "use_ast": true,
  "mock": false
}
```

**Headers:**

```
Content-Type: application/json
```

## 🔐 Segurança (Opcional)

Para adicionar segurança aos webhooks, você pode:

### Opção 1: Token no Header

Adicione um header de autenticação:

**Headers:**

```
Content-Type: application/json
X-Webhook-Secret: seu-token-secreto-aqui
```

### Opção 2: Validação de IP

Configure o firewall para aceitar requisições apenas do IP do Directus.

## 📊 Variáveis Disponíveis do Directus

O Directus fornece as seguintes variáveis nos webhooks:

- `{{$trigger.key}}` - ID do item atualizado
- `{{$trigger.payload}}` - Dados completos do item
- `{{$trigger.event}}` - Tipo de evento (create, update, delete)
- `{{$trigger.collection}}` - Nome da coleção
- `{{$accountability.user}}` - ID do usuário que fez a ação

## 🎯 Fluxos de Trabalho

### Fluxo: Processar Modelo Completo

1. Usuário edita modelo_contrato no Directus
2. Usuário muda status para "processar"
3. Webhook dispara automaticamente
4. Sistema processa:
   - Extrai tags do modelo
   - Busca todas as versões vinculadas
   - Processa cada versão com AST
   - Grava modificações no Directus
5. Status do modelo é atualizado automaticamente

### Fluxo: Processar Versão Individual

1. Usuário edita versão no Directus
2. Usuário muda status para "processar"
3. Webhook dispara automaticamente
4. Sistema processa:
   - Compara documentos (original vs modificado)
   - Detecta modificações com AST
   - Vincula a cláusulas
   - Grava modificações no Directus
5. Status da versão é atualizado para "processada"

## 🧪 Testando os Webhooks

### Teste Manual via Curl

**Processar Modelo:**

```bash
curl -X POST "https://ignai-contract-ia.paas.node10.de.vix.br/api/process-modelo" \
  -H "Content-Type: application/json" \
  -d '{
    "modelo_id": "d2699a57-b0ff-472b-a130-626f5fc2852b",
    "use_ast": true,
    "process_tags": false,
    "process_versions": true
  }'
```

**Processar Versão:**

```bash
curl -X POST "https://ignai-contract-ia.paas.node10.de.vix.br/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "versao_id": "322e56c0-4b38-4e62-b563-8f29a131889c",
    "use_ast": true
  }'
```

### Verificar Logs

Acesse os logs do CapRover para verificar o processamento:

```
https://captain.paas.node10.de.vix.br/
```

## 📈 Monitoramento

### Verificar Status dos Webhooks

No Directus:

1. Vá em **Settings** → **Webhooks**
2. Clique no webhook configurado
3. Veja a aba **Logs** para histórico de disparos

### Métricas no Directus

Após o processamento, você pode verificar:

**Para Modelos:**

```sql
SELECT
  m.nome,
  m.status,
  COUNT(DISTINCT v.id) as total_versoes,
  COUNT(mod.id) as total_modificacoes
FROM modelo_contrato m
LEFT JOIN contrato c ON c.modelo_contrato = m.id
LEFT JOIN versao v ON v.contrato = c.id
LEFT JOIN modificacao mod ON mod.versao = v.id
WHERE m.id = 'd2699a57-b0ff-472b-a130-626f5fc2852b'
GROUP BY m.id;
```

**Para Versões:**

```sql
SELECT
  v.versao,
  v.status,
  COUNT(m.id) as total_modificacoes,
  SUM(CASE WHEN m.categoria = 'ALTERACAO' THEN 1 ELSE 0 END) as alteracoes,
  SUM(CASE WHEN m.categoria = 'INSERCAO' THEN 1 ELSE 0 END) as insercoes,
  SUM(CASE WHEN m.categoria = 'REMOCAO' THEN 1 ELSE 0 END) as remocoes
FROM versao v
LEFT JOIN modificacao m ON m.versao = v.id
WHERE v.id = '322e56c0-4b38-4e62-b563-8f29a131889c'
GROUP BY v.id;
```

## ⚠️ Troubleshooting

### Webhook não dispara

1. Verifique se o webhook está **Ativo**
2. Confirme os **Filtros** (status = "processar")
3. Teste com curl manualmente
4. Verifique logs do Directus

### Erro 404 ou 500

1. Verifique se a URL está correta
2. Confirme que o servidor está rodando
3. Verifique logs do CapRover
4. Teste o endpoint manualmente

### Processamento não completa

1. Verifique se os arquivos DOCX existem
2. Confirme permissões no Directus
3. Verifique se o DIRECTUS_TOKEN está configurado
4. Analise logs do servidor

## 🔄 Atualizando Status Automaticamente

Para atualizar o status automaticamente após o processamento, os endpoints já fazem isso. O sistema atualiza:

- **Modelo:** Status permanece "processar" durante execução
- **Versão:** Status muda para "processada" após conclusão

## 📚 Recursos Adicionais

- [Documentação de Webhooks do Directus](https://docs.directus.io/configuration/webhooks.html)
- [Documentação da API (Swagger)](https://ignai-contract-ia.paas.node10.de.vix.br/docs/)
- [Código fonte dos endpoints](https://github.com/devix-tecnologia/docx-compare)

## 🎓 Exemplo Completo

Aqui está um exemplo passo-a-passo de como configurar e testar:

### 1. Configure o Webhook no Directus

Siga as instruções da seção "Configuração no Directus" acima.

### 2. Teste Manualmente

```bash
# 1. Obtenha um modelo_id do Directus
curl -H "Authorization: Bearer ${DIRECTUS_TOKEN}" \
  "https://contract.devix.co/items/modelo_contrato?limit=1" | jq '.data[0].id'

# 2. Teste o webhook manualmente
curl -X POST "https://ignai-contract-ia.paas.node10.de.vix.br/api/process-modelo" \
  -H "Content-Type: application/json" \
  -d '{
    "modelo_id": "SEU_MODELO_ID_AQUI",
    "use_ast": true,
    "process_tags": false,
    "process_versions": true
  }' | jq '.'
```

### 3. Teste via Directus

1. Abra um modelo_contrato no Directus
2. Mude o status para "processar"
3. Salve
4. Aguarde alguns segundos
5. Verifique os resultados:
   - Versões processadas
   - Modificações detectadas
   - Status atualizado

### 4. Monitore

- Verifique logs no CapRover
- Confirme modificações no Directus
- Valide métricas de processamento

---

**Última atualização:** 2025-10-19
**Versão da API:** 1.0
**Ambiente:** Production (CapRover)
