# 📋 Guia de Gerenciamento de Tarefas

## 🆕 Como Criar uma Nova Tarefa

### 1. Estrutura do Arquivo

Cada tarefa deve ser criada como um arquivo Markdown seguindo o padrão:

```
task-XXX-titulo-da-task-em-kebab-case.md
```

### 2. Template Básico

```markdown
# Task XXX - Título da Tarefa

## Status

pendente

## Responsável

Nome do responsável

## Descrição

Descrição detalhada do que precisa ser feito.

## Objetivos

- Objetivo 1
- Objetivo 2
- Objetivo N

## Prioridade

alta

## Estimativa

X horas/dias

## Dependências

- Task XXX (se houver)
- Recurso/sistema Y

## Critérios de Aceitação

- [ ] Critério 1
- [ ] Critério 2
- [ ] Critério N

## Observações

Informações adicionais relevantes.
```

### 3. Numeração

- Use numeração sequencial (001, 002, 003...)
- Verifique a última tarefa criada para usar o próximo número

### 4. Tipos de Tarefa

Identifique o tipo da tarefa para o nome do branch:

- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **refactor**: Refatoração de código
- **docs**: Documentação
- **test**: Testes
- **chore**: Tarefas de manutenção

## ⚡ Como Iniciar uma Tarefa

### 1. Usando o CLI Moderno (Recomendado)

```bash
# Na raiz do projeto - inicia a partir da branch atual (padrão)
pnpm task start 5
# ou
pnpm task start task-005
# ou
pnpm task start task-005-validar-janela

# Opções avançadas:
pnpm task start 5 --base develop        # Especifica branch base
pnpm task start 5 --from-develop        # Força uso do develop (comportamento antigo)
pnpm task start 5 --force              # Ignora mudanças não commitadas
```

O CLI irá:

- **Novo comportamento padrão**: Criar branch a partir da branch atual
- Verificar se há mudanças não commitadas (pode ser ignorado com `--force`)
- Criar um novo branch baseado no tipo da tarefa
- Atualizar o status da tarefa para "Em Andamento"
- Mostrar resumo com branch base e nova branch criada

### 2. Outros Comandos Úteis

```bash
# Listar todas as tarefas
pnpm task list
# ou
pnpm task ls

# Filtrar tarefas
pnpm task list pendente
pnpm task list bruno
pnpm task list --status concluida

# Pausar tarefa (commit sem push)
pnpm task pause 5
pnpm task pause 5 -m "salvando progresso"

# Finalizar tarefa
pnpm task finish 5
pnpm task done 5

# Ajuda geral
pnpm task

# Ajuda específica de comando
pnpm task start --help
```

### 3. Processo Manual (Opcional)

Se preferir fazer manualmente ou entender o que acontece por baixo dos panos:

1. **Verificar status do repositório:**

   ```bash
   git status
   ```

2. **Committar mudanças pendentes (se houver):**

   ```bash
   git add .
   git commit -m "Descrição das mudanças"
   ```

3. **Ir para a branch base (opcional - agora o padrão é usar a branch atual):**

   ```bash
   git checkout develop  # Apenas se quiser usar o comportamento antigo
   git pull origin develop
   ```

4. **Criar novo branch a partir da branch atual:**

   ```bash
   git checkout -b feat/nome-da-task
   # ou fix/nome-da-task, refactor/nome-da-task, etc.
   ```

5. **Atualizar status da tarefa:**
   - Marcar como "Em Andamento" no arquivo da tarefa

## ✅ Como Registrar a Conclusão de uma Tarefa

### 1. Usando o CLI (Recomendado)

```bash
# Finalizar tarefa automaticamente
pnpm task finish 5
# ou
pnpm task done task-005
```

O CLI irá:

- Atualizar o status para "Concluída"
- Adicionar data de conclusão
- Mostrar próximos passos para commit e PR

### 2. Processo Manual

### 3. Verificar Critérios de Aceitação

- [ ] Todos os critérios foram atendidos?
- [ ] Código foi testado?
- [ ] Documentação foi atualizada?

### 4. Atualizar Status da Tarefa (se feito manualmente)

```markdown
## Status

concluida

## Data de Conclusão

YYYY-MM-DD

## Resultado

Breve descrição do que foi entregue.
```

### 5. Commit e Push

