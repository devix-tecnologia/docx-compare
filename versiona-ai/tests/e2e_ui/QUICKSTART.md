# 🚀 Quick Start - Testes E2E UI (Task 011)

## Execução Rápida (1 comando)

```bash
make e2e-ui-test
```

Isso irá:
- ✅ Subir PostgreSQL com seed de dados
- ✅ Inicializar Directus CMS
- ✅ Subir API Versiona AI  
- ✅ Executar 22 testes (Playwright + SDK)
- ✅ Gerar relatório HTML

⏱️ **Tempo esperado**: 5-10 minutos na primeira execução (incluindo build Docker)

---

## Ou use o script interativo

```bash
./tests/e2e_ui/run-tests.sh
```

Menu com opções:
1. Executar todos testes
2. Apenas testes críticos Task 010
3. Subir infraestrutura para debug
4. Limpar ambiente

---

## Comandos Úteis

### Ver resultados
```bash
make e2e-ui-test-report   # Abre HTML no browser
```

### Debug
```bash
make e2e-ui-up            # Subir infra sem rodar testes
make e2e-ui-logs          # Ver logs em tempo real
make e2e-ui-shell         # Shell no container de testes
```

### Limpeza
```bash
make e2e-ui-down          # Parar containers
make e2e-ui-clean         # Limpar volumes e cache
```

---

## Acesso à Infraestrutura

Quando infraestrutura estiver rodando (`make e2e-ui-up`):

- **Directus Admin**: http://localhost:8055
  - Login: `admin@test.local`
  - Senha: `TestPassword123!`

- **API Versiona**: http://localhost:8001
  - Health: http://localhost:8001/health

- **PostgreSQL**: localhost:5432
  - User: `directus`
  - Password: `directus`
  - Database: `directus_test`

---

## Estrutura dos Testes

```
22 testes divididos em:

✅ Autenticação (4 testes)
   - Login válido/inválido
   - Navegação dashboard

✅ Processamento (5 testes)
   - Criar versão
   - Aguardar processamento
   - Visualizar detalhes

⭐ Visualização - CRÍTICO Task 010 (7 testes)
   - Modificações têm clausula_id preenchido
   - UI exibe nome da cláusula
   - Navegação modificação → cláusula
   - Filtros funcionam
   - Integridade referencial

✅ Validações SDK (7 testes)
   - Modelo existe
   - Cláusulas válidas
   - Health checks
   - Consistência de dados
```

---

## Validação Task 010

Os testes garantem:

### ✅ Backend (Dados)
- `clausula_id` preenchido em 100% modificações
- Foreign keys válidos
- Integridade referencial OK

### ✅ Frontend (UI)
- Nome de cláusula visível na interface
- Navegação funciona
- Filtros operacionais

---

## Troubleshooting

### Erro: Connection refused
```bash
# Ver logs do Directus
docker-compose -f docker-compose.ui-test.yml logs directus

# Aumentar timeout se necessário (editar docker-compose.ui-test.yml)
```

### Seed não aplicado
```bash
# Limpar e recriar do zero
make e2e-ui-clean
make e2e-ui-test
```

### Testes muito lentos
```bash
# Rodar apenas validações SDK (sem Playwright)
make e2e-ui-test-sdk
```

### Element not found no Playwright
```bash
# Rodar com browser visível
docker-compose -f docker-compose.ui-test.yml run --rm test-runner \
  pytest tests/e2e_ui/test_ui_*.py -v -s --headed --slowmo 1000
```

---

## Arquivos Importantes

- `docker-compose.ui-test.yml` - Configuração da stack
- `tests/e2e_ui/conftest.py` - Fixtures pytest
- `tests/e2e_ui/seed/*.sql` - Dados de teste
- `tests/e2e_ui/test_ui_visualizar_modificacoes.py` - Testes críticos Task 010

---

## Relatórios

Após execução, relatórios disponíveis em:
- `test-results/report-ui.html` - Relatório principal
- `test-results/junit-ui.xml` - Para CI/CD
- `test-results/screenshots/` - Screenshots de falhas
- `test-results/traces/` - Traces Playwright

---

## CI/CD

Para integração contínua, use:

```bash
make e2e-ui-test
```

Exit code:
- `0` = todos testes passaram
- `!= 0` = pelo menos 1 teste falhou

---

## Mais Informações

- 📖 Documentação completa: `tests/e2e_ui/README.md`
- 🔧 Detalhes implementação: `tests/e2e_ui/__IMPLEMENTATION_SUMMARY.md`
- 🎯 Task original: `TASKS/task-011-testes-e2e-interface-usuario-validacao-vinculacao-clausulas.md`

---

**Pronto para começar?**

```bash
make e2e-ui-test
```

🚀 Boa sorte!
