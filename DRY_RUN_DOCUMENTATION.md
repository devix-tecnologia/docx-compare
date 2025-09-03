# Funcionalidade Dry-Run - Documentação

## Visão Geral

A funcionalidade `--dry-run` foi implementada para permitir a execução da API e do processador automático em modo de análise, sem fazer modificações nos registros do Directus. Isso é útil para:

- **Teste e validação**: Verificar se a lógica está funcionando corretamente
- **Desenvolvimento**: Testar alterações sem afetar o banco de dados
- **Demonstrações**: Mostrar a funcionalidade sem criar dados reais
- **Depuração**: Analisar problemas sem efeitos colaterais

## Componentes Atualizados

### 1. API Simple (`api_simple.py`)

#### Modificações Realizadas
- ✅ Adicionado `argparse` para suporte a linha de comando
- ✅ Parâmetro `--dry-run` no CLI
- ✅ Função `update_versao_status()` com parâmetro `dry_run`
- ✅ Função `save_modifications_to_directus()` com parâmetro `dry_run`
- ✅ Endpoint `/compare_versao` aceita `dry_run` no JSON
- ✅ Mensagens específicas para modo dry-run

#### Uso

**Via linha de comando:**
```bash
# Modo normal
python api_simple.py

# Modo dry-run
python api_simple.py --dry-run

# Com parâmetros customizados
python api_simple.py --dry-run --host localhost --port 8000
```

**Via Makefile:**
```bash
# Modo normal
make run-api

# Modo dry-run
make run-api-dry
```

**Via API JSON (endpoint /compare_versao):**
```json
{
    "versao_id": "123",
    "dry_run": true
}
```

### 2. Processador Automático (`processador_automatico.py`)

#### Modificações Realizadas
- ✅ Adicionado `argparse` para suporte a linha de comando
- ✅ Parâmetro `--dry-run` no CLI
- ✅ Função `update_versao_status()` com parâmetro `dry_run`
- ✅ Função `processar_versao()` com parâmetro `dry_run`
- ✅ Função `loop_processador()` com parâmetro `dry_run`
- ✅ Mensagens específicas para modo dry-run

#### Uso

**Via linha de comando:**
```bash
# Modo normal
python processador_automatico.py

# Modo dry-run
python processador_automatico.py --dry-run

# Com parâmetros customizados
python processador_automatico.py --dry-run --host localhost --port 8001
```

**Via Makefile:**
```bash
# Modo normal
make run-processor

# Modo dry-run
make run-processor-dry
```

### 3. Makefile

#### Novos Comandos
- ✅ `run-api-dry`: Executa API em modo dry-run
- ✅ `run-processor-dry`: Executa processador em modo dry-run

## Comportamento em Modo Dry-Run

### O que NÃO é executado:
- ❌ Atualizações no Directus (PATCH/POST)
- ❌ Criação de registros de modificação
- ❌ Alteração de status das versões
- ❌ Gravação de dados no banco

### O que É executado:
- ✅ Download de arquivos do Directus
- ✅ Conversão e análise de documentos
- ✅ Geração de HTML de comparação
- ✅ Cálculo de diferenças e modificações
- ✅ Logs detalhados do processo
- ✅ Retorno de dados simulados

### Mensagens de Identificação

Todos os comandos em modo dry-run exibem claramente:
```
🏃‍♂️ DRY-RUN: [descrição da ação não executada]
🏃‍♂️ MODO DRY-RUN ATIVADO - Nenhuma alteração será feita no Directus
```

## Exemplos de Uso

### 1. Testar API com Versão Específica

```bash
# Iniciar API em modo dry-run
make run-api-dry

# Em outro terminal, fazer requisição
curl -X POST http://localhost:5002/compare_versao \
  -H "Content-Type: application/json" \
  -d '{"versao_id": "sua-versao-id", "dry_run": true}'
```

### 2. Testar Processador Automático

```bash
# Executar processador em modo dry-run
make run-processor-dry
```

### 3. Validar Configurações

```bash
# Testar com configurações customizadas
python api_simple.py --dry-run --host 0.0.0.0 --port 9000
python processador_automatico.py --dry-run --host 127.0.0.1 --port 9001
```

## Validação e Testes

### Testes Automatizados
O arquivo `tests/test_dry_run_api.py` contém:
- ✅ Teste de argumentos CLI
- ✅ Validação de help commands  
- ✅ Verificação de assinaturas de função
- ✅ Validação de comandos Makefile
- ✅ Teste de mensagens dry-run

### Executar Testes
```bash
python tests/test_dry_run_api.py
```

## Estrutura de Dados de Retorno

### Em Modo Normal
```json
{
  "id": "versao-real-id",
  "status": "concluido",
  "observacao": "Comparação concluída em 01/01/2024 10:00...",
  "modificacoes": [...]
}
```

### Em Modo Dry-Run
```json
{
  "id": "versao-id",
  "status": "concluido", 
  "observacao": "Comparação concluída em 01/01/2024 10:00...",
  "modificacoes": [
    {
      "id": "dry-run-1",
      "categoria": "texto",
      "conteudo": "...",
      "status": "draft"
    }
  ]
}
```

## Compatibilidade

### Retrocompatibilidade
- ✅ Código existente continua funcionando
- ✅ APIs mantêm comportamento padrão quando `dry_run` não especificado
- ✅ Makefile mantém comandos originais

### Dependências
- ✅ Nenhuma nova dependência externa
- ✅ Usa apenas `argparse` (biblioteca padrão Python)
- ✅ Mantém todas as funcionalidades existentes

## Resumo dos Arquivos Modificados

1. **`api_simple.py`**: Adicionado argparse, dry-run em funções e endpoints
2. **`processador_automatico.py`**: Adicionado argparse, dry-run em funções de processamento
3. **`Makefile`**: Novos comandos `run-api-dry` e `run-processor-dry`
4. **`tests/test_dry_run_api.py`**: Testes para validar funcionalidade

## Próximos Passos

Para usar a funcionalidade:

1. **Para desenvolvimento**: Use `make run-api-dry` ou `make run-processor-dry`
2. **Para testes de API**: Adicione `"dry_run": true` nas requisições JSON
3. **Para validação**: Execute os testes com `python tests/test_dry_run_api.py`

A implementação é completa e está pronta para uso em desenvolvimento e testes! 🎉
