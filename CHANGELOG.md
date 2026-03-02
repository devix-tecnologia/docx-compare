# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Adicionado

- 📚 **Documentação de Arquitetura Completa**: Novo documento [docs/ARQUITETURA_E_FLUXO.md](docs/ARQUITETURA_E_FLUXO.md)
  - Explicação didática completa do funcionamento do sistema
  - Fluxo de processamento detalhado em 11 etapas (criação → conclusão)
  - Visão geral dos componentes (Directus, Orquestrador, Processadores)
  - Componentes técnicos principais (Repository Pattern, AST, Flask, Orquestrador)
  - Diferença entre endpoints de processamento vs visualização
  - Casos de uso práticos com exemplos reais
  - Métricas de performance e limites do sistema
  - Comandos úteis para operação e troubleshooting
  - Seção de troubleshooting com soluções para problemas comuns
  - Explicação de conceitos técnicos (AST, Repository Pattern, Protocols, IoD)

- 🎯 **Orquestrador de Processadores**: Novo componente central para coordenar execução de múltiplos processadores
  - Modo sequencial: executa processadores um após o outro
  - Modo paralelo: executa processadores simultaneamente
  - Modo single-run: execução única com encerramento automático
  - Modo contínuo: execução em loop com intervalos configuráveis
  - API REST completa para monitoramento (porta 5007)
  - Dashboard web para visualização de status
  - Tratamento robusto de erros e timeouts
  - Signal handling para encerramento gracioso

- 📋 **Comandos Make para Orquestrador**:
  - `make run-orquestrador-single`: Execução única sequencial (recomendado)
  - `make run-orquestrador-single-verbose`: Execução única com logs detalhados
  - `make run-orquestrador`: Modo contínuo paralelo
  - `make run-orquestrador-sequencial`: Modo contínuo sequencial
  - `make run-orquestrador-paralelo`: Modo contínuo paralelo
  - E várias outras variações para diferentes necessidades

- 📊 **Endpoints de Monitoramento**:
  - `GET /`: Dashboard principal com interface web
  - `GET /health`: Health check do orquestrador
  - `GET /status`: Status detalhado dos processadores
  - `GET /metrics`: Métricas completas do sistema

- 📚 **Documentação Expandida**:
  - [docs/ORQUESTRADOR.md](docs/ORQUESTRADOR.md): Guia completo do orquestrador
  - Documentação atualizada da API com novos endpoints
  - README.md atualizado com todos os novos comandos
  - Makefile com help expandido e organizado

### Melhorado

- 🔄 **Processador Automático**: Correção do encerramento em modo single-run
  - Adicionado `sys.exit(0)` para encerramento completo
  - Evita que o Flask continue rodando após execução única

- 🏷️ **Processador de Modelo de Contrato**: Correção do encerramento em modo single-run
  - Adicionado `sys.exit(0)` para encerramento completo
  - Consistência com o processador automático

- 📋 **Sistema de Build**:
  - Makefile reorganizado e expandido
  - Help do Makefile com categorização e exemplos
  - Comandos mais intuitivos e organizados

### Corrigido

- ✅ **Encerramento de Processos**: Processadores agora encerram corretamente em modo single-run
- 🔄 **Sequência de Execução**: Orquestrador executa primeiro o processador de modelo de contrato, depois o automático
- 📊 **Monitoramento**: APIs de status agora retornam informações precisas sobre o estado dos processadores

### Arquitetura

- 🏗️ **Separação de Responsabilidades**: Cada processador mantém suas responsabilidades específicas
- 🔧 **Orquestração Inteligente**: Coordenação central sem acoplamento entre processadores
- 📡 **APIs Independentes**: Cada componente expõe sua própria API de monitoramento
- 🔄 **Execução Isolada**: Processadores executam em subprocessos isolados para máxima estabilidade

## Roadmap

### Próximas Funcionalidades

- 📅 **Scheduling**: Integração com cron para execução programada
- 🚨 **Alertas**: Sistema de notificações para falhas e eventos importantes
- 📈 **Métricas Avançadas**: Integração com Prometheus/Grafana
- ⚖️ **Load Balancing**: Distribuição de carga entre múltiplas instâncias
- 🔄 **Auto-scaling**: Ajuste automático baseado na carga de trabalho
- 🐳 **Docker Compose**: Orquestração completa com containers
- 🔐 **Autenticação**: Sistema de autenticação para APIs de monitoramento
- 📱 **Interface Mobile**: Dashboard responsivo para dispositivos móveis

### Melhorias Planejadas

- 🧪 **Testes**: Cobertura de testes para o orquestrador
- 🔍 **Observabilidade**: Logs estruturados e tracing distribuído
- 🛡️ **Resiliência**: Circuit breakers e retry policies
- 🚀 **Performance**: Otimizações para alto volume de processamento
- 📦 **Packaging**: Distribuição via PyPI

---

## Histórico de Versões

### [1.0.0] - 2025-09-08

- Versão inicial com orquestrador de processadores
- Sistema completo de monitoramento e coordenação
- Documentação completa e comandos organizados
