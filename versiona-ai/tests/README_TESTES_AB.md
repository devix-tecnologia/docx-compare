# Framework de Teste A/B para Algoritmos de Vinculação

## 🎯 Objetivo

Framework para desenvolver, testar e comparar diferentes algoritmos de vinculação de modificações a cláusulas de contratos, usando **métricas objetivas** e **fixtures reproduzíveis**.

## 🚀 Quick Start

```bash
# 1. Instalar dependências
cd versiona-ai
uv sync

# 2. Rodar comparação básica
uv run python tests/comparar_algoritmos.py

# 3. Rodar testes automatizados
uv run pytest tests/test_comparacao_algoritmos.py -v

# 4. Gerar relatório HTML
uv run python tests/comparar_algoritmos.py --report html -o relatorio.html
```

## 📁 Estrutura

```
versiona-ai/tests/
├── fixtures/                           # Casos de teste
│   ├── README.md                      # Documentação das fixtures
│   ├── caso_01_insercao_simples.json  # Nível: simples
│   ├── caso_02_alteracao_simples.json
│   ├── caso_03_fora_de_tags.json
│   ├── caso_04_multiplas_modificacoes_interdependentes.json  # Nível: médio
│   └── caso_08_versao_2573b998.json   # Nível: complexo (caso real)
│
├── framework_comparacao.py            # Classes base e framework
├── test_comparacao_algoritmos.py      # Testes pytest + algoritmos exemplo
├── comparar_algoritmos.py             # CLI para comparação
├── COMO_ADICIONAR_ALGORITMOS.md       # Guia para desenvolvedores
└── README.md                          # Este arquivo
```

## 🧪 Como Funciona

### 1. Fixtures (Casos de Teste)

Cada fixture contém:

- **Documento**: Texto completo + tags com posições
- **Modificações**: Lista de modificações detectadas (entrada)
- **Ground Truth**: Vinculações esperadas (saída correta)
- **Métricas objetivo**: Critérios de sucesso

Exemplo:

```json
{
  "id": "caso_01_insercao_simples",
  "descricao": "Inserção única dentro de uma cláusula",
  "nivel_complexidade": "simples",
  "documento": {
    "texto_completo": "...",
    "tags": [{ "id": "tag_1", "posicao_inicio": 100, "posicao_fim": 200 }]
  },
  "modificacoes": [{ "tipo": "INSERCAO", "conteudo": { "novo": "..." } }],
  "vinculacoes_esperadas": [{ "modificacao_index": 0, "tag_id": "tag_1" }]
}
```

### 2. Algoritmos

Cada algoritmo implementa:

```python
class MeuAlgoritmo(AlgoritmoVinculacao):
    def calcular_posicoes(self, modificacoes, texto):
        # Calcular posicao_inicio/posicao_fim
        return modificacoes

    def vincular_clausulas(self, modificacoes, tags, texto):
        # Vincular modificações às tags
        return modificacoes
```

### 3. Comparação

O framework roda cada algoritmo em cada fixture e calcula:

- **Taxa de vinculação**: % de modificações vinculadas
- **Precisão**: % de vinculações corretas
- **Recall**: % de vinculações esperadas encontradas
- **F1-Score**: Média harmônica de precisão/recall
- **Erro de posição**: Diferença média em caracteres
- **Tempo de execução**: Performance

## 📊 Uso do CLI

```bash
# Comparar todos os algoritmos em todas as fixtures
python comparar_algoritmos.py

# Testar apenas casos simples
python comparar_algoritmos.py --nivel simples

# Comparar algoritmos específicos
python comparar_algoritmos.py --algoritmos naive_sequencial offset_acumulado

# Testar fixtures específicas
python comparar_algoritmos.py --fixtures caso_01 caso_04

# Gerar relatório markdown
python comparar_algoritmos.py --report markdown -o relatorio.md

# Gerar relatório HTML
python comparar_algoritmos.py --report html -o relatorio.html

# Modo verbose
python comparar_algoritmos.py -v
```

## 🧑‍💻 Desenvolvendo Novo Algoritmo

Veja [COMO_ADICIONAR_ALGORITMOS.md](COMO_ADICIONAR_ALGORITMOS.md) para guia completo.

Resumo:

1. **Criar classe**:

```python
class AlgoritmoFuzzy(AlgoritmoVinculacao):
    @property
    def nome(self):
        return "fuzzy_matching"

    def calcular_posicoes(self, modificacoes, texto):
        # Sua implementação
        pass

    def vincular_clausulas(self, modificacoes, tags, texto):
        # Sua implementação
        pass
```

2. **Registrar** em `comparar_algoritmos.py` e `test_comparacao_algoritmos.py`

3. **Testar**:

```bash
python comparar_algoritmos.py --algoritmos fuzzy_matching
```

## 📝 Criando Nova Fixture

1. Copiar template:

```bash
cp fixtures/caso_01_insercao_simples.json fixtures/caso_05_meu_caso.json
```

2. Editar:

- Documento com texto e tags
- Modificações de entrada
- Vinculações esperadas (ground truth)
- Métricas objetivo

3. Validar:

```bash
uv run pytest tests/test_comparacao_algoritmos.py::test_validacao_fixtures -v
```

## 🎓 Estratégias Disponíveis

### Naive Sequencial (Baseline)

- Busca simples de texto sem ajustes
- Score esperado: ~60-70 em casos simples

### Offset Acumulado

- Aplica modificações sequencialmente
- Ajusta offset para próximas buscas
- Score esperado: ~80-90 em casos médios

### Próximos (Sugestões)

- Fuzzy matching com contexto
- Machine Learning
- Regex patterns flexíveis
- Híbrido (combinar estratégias)

## 📈 Métricas de Sucesso

Um algoritmo "ótimo" deve ter:

- ✅ Taxa de vinculação: >90%
- ✅ Precisão: >95%
- ✅ Recall: >90%
- ✅ F1-Score: >90
- ✅ Erro de posição: <10 chars
- ✅ Tempo: <100ms

## 🔬 Workflow de Desenvolvimento

1. **Implementar** algoritmo seguindo interface
2. **Testar** em casos simples primeiro
3. **Comparar** com baseline (naive)
4. **Iterar** baseado em métricas
5. **Testar** em casos complexos
6. **Documentar** estratégia e resultados

## 📊 Exemplo de Relatório

```
🏆 RANKING GERAL:
🥇 1. offset_acumulado: 85.3 pontos
🥈 2. naive_sequencial: 72.1 pontos

📋 DETALHAMENTO POR FIXTURE:
  caso_01_insercao_simples:
    offset_acumulado: Taxa: 100% | Precisão: 100% | F1: 100 | Score: 95.2
    naive_sequencial: Taxa: 100% | Precisão: 100% | F1: 100 | Score: 93.8

  caso_04_multiplas_modificacoes_interdependentes:
    offset_acumulado: Taxa: 100% | Precisão: 100% | F1: 100 | Score: 91.7
    naive_sequencial: Taxa: 67% | Precisão: 67% | F1: 67 | Score: 65.3
```

## 🤝 Contribuindo

Para adicionar novos casos de teste:

1. Criar fixture com caso real ou sintético
2. Definir ground truth (vinculações corretas)
3. Validar estrutura com teste automatizado
4. Documentar complexidade e motivação

Para adicionar novos algoritmos:

1. Implementar interface `AlgoritmoVinculacao`
2. Adicionar a `ALGORITMOS_DISPONIVEIS`
3. Rodar comparação em todas fixtures
4. Documentar estratégia e resultados

## 🐛 Debugging

```bash
# Ver logs detalhados de um algoritmo
python comparar_algoritmos.py --algoritmos meu_algoritmo -v

# Rodar teste específico
uv run pytest tests/test_comparacao_algoritmos.py::test_caso_simples_insercao -v -s

# Ver fixture específica
cat fixtures/caso_01_insercao_simples.json | jq
```

## 📚 Referências

- [Documentação de Fixtures](fixtures/README.md)
- [Guia de Desenvolvimento](COMO_ADICIONAR_ALGORITMOS.md)
- [Framework de Comparação](framework_comparacao.py)

## 🎯 Próximos Passos

1. ✅ Framework base implementado
2. ✅ 3 fixtures simples
3. ✅ 1 fixture média (interdependente)
4. ✅ 2 algoritmos exemplo
5. 🔄 Converter caso real (versão 2573b998) para fixture
6. 🔄 Implementar algoritmo "production" atual
7. 🔄 Implementar 2-3 novos algoritmos
8. 🔄 Comparação em larga escala (>20 fixtures)
9. 🔄 Integração com CI/CD

## 📞 Suporte

Para dúvidas ou sugestões, abra issue ou contate a equipe Versiona.

---

**Versão**: 1.0.0
**Data**: 2026-05-16
**Autores**: Equipe Versiona AI
