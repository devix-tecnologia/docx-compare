# 📄 Sistema de Comparação de Documentos DOCX com Processamento Automático

Sistema completo para comparação de documentos DOCX com interface CLI, API REST e processamento automático integrado com Directus CMS.

## 🚀 Funcionalidades

### 🔧 CLI - Comparação Local
- **Comparação Direta**: Comparação local de arquivos DOCX
- **HTML Responsivo**: Visualização profissional das diferenças
- **Filtro Lua**: Remove tags HTML desnecessárias com Pandoc

### 🌐 API REST - Integração Directus
- **Endpoint HTTP**: Comparação via API REST
- **Download Automático**: Busca arquivos do Directus por UUID
- **Validação de Segurança**: Prevenção de path traversal
- **Limpeza Automática**: Remove arquivos temporários

### 🤖 Processador Automático
- **Monitoramento Contínuo**: Busca versões com status "processar" no Directus
- **Processamento Inteligente**: 
  - Primeira versão: compara com template
  - Versões subsequentes: compara com versão anterior
- **Transação Única**: Salva status, observações e modificações em uma única operação
- **Signal Handling**: Encerramento gracioso com SIGINT/SIGTERM/SIGHUP
- **Monitoramento Web**: Endpoints para verificação de saúde e status

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

```bash
# 1. Clone o repositório
git clone <repository-url>
cd docx-compare

# 2. Instale as dependências Python
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações do Directus
```

## 🎯 Uso

### CLI - Comparação Local

```bash
python docx_diff_viewer.py original.docx modificado.docx resultado.html
```

**Exemplo:**
```bash
python docx_diff_viewer.py documentos/doc-rafael-original.docx documentos/doc-rafael-alterado.docx resultado.html
```

### API REST - Integração com Directus

#### 1. Configurar o .env

```env
# Configurações do Directus
DIRECTUS_BASE_URL=https://your-directus-instance.com
DIRECTUS_TOKEN=your-directus-token-here

# Configurações da API
FLASK_HOST=0.0.0.0
FLASK_PORT=5002
FLASK_DEBUG=True

# Diretórios
RESULTS_DIR=results
```

#### 2. Executar a API

```bash
python api_simple.py
```

A API estará disponível em `http://localhost:5002`

#### 3. Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Verificação de saúde da API |
| `/compare` | POST | Comparar dois documentos DOCX |
| `/results/<filename>` | GET | Servir arquivo HTML de resultado |

### 🤖 Processador Automático

O processador automático monitora o Directus continuamente e processa versões automaticamente.

#### 1. Executar o Processador

```bash
python processador_automatico.py
```

#### 2. Endpoints de Monitoramento

O processador executa na porta 5005 e oferece:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Verificação de saúde do processador |
| `/status` | GET | Status detalhado do processamento |
| `/results/<filename>` | GET | Visualizar resultados HTML |

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
# Testar a API
python test_api_simple.py

# Testar processamento completo
python test_processamento_completo.py

# Testar conexão Directus
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
├── 📁 results/                          # Resultados HTML gerados
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

## 🚀 Deploy em Produção

### API REST
```bash
# Com Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 api_simple:app
```

### Processador Automático
```bash
# Com systemd (Linux)
sudo systemctl enable docx-processor
sudo systemctl start docx-processor

# Como serviço em background
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
- `GET /results/<filename>`: Visualizar resultados

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

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.