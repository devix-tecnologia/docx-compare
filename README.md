# 📄 Sistema de Processamento Automático de Documentos DOCX

## 🚀 Execução Rápida

### Processador Automático

```bash
# Executar o processador automático (principal)
uv run python processador_automatico.py

# Executar com logs detalhados
uv run python processador_automatico.py --verbose

# Executar em modo simulação (sem alterações)
uv run python processador_automatico.py --dry-run
```

### Comparação Local de Documentos

```bash
# Comparar dois documentos DOCX
uv run python docx_diff_viewer.py original.docx modificado.docx

# Exemplo com arquivos do projeto
uv run python docx_diff_viewer.py documentos/doc-rafael-original.docx documentos/doc-rafael-alterado.docx
```

### Endpoints de Monitoramento

- **Dashboard**: http://localhost:5005
- **Health Check**: http://localhost:5005/health
- **Métricas**: http://localhost:5005/metrics
- **Resultados**: http://localhost:5005/results

---

Sistema de processamento automático para comparação de documentos DOCX integrado com Directus CMS. Monitora continuamente o Directus em busca de versões para processar e gera comparações visuais automaticamente.

## 🚀 Funcionalidades

### 🤖 Processamento Automático

- **Monitoramento Contínuo**: Busca versões com status "processar" no Directus a cada minuto
- **Processamento Inteligente**:
  - Primeira versão: compara com template do modelo de contrato
  - Versões subsequentes: compara com versão anterior
- **Transação Única**: Salva status, observações e modificações em uma única operação
- **Signal Handling**: Encerramento gracioso com SIGINT/SIGTERM/SIGHUP
- **Upload Automático**: Envia relatórios HTML para o Directus
- **Cache Inteligente**: Evita downloads desnecessários

### 🔧 CLI - Comparação Local

- **Comparação Direta**: Comparação local de arquivos DOCX
- **HTML Responsivo**: Visualização profissional das diferenças
- **Filtro Lua**: Remove tags HTML desnecessárias com Pandoc
- **CSP Compatível**: HTML gerado sem estilos inline para máxima segurança

### 📊 Monitoramento e Observabilidade

- **Dashboard Web**: Interface visual para monitoramento do sistema
- **Endpoints REST**: APIs para verificação de saúde e métricas
- **Modo Debug**: Logs detalhados para troubleshooting
- **Modo Dry-Run**: Simulação sem alterações no banco
- **Listagem de Resultados**: Visualização de todos os processamentos realizados

## 📋 Pré-requisitos

- Python 3.8+
- Pandoc
- Directus CMS configurado
- Arquivo Lua filter: `comments_html_filter_direct.lua`

### Instalação do Pandoc

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc

# Windows
# Baixe de: https://pandoc.org/installing.html
```

## 🔧 Instalação

### Opção 1: Com UV (Recomendado)

```bash
# 1. Clone o repositório
git clone <repository-url>
cd docx-compare

# 2. Instale o UV (se não tiver)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Instale as dependências Python
uv sync

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações do Directus
```

### Opção 2: Com pip tradicional

```bash
# 1. Clone o repositório
git clone <repository-url>
cd docx-compare

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou: venv\Scripts\activate  # Windows

# 3. Instale as dependências Python
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações do Directus
```

## 🎯 Uso

### 🤖 Processador Automático (Principal)

#### 1. Configurar o .env

```env
# Configurações do Directus
DIRECTUS_BASE_URL=https://your-directus-instance.com
DIRECTUS_TOKEN=your-directus-token-here

# Configurações do Processador
VERBOSE_MODE=false
CHECK_INTERVAL=60
REQUEST_TIMEOUT=30

# Diretórios
RESULTS_DIR=results
```

#### 2. Executar o Processador

```bash
# Modo normal (produção)
uv run python processador_automatico.py

# Modo debug com logs detalhados
uv run python processador_automatico.py --verbose

# Modo dry-run (análise sem alterações)
uv run python processador_automatico.py --dry-run

# Configurar intervalo personalizado
uv run python processador_automatico.py --interval 30 --timeout 60
```

#### 3. Endpoints de Monitoramento

| Endpoint                  | Descrição                                |
| ------------------------- | ---------------------------------------- |
| `GET /`                   | Dashboard web com informações do sistema |
| `GET /health`             | Verificação de saúde                     |
| `GET /status`             | Status detalhado do processador          |
| `GET /metrics`            | Métricas do sistema                      |
| `GET /results`            | Lista de resultados processados          |
| `GET /outputs/<filename>` | Visualizar resultado específico          |

#### 4. Monitoramento Web

Acesse `http://localhost:5005` para ver o dashboard de monitoramento com:

