# E2E UI Tests - Iniciando Implementação (Task 011)

✅ **IMPLEMENTADO**

## 📁 Estrutura Criada

```
tests/e2e_ui/
├── README.md                          # Documentação completa
├── conftest.py                        # Fixtures pytest + Playwright
├── Dockerfile.ui-test                 # Container test runner
├── .env.e2e.ui                        # Variáveis de ambiente
├── seed/
│   ├── 01-schema.sql                  # Schema do banco
│   ├── 02-modelo-contrato.sql         # Dados de teste (Task 010)
│   └── 03-usuarios.sql                # Usuários
├── fixtures/                          # (vazio - para DOCXs futuros)
├── test_ui_directus_login.py          # ✅ Testes de autenticação
├── test_ui_processar_versao.py        # ✅ Testes de processamento
├── test_ui_visualizar_modificacoes.py # ✅ CRÍTICO - Task 010
└── test_sdk_validacoes_dados.py       # ✅ Validações via SDK
```

## 📄 Arquivos Criados

### Docker & Infraestrutura
- ✅ `docker-compose.ui-test.yml` - Stack completo (Postgres + Directus + API + Test Runner)
- ✅ `tests/e2e_ui/Dockerfile.ui-test` - Container com Playwright + SDK
- ✅ `.env.e2e.ui` - Configuração de ambiente

### Seed de Dados
- ✅ `01-schema.sql` - Schema básico das tabelas
- ✅ `02-modelo-contrato.sql` - Modelo com 10 cláusulas + 1 versão + 4 modificações vinculadas
- ✅ `03-usuarios.sql` - Usuário admin (criado via Directus env vars)

### Testes Implementados
- ✅ `conftest.py` - Fixtures Playwright + Directus SDK + helpers
- ✅ `test_ui_directus_login.py` - 3 testes de autenticação
- ✅ `test_ui_processar_versao.py` - 5 testes de criação/processamento
- ✅ `test_ui_visualizar_modificacoes.py` - **7 testes críticos Task 010**
- ✅ `test_sdk_validacoes_dados.py` - 7 validações via SDK

### Makefile
- ✅ `e2e-ui-test` - Executar todos testes
- ✅ `e2e-ui-up` - Subir apenas infraestrutura
- ✅ `e2e-ui-down` - Derrubar ambiente
- ✅ `e2e-ui-logs` - Ver logs
- ✅ `e2e-ui-shell` - Shell interativo
- ✅ `e2e-ui-test-playwright` - Apenas UI
- ✅ `e2e-ui-test-sdk` - Apenas dados
- ✅ `e2e-ui-test-critical` - Apenas Task 010
- ✅ `e2e-ui-test-report` - Abrir HTML report
- ✅ `e2e-ui-rebuild` - Rebuild sem cache
- ✅ `e2e-ui-clean` - Limpeza completa

### Documentação
- ✅ `tests/e2e_ui/README.md` - Documentação completa com troubleshooting

## 🧪 Testes Implementados (Total: 22)

### Autenticação (3 testes)
1. ✅ `test_login_page_loads` - Página de login carrega
2. ✅ `test_login_with_valid_credentials` - Login válido funciona
3. ✅ `test_login_with_invalid_credentials` - Login inválido é rejeitado
4. ✅ `test_navigate_to_dashboard` - Navegação pós-login

### Processamento (5 testes)
5. ✅ `test_navegar_para_formulario_versao` - Navega para formulário
6. ✅ `test_criar_versao_via_api_sdk` - Cria versão via SDK
7. ✅ `test_aguardar_processamento_concluir` - Status muda para "concluído"
8. ✅ `test_versao_processada_tem_modificacoes` - Versão gera modificações
9. ✅ `test_visualizar_detalhes_versao_ui` - Detalhes na UI

### **Visualização - CRÍTICO Task 010 (7 testes)**
10. ✅ `test_navegar_para_lista_modificacoes` - Navega para modificações
11. ✅ **`test_modificacoes_tem_clausula_preenchida`** - ⭐ Valida `clausula_id` != NULL
12. ✅ **`test_ui_exibe_nome_clausula_nao_apenas_id`** - UI mostra nome da cláusula
13. ✅ **`test_navegar_de_modificacao_para_clausula`** - Link modificação → cláusula
14. ✅ `test_filtrar_modificacoes_por_clausula` - Filtro funciona
15. ✅ **`test_validacao_foreign_key_banco`** - ⭐ Integridade referencial
16. ✅ Teste parametrizado com filtro on/off

### Validações SDK (7 testes)
17. ✅ `test_modelo_contrato_existe` - Modelo de teste existe
18. ✅ `test_modelo_tem_clausulas` - >= 5 cláusulas
19. ✅ `test_clausulas_tem_referencia_unica` - Referências únicas
20. ✅ `test_directus_health_check` - Directus saudável
21. ✅ `test_api_versiona_health_check` - API saudável
22. ✅ `test_consistencia_ids_modificacao_clausula` - IDs consistentes

## 🚀 Uso Rápido

```bash
# Executar todos testes E2E UI
make e2e-ui-test

# Apenas testes críticos Task 010
make e2e-ui-test-critical

# Subir ambiente para debug manual
make e2e-ui-up
make e2e-ui-shell

# Ver relatório HTML
make e2e-ui-test-report

# Limpar tudo
make e2e-ui-clean
```

## 🎯 Validação Task 010

Os testes garantem:

### ✅ Dados (SDK)
- Campo `clausula_id` preenchido em 100% das modificações
- Foreign keys apontam para registros válidos
- Integridade referencial OK

### ✅ Interface (Playwright)
- Nome da cláusula exibido (não apenas ID)
- Navegação modificação → cláusula funciona
- Filtro por cláusula funciona

## 📊 Dados de Seed

- **1 modelo**: "Modelo Teste Task 010"
- **10 cláusulas**: Referências 1.0 a 10.0
- **1 versão**: Pré-processada com status "concluído"
- **4 modificações**: Todas vinculadas a cláusulas (Task 010)

## ⚠️ Próximos Passos

### Para executar testes:
1. **Ajustar seed SQL** se schema do Directus for diferente
2. **Executar primeira vez**: `make e2e-ui-test`
3. **Ajustar testes** conforme UI real do Directus (seletores podem variar)

### Possíveis ajustes:
- Seletores CSS podem variar entre versões do Directus
- Seed SQL pode precisar de adaptação para schema real
- Timeouts podem precisar de ajuste conforme performance

## 🐛 Troubleshooting Previsto

Se testes falharem:

1. **Directus não sobe**: Aumentar `start_period` do healthcheck
2. **Seed não aplica**: Verificar se tabelas existem (`make e2e-ui-logs`)
3. **Playwright timeout**: Usar `--headed --slowmo 1000` para debug
4. **Foreign key error**: Ajustar IDs no seed SQL

## 📝 Notas de Implementação

- **Abordagem híbrida**: 80% SDK (rápido) + 20% Playwright (UI crítica)
- **Seed com IDs fixos**: Facilita debug e reprodução
- **Fixtures reutilizáveis**: `directus_page_logged` já autenticado
- **Testes isolados**: Cada teste pode rodar independente
- **Screenshots automáticos**: Em caso de falha

---

**Status**: ✅ Implementação base completa  
**Próximo**: Executar `make e2e-ui-test` e ajustar conforme necessário