```bash
# Adicionar mudanças
git add .

# Commit com mensagem descritiva
git commit -m "feat: implementa funcionalidade X

- Adiciona feature Y
- Resolve issue Z
- Closes #XXX"

# Push do branch
git push origin nome-do-branch
```

### 6. Criar Pull Request

1. Abrir PR no GitHub/GitLab
2. Referenciar a tarefa no PR
3. Solicitar revisão de código
4. Aguardar aprovação e merge

### 7. Limpeza Pós-Conclusão

```bash
# Após merge do PR
git checkout develop
git pull origin develop
git branch -d nome-do-branch
```

## 🚫 Quando uma Tarefa é Bloqueada

### 1. Atualizar Status

```markdown
## Status

bloqueada

## Motivo do Bloqueio

- Dependência X não está pronta
- Aguardando definição Y
- Problema técnico Z
```

### 2. Documentar Bloqueio

- Descrever claramente o motivo
- Definir o que é necessário para desbloquear
- Atribuir responsável pela resolução do bloqueio

### 3. Comunicar

- Informar a equipe sobre o bloqueio
- Buscar alternativas ou workarounds
- Acompanhar progresso da resolução

## 📊 Acompanhamento de Progresso

### Status Disponíveis

- **pendente**: Tarefa criada, aguardando início
- **em_andamento**: Tarefa sendo executada
- **concluida**: Tarefa finalizada e entregue
- **bloqueada**: Tarefa impedida por dependência externa

### Relatórios

Use o CLI moderno para gerar relatórios:

```bash
# Listar todas as tarefas
pnpm task list

# Filtrar por status
pnpm task list pendente
pnpm task list andamento
pnpm task list concluida
pnpm task list bloqueada

# Filtrar por responsável
pnpm task list bruno
pnpm task list --responsavel harrison

# Combinações
pnpm task list --status pendente --responsavel bruno
```

Ou use comandos tradicionais:

```bash
# Listar tarefas por status
grep -l "Em Andamento" TASKS/*.md

# Contar tarefas por responsável
grep -h "## Responsável" TASKS/*.md | sort | uniq -c
```

## 🆕 Novas Funcionalidades do Sistema

### 🌿 Branch Base Flexível

- **Padrão**: Nova tarefa inicia a partir da branch atual
- **Benefício**: Permite trabalhar em tarefas relacionadas sem voltar ao develop
- **Exemplo**: Trabalhando em `feat/api-usuarios` e precisa criar `fix/api-usuarios-bug`

### 🎨 Interface Colorida

- CLI com cores e ícones para melhor experiência
- Tabelas organizadas para visualização de tarefas
- Mensagens de erro e sucesso destacadas

### ⚡ Comandos Inteligentes

- Resolução flexível de nomes: `5`, `005`, `task-005`, `task-005-titulo`
- Aliases para comandos: `ls`, `begin`, `stop`, `done`
- Opções avançadas para diferentes cenários

### 📊 Relatórios Avançados

- Filtros por status, responsável e combinações
- Contadores automáticos por categoria
- Tabelas formatadas para fácil leitura

## 💡 Dicas e Boas Práticas

### Para Programadores

1. **Use o CLI moderno**: `pnpm task` para todos os comandos
2. **Aproveite a flexibilidade de branches**: Inicie tarefas relacionadas a partir da branch atual
3. **Use nomes curtos**: `pnpm task start 5` é mais rápido que o nome completo
4. **Sempre leia a tarefa completamente** antes de começar
5. **Esclareça dúvidas** antes de iniciar o desenvolvimento
6. **Use `--force` com cautela**: Apenas quando certeza de que mudanças não commitadas são irrelevantes
7. **Mantenha commits pequenos e frequentes**
8. **Teste seu código** antes de marcar como concluído
9. **Use `pnpm task pause` para salvar progresso** sem fazer push

### Para IAs

1. **Use o sistema CLI**: Prefira `pnpm task` aos comandos manuais
2. **Analise o contexto da branch atual**: Considere se faz sentido partir da branch atual ou do develop
3. **Verifique as dependências** antes de sugerir implementações
4. **Considere o contexto do projeto** ao propor soluções
5. **Verifique a estrutura existente** antes de criar novos arquivos
6. **Mantenha consistência** com padrões do projeto
7. **Use filtros inteligentes**: `pnpm task list` com filtros para encontrar tarefas relacionadas
8. **Documente decisões técnicas** tomadas durante a implementação

---

**Lembre-se**: Uma tarefa bem documentada é uma tarefa meio feita! 🚀