- Status do processador em tempo real
- Lista de todos os endpoints disponíveis
- Informações de configuração
- Última atualização do sistema

### CLI - Comparação Local (Para desenvolvimento/testes)

```bash
# Com UV (recomendado)
uv run python docx_diff_viewer.py original.docx modificado.docx
# Criará automaticamente outputs/resultado.html

# Ou especificar arquivo de saída:
uv run python docx_diff_viewer.py original.docx modificado.docx outputs/minha_comparacao.html

# Com Python tradicional
python docx_diff_viewer.py original.docx modificado.docx
```

**Exemplo:**

```bash
uv run python docx_diff_viewer.py documentos/doc-rafael-original.docx documentos/doc-rafael-alterado.docx
# Criará automaticamente outputs/resultado.html
```

O processador automático monitora o Directus continuamente e processa versões automaticamente.

#### 1. Executar o Processador

```bash
# Com UV (recomendado)
uv run python processador_automatico.py

# Com Python tradicional
python processador_automatico.py
```

#### 2. Endpoints de Monitoramento

O processador executa na porta 5005 e oferece:

| Endpoint              | Método | Descrição                           |
| --------------------- | ------ | ----------------------------------- |
| `/health`             | GET    | Verificação de saúde do processador |
| `/status`             | GET    | Status detalhado do processamento   |
| `/outputs/<filename>` | GET    | Visualizar resultados HTML          |

#### 3. Lógica de Processamento

**Busca Automática**: A cada minuto, busca versões com `status = "processar"`

**Determinação do Arquivo Original**:

- **Primeira versão** (`is_first_version = true`): Compara `arquivoPreenchido` vs `arquivoTemplate`
- **Versões subsequentes** (`is_first_version = false`): Compara `arquivoPreenchido` vs `arquivoBranco`

**Fluxo de Processamento**:

1. 🔍 Busca versões pendentes no Directus
2. 📝 Atualiza status para "processando"
3. 📥 Baixa arquivos original e modificado
4. 🔄 Executa comparação usando CLI
5. 📊 Analisa diferenças textuais
6. 💾 **Transação Única**: Atualiza status para "concluido", salva observações E modificações
7. 🧹 Limpa arquivos temporários

**Tratamento de Erros**:

- Atualiza status para "erro" com mensagem detalhada
- Continua processamento das próximas versões
- Log completo de todas as operações

#### 4. Estrutura de Dados no Directus

**Campo `versiona_ai_request_json`** deve conter:

```json
{
  "arquivoTemplate": "/directus/uploads/xxx.docx",
  "arquivoBranco": "/directus/uploads/yyy.docx",
  "arquivoPreenchido": "/directus/uploads/zzz.docx",
  "is_first_version": true/false,
  "versao_comparacao_tipo": "modelo_template" | "versao_anterior"
}
```

**Campo `modificacoes`** será automaticamente populado com:

```json
[
  {
    "versao": "uuid-da-versao",
    "categoria": "Adição" | "Remoção" | "Modificação",
    "conteudo": "texto original",
    "alteracao": "texto modificado",
    "sort": 1,
    "status": "published"
  }
]
```

## 🧪 Testes

```bash
# Com UV (recomendado)
uv run python test_api_simple.py
uv run python test_processamento_completo.py
uv run python test_directus_sdk.py

# Executar todos os testes com pytest
uv run pytest tests/

# Com Python tradicional
python test_api_simple.py
python test_processamento_completo.py
python test_directus_sdk.py
```

## 🏗️ Arquitetura do Sistema

### API REST

1. **📥 Receber Request**: Endpoint `/compare` recebe UUIDs dos arquivos
2. **⬇️ Download**: Baixa arquivos do Directus usando os UUIDs
3. **💾 Salvar**: Salva arquivos temporariamente no disco
4. **🔄 Processar**: Executa `docx_diff_viewer.py` para gerar comparação
5. **📊 Retornar**: Retorna URL do arquivo HTML gerado
6. **🗑️ Limpar**: Remove arquivos temporários automaticamente

### Processador Automático

1. **⏰ Loop Contínuo**: Monitora Directus a cada minuto
2. **🔍 Busca Inteligente**: Filtra versões com status "processar"
3. **🧠 Lógica de Negócio**: Determina arquivo original automaticamente
4. **⚡ Processamento**: Executa comparação usando infraestrutura existente
5. **💾 Transação Atômica**: Salva tudo em uma única operação no Directus
6. **🔄 Continuidade**: Processa múltiplas versões em sequência

