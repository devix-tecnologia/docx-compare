# Diretório de Uploads do Directus (Testes E2E)

Este diretório é mapeado para `/directus/uploads` dentro do container Directus nos testes E2E UI.

**⚠️ Importante:** O Directus armazena TODOS os arquivos **na raiz** desta pasta (sem subpastas). Não crie subpastas organizacionais - o Directus gerencia isso internamente.

## Como Adicionar Arquivos

Para disponibilizar arquivos no Directus dos testes E2E:

1. **Copie seus arquivos para esta pasta (raiz):**
   ```bash
   cp /caminho/do/seu/arquivo.docx versiona-ai/tests/e2e_ui/uploads/
   ```

2. **Ou use o comando Make (de dentro de versiona-ai/):**
   ```bash
   cd versiona-ai
   make e2e-ui-uploads-add FILE=/caminho/do/arquivo.docx
   ```

3. **Reinicie o Directus** (se já estiver rodando):
   ```bash
   cd versiona-ai
   make e2e-ui-down && make e2e-ui-up
   ```

4. **Acesse via Directus UI:**
   - URL: http://localhost:8065/admin
   - Login: admin@example.com
   - Senha: TestPassword123!

## Estrutura (Tudo na Raiz)

```
uploads/
├── README.md
├── exemplo-teste.txt
├── modelo-teste-001.docx
├── versao-processada.docx
└── arquivo-fixture.txt
```

**Não crie subpastas!** O Directus gerencia uploads na raiz.

## Comandos Make Úteis

Todos comandos devem ser executados de dentro de `versiona-ai/`:

```bash
cd versiona-ai

# Listar arquivos na pasta uploads
make e2e-ui-uploads

# Adicionar arquivo aos uploads
make e2e-ui-uploads-add FILE=/caminho/arquivo.docx

# Limpar uploads (exceto README e exemplos)
make e2e-ui-uploads-clean

# Subir/derrubar ambiente
make e2e-ui-up
make e2e-ui-down
```

## Importante

- ⚠️ **Não crie subpastas** - o Directus usa a raiz
- 🚫 Não commite arquivos sensíveis ou muito grandes  
- ✅ Arquivos de teste pequenos (< 1MB) podem ter prefixo `exemplo-` ou `test-`
- 📦 O Directus precisa de permissões de leitura (chmod 644)

## Troubleshooting

**Arquivos não aparecem no Directus?**
- Verifique permissões: `chmod 644 versiona-ai/tests/e2e_ui/uploads/*.docx`
- Reinicie: `cd versiona-ai && make e2e-ui-down && make e2e-ui-up`

**Erro de permissão?**
- O Directus roda como `node` (UID 1000)
- Ajuste: `chown -R 1000:1000 versiona-ai/tests/e2e_ui/uploads/`
