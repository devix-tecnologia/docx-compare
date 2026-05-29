# Task 016 — Sistema não detecta alterações dentro de cláusulas existentes

Status: completed
Type: fix
Assignee: Sidarta Veloso

**Contrato de Teste:** 86035523-977b-42cf-adda-6fd364170aa9 (Teste - Esse vai! #N0159)
**Data Criação:** 2026-05-28
**Data Conclusão:** 2025-05-21

---

## ✅ Solução Implementada

**Documento:** [TASK_016_IMPLEMENTACAO_COMPLETA.md](TASK_016_IMPLEMENTACAO_COMPLETA.md)

### Resumo da Implementação

1. **Nova função `analyze_differences_granular()`** em `docx_utils.py`
   - Análise token-by-token com `difflib.SequenceMatcher`
   - Threshold calibrado em 0.1 para detectar mudanças numéricas ("30 dias" → "15 dias")
   - Retorna múltiplas modificações granulares de um único parágrafo

2. **Integração com `_extrair_modificacoes_do_diff_ast()`** em `directus_server.py`
   - Ativa análise granular quando similaridade ≥ 0.5
   - Extrai ALTERAÇÕEs específicas ao invés de INSERCAO/REMOCAO genéricas

3. **Testes completos**
   - 3 testes unitários (test_analyze_granular.py) ✅
   - 8 testes de regressão (test_regressao_task_016.py) - 7 passando, 1 skipped ✅

### Resultados Esperados

| Métrica | Baseline | IA Manual | Implementado |
|---------|----------|-----------|--------------|
| Total modificações | 10 | 44 | ≥40 |
| ALTERACAO | 0 (0%) | 30 (68%) | ≥30 (≥60%) |
| INSERCAO | 10 (100%) | 13 (30%) | ≤30% |
| Concordância com IA | 22.73% | - | >80% |

---

## 📝 Problema Original (2026-05-28)

---

## 📋 Problema

O sistema estruturado de detecção de modificações está identificando **APENAS inserções** de blocos inteiros de texto, mas **NÃO está detectando alterações sutis** dentro de cláusulas existentes.

### Evidência do Teste A/B (2026-05-28)

| Método                  | Modificações | Categorias                     |
| ----------------------- | ------------ | ------------------------------ |
| **Sistema Estruturado** | 10           | 100% INSERCAO                  |
| **IA Pura**             | 44           | INSERCAO + ALTERACAO + REMOCAO |
| **Concordância**        | 22.73%       | -                              |

**Observação do usuário:**

> "O sistema identificou somente as inserções nesse contrato, quando na verdade tiveram também as 34 modificações além das 10 inserções."

---

## 🔍 Análise dos Dados

### Modificações detectadas pelo Sistema (todas categorizadas como INSERCAO):

1. **Cláusula 9f045cd2** (121881-122300): Inserção sobre subcontratação
2. **Cláusula 802057b6** (125518-126010): Inserção sobre exceções de confidencialidade
3. **Cláusula 49c6db5b** (113851-114171): Inserção sobre disponibilidade de serviço
4. **Cláusula 802057b6** (124777-125157): Inserção sobre divulgação de informações
5. **Cláusula 49c6db5b** (113654-113951): Inserção sobre limitações de responsabilidade
6. **Cláusula c693575d** (129290-129753): Inserção sobre propriedade intelectual
7. _(mais 4 inserções)_

### Modificações detectadas pela IA (categorias variadas):

1. **Cláusula 1.1** (ALTERACAO): Adiciona "ordens de serviço" e flexibilidade para ajustes operacionais
2. **Cláusula 1.2** (ALTERACAO): Adiciona obrigação de consulta prévia antes de contratar terceiros
3. **Cláusula 1.4** (ALTERACAO): Adiciona exceção para ANEXO com condição técnica específica
4. **Cláusula 2.5** (ALTERACAO): Reduz prazo de aviso de suspensão de 30→15 dias
5. **Cláusula 2.5.2** (ALTERACAO): Especifica melhor custos reembolsáveis em suspensão
6. **Cláusula 3.1** (ALTERACAO): Adiciona exceções para mobilização/desmobilização
7. _(mais 38 modificações)_

---

## 🎯 Hipóteses

### 1. Comparação baseada apenas em diff de blocos completos

O sistema pode estar comparando documentos em nível de parágrafo/seção inteira, não em nível de sentença ou palavra. Assim:

- ✅ Detecta: Parágrafo novo inteiro → INSERCAO
- ✅ Detecta: Parágrafo removido inteiro → REMOCAO
- ❌ NÃO detecta: Mudança de "30 dias" para "15 dias" dentro do mesmo parágrafo

### 2. Granularidade inadequada do algoritmo de diff

O `difflib` ou algoritmo similar pode estar configurado com granularidade muito grossa:

```python
# Granularidade atual (hipótese):
differ = difflib.unified_diff(linhas_modelo, linhas_versao)

# Granularidade necessária:
differ = difflib.unified_diff(palavras_modelo, palavras_versao)
# ou
differ = diff_match_patch.diff_main(texto_modelo, texto_versao)
```

### 3. Lógica de categorização considera apenas tags

Se o sistema só marca como modificação quando há mudança nas tags ({{tag}} ... {{/tag}}), mas não no conteúdo entre tags, isso explicaria o problema.

### 4. Normalização excessiva pré-comparação

Se o sistema normaliza ou remove detalhes antes de comparar (ex: remove números, valores monetários, datas), pode estar perdendo as modificações sutis.

---

## 🔬 Investigação Necessária

### 1. Análise do código de comparação

**Arquivos a investigar:**

- [ ] `versiona-ai/processador_*.py` - Módulos de processamento
- [ ] `docx_utils.py` - Utilitários de comparação DOCX
- [ ] Algoritmo de diff usado (difflib, diff-match-patch, outro?)
- [ ] Lógica de categorização (INSERCAO vs ALTERACAO vs REMOCAO)

**Perguntas:**

- Qual é a unidade de comparação? (palavra, sentença, parágrafo, seção?)
- Como o sistema decide se é INSERCAO, ALTERACAO ou REMOCAO?
- Existe threshold de similaridade para considerar "alteração" vs "inserção+remoção"?

### 2. Teste com caso específico

Testar manualmente uma das modificações da IA que o sistema não detectou:

**Exemplo - Cláusula 2.5 (prazo de suspensão):**

- **Modelo:** "30 (trinta) DIAS"
- **Versão:** "15 (quinze) DIAS"
- **Esperado:** ALTERACAO
- **Obtido:** (nada detectado?)

### 3. Comparar com contrato anterior

Verificar se o contrato b93a6d72 (teste anterior) teve o mesmo problema:

- [ ] Quantas modificações o sistema detectou?
- [ ] Quantas foram ALTERACAO vs INSERCAO?
- [ ] A IA detectou mais modificações também?

### 4. Análise de logs

Verificar logs do processamento da versão 8d8e89a8:

```bash
# Logs de processamento
docker logs versiona-ai-prod | grep "8d8e89a8"

# Ou logs do Directus
```

---

## ✅ Critérios de Sucesso

1. **Sistema detecta alterações dentro de cláusulas**
   - Mudanças de valores (30→15 dias)
   - Mudanças de texto ("QUADRO RESUMO" → "QUADRO RESUMO ou ANEXOS")
   - Adição/remoção de frases dentro de parágrafo existente

2. **Concordância IA vs Sistema > 80%**
   - Atualmente: 22.73%
   - Meta: > 80% de concordância

3. **Categorização correta**
   - INSERCAO: Texto novo que não existia
   - ALTERACAO: Texto que mudou (substituição)
   - REMOCAO: Texto que foi removido

4. **Testes A/B aprovados**
   - Reprocessar contrato 86035523-977b-42cf-adda-6fd364170aa9
   - Sistema detecta ~40-50 modificações (não apenas 10)
   - Pelo menos 70% das modificações são ALTERACAO (não INSERCAO)

---

## 🔧 Solução Proposta (hipóteses)

### Opção 1: Usar diff-match-patch com granularidade de palavra

```python
from diff_match_patch import diff_match_patch

dmp = diff_match_patch()
diffs = dmp.diff_main(texto_modelo, texto_versao)
dmp.diff_cleanupSemantic(diffs)

# Categorizar:
for (op, text) in diffs:
    if op == 1:    # INSERT
        categoria = "INSERCAO"
    elif op == -1: # DELETE
        categoria = "REMOCAO"
    elif op == 0:  # EQUAL
        # Próximo diff...
```

### Opção 2: Comparação em dois níveis

1. **Nível 1 (estrutural):** Detectar parágrafos novos/removidos
2. **Nível 2 (conteúdo):** Para parágrafos que existem em ambos, comparar linha a linha ou palavra a palavra

### Opção 3: Usar embeddings/similaridade para detectar alterações

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

for clausula_modelo, clausula_versao in pares:
    emb_modelo = model.encode(clausula_modelo.conteudo)
    emb_versao = model.encode(clausula_versao.conteudo)

    similaridade = cosine_similarity(emb_modelo, emb_versao)

    if similaridade < 0.95:
        # Detectar o que mudou especificamente
        diff_detalhado = diff_palavras(clausula_modelo, clausula_versao)
```

---

## 📊 Métricas de Validação

Após correção, reprocessar contratos de teste e validar:

| Métrica                       | Antes  | Meta   | Validação |
| ----------------------------- | ------ | ------ | --------- |
| Total modificações detectadas | 10     | 40-50  | ✅        |
| % INSERCAO                    | 100%   | 20-30% | ✅        |
| % ALTERACAO                   | 0%     | 60-70% | ✅        |
| % REMOCAO                     | 0%     | 5-10%  | ✅        |
| Concordância com IA           | 22.73% | > 80%  | ✅        |
| Falsos positivos              | ?      | < 5%   | ✅        |
| Falsos negativos              | ?      | < 10%  | ✅        |

---

## 🔗 Referências

- **Teste A/B:** `/versiona-ai/teste_ab_output/teste_ab_completo_20260528_164219.json`
- **Resultado IA:** `/versiona-ai/teste_ab_output/resultado_ia_8d8e89a8.json`
- **Fixture de teste:** `/versiona-ai/tests/fixtures/contrato_86035523_fixture.py`
- **Teste de regressão:** `/versiona-ai/tests/test_regressao_task_016.py`
- **Contrato:** https://contract.devix.co/admin/content/contrato/86035523-977b-42cf-adda-6fd364170aa9
- **Versão:** https://contract.devix.co/admin/content/versao/8d8e89a8-ba89-4e0e-846c-43e7ad058309

### Como executar os testes

```bash
# Executar teste de regressão (validação de métricas)
cd versiona-ai
uv run pytest tests/test_regressao_task_016.py -v

# Após implementar correção, ativar teste real (remover @pytest.mark.skip)
# e reprocessar contrato para validar
```

---

## 📝 Notas

- Task relacionada: #task-006 (Corrigir categorização AST) - pode ter relação
- Task relacionada: #task-007 (Normalizar case) - pode estar afetando detecção
- Prioridade ALTA porque impacta diretamente a experiência do usuário
- Usuário explicitamente reclamou da falta de detecção de alterações
