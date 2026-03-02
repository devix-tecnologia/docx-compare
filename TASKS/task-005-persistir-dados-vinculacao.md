# Task 005: Persistir Dados de Vinculação no Directus

## Objetivo

Adicionar campos de metadados de vinculação à coleção `modificacao` no Directus e persistir esses dados durante o processamento, enriquecendo as informações sobre como cada modificação foi vinculada a uma cláusula.

## Contexto

Atualmente, o sistema:

- ✅ Vincula modificações às cláusulas usando diferentes métodos (conteúdo, sobreposição, etc.)
- ✅ Calcula scores de confiança para cada vinculação
- ✅ Determina se vinculação foi automática ou precisa revisão manual
- ❌ **Não persiste** esses metadados no Directus

Esses dados são importantes para:

- Auditoria e rastreabilidade das decisões de vinculação
- Identificar vinculações que precisam revisão manual
- Análise de qualidade do algoritmo de matching
- Interface frontend para mostrar nível de confiança

## Requisitos Funcionais

### 1. Adicionar Campos na Coleção `modificacao`

Novos campos a serem adicionados:

| Campo               | Tipo     | Nullable | Default | Descrição                                                     |
| ------------------- | -------- | -------- | ------- | ------------------------------------------------------------- |
| `metodo_vinculacao` | `string` | `true`   | `null`  | Método usado: "conteudo", "sobreposicao", "posicao", "manual" |
| `score_vinculacao`  | `float`  | `true`   | `null`  | Score de confiança (0.0 a 1.0)                                |
| `status_vinculacao` | `string` | `true`   | `null`  | Status: "automatico", "revisao_manual", "nao_vinculada"       |

**Notas:**

- Todos os campos são **nullable** para compatibilidade com dados já processados
- Modificações antigas sem esses campos continuam funcionando
- Novos processamentos devem preencher esses campos quando disponíveis

### 2. Popular Dados Durante Processamento

No método que persiste modificações (`_converter_modificacao_para_directus` ou similar), adicionar:

```python
def _converter_modificacao_para_directus(mod: dict, versao_id: str, ordem: int) -> dict:
    """
    Converte modificação para formato do Directus.
    """
    payload = {
        "versao": versao_id,
        "categoria": mod.get("tipo", "modificacao"),
        "conteudo": conteudo_str,
        "alteracao": alteracao_str,
        "posicao_inicio": mod.get("posicao_inicio", 0),
        "posicao_fim": mod.get("posicao_fim", 0),
        "caminho_inicio": mod.get("caminho_inicio"),
        "caminho_fim": mod.get("caminho_fim"),
        "ordem": ordem,
        "clausula": clausula_id,

        # NOVOS CAMPOS DE VINCULAÇÃO
        "metodo_vinculacao": mod.get("metodo_vinculacao"),
        "score_vinculacao": mod.get("score_vinculacao"),
        "status_vinculacao": mod.get("status_vinculacao"),
    }

    return payload
```

### 3. Garantir Algoritmo Popula Metadados

O algoritmo de vinculação (`_vincular_modificacoes_com_tags`) já deve estar retornando esses dados nas modificações. Verificar e garantir que:

```python
# No algoritmo de vinculação
modificacao_vinculada = {
    **modificacao,
    "clausula_id": clausula_vinculada["id"],
    "metodo_vinculacao": "conteudo",  # ou "sobreposicao", "posicao"
    "score_vinculacao": 0.95,
    "status_vinculacao": "automatico",  # ou "revisao_manual" se score < threshold
}
```

### 4. Lógica de Status

Determinar `status_vinculacao` baseado no score:

```python
def _determinar_status_vinculacao(score: float) -> str:
    """
    Determina status da vinculação baseado no score de confiança.

    Args:
        score: Score de 0.0 a 1.0

    Returns:
        "automatico": score >= 0.85 (alta confiança)
        "revisao_manual": 0.5 <= score < 0.85 (média confiança, precisa revisão)
        "nao_vinculada": score < 0.5 (baixa confiança, não vincular)
    """
    if score >= 0.85:
        return "automatico"
    elif score >= 0.5:
        return "revisao_manual"
    else:
        return "nao_vinculada"
```

## Requisitos Técnicos

### 1. Migração do Schema Directus

Adicionar os campos via API ou interface administrativa:

```bash
# Via API (exemplo usando curl)
curl -X PATCH "https://contract.devix.co/fields/modificacao/metodo_vinculacao" \
  -H "Authorization: Bearer $DIRECTUS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field": "metodo_vinculacao",
    "type": "string",
    "meta": {
      "interface": "select-dropdown",
      "options": {
        "choices": [
          {"text": "Conteúdo", "value": "conteudo"},
          {"text": "Sobreposição", "value": "sobreposicao"},
          {"text": "Posição", "value": "posicao"},
          {"text": "Manual", "value": "manual"}
        ]
      }
    }
  }'

curl -X PATCH "https://contract.devix.co/fields/modificacao/score_vinculacao" \
  -H "Authorization: Bearer $DIRECTUS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field": "score_vinculacao",
    "type": "float",
    "meta": {
      "interface": "input",
      "options": {
        "min": 0,
        "max": 1,
        "step": 0.01
      }
    }
  }'

curl -X PATCH "https://contract.devix.co/fields/modificacao/status_vinculacao" \
  -H "Authorization: Bearer $DIRECTUS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field": "status_vinculacao",
    "type": "string",
    "meta": {
      "interface": "select-dropdown",
      "options": {
        "choices": [
          {"text": "Automático", "value": "automatico"},
          {"text": "Revisão Manual", "value": "revisao_manual"},
          {"text": "Não Vinculada", "value": "nao_vinculada"}
        ]
      }
    }
  }'
```

### 2. Modificar Código de Persistência