## 📁 Estrutura do Projeto

```
docx-compare/
├── 📄 README.md                         # Este arquivo
├── 🐍 docx_diff_viewer.py               # CLI principal
├── 🌐 api_simple.py                     # API REST
├── 🤖 processador_automatico.py         # Processador automático principal
├── 🧪 processador_automatico_limpo.py   # Versão limpa do processador
├── 🧪 test_api_simple.py                # Testes da API
├── 🧪 test_processamento.py             # Testes de processamento
├── 🧪 test_processamento_completo.py    # Testes completos
├── 🧪 test_directus_sdk.py              # Testes Directus
├── 🔧 requirements.txt                  # Dependências Python
├── ⚙️ .env.example                      # Exemplo de configuração
├── 🎨 comments_html_filter_direct.lua   # Filtro Pandoc
├── 📁 documentos/                       # Documentos de exemplo
├── 📁 outputs/                          # Resultados HTML gerados
├── 📁 tests/                           # Scripts de teste organizados
└── 📋 API_DOCUMENTATION.md              # Documentação detalhada da API
```

## 🎨 Características do HTML Gerado

- **Design Responsivo**: Adapta-se a diferentes tamanhos de tela
- **Estatísticas**: Contadores de adições, remoções e modificações
- **Cores Intuitivas**:
  - 🟢 Verde para adições
  - 🔴 Vermelho para remoções
  - 🟡 Amarelo para modificações
- **Tipografia Limpa**: Fonte moderna e legível
- **Estrutura Clara**: Cabeçalho, estatísticas e conteúdo organizados

## 🔒 Segurança

- **Path Traversal**: Validação de nomes de arquivos
- **Limpeza Automática**: Remove arquivos temporários
- **Validação de Entrada**: Endpoints da API validados
- **Tratamento de Erros**: Robusto e seguro
- **Signal Handling**: Encerramento gracioso do processador
- **Transações Atômicas**: Operações consistentes no Directus
- **CSP Compatível**: HTML gerado sem estilos inline para máxima compatibilidade com Content Security Policy

### 🛡️ Content Security Policy (CSP)

O sistema gera HTML completamente compatível com Content Security Policy restritivo:

- ✅ **Sem estilos inline**: Todos os estilos são movidos para blocos `<style>`
- ✅ **Sem scripts inline**: JavaScript externo opcional
- ✅ **Sanitização automática**: Remove estilos inline do Pandoc
- ✅ **Classes CSS**: Usa apenas classes para estilização

**Configuração CSP recomendada:**

```
Content-Security-Policy: default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self';
```

## 🚀 Deploy em Produção

### API REST

```bash
# Com UV e Gunicorn (recomendado)
uv add gunicorn
uv run gunicorn -w 4 -b 0.0.0.0:5002 api_simple:app

# Com pip tradicional
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 api_simple:app
```

### Processador Automático

```bash
# Com systemd (Linux)
sudo systemctl enable docx-processor
sudo systemctl start docx-processor

# Como serviço em background com UV
nohup uv run python processador_automatico.py > processador.log 2>&1 &

# Com Python tradicional
nohup python processador_automatico.py > processador.log 2>&1 &
```

### Considerações para Produção

1. **Servidor WSGI**: Use Gunicorn ou uWSGI
2. **Proxy Reverso**: Configure Nginx
3. **HTTPS**: Configure certificados SSL/TLS
4. **Monitoramento**: Implemente logs e métricas
5. **Rate Limiting**: Limitação de taxa
6. **Systemd**: Configure como serviço do sistema
7. **Backup**: Estratégia de backup dos resultados

## 🐛 Solução de Problemas

### Erro: "Pandoc not found"

```bash
# Instale o Pandoc
brew install pandoc  # macOS
sudo apt-get install pandoc  # Ubuntu
```

### Erro: "Filtro Lua não encontrado"

- Verifique se `comments_html_filter_direct.lua` está no diretório raiz
- Confirme o caminho no arquivo `.env`

### Erro: "Connection refused" na API

- Verifique se a API está rodando: `python api_simple.py`
- Confirme a porta no arquivo `.env`
- Verifique se a porta não está ocupada: `lsof -i :5002`

### Erro: "Directus authentication failed"

- Verifique `DIRECTUS_BASE_URL` e `DIRECTUS_TOKEN` no `.env`
- Confirme se o token tem permissões para acessar arquivos
- Teste a conexão: `curl -H "Authorization: Bearer $TOKEN" $DIRECTUS_URL/users/me`

### Processador Automático não encontra versões

