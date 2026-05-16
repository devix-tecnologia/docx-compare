# Task 011 — Testes E2E via Interface de Usuário para Validação de Vinculação Cláusulas-Modificações

Status: done
Type: test
Priority: high
Assignee: Sidarta Veloso
Related: task-010
Completed: 2026-05-15

## Description

Os testes E2E atuais validam apenas endpoints REST da API, mas não garantem que o fluxo completo funciona do ponto de vista do usuário final. Precisamos de testes que simulem interação real através das interfaces de usuário (Directus Admin UI) para validar que:

1. **Task 010 funciona end-to-end**: Modificações detectadas são corretamente vinculadas às suas cláusulas correspondentes
2. **Fluxo completo do usuário**: Desde upload/criação de versão até visualização dos resultados no Directus
3. **Interface é utilizável**: Usuários conseguem completar todo o processo sem erros

**Problema atual:**

- ✅ Testes unitários validam lógica de matching (task-010)
- ✅ Testes E2E validam endpoints REST
- ❌ **Nenhum teste valida experiência do usuário real**
- ❌ **Não garantimos que interface do Directus mostra vinculações corretas**

**Impacto:**

- Risco de bugs na UI que quebram fluxo do usuário
- Impossível garantir que correção da Task 010 é visível/acessível aos usuários
- Deploy sem validação de UX completa

## Escopo dos Testes

### 1. Configuração do Ambiente (docker-compose)

- Subir stack completo: API + Directus + Banco de dados
- Garantir dados de teste (modelo de contrato, cláusulas base)
- Seed de dados mínimos para testes funcionarem

### 2. Testes via Interface Directus

#### 2.1 Upload e Processamento de Versão

- **Ação**: Usuário cria nova versão de contrato via interface Directus
- **Validação**:
  - Formulário de criação aceita dados necessários
  - Upload de arquivo DOCX funciona
  - Processamento é disparado automaticamente

#### 2.2 Aguardar Processamento

- **Ação**: Interface mostra status "processando" → "concluído"
- **Validação**:
  - Status é atualizado corretamente
  - Tempo de processamento razoável (< 30s para docs pequenos)
  - Erros são exibidos claramente se houver falha

#### 2.3 Visualizar Modificações Vinculadas (CORE - Task 010)

- **Ação**: Usuário navega para lista de modificações da versão processada
- **Validação crítica**:
  - ✅ **Campo `clausula` está preenchido** em cada modificação
  - ✅ **Vinculação aponta para cláusula correta** do modelo
  - ✅ **Interface mostra nome/referência da cláusula** (não apenas ID)
  - ✅ **Possível navegar de modificação → cláusula** via interface

#### 2.4 Filtrar e Buscar

- **Ação**: Usuário filtra modificações por cláusula específica
- **Validação**:
  - Filtro funciona corretamente
  - Resultados mostram apenas modificações da cláusula selecionada

#### 2.5 Validar Dados Persistidos

- **Ação**: Query direta no banco de dados (via Directus API ou SQL)
- **Validação**:
  - Tabela `modificacao` tem `clausula_id` preenchido (não NULL)
  - Foreign key aponta para registro válido em `clausula`
  - Dados consistentes entre interface e banco

### 3. Cenários de Erro

#### 3.1 Documento Sem Cláusulas Correspondentes

- **Ação**: Processar versão com texto muito diferente do modelo
- **Validação**:
  - Sistema processa sem crash
  - Modificações sem match claro têm `clausula_id = NULL` ou cláusula genérica
  - Interface exibe aviso/status apropriado

#### 3.2 Modelo de Contrato Inexistente

- **Ação**: Versão sem modelo de contrato vinculado
- **Validação**:
  - Processamento retorna erro claro
  - Interface mostra mensagem compreensível
  - Não cria modificações órfãs

## Ferramentas Sugeridas

### Opção 1: Playwright/Puppeteer (Browser Automation)

```python
# Testa interface web do Directus
playwright = Playwright()
browser = playwright.chromium.launch()
page = browser.new_page()
page.goto("http://localhost:8055/admin/content/contrato_versao")
# ... simular ações do usuário
```

**Vantagens:**

- Testa exatamente o que usuário vê
- Detecta bugs de UI/UX
- Screenshots de evidências

**Desvantagens:**

- Mais lento
- Requer headless browser no CI/CD

### Opção 2: Directus SDK + Validações de Estado

```python
# Usa SDK do Directus para simular ações e validar estados
directus = DirectusClient("http://localhost:8055", token)
versao = directus.items("contrato_versao").create({...})
# ... aguardar processamento
modificacoes = directus.items("modificacao").read(filters={"versao": versao_id})
assert all(mod["clausula"] is not None for mod in modificacoes)
```