Arquivos a modificar:

- `versiona-ai/directus_server.py`:
  - `_converter_modificacao_para_directus()`: adicionar novos campos
  - Verificar se algoritmo de vinculação já popula metadados
  - Adicionar função `_determinar_status_vinculacao()` se necessário

### 3. Compatibilidade com Dados Antigos

- Modificações já persistidas continuam funcionando (campos nullable)
- Consultas não quebram se campos forem `null`
- Frontend (task-004) já trata campos opcionais

## Estrutura de Dados Completa

### Antes (Atual)

```json
{
  "id": "mod-001",
  "categoria": "modificacao",
  "conteudo": "prazo de 30 dias",
  "alteracao": "prazo de 45 dias",
  "clausula": "clausula-001"
}
```

### Depois (Com Metadados)

```json
{
  "id": "mod-001",
  "categoria": "modificacao",
  "conteudo": "prazo de 30 dias",
  "alteracao": "prazo de 45 dias",
  "clausula": "clausula-001",
  "metodo_vinculacao": "conteudo",
  "score_vinculacao": 0.95,
  "status_vinculacao": "automatico"
}
```

## Benefícios

1. **Auditoria**: Rastrear como cada vinculação foi feita
2. **Qualidade**: Identificar vinculações duvidosas para revisão manual
3. **Analytics**: Analisar performance dos algoritmos de matching
4. **UX**: Frontend pode mostrar indicadores de confiança ao usuário
5. **Debug**: Facilita investigação de vinculações incorretas

## Validação

### Testes

- [ ] Schema do Directus atualizado com novos campos
- [ ] Campos aparecem na interface administrativa do Directus
- [ ] Processamento de nova versão preenche campos de vinculação
- [ ] Modificações com vinculação automática têm `status_vinculacao="automatico"`
- [ ] Modificações com baixo score têm `status_vinculacao="revisao_manual"`
- [ ] Modificações não vinculadas têm `status_vinculacao="nao_vinculada"`
- [ ] Dados antigos (sem metadados) continuam funcionando
- [ ] API `/view` retorna metadados quando disponíveis (task-004)
- [ ] Queries no Directus com filtro por `status_vinculacao` funcionam

### Checklist de Implementação

- [ ] Adicionar campos `metodo_vinculacao`, `score_vinculacao`, `status_vinculacao` no schema Directus
- [ ] Criar função `_determinar_status_vinculacao(score) -> str`
- [ ] Modificar algoritmo de vinculação para popular metadados em cada modificação
- [ ] Atualizar `_converter_modificacao_para_directus()` para incluir novos campos
- [ ] Testar com processamento de versão real
- [ ] Verificar compatibilidade: dados antigos sem metadados continuam funcionando
- [ ] Validar que task-004 exibe metadados corretamente
- [ ] Documentar novos campos na API
- [ ] Criar consultas/views no Directus para análise de qualidade
- [ ] Escrever testes unitários para `_determinar_status_vinculacao()`
- [ ] Escrever testes de integração com Directus

## Arquivos Afetados

- `versiona-ai/directus_server.py`:
  - `_converter_modificacao_para_directus()`
  - `_determinar_status_vinculacao()` (nova função)
  - Algoritmo de vinculação (verificar se já popula metadados)
- `config/directus-schema.json` (atualizar documentação do schema)
- `API_DOCUMENTATION.md` (documentar novos campos)
- `tests/test_vinculacao_metadados.py` (novos testes)

## Prioridade

**MÉDIA** - Melhoria incremental, não bloqueia task-004

## Dependências

- ✅ Task 003 concluída (vinculação básica funcionando)
- ✅ Task 004 iniciada (já preparada para campos opcionais)
- Acesso administrativo ao Directus para modificar schema

## Observações

### Thresholds de Score

Os thresholds podem ser ajustados baseado em análise empírica:

```python
THRESHOLD_AUTOMATICO = 0.85  # Alta confiança
THRESHOLD_REVISAO = 0.5      # Média confiança
# < 0.5 = não vincular
```

### Análise de Qualidade

Com esses dados, é possível criar dashboards no Directus ou ferramentas de análise:

```sql
-- Quantas vinculações automáticas vs revisão manual?
SELECT status_vinculacao, COUNT(*)
FROM modificacao
GROUP BY status_vinculacao;

-- Distribuição de scores
SELECT
  CASE
    WHEN score_vinculacao >= 0.9 THEN 'Excelente (>= 0.9)'
    WHEN score_vinculacao >= 0.8 THEN 'Bom (0.8-0.9)'
    WHEN score_vinculacao >= 0.6 THEN 'Médio (0.6-0.8)'
    ELSE 'Baixo (< 0.6)'
  END as faixa,
  COUNT(*)
FROM modificacao
WHERE score_vinculacao IS NOT NULL
GROUP BY faixa;

-- Qual método tem melhor score médio?
SELECT metodo_vinculacao, AVG(score_vinculacao) as score_medio
FROM modificacao
WHERE score_vinculacao IS NOT NULL
GROUP BY metodo_vinculacao;
```

### Interface Administrativa

Configurar no Directus:

- **Filtros**: por `status_vinculacao` (mostrar só as que precisam revisão)
- **Ordenação**: por `score_vinculacao` (piores primeiro)
- **Badges**: cores diferentes para cada status (verde=automático, amarelo=revisão, vermelho=não vinculada)
- **Alertas**: notificar quando muitas modificações precisam revisão

### Revisão Manual Futura

Com esses campos, é possível criar uma interface de revisão onde:

1. Usuário vê modificações com `status_vinculacao="revisao_manual"`
2. Pode confirmar vinculação automática ou escolher outra cláusula
3. Ao confirmar, status muda para "manual" (confirmado por humano)
4. Score original é preservado para análise
