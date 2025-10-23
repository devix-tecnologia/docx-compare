# Diagrama de Fluxo dos Webhooks

## Fluxo de Processamento via Webhook

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Directus as Directus CMS
    participant Webhook as Webhook System
    participant API as Versiona.ai API
    participant DB as Database

    Note over User,DB: Fluxo de Processamento de Modelo

    User->>Directus: Edita modelo_contrato
    User->>Directus: Muda status para "processar"
    Directus->>Webhook: Trigger webhook (items.update)
    Webhook->>API: POST /api/process-modelo

    Note over API: Valida request

    API->>Directus: Busca dados do modelo
    Directus-->>API: Retorna modelo + tags

    API->>Directus: Busca versões vinculadas
    Directus-->>API: Retorna lista de versões

    loop Para cada versão
        API->>API: Processa com AST (Pandoc)
        API->>API: Detecta modificações
        API->>API: Vincula a cláusulas
        API->>Directus: Grava modificações
    end

    API->>Directus: Atualiza status do modelo
    API-->>Webhook: Retorna resultado
    Webhook-->>Directus: Log de execução
    Directus-->>User: Notifica conclusão

    Note over User,DB: Fluxo de Processamento de Versão

    User->>Directus: Edita versão
    User->>Directus: Muda status para "processar"
    Directus->>Webhook: Trigger webhook (items.update)
    Webhook->>API: POST /api/process

    API->>Directus: Busca arquivos DOCX
    Directus-->>API: Retorna original + modificado

    API->>API: Converte para AST (Pandoc)
    API->>API: Compara documentos
    API->>API: Detecta modificações
    API->>API: Classifica (ALTERACAO, REMOCAO, INSERCAO)

    API->>Directus: Grava modificações
    API->>Directus: Atualiza status para "processada"

    API-->>Webhook: Retorna diff_id
    Webhook-->>Directus: Log de execução
    Directus-->>User: Notifica conclusão
```

## Arquitetura de Webhooks

```mermaid
graph TB
    subgraph Directus CMS
        MC[modelo_contrato]
        V[versao]
        W[Webhook System]
    end

    subgraph "Versiona.ai API"
        PM[POST /api/process-modelo]
        PV[POST /api/process]
        AST[AST Processor]
        DIFF[Diff Generator]
    end

    subgraph Database
        TAG[Tags]
        MOD[Modificações]
        CLAUSE[Cláusulas]
    end

    MC -->|status=processar| W
    V -->|status=processar| W

    W -->|trigger| PM
    W -->|trigger| PV

    PM --> AST
    PV --> AST

    AST --> DIFF
    DIFF --> MOD

    MOD -->|vincula| CLAUSE
    MOD -->|referencia| TAG

    style MC fill:#e1f5ff
    style V fill:#e1f5ff
    style W fill:#fff4e6
    style PM fill:#f3e5f5
    style PV fill:#f3e5f5
    style AST fill:#e8f5e9
    style DIFF fill:#e8f5e9
```

## Estados e Transições

```mermaid
stateDiagram-v2
    [*] --> Rascunho: Criar modelo/versão

    Rascunho --> Processar: Usuário aciona

    Processar --> Processando: Webhook dispara

    Processando --> Processada: Sucesso
    Processando --> Erro: Falha

    Erro --> Processar: Retry

    Processada --> Revisao: Revisar resultados
    Revisao --> Aprovada: Aprovar
    Revisao --> Processar: Reprocessar

    Aprovada --> [*]

    note right of Processar
        Webhook é disparado
        quando status = "processar"
    end note

    note right of Processando
        API processa com AST
        Detecta modificações
        Vincula cláusulas
    end note
```

## Dados Trafegados

### Webhook de Modelo

```json
{
  "trigger": "items.update",
  "collection": "modelo_contrato",
  "key": "d2699a57-b0ff-472b-a130-626f5fc2852b",
  "payload": {
    "status": "processar"
  }
}
```

**Request para API:**

```json
{
  "modelo_id": "d2699a57-b0ff-472b-a130-626f5fc2852b",
  "use_ast": true,
  "process_tags": true,
  "process_versions": true,
  "dry_run": false
}
```

**Response da API:**

```json
{
  "status": "sucesso",
  "modelo_id": "d2699a57-b0ff-472b-a130-626f5fc2852b",
  "tags_encontradas": 11,
  "tags_criadas": 11,
  "versoes_processadas": 1,
  "total_modificacoes": 8
}
```

### Webhook de Versão

```json
{
  "trigger": "items.update",
  "collection": "versao",
  "key": "322e56c0-4b38-4e62-b563-8f29a131889c",
  "payload": {
    "status": "processar"
  }
}
```

**Request para API:**

```json
{
  "versao_id": "322e56c0-4b38-4e62-b563-8f29a131889c",
  "use_ast": true,
  "mock": false
}
```

**Response da API:**

```json
{
  "success": true,
  "diff_id": "e1133041-16dd-4893-a92c-8226319cebad",
  "url": "http://localhost:8000/view/e1133041-16dd-4893-a92c-8226319cebad",
  "modificacoes": [...],
  "metricas": {
    "total_modificacoes": 8,
    "alteracoes": 4,
    "remocoes": 2,
    "insercoes": 2
  },
  "metodo": "AST_PANDOC"
}
```
