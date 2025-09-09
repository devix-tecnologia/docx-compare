# Processador de Limpeza de Modificações

## 📋 Visão Geral

O **Processador de Limpeza** monitora versões de contratos que voltaram para o status `draft` e remove automaticamente todas as modificações associadas a essas versões. Isso permite que as versões sejam reprocessadas do zero quando necessário.

## 🎯 Funcionalidades

### 🔍 **Monitoramento Automático**

- Identifica versões com status `draft` que possuem modificações
- Executa limpeza automática em intervalos regulares
- Integrado ao orquestrador principal do sistema

### 🧹 **Limpeza Inteligente**

- Remove todas as modificações de uma versão específica
- Mantém logs detalhados das operações
- Suporte a modo `dry-run` para simulação

### ⚡ **Execução Flexível**

- **Automática**: Via orquestrador (executada em paralelo com outros processadores)
- **Manual**: Via comando direto para versões específicas
- **Simulação**: Modo dry-run para testar antes de executar

## 🚀 Como Usar

### 1. **Execução via Orquestrador (Recomendado)**

O processador de limpeza roda automaticamente junto com os outros processadores:

```bash
# Ciclo único (para testes)
make run-orquestrador-single

# Monitoramento contínuo
make run-orquestrador
```

### 2. **Execução Manual**

#### Ciclo único de limpeza:

```bash
uv run python src/docx_compare/processors/processador_limpeza.py --single-run
```

#### Simulação (dry-run):

```bash
uv run python src/docx_compare/processors/processador_limpeza.py --single-run --dry-run
```

#### Monitoramento contínuo:

```bash
# Com intervalo padrão (5 minutos)
uv run python src/docx_compare/processors/processador_limpeza.py

# Com intervalo personalizado (10 minutos)
uv run python src/docx_compare/processors/processador_limpeza.py --intervalo 600
```

### 3. **Limpeza Manual de Versão Específica**

Você também pode usar o agrupador de modificações diretamente:

```python
from src.docx_compare.utils.agrupador_modificacoes import AgrupadorModificacoes

agrupador = AgrupadorModificacoes(
    directus_base_url="https://contract.devix.co",
    directus_token="seu-token",
)

# Simular limpeza
resultado = agrupador.limpar_modificacoes_versao("versao-id", dry_run=True)

# Executar limpeza real
resultado = agrupador.limpar_modificacoes_versao("versao-id", dry_run=False)
```

## 📊 Exemplo de Saída

```
🚀 Iniciando ciclo de limpeza - 09/09/2025 08:44:17
🏃‍♂️ Modo DRY-RUN ativo - nenhuma alteração será feita

🔍 08:44:17 - Buscando versões em draft com modificações...
📋 Encontradas 2 versões em draft
   ✅ Versão 1.2 (abc12345...) tem 15 modificações
   ✅ Versão 2.1 (def67890...) tem 8 modificações
🎯 2 versões draft precisam de limpeza

🧹 Processando limpeza - Versão 1.2 (abc12345...) - 15 modificações
🔍 Encontradas 15 modificações para remoção
🏃‍♂️ DRY-RUN: Simulando remoção das modificações

📊 Limpeza concluída:
   🔍 Modificações encontradas: 15
   🗑️ Modificações removidas: 15
   ❌ Falhas: 0

📊 Ciclo de limpeza concluído:
   📝 Versões processadas: 2
   ✅ Sucessos: 2
   ❌ Erros: 0
   🗑️ Total de modificações removidas: 23
```

## ⚙️ Configuração

### Variáveis de Ambiente

```env
DIRECTUS_BASE_URL=https://contract.devix.co
DIRECTUS_TOKEN=seu-token-aqui
```

### Integração com Orquestrador

O processador está automaticamente integrado no `orquestrador.py`:

- **Modo Paralelo**: Executa simultaneamente com processador automático e de modelo
- **Modo Sequencial**: Executa após os outros processadores
- **Independente**: Não depende do sucesso dos outros processadores

## 🔧 Casos de Uso

### 1. **Versão Rejeitada**

```
Status: concluido → draft
Ação: Todas as modificações são removidas automaticamente
Resultado: Versão pronta para reprocessamento
```

### 2. **Correção de Processamento**

```
Status: erro → draft
Ação: Limpeza das modificações parciais/corrompidas
Resultado: Estado limpo para novo processamento
```

### 3. **Reprocessamento Solicitado**

```
Status: concluido → draft (manual)
Ação: Limpeza completa das modificações existentes
Resultado: Versão zerada para nova análise
```

## 🛡️ Segurança

- **Modo Dry-Run**: Sempre teste com `--dry-run` antes de executar em produção
- **Logs Detalhados**: Todas as operações são registradas com timestamps
- **Reversibilidade**: ⚠️ **A limpeza é irreversível** - certifique-se antes de executar
- **Permissões**: Requer token Directus com permissões de escrita em `modificacao`

## 📈 Monitoramento

### Através do Orquestrador:

```bash
# Status via API
curl http://localhost:5007/status

# Logs em tempo real
tail -f logs/orquestrador.log
```

### Indicadores de Sucesso:

- ✅ **Processador limpeza**: Status OK no orquestrador
- 🗑️ **Modificações removidas**: Count > 0 quando há versões draft
- 📊 **Zero erros**: Todas as operações concluídas com sucesso

## 🎉 Benefícios

1. **🔄 Automatização Total**: Sem intervenção manual necessária
2. **🛡️ Segurança**: Modo dry-run para validação prévia
3. **📊 Visibilidade**: Logs completos de todas as operações
4. **⚡ Performance**: Execução em paralelo sem impacto nos outros processadores
5. **🎯 Precisão**: Remove apenas modificações de versões em draft
6. **🔧 Flexibilidade**: Configurável via parâmetros e variáveis de ambiente

---

**✅ Status**: Implementado e testado
**🔗 Integração**: Ativo no orquestrador principal
**🎯 Próximos passos**: Monitoramento em produção e ajustes de performance
