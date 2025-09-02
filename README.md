# 📄 Comparador de Documentos DOCX

Sistema para comparação de documentos DOCX com interface CLI e API REST, integrado com Directus CMS.

## 🚀 Funcionalidades

- **CLI**: Comparação local de arquivos DOCX
- **API REST**: Endpoint HTTP para comparação via Directus
- **HTML Responsivo**: Visualização profissional das diferenças
- **Integração Directus**: Download automático de arquivos por UUID
- **Limpeza Automática**: Remove tags HTML desnecessárias

## 📋 Pré-requisitos

- Python 3.8+
- Pandoc
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

#### 4. Exemplo de Uso da API

**Verificar saúde:**
```bash
curl http://localhost:5002/health
```

**Comparar documentos:**
```bash
curl -X POST http://localhost:5002/compare \
  -H "Content-Type: application/json" \
  -d '{
    "original_file_id": "550e8400-e29b-41d4-a716-446655440000",
    "modified_file_id": "550e8400-e29b-41d4-a716-446655440001"
  }'
```

**Resposta da comparação:**
```json
{
  "success": true,
  "result_url": "http://localhost:5002/results/comparison_abc123.html",
  "result_filename": "comparison_abc123.html",
  "timestamp": "2025-09-02T14:15:30"
}
```

## 🧪 Testes

```bash
# Testar a API
python test_api_simple.py
```

## 🏗️ Arquitetura da API

A API segue um fluxo simples e eficiente:

1. **📥 Receber Request**: Endpoint `/compare` recebe UUIDs dos arquivos
2. **⬇️ Download**: Baixa arquivos do Directus usando os UUIDs
3. **💾 Salvar**: Salva arquivos temporariamente no disco
4. **🔄 Processar**: Executa `docx_diff_viewer.py` para gerar comparação
5. **📊 Retornar**: Retorna URL do arquivo HTML gerado
6. **🗑️ Limpar**: Remove arquivos temporários automaticamente

## 📁 Estrutura do Projeto

```
docx-compare/
├── 📄 README.md                    # Este arquivo
├── 🐍 docx_diff_viewer.py          # CLI principal
├── 🌐 api_simple.py                # API REST
├── 🧪 test_api_simple.py           # Testes da API
├── 🔧 requirements.txt             # Dependências Python
├── ⚙️ .env.example                 # Exemplo de configuração
├── 🎨 comments_html_filter_direct.lua  # Filtro Pandoc
├── 📁 documentos/                  # Documentos de exemplo
├── 📁 results/                     # Resultados HTML gerados
└── 📋 API_DOCUMENTATION.md         # Documentação detalhada da API
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

- Validação de nomes de arquivos para prevenir path traversal
- Limpeza automática de arquivos temporários
- Validação de entrada nos endpoints da API
- Tratamento de erros robusto

## 🚀 Deploy em Produção

Para produção, considere:

1. **Servidor WSGI**: Use Gunicorn ou uWSGI em vez do servidor de desenvolvimento Flask
2. **Proxy Reverso**: Configure Nginx na frente da aplicação
3. **HTTPS**: Configure certificados SSL/TLS
4. **Monitoramento**: Implemente logs e métricas
5. **Rate Limiting**: Adicione limitação de taxa para prevenir abuso

**Exemplo com Gunicorn:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 api_simple:app
```

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
- Teste a conexão: `curl -H "Authorization: Bearer $TOKEN" $DIRECTUS_URL/files`

## 📖 Documentação Adicional

Para mais detalhes sobre a API, consulte [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.