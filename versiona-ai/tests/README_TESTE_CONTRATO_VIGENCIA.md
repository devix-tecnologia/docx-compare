# Teste Automatizado - Contrato de Vigência e Suspensão

## Objetivo

Este teste valida o processamento correto do modelo e versão do contrato de vigência, garantindo que:

1. **Tags de seção** (números sem ponto, ex: "2") não sejam vinculadas diretamente a modificações
2. **Score ≥75%** seja considerado automático quando a tag aparece explicitamente no texto
3. **Modificações sejam detectadas** com precisão (alterações, inserções e remoções)
4. **Vinculações sejam precisas** com as cláusulas corretas

## Estrutura

```
tests/
├── fixtures/
│   └── contrato_vigencia_fixture.py  # Dados do modelo e versão
└── test_contrato_vigencia.py         # Casos de teste
```

## Fixtures

### `contrato_vigencia_fixture.py`

Contém os dados reais do contrato processado:

- **MODELO_TEXTO_ORIGINAL**: Texto completo do modelo (11 cláusulas)
- **VERSAO_TEXTO_MODIFICADO**: Texto da versão modificada
- **MODELO_CLAUSULAS**: Estrutura de cláusulas do modelo
- **MODIFICACOES_ESPERADAS**: 7 modificações esperadas
- **METRICAS_ESPERADAS**: Métricas de qualidade esperadas

### Modificações Esperadas (7 total)

1. **Alteração 1.1**: QUADRO RESUMO → ESCOPO INICIAL PREVISTO
2. **Remoção 1.2**: Remoção completa da cláusula sobre exclusividade
3. **Alteração 1.4**: Reorganização do texto sobre conflitos entre ANEXOS
4. **Alteração 1.5**: Movimentação do texto sobre conflitos para o final
5. **Alteração 2.2**: Mudança para maiúsculas (capitalização)
6. **Alteração 2.3**: CONTRATADA → EMPRESA CONTRATADA (no contexto de desmobilização)
7. **Inserção 2.5**: Nova cláusula sobre obrigações tributárias

### Métricas Esperadas

- **Total**: 7 modificações
- **Automáticas**: ≥5 (71%+)
- **Revisão manual**: 0
- **Não vinculadas**: 2 (remoção 1.2 + inserção 2.5)
- **Taxa de vinculação**: ≥71%

## Casos de Teste

### 1. `test_processamento_modelo_cria_tags_corretas`

Valida que o processamento do modelo:
- Cria 11+ tags
- Tags de seção (1, 2) **NÃO** têm `clausula_id`
- Tags específicas (1.1, 2.3) **TÊM** `clausula_id`

### 2. `test_processamento_versao_detecta_modificacoes_corretas`

Valida que o processamento da versão detecta exatamente 7 modificações.

### 3. `test_modificacao_1_1_alteracao_quadro_resumo`

Valida detecção da mudança QUADRO RESUMO → ESCOPO INICIAL PREVISTO:
- Tipo: ALTERACAO
- Status: automático
- Score: ≥75%
- Conteúdo correto nos textos original e novo

### 4. `test_modificacao_1_2_remocao_exclusividade`

Valida detecção da remoção da cláusula 1.2:
- Tipo: REMOCAO
- Contém palavra-chave "exclusividade"
- Se vinculada, deve ser automática e para cláusula 1.2

### 5. `test_modificacao_2_2_caixa_alta`

Valida mudança para maiúsculas na cláusula 2.2:
- Tipo: ALTERACAO
- Status: automático
- Apenas mudança de capitalização (mesmo texto em lowercase)

### 6. `test_modificacao_2_3_empresa_contratada`

Valida mudança CONTRATADA → EMPRESA CONTRATADA:
- Tipo: ALTERACAO
- Status: automático
- Mudança no contexto correto (desmobilização)

### 7. `test_modificacao_2_5_insercao_tributaria`