**Vantagens:**

- Mais rápido
- Fácil de debugar
- CI/CD simples

**Desvantagens:**

- Não testa UI real
- Pode divergir da experiência do usuário

### Opção 3: Híbrida (Recomendada)

- SDK para setup e validações críticas (rápido)
- Playwright para 2-3 cenários críticos de UI (completo)

## Tasks

- [ ] Criar estrutura de testes E2E de UI em `tests/e2e_ui/`
- [ ] Configurar docker-compose com seed de dados de teste
  - [ ] Modelo de contrato com 5-10 cláusulas
  - [ ] Documentos DOCX de teste (versão original + modificada)
  - [ ] Credenciais de teste para Directus
- [ ] Implementar testes com Playwright/Puppeteer
  - [ ] Test: Login no Directus Admin
  - [ ] Test: Criar versão via formulário
  - [ ] Test: Upload de documento DOCX
  - [ ] Test: Aguardar processamento (polling status)
  - [ ] Test: Navegar para lista de modificações
  - [ ] Test: **CRÍTICO** - Verificar que `clausula` está preenchido
  - [ ] Test: Visualizar detalhes de modificação e navegar para cláusula
  - [ ] Test: Filtrar modificações por cláusula
- [ ] Implementar testes com Directus SDK (validações de dados)
  - [ ] Consultar modificações criadas
  - [ ] Validar foreign keys
  - [ ] Verificar consistência de dados
- [ ] Documentar setup e execução dos testes
  - [ ] README em `tests/e2e_ui/README.md`
  - [ ] Scripts de inicialização (`make e2e-ui-test`)
  - [ ] Instruções para CI/CD
- [ ] Adicionar testes ao pipeline de CI
  - [ ] GitHub Actions workflow
  - [ ] Gerar screenshots/vídeos de falhas
  - [ ] Reportar resultados

## Definição de Pronto

- ✅ Testes passam em ambiente local com `make e2e-ui-test`
- ✅ Testes validam que modificações têm `clausula_id` preenchido
- ✅ Pelo menos 1 teste usa browser automation (Playwright)
- ✅ Testes rodam em < 5 minutos
- ✅ Documentação completa de setup
- ✅ CI/CD configurado e passando
- ✅ Screenshots/evidências geradas automaticamente

## Benefícios Esperados

1. **Confiança em deploy**: Garantia de que Task 010 funciona na prática
2. **Prevenção de bugs de UI**: Detectar problemas que APIs não revelam
3. **Documentação viva**: Testes mostram como usar o sistema
4. **Regressão zero**: Mudanças futuras não quebram fluxo crítico
5. **UX validada**: Usuários conseguem completar processos sem frustração

## Riscos e Mitigações

| Risco                        | Impacto               | Mitigação                             |
| ---------------------------- | --------------------- | ------------------------------------- |
| Testes lentos (> 10min)      | CI/CD inviável        | Rodar UI tests apenas em merge/deploy |
| Flakiness (testes instáveis) | Falsos positivos      | Retry automático + waits explícitos   |
| Manutenção alta              | Equipe sobrecarregada | Focar em 5-7 cenários críticos apenas |
| Ambiente complexo            | Setup difícil         | docker-compose com seed automatizado  |

## Notas Técnicas

### Docker Compose Stack Completo

```yaml
services:
  postgres:
    image: postgres:15

  directus:
    image: directus/directus:latest
    depends_on: [postgres]
    volumes:
      - ./tests/e2e_ui/seed:/docker-entrypoint-initdb.d

  api-server:
    build: ./versiona-ai
    depends_on: [directus]

  test-runner:
    build: ./tests/e2e_ui
    depends_on: [api-server, directus]
    command: pytest tests/e2e_ui/ --playwright
```

### Seed de Dados Mínimos

- 1 modelo de contrato com 10 cláusulas típicas
- 2 documentos DOCX: original + versão modificada (3-5 alterações)
- 1 usuário admin de teste

### Métricas de Sucesso

- **Coverage**: 100% do fluxo crítico usuário (criar versão → ver vinculações)
- **Tempo**: < 5min para suite completa
- **Confiabilidade**: < 1% de falsos positivos

## Referências

- Task 010: Correção de vinculação modificação-cláusula
- Testes unitários: `versiona-ai/tests/test_vinculacao_clausulas.py`
- Testes E2E REST: `tests/e2e/test_processamento_completo_remoto.py`
- Documentação Directus: https://docs.directus.io/
- Playwright Python: https://playwright.dev/python/

---

**Criado**: 2026-05-15
**Última atualização**: 2026-05-15
