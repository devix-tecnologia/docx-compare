# Ferramentas de Verificação e CLI - Versiona.ai

Este documento descreve os novos métodos de verificação no repositório e os scripts/CLI criados para facilitar o trabalho com processamento de versões.

## 📋 Índice

1. [Métodos de Verificação no Repositório](#métodos-de-verificação-no-repositório)
2. [Scripts Utilitários](#scripts-utilitários)
3. [CLI Principal](#cli-principal)
4. [Exemplos de Uso](#exemplos-de-uso)

---

## 🔍 Métodos de Verificação no Repositório

### `get_resumo_processamento_versao(versao_id)`

Retorna um resumo completo do processamento de uma versão.

**Retorna:**

```python
{
    "versao_id": str,
    "status": str,  # status da versão no Directus
    "total_modificacoes": int,
    "modificacoes_por_categoria": dict[str, int],
    "modificacoes_com_clausula": int,
    "taxa_vinculacao": float,  # em %
    "data_processamento": str,  # ISO 8601
    "modificacoes_sample": list[dict]  # primeiras 3
}
```

**Exemplo:**

```python
from repositorio import DirectusRepository

repo = DirectusRepository(base_url=DIRECTUS_BASE_URL, token=DIRECTUS_TOKEN)
resumo = repo.get_resumo_processamento_versao("73b215cb-...")

print(f"Total: {resumo['total_modificacoes']}")
print(f"Taxa vinculação: {resumo['taxa_vinculacao']}%")
```

---

### `verificar_modificacoes_versao(versao_id)`

Verificação rápida (True/False) do estado do processamento.

**Retorna:**

```python
{
    "sucesso": bool,  # True se tem modificações
    "total_modificacoes": int,
    "possui_vinculacao": bool,  # pelo menos 1 mod tem cláusula
    "status_versao": str,
    "erro": Optional[str]
}
```

**Exemplo:**

```python
verificacao = repo.verificar_modificacoes_versao("73b215cb-...")

if verificacao["sucesso"]:
    print("✅ Versão processada com sucesso!")
else:
    print(f"❌ Erro: {verificacao['erro']}")
```

---

### `comparar_modificacoes_entre_versoes(versao_id_1, versao_id_2)`

Compara modificações entre duas versões (útil para verificar reprocessamento).

**Retorna:**

```python
{
    "versao_1_total": int,
    "versao_2_total": int,
    "diferenca": int,
    "ids_apenas_v1": list[str],
    "ids_apenas_v2": list[str],
    "ids_comuns": list[str],
    "conclusao": str  # "substitui", "acumula", "igual", "parcial"
}
```

**Exemplo:**

```python
# Comparar antes e depois de reprocessamento
comparacao = repo.comparar_modificacoes_entre_versoes("73b215cb-...", "73b215cb-...")

if comparacao["conclusao"] == "substitui":
    print("✅ Reprocessamento substitui corretamente!")
elif comparacao["conclusao"] == "acumula":
    print("❌ Reprocessamento está acumulando duplicatas!")
```

---

## 📂 Scripts Utilitários

### `scripts/verifica_versao.py`

Verifica o estado de processamento de uma versão e exibe resumo formatado.

**Uso:**

```bash
python scripts/verifica_versao.py <versao_id>
```

**Exemplo:**

```bash
python scripts/verifica_versao.py 73b215cb-7e38-4e8c-80a7-4be90f21d654
```

**Saída:**

```
🔍 Consultando versão 73b215cb-7e38-4e8c-80a7-4be90f21d654...

======================================================================
RESUMO DO PROCESSAMENTO DA VERSÃO: 73b215cb-7e38-4e8c-80a7-4be90f21d654
======================================================================

📊 STATUS: concluido
📅 Data Processamento: 2025-01-21T14:30:00
📝 Total Modificações: 42
🔗 Modificações com Cláusula: 35
📈 Taxa de Vinculação: 83.33%

📂 Por Categoria:
   - addition: 15
   - deletion: 10
   - modification: 17

🔍 Amostra de Modificações (primeiras 3):
   1. ID: abc123
      Categoria: addition
      Cláusula: clausula_1_1
      Posição: 100 - 200
   ...

======================================================================

✅ SUCESSO: Versão processada corretamente!
```

**Exit codes:**

- `0` - Versão processada com sucesso
- `1` - Versão sem modificações ou erro
- `2` - Argumentos inválidos

---

### `scripts/confirma_reprocessamento_substitui.py`

Processa uma versão duas vezes e verifica se reprocessamento substitui ou acumula modificações.

**Uso:**

```bash
python scripts/confirma_reprocessamento_substitui.py <versao_id>
```

**Exemplo:**

```bash
python scripts/confirma_reprocessamento_substitui.py 73b215cb-7e38-4e8c-80a7-4be90f21d654
```

**Saída:**

```
======================================================================
TESTE: REPROCESSAMENTO SUBSTITUI OU ACUMULA?
======================================================================

📊 ETAPA 1: Verificando estado inicial...
   Total modificações inicial: 42

📊 ETAPA 2: Iniciando reprocessamento...
✅ Processamento iniciado (status 200)

⏳ Aguardando conclusão do processamento...
   📝 Modificações encontradas: 42

📊 ETAPA 3: Comparando resultados...

📈 Total modificações ANTES: 42
📈 Total modificações DEPOIS: 42
📊 Diferença: 0

======================================================================
✅ SUCESSO: Reprocessamento SUBSTITUI modificações!
   Comportamento correto - não acumula duplicatas
======================================================================
```

**Exit codes:**

- `0` - Reprocessamento SUBSTITUI (correto)
- `1` - Reprocessamento ACUMULA (erro)
- `2` - Erro na execução

---

## 🖥️ CLI Principal

### `versiona_cli.py`

CLI completo para operações de processamento e verificação.

**Comandos disponíveis:**

#### 1. `processa` - Processa uma versão

```bash
python versiona_cli.py processa <versao_id> [--use-ast] [--no-ast] [--api-url URL]
```

**Opções:**

- `--use-ast` - Usar AST no processamento (padrão)
- `--no-ast` - Não usar AST
- `--api-url` - URL da API (padrão: config ou localhost:5005)

**Exemplo:**

```bash
python versiona_cli.py processa 73b215cb-... --use-ast
```

---

#### 2. `verifica` - Verifica estado de uma versão

```bash
python versiona_cli.py verifica <versao_id>
```

**Exemplo:**

```bash
python versiona_cli.py verifica 73b215cb-...
```

**Saída:**

```
🔍 Verificando versão 73b215cb-...

✅ SUCESSO
Status: concluido
Total Modificações: 42
```

---

#### 3. `reprocessa` - Reprocessa e compara

```bash
python versiona_cli.py reprocessa <versao_id> [--use-ast]
```

**Exemplo:**

```bash
python versiona_cli.py reprocessa 73b215cb-... --use-ast
```

**Saída:**

```
🔄 Reprocessando versão 73b215cb-...
   📊 Total modificações antes: 42

🚀 Iniciando processamento...
   ✅ Processamento iniciado
   ⏳ Aguardando conclusão...
   📝 Modificações: 42
   ✅ Processamento concluído em 45.2s

   📊 Total modificações depois: 42
   ✅ Reprocessamento SUBSTITUIU modificações (correto)

✅ SUCESSO
Antes: 42 | Depois: 42
Substituiu: Sim
```

---

#### 4. `resumo` - Exibe resumo detalhado

```bash
python versiona_cli.py resumo <versao_id>
```

**Exemplo:**

```bash
python versiona_cli.py resumo 73b215cb-...
```

---

## 📚 Exemplos de Uso

### 1. Fluxo Completo: Processar e Verificar

```bash
# 1. Processar versão
python versiona_cli.py processa 73b215cb-... --use-ast

# 2. Verificar resultado
python scripts/verifica_versao.py 73b215cb-...

# 3. Ver resumo detalhado
python versiona_cli.py resumo 73b215cb-...
```

---

### 2. Testar Reprocessamento

```bash
# Opção 1: Script dedicado (mais detalhado)
python scripts/confirma_reprocessamento_substitui.py 73b215cb-...

# Opção 2: CLI
python versiona_cli.py reprocessa 73b215cb-...
```

---

### 3. Integração com Scripts Python

```python
from pathlib import Path
import sys

# Adicionar ao path
sys.path.insert(0, str(Path.cwd() / "versiona-ai"))

import config
from repositorio import DirectusRepository

# Criar repositório
repo = DirectusRepository(
    base_url=config.DIRECTUS_BASE_URL,
    token=config.DIRECTUS_TOKEN
)

# Verificar versão
verificacao = repo.verificar_modificacoes_versao("73b215cb-...")

if verificacao["sucesso"]:
    # Buscar resumo completo
    resumo = repo.get_resumo_processamento_versao("73b215cb-...")

    print(f"Total: {resumo['total_modificacoes']}")
    print(f"Taxa vinculação: {resumo['taxa_vinculacao']}%")

    # Iterar por categoria
    for cat, count in resumo["modificacoes_por_categoria"].items():
        print(f"  {cat}: {count}")
else:
    print(f"Erro: {verificacao['erro']}")
```

---

### 4. Automação com Shell Scripts

```bash
#!/bin/bash
# processar_e_verificar.sh

VERSAO_ID="73b215cb-7e38-4e8c-80a7-4be90f21d654"

echo "Processando versão ${VERSAO_ID}..."
python versiona_cli.py processa "${VERSAO_ID}" --use-ast

if [ $? -eq 0 ]; then
    echo "Verificando resultado..."
    python scripts/verifica_versao.py "${VERSAO_ID}"
    exit $?
else
    echo "Erro no processamento"
    exit 1
fi
```

---

## 🚀 Deploy e Produção

Após modificar os métodos do repositório ou criar novos scripts:

1. **Rodar testes:**

   ```bash
   uv run pytest tests/ -v
   ```

2. **Verificar lint:**

   ```bash
   uv run ruff check . --fix
   uv run ruff format .
   ```

3. **Deploy:**

   ```bash
   ./deploy-caprover.sh
   ```

4. **Testar em produção:**

   ```bash
   # Aguardar 60s para app inicializar
   sleep 60

   # Verificar health
   curl https://ignai-contract-ia.paas.node10.de.vix.br/health

   # Testar verificação
   python scripts/verifica_versao.py <versao_id>
   ```

---

## 📊 Exit Codes Padrão

Todos os scripts e comandos do CLI seguem a mesma convenção:

- **0** - Sucesso
- **1** - Erro na operação (processamento falhou, versão sem modificações, etc)
- **2** - Erro de argumentos ou uso incorreto
- **3** - Erro inesperado (exception)

Isso facilita integração com CI/CD e automação:

```bash
python versiona_cli.py processa 73b215cb-... || exit 1
python scripts/verifica_versao.py 73b215cb-... || exit 1
```

---

## 🔧 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'config'"

**Solução:** Executar scripts a partir do diretório raiz:

```bash
cd /Users/sidarta/repositorios/docx-compare
python scripts/verifica_versao.py <versao_id>
```

---

### Erro: "403 Forbidden" ao consultar Directus

**Causa:** Tentando acessar campos que não existem no schema.

**Solução:** Os métodos já tratam isso automaticamente, consultando apenas campos conhecidos. Se persistir, verificar se o token tem permissões corretas.

---

### Timeout ao processar

**Causa:** Processamento demora mais que o timeout configurado.

**Solução:** Aumentar timeout no método `processar_versao()` ou `aguardar_processamento()`:

```python
resultado = processar_versao(versao_id, use_ast=True)
# Timeout padrão: 300s (5 minutos)
```

Para processamentos longos, editar o timeout em `versiona_cli.py` linha ~95.

---

## 📝 Contribuindo

Ao adicionar novos métodos de verificação:

1. **Adicionar método em `repositorio.py`**

   - Usar typing completo
   - Documentar com docstring detalhado
   - Retornar dict estruturado

2. **Criar testes em `tests/test_repositorio.py`**

   - Mock HTTP com `responses`
   - Testar success e error cases
   - Coverage > 85%

3. **Atualizar este README**

   - Documentar novo método
   - Adicionar exemplos de uso
   - Explicar return structure

4. **Criar script se necessário**
   - Seguir padrão dos scripts existentes
   - Exit codes consistentes
   - Mensagens formatadas e claras

---

## 📞 Contato

Para dúvidas ou sugestões sobre as ferramentas de verificação, abrir issue no repositório.

---

**Última atualização:** 2025-01-21
**Versão:** 1.0.0