Valida inserção da cláusula 2.5:
- Tipo: INSERCAO
- Status: nao_vinculada
- Sem texto original
- Contém "obrigações tributárias"

### 8. `test_nenhuma_modificacao_requer_revisao_manual`

Valida que **nenhuma** modificação está em `revisao_manual`.

### 9. `test_metricas_vinculacao`

Valida métricas gerais:
- ≥5 automáticas
- 0 em revisão manual
- Taxa de vinculação ≥71%

### 10. `test_tags_secao_nao_vinculam_modificacoes`

**PROBLEMA #1 CORRIGIDO**: Garante que tags de seção não sejam vinculadas sem cláusula específica.

### 11. `test_threshold_75_para_tags_explicitas`

**PROBLEMA #2 CORRIGIDO**: Garante que score ≥75% com tag explícita seja automático.

## Como Executar

### Executar todos os testes

```bash
# Usando pytest diretamente
uv run pytest tests/test_contrato_vigencia.py -v

# Usando a task configurada
uv run pytest tests/ -v
```

### Executar teste específico

```bash
uv run pytest tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_modificacao_1_1_alteracao_quadro_resumo -v
```

### Executar com coverage

```bash
uv run pytest tests/test_contrato_vigencia.py -v --cov=versiona-ai --cov-report=html
```

### Executar em modo verbose com detalhes

```bash
uv run pytest tests/test_contrato_vigencia.py -vv --tb=long
```

## Saída Esperada

```
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_processamento_modelo_cria_tags_corretas PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_processamento_versao_detecta_modificacoes_corretas PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_modificacao_1_1_alteracao_quadro_resumo PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_modificacao_1_2_remocao_exclusividade PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_modificacao_2_2_caixa_alta PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_modificacao_2_3_empresa_contratada PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_modificacao_2_5_insercao_tributaria PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_nenhuma_modificacao_requer_revisao_manual PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_metricas_vinculacao PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_tags_secao_nao_vinculam_modificacoes PASSED
tests/test_contrato_vigencia.py::TestContratoVigenciaProcessamento::test_threshold_75_para_tags_explicitas PASSED

============================================ 11 passed in 2.34s ============================================
```

## Problemas Corrigidos

### Problema #1: Tags de Seção

**Antes**: Tag "2" (VIGÊNCIA E SUSPENSÃO) era vinculada a modificações sem `clausula_id`.

**Depois**: Tags de seção não são vinculadas diretamente, ou são vinculadas com cláusula específica.

### Problema #2: Threshold de Score

**Antes**: Score de 77% causava `revisao_manual` mesmo com tag explícita.

**Depois**: Score ≥75% com tag explícita no texto é classificado como `automatico`.

### Problema #3: Granularidade

**Antes**: Uma modificação grande combinava múltiplas mudanças.

**Depois**: Esperamos modificações separadas por cláusula.

### Problema #4: Detecção Precisa

**Antes**: Sistema reportava "EMPRESA CONTRATADA" na localização errada.

**Depois**: Validamos que a mudança está no contexto correto (desmobilização).

## Integração com CI/CD

Este teste pode ser integrado ao pipeline de CI/CD:

```yaml
# .github/workflows/tests.yml
- name: Run Contract Tests
  run: |
    uv run pytest tests/test_contrato_vigencia.py -v --junitxml=test-results.xml
```

## Manutenção

Para adicionar novos cenários de teste:

1. Adicione os dados em `contrato_vigencia_fixture.py`
2. Crie novo método `test_*` na classe `TestContratoVigenciaProcessamento`
3. Use as fixtures existentes como base
4. Execute e valide

## Referências

- **Modelo ID**: d2699a57-b0ff-472b-a130-626f5fc2852b
- **Versão ID**: 322e56c0-4b38-4e62-b563-8f29a131889c
- **Diff ID**: 3c56744f-29d3-4846-ac7a-1eef6ca25287
- **Análise Original**: `/tmp/versiona_data.json`