- Verifique se existem registros com `status = "processar"`
- Confirme se o campo `versiona_ai_request_json` está populado
- Verifique logs no terminal do processador
- Teste conexão: `curl http://localhost:5005/health`

### Modificações não são salvas

- Confirme que o processador está usando transação única
- Verifique permissões do token para criar/editar modificações
- Verifique logs para mensagens de erro de transação

## 📊 Monitoramento

### Processador Automático

**Logs em Tempo Real**: O processador exibe logs detalhados:

```
🔍 00:49:15 - Buscando versões para processar...
✅ Encontradas 2 versões para processar
📋 IDs encontrados: 905c2171..., 06319e34...
🚀 Processando versão 905c2171...
💾 Incluindo 4 modificações na transação...
✅ Versão atualizada com status 'concluido' e 4 modificações salvas
```

**Endpoints de Status**:

- `GET /health`: Status geral do sistema
- `GET /status`: Detalhes do processador
- `GET /outputs/<filename>`: Visualizar resultados

**Métricas Importantes**:

- Número de versões processadas por execução
- Tempo de processamento por versão
- Taxa de sucesso vs erro
- Tamanho dos arquivos processados

## 📖 Documentação Adicional

Para mais detalhes sobre a API, consulte [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 🎯 Roadmap

- [ ] Interface web para visualização de resultados
- [ ] Métricas e dashboard de monitoramento
- [ ] Processamento em paralelo de múltiplas versões
- [ ] Cache de resultados para comparações similares
- [ ] Notificações webhook para conclusão de processamento
- [ ] API GraphQL para consultas avançadas

## �️ Ferramentas de Desenvolvimento

### UV e Ruff

O projeto utiliza ferramentas modernas para desenvolvimento Python:

- **UV**: Gerenciador de dependências e ambientes virtuais ultra-rápido
- **Ruff**: Linter e formatador de código extremamente performático
- **ASDF**: Gerenciamento de versões de ferramentas (opcional)

### Por que UV?

**UV vs pip tradicional:**

- ⚡ **Performance**: 10-100x mais rápido que pip
- 🔒 **Resolução de dependências**: Mais robusta e determinística
- 📦 **Gestão unificada**: Dependências, ambientes virtuais e ferramentas em um só lugar
- 🛠️ **Compatibilidade**: Funciona com arquivos `requirements.txt` existentes
- 📋 **pyproject.toml**: Suporte nativo ao padrão moderno Python

### Comandos UV Principais

```bash
# Instalar dependências
uv sync                    # Instalar todas as dependências
uv sync --group dev        # Instalar dependências de desenvolvimento
uv add requests            # Adicionar nova dependência
uv add pytest --group dev # Adicionar dependência de desenvolvimento
uv remove requests         # Remover dependência

# Executar aplicações
uv run python script.py           # Executar script
uv run python api_simple.py       # Executar API
uv run python processador_automatico.py  # Executar processador

# Ferramentas de qualidade de código
uv run ruff check .               # Linting
uv run ruff check . --fix         # Corrigir problemas automaticamente
uv run ruff format .              # Formatar código
uv run pytest tests/             # Executar testes

# Comparar documentos
uv run python docx_diff_viewer.py doc1.docx doc2.docx result.html
```

### Scripts de Desenvolvimento com Makefile

```bash
# Makefile (recomendado para automação)
make help              # Ver todos os comandos
make install           # Instalar dependências
make lint              # Linting com Ruff
make lint-fix          # Corrigir problemas automaticamente
make format            # Formatar código
make test              # Executar testes
make test-coverage     # Testes com cobertura
make check             # Verificação completa
make clean             # Limpar arquivos temporários

# Executar aplicações
make run-processor     # Processador automático
make run-api           # API simples

# Comparar documentos
make compare ORIG=doc1.docx MOD=doc2.docx OUT=result.html
```

### Scripts Bash Alternativos

```bash
# scripts.sh (para ambientes sem Make)
./scripts.sh install      # Instalar dependências
./scripts.sh lint         # Linting
./scripts.sh format       # Formatar código
./scripts.sh test         # Executar testes
./scripts.sh run-api      # Executar API
./scripts.sh run-processor # Executar processador
```

### Configuração de Ambiente

O projeto usa `.tool-versions` (ASDF) para versões:

```text
python 3.13.2
uv 0.4.27
```

Estrutura de arquivos de configuração:

```
├── pyproject.toml     # Configuração UV, Ruff, pytest
├── .tool-versions     # Versões ASDF
├── Makefile          # Scripts de desenvolvimento
├── scripts.sh        # Scripts alternativos em Bash
└── .gitignore        # Inclui arquivos UV e coverage
```

## �📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
