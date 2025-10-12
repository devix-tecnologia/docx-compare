# Task 003: Corrigir Vinculação de Modificações às Cláusulas (Meta: 100%)

**Data de Criação:** 2025-10-11
**Status:** 🟡 Solução Proposta (Refinada)
**Prioridade:** Alta
**Responsável:** A definir

---

## 🎯 Resumo Executivo

**Problema:** Apenas 14.5% (8/55) das modificações estão sendo vinculadas às cláusulas corretas devido a um deslocamento no sistema de coordenadas entre o arquivo COM tags (modelo) e o arquivo original da versão.

**Solução:** Implementar algoritmo unificado com duas estratégias:

1. **Caminho Feliz (95%+ similaridade):** Cálculo matemático de offset → 100% preciso
2. **Caminho Real (<95% similaridade):** Inferência por conteúdo com contexto → 85-95% preciso

**Benefícios:**

- 📈 **+500% de melhoria:** De 14.5% para 75-85% de vinculação automática
- 🎯 **90-98% de cobertura total:** Incluindo fila de revisão manual
- 📊 **Sistema de qualidade:** Score de confiança (0.0-1.0) para cada vinculação
- 🔍 **Revisão inteligente:** Apenas casos ambíguos vão para revisão humana

**Esforço:** 30-44 horas (~1 semana) dividido em 6 fases incrementais

**Risco:** 🟢 Baixo - Solução testável por partes, com fallback e reversibilidade

---

## � Índice

1. [🎯 Resumo Executivo](#-resumo-executivo)
2. [📋 Contexto](#-contexto)
3. [🎯 Objetivo](#-objetivo)
4. [⚠️ Problema Identificado](#️-problema-identificado-revisado)
5. [💡 Solução Proposta](#-solução-proposta-algoritmo-unificado-de-mapeamento-de-coordenadas)
   - [Cenário 1: Caminho Feliz](#cenário-1-caminho-feliz-arquivos-idênticos)
   - [Cenário 2: Caminho Real](#cenário-2-caminho-real-arquivos-diferentes)
   - [Algoritmo Unificado](#o-algoritmo-unificado)
6. [🔧 Casos de Borda e Robustez](#-casos-de-borda-e-robustez)
7. [📁 Arquivos Relevantes](#-arquivos-relevantes-para-a-solução)
8. [🧪 Como Testar](#-como-testar-a-solução)
9. [📊 Critérios de Sucesso](#-critérios-de-sucesso)
10. [📈 Estimativa de Taxa de Sucesso](#-estimativa-de-taxa-de-sucesso)
11. [🔍 Considerações Técnicas](#-considerações-técnicas-adicionais)
12. [🚀 Próximos Passos](#-próximos-passos-sugeridos-ordem-de-implementação)
13. [📚 Referências](#-referências-e-recursos)

---

## �📋 Contexto

Após implementação inicial da vinculação de modificações às cláusulas via tags do modelo de contrato, obtivemos apenas **14.5% de sucesso (8/55 modificações vinculadas)**. O objetivo é alcançar **100% de vinculação** para todas as modificações que possuem correspondência válida no modelo.

---

## 🎯 Objetivo

Implementar um **algoritmo unificado de mapeamento de coordenadas** para que **100% das modificações válidas sejam vinculadas às suas cláusulas correspondentes**, corrigindo o deslocamento entre os sistemas de coordenadas do `diff` e das tags.

---

## ⚠️ Problema Identificado (Revisado)

### Raiz do Problema: Deslocamento de Coordenadas

O problema não é que os documentos são fundamentalmente diferentes, mas sim que o **`arquivo_com_tags` é uma derivação do `arquivo_original`**, com as tags injetadas. Essa injeção **desloca as coordenadas** de tudo que vem depois da primeira tag.

1.  **Arquivo Original (Base):** `BOM DIA.`
2.  **Arquivo COM Tags (Derivado):** `BOM{{TAG-1}} DIA{{/TAG-1}}.`

A posição da modificação é calculada no Arquivo 1, enquanto a posição da tag é salva no Arquivo 2. Compará-las diretamente é como comparar o endereço de uma casa em uma rua antes e depois de construir um novo prédio no quarteirão.

### O Que Acontece Hoje

```
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 1: Gerar Diff                                             │
│ diff = compare(arquivo_original_versao, arquivo_modificado)     │
│ → Modificações têm posições no arquivo_original_versão          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PASSO 2: Vincular às Tags                                       │
│ tags = buscar_tags_do_modelo()                                  │
│ → Tags têm posições no arquivo_com_tags (SISTEMA DESLOCADO!)    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PROBLEMA: Comparação Inválida                                   │
│ if tag.posicao_inicio <= mod.posicao <= tag.posicao_fim:        │
│    ❌ FALSO POSITIVO ou FALSO NEGATIVO                          │
│    (comparando posições de sistemas deslocados!)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💡 Solução Proposta: Algoritmo Unificado de Mapeamento de Coordenadas

Propomos um algoritmo robusto que lida com dois cenários principais, escolhendo a estratégia ideal para cada caso.

### Cenário 1: "Caminho Feliz" (Arquivos Idênticos)

Quando o `arquivo_original_versao` é idêntico ao texto base usado para gerar as tags, podemos usar um cálculo matemático preciso.

**Abordagem: Cálculo de Offset com Tags Aninhadas**

1.  **Verificar similaridade:** Calcular similaridade entre `arquivo_original_versao` (normalizado) e `arquivo_com_tags` (sem tags e normalizado). Threshold: **≥ 95%** para considerar idênticos.
2.  **Calcular offset acumulado:** Percorrer o arquivo COM tags em ordem linear, acumulando o tamanho de cada tag encontrada. Isso gera um mapa: `(posicao_com_tag → offset_acumulado)`.

```python
# Exemplo:
# Arquivo Original: "ABC DEF GHI"
# Arquivo COM Tags: "ABC {{TAG-1}}DEF {{TAG-2}}GHI{{/TAG-2}}{{/TAG-1}}"
#
# Mapa de offsets:
# posicao 0-3:   offset = 0   (antes de qualquer tag)
# posicao 4-6:   offset = 11  (depois de "{{TAG-1}}")
# posicao 7-9:   offset = 22  (depois de "{{TAG-1}}" e "{{TAG-2}}")
```

3.  **Mapear tags para coordenadas originais:** Para cada tag, calcular:

- `posicao_original_inicio = posicao_com_tags_inicio - offset_antes_da_tag`
- `posicao_original_fim = posicao_com_tags_fim - offset_antes_da_tag`

4.  **Vincular:** Comparar a posição da modificação com a posição da tag recalculada.

**Vantagens:**

- ✅ **100% preciso e infalível** para este cenário.
- ✅ **Extremamente rápido** (complexidade O(N log N) por ordenação).
- ✅ **Lida corretamente com tags aninhadas** através do offset acumulado.

### Cenário 2: "Caminho Real" (Arquivos Diferentes)

Quando o `arquivo_original_versao` é uma versão antiga ou foi alterado, o cálculo de offset falha. Usamos uma abordagem de inferência baseada em conteúdo com contexto de vizinhança.

**Abordagem: Inferência por Conteúdo com Contexto (LCS + Vizinhança)**

1.  **Para cada tag:** Extrair três elementos:
    - **Conteúdo textual:** O texto dentro da tag (ex: " DIA ")
    - **Contexto anterior:** N caracteres antes da tag (sugerido: 50 caracteres)
    - **Contexto posterior:** N caracteres depois da tag (sugerido: 50 caracteres)
2.  **Normalizar** o conteúdo da tag e o texto do `arquivo_original_versao`.
3.  **Inferir posição com contexto:** Buscar a sequência `contexto_antes + conteudo + contexto_depois` dentro do arquivo da versão usando busca por subsequência comum (LCS).
    - **Benefício do contexto:** Resolve ambiguidade quando o mesmo texto aparece em múltiplas cláusulas.
    - **Exemplo:** "O contratante pagará" pode aparecer em cláusulas diferentes, mas o contexto diferencia.
4.  **Fallback:** Se não encontrar com contexto completo, tentar:
    - Apenas conteúdo + contexto posterior
    - Apenas conteúdo + contexto anterior
    - Apenas conteúdo (último recurso)
5.  **Score de confiança:** Atribuir score baseado no método usado:
    - Contexto completo: **0.9**
    - Contexto parcial: **0.7**
    - Apenas conteúdo: **0.5**
6.  **Vincular:** Usar a posição inferida para vincular a modificação.

**Vantagens:**

- ✅ **Robusto**, lida com documentos de bases diferentes.
- ✅ **Funciona mesmo se o conteúdo da cláusula foi alterado** (usando contexto).
- ✅ **Resolve ambiguidade** através do contexto de vizinhança.
- ✅ **Múltiplos níveis de fallback** aumentam taxa de sucesso.

**Otimizações de Performance:**

- 🚀 **Índice de n-gramas:** Pré-processar o arquivo original em chunks de 20-50 caracteres para busca rápida.
- 🚀 **Early exit:** Se encontrar match exato com contexto, não testar outras variações.
- 🚀 **Paralelização:** Processar tags em paralelo usando `multiprocessing` para documentos grandes.

### O Algoritmo Unificado

A solução final é uma função que tenta o "Caminho Feliz" primeiro e, em caso de falha, recorre ao "Caminho Real", com sistema de score e revisão manual.

```python
def vincular_modificacoes_unificado(tags, modificacoes, arquivo_original_versao, arquivo_com_tags):
    """
    Algoritmo unificado com fallback e score de confiança.

    Returns:
        dict: {
            'vinculadas': [(mod, clausula, score), ...],
            'nao_vinculadas': [mod, ...],
            'revisao_manual': [(mod, candidatos, score), ...]
        }
    """
    # 1. Normalizar textos
    texto_base = normalizar(extrair_texto_sem_tags(arquivo_com_tags))
    texto_versao = normalizar(arquivo_original_versao)

    # 2. Escolher estratégia baseado em similaridade
    similaridade = calcular_similaridade(texto_base, texto_versao)

    if similaridade >= 0.95:  # Threshold: 95%
        print(f"🎯 Caminho Feliz: Documentos idênticos (similaridade: {similaridade:.2%})")
        tags_mapeadas = mapear_via_offset(tags, arquivo_com_tags)
        score_base = 1.0  # Confiança máxima
    else:
        print(f"🎯 Caminho Real: Documentos divergentes (similaridade: {similaridade:.2%})")
        tags_mapeadas = inferir_via_conteudo_com_contexto(tags, texto_versao, arquivo_com_tags)
        score_base = 0.8  # Confiança reduzida (ajustado durante inferência)

    # 3. Vincular com cálculo de score e categorização
    resultados = {
        'vinculadas': [],
        'nao_vinculadas': [],
        'revisao_manual': []
    }

    for mod in modificacoes:
        candidatos = encontrar_tags_sobrepostas(mod, tags_mapeadas)

        if not candidatos:
            resultados['nao_vinculadas'].append(mod)
            continue

        # Calcular score para cada candidato
        melhor_candidato = None
        melhor_score = 0

        for tag in candidatos:
            percentual_sobreposicao = calcular_sobreposicao(mod, tag)
            score = tag.score_inferencia * percentual_sobreposicao  # score_inferencia vem do "Caminho"

            if score > melhor_score:
                melhor_score = score
                melhor_candidato = tag

        # Decidir destino baseado no score
        if melhor_score >= 0.7:  # Alta confiança
            resultados['vinculadas'].append((mod, melhor_candidato.clausula, melhor_score))
        elif melhor_score >= 0.4:  # Média confiança - revisão manual
            resultados['revisao_manual'].append((mod, candidatos, melhor_score))
        else:  # Baixa confiança
            resultados['nao_vinculadas'].append(mod)

    # 4. Log de estatísticas
    total = len(modificacoes)
    print(f"📊 Vinculação concluída:")
    print(f"   ✅ Vinculadas: {len(resultados['vinculadas'])}/{total} ({len(resultados['vinculadas'])/total*100:.1f}%)")
    print(f"   🔍 Revisão manual: {len(resultados['revisao_manual'])}/{total} ({len(resultados['revisao_manual'])/total*100:.1f}%)")
    print(f"   ❌ Não vinculadas: {len(resultados['nao_vinculadas'])}/{total} ({len(resultados['nao_vinculadas'])/total*100:.1f}%)")

    return resultados
```

**Thresholds Configuráveis:**

- **Similaridade para Caminho Feliz:** 95% (ajustar se necessário)
- **Score mínimo para vinculação automática:** 0.7
- **Score mínimo para revisão manual:** 0.4
- **Contexto de vizinhança:** 50 caracteres (ajustar para cláusulas muito curtas/longas)

---

## 🔧 Casos de Borda e Robustez

A solução incluirá mecanismos para lidar com situações complexas:

### 1. Modificações que Cruzam Fronteiras de Cláusulas

**Problema:** Uma modificação pode afetar o final de uma cláusula e o início da próxima.

```
Exemplo:
Cláusula 1.1: [pos 0-1000]   "...final da cláusula"
Cláusula 1.2: [pos 1001-2000] "início da próxima..."
Modificação: [pos 950-1050]   Afeta ambas! (50 chars em cada)
```

**Solução:**

- **Regra Principal:** Vincular à cláusula que contém a **maior parte** da modificação.
- **Vinculação Múltipla (Opcional):** Se ambas as cláusulas têm sobreposição ≥ 30% (threshold configurável):
  ```python
  if percentual_sobreposicao_clausula_2 >= 0.30:
      modificacao.clausulas = [clausula_1, clausula_2]  # Array
      modificacao.clausula_principal = clausula_com_maior_sobreposicao
      modificacao.flag_multi_clausula = True
  ```
- **Benefício:** Permite análises mais ricas (ex: "modificações que afetam múltiplas cláusulas").

### 2. Score de Confiança em Três Níveis

Cada vinculação terá um score que determina seu tratamento:

| Nível                  | Score      | Ação                   | Exemplo                           |
| ---------------------- | ---------- | ---------------------- | --------------------------------- |
| 🟢 **Alta Confiança**  | ≥ 0.7      | Vinculação automática  | Caminho Feliz + 100% sobreposição |
| 🟡 **Média Confiança** | 0.4 - 0.69 | Fila de revisão manual | Inferência com contexto parcial   |
| 🔴 **Baixa Confiança** | < 0.4      | Não vincular (orphan)  | Múltiplos candidatos ambíguos     |

**Cálculo do Score:**

```python
score_final = score_metodo × percentual_sobreposicao × fator_contexto

Onde:
- score_metodo: 1.0 (offset), 0.9 (contexto completo), 0.7 (parcial), 0.5 (só conteúdo)
- percentual_sobreposicao: 0.0 a 1.0 (quanto da modificação está dentro da tag)
- fator_contexto: 1.0 (único candidato), 0.8 (múltiplos candidatos mas um claro vencedor)
```

### 3. Fila de Revisão Manual

Modificações com média confiança (0.4-0.69) são enviadas para revisão:

```json
{
  "modificacao_id": 42,
  "candidatos": [
    {
      "clausula": "1.1 - Objeto do Contrato",
      "score": 0.62,
      "razao": "Inferência com contexto parcial, 80% de sobreposição"
    },
    {
      "clausula": "2.1 - Objeto da Empreitada",
      "score": 0.45,
      "razao": "Texto similar mas contexto diferente, 50% de sobreposição"
    }
  ],
  "recomendacao": "clausula_1",
  "requer_revisao_humana": true
}
```

**Interface Sugerida (futuro):**

- Dashboard mostrando modificações pendentes de revisão
- Botões: "Aprovar recomendação", "Escolher outro candidato", "Marcar como sem cláusula"

### 4. Textos Ambíguos (Repetidos)

**Problema:** Cláusulas com texto idêntico ou muito similar.

```
Cláusula 1.1: "O contratante pagará o valor acordado..."
Cláusula 5.1: "O contratante pagará o valor acordado..."  # Idêntico!
```

**Soluções Implementadas:**

- ✅ **Contexto de vizinhança** (50 chars antes/depois) diferencia na maioria dos casos
- ✅ **Ordenação por score** garante que apenas o melhor candidato seja escolhido
- ✅ Se múltiplos candidatos com score similar (diferença < 0.1), marcar para revisão manual

### 5. Performance com Documentos Grandes

**Problema:** Busca por subsequência (LCS) é O(n×m). Com 100 tags e documento de 200KB:

- Pior caso: ~2 segundos por documento

**Otimizações:**

1. **Índice de N-gramas (Pré-processamento):**

   ```python
   # Construir índice uma vez por documento
   indice = construir_indice_ngramas(arquivo_original, n=20)
   # {
   #   "O contratante paga": [pos1, pos37, pos842, ...],
   #   "contratante pagará": [pos2, pos38, pos843, ...],
   #   ...
   # }

   # Busca se torna O(1) amortizado
   posicoes_candidatas = indice.buscar(primeiros_20_chars_da_tag)
   ```

2. **Early Exit:**

   ```python
   if encontrou_match_com_contexto_completo_e_score_1_0:
       return resultado  # Não testar fallbacks
   ```

3. **Paralelização (Opcional):**

   ```python
   from multiprocessing import Pool

   with Pool(processes=4) as pool:
       tags_mapeadas = pool.map(inferir_posicao_tag, tags)
   ```

   - Útil para documentos com 100+ tags
   - Reduz tempo de ~2s para ~0.5s (4 cores)

### 6. Normalização Consistente

Garantir que a normalização seja **idempotente e consistente** em todos os pontos:

```python
def normalizar_texto(texto):
    """Normalização padronizada para todo o sistema."""
    # 1. Converter para minúsculas (opcional, depende do caso de uso)
    # texto = texto.lower()

    # 2. Normalizar espaços em branco
    texto = re.sub(r'\s+', ' ', texto)

    # 3. Remover espaços no início/fim
    texto = texto.strip()

    # 4. Normalizar quebras de linha (se relevante)
    texto = texto.replace('\r\n', '\n').replace('\r', '\n')

    # 5. Unicode normalization (NFC)
    import unicodedata
    texto = unicodedata.normalize('NFC', texto)

    return texto
```

**IMPORTANTE:** Aplicar a **mesma função** em:

- Arquivo COM tags (ao remover tags)
- Arquivo original da versão
- Conteúdo extraído das tags
- Contexto de vizinhança

---

## 📁 Arquivos Relevantes para a Solução

### Código Principal

1.  **`versiona-ai/directus_server.py`**

    **Funções a Criar:**

    - **`_vincular_modificacoes_clausulas_unificado()`** (nova - principal)

      - Implementa a lógica `if/else` do algoritmo unificado
      - Calcula similaridade e escolhe entre Caminho Feliz ou Real
      - Retorna dict com vinculadas/nao_vinculadas/revisao_manual
      - **Assinatura:** `(tags, modificacoes, arquivo_original_versao, arquivo_com_tags) → dict`

    - **`_mapear_tags_via_offset()`** (nova - Caminho Feliz)

      - Implementa o cálculo de offset acumulado para tags aninhadas
      - Percorre arquivo COM tags, identifica todas as tags via regex
      - Para cada tag, calcula: `posicao_original = posicao_com_tags - offset_acumulado`
      - **Assinatura:** `(tags, arquivo_com_tags) → List[TagMapeada]`
      - **Complexidade:** O(N log N) onde N = número de tags

    - **`_inferir_posicoes_via_conteudo_com_contexto()`** (nova - Caminho Real)

      - Implementa busca por subsequência com contexto de vizinhança
      - Para cada tag: extrai conteúdo + 50 chars antes + 50 chars depois
      - Tenta match com contexto completo, depois parcial, depois só conteúdo
      - Atribui score baseado no método usado (0.9, 0.7, 0.5)
      - **Assinatura:** `(tags, arquivo_original_versao, arquivo_com_tags) → List[TagMapeada]`
      - **Complexidade:** O(T × M) onde T = número de tags, M = tamanho do documento
      - **Otimização:** Usar índice de n-gramas para reduzir M

    - **`_vincular_por_sobreposicao_com_score()`** (nova)

      - Lógica final de vinculação com coordenadas já alinhadas
      - Para cada modificação, encontra tags que se sobrepõem
      - Calcula score: `tag.score_inferencia × percentual_sobreposicao × fator_contexto`
      - Categoriza: alta confiança (≥0.7), revisão (0.4-0.69), baixa (<0.4)
      - **Assinatura:** `(modificacoes, tags_mapeadas) → dict`

    - **`_calcular_similaridade_textos()`** (nova - utilitário)

      - Calcula similaridade entre dois textos normalizados
      - Usa algoritmo de distância de Levenshtein ou ratio do difflib
      - **Assinatura:** `(texto1, texto2) → float (0.0 a 1.0)`

    - **`_construir_indice_ngramas()`** (nova - otimização)

      - Constrói índice de n-gramas para busca rápida
      - **Assinatura:** `(texto, n=20) → Dict[str, List[int]]`
      - **Opcional:** Implementar apenas se performance for problema

    - **`normalizar_texto()`** (modificar existente ou criar nova)
      - Função centralizada de normalização
      - Deve ser usada em TODOS os pontos: tags, modificações, contexto
      - Garante consistência: espaços, quebras de linha, unicode
      - **Assinatura:** `(texto) → str`

    **Classes de Dados Sugeridas:**

    ```python
    @dataclass
    class TagMapeada:
        """Tag com posições recalculadas no sistema de coordenadas original."""
        tag_id: str
        tag_nome: str
        posicao_inicio_original: int  # Posição no arquivo SEM tags
        posicao_fim_original: int
        clausulas: List[Dict]
        score_inferencia: float  # 1.0 (offset), 0.9-0.5 (contexto)
        metodo: str  # "offset", "contexto_completo", "contexto_parcial", "conteudo"

    @dataclass
    class ResultadoVinculacao:
        """Resultado da vinculação com categorização por confiança."""
        vinculadas: List[Tuple[Dict, str, float]]  # (modificacao, clausula_id, score)
        nao_vinculadas: List[Dict]  # modificacoes sem candidatos
        revisao_manual: List[Tuple[Dict, List[Dict], float]]  # (mod, candidatos, score)

        def taxa_sucesso(self) -> float:
            total = len(self.vinculadas) + len(self.nao_vinculadas) + len(self.revisao_manual)
            return len(self.vinculadas) / total if total > 0 else 0.0

        def taxa_cobertura(self) -> float:
            """Inclui revisão manual como potencial sucesso."""
            total = len(self.vinculadas) + len(self.nao_vinculadas) + len(self.revisao_manual)
            cobertos = len(self.vinculadas) + len(self.revisao_manual)
            return cobertos / total if total > 0 else 0.0
    ```

### Testes

2.  **`versiona-ai/tests/test_vinculacao_formatacao.py`**

    **Testes Existentes (Manter e Adaptar):**

    - `test_vinculacao_com_formatacao_variada()` - Validar normalização
    - `test_vinculacao_com_normalizacao()` - Validar estratégia de normalização
    - `test_vinculacao_com_mock_completo()` - Testar com mocks (adaptar para novo algoritmo)

    **Novos Testes a Criar:**

    - **`test_caminho_feliz_offset_simples()`**

      - Arquivo original idêntico ao arquivo COM tags (sem as tags)
      - Tags não aninhadas, posições simples
      - **Esperado:** 100% de vinculação, todos com score 1.0

    - **`test_caminho_feliz_offset_tags_aninhadas()`**

      - Tags aninhadas: `{{TAG-1}}...{{TAG-1.1}}...{{/TAG-1.1}}...{{/TAG-1}}`
      - Validar que offset acumulado funciona corretamente
      - **Esperado:** 100% de vinculação, posições corretas mesmo com aninhamento

    - **`test_caminho_real_contexto_completo()`**

      - Arquivo original DIFERENTE do arquivo COM tags
      - Modificações com contexto único que permite inferência precisa
      - **Esperado:** ≥90% de vinculação, scores entre 0.8-0.9

    - **`test_caminho_real_texto_ambiguo()`**

      - Múltiplas cláusulas com texto similar
      - Contexto de vizinhança diferencia
      - **Esperado:** Vinculação correta usando contexto, score 0.9

    - **`test_modificacao_cruzando_fronteiras()`**

      - Modificação que afeta duas cláusulas (50% em cada)
      - **Esperado:** Vinculada à cláusula principal, flag `multi_clausula=True`

    - **`test_score_confianca_e_categorizacao()`**

      - Mix de modificações com diferentes scores
      - **Esperado:** Categorização correta (vinculadas / revisao / nao_vinculadas)
      - Validar thresholds: 0.7 e 0.4

    - **`test_similaridade_threshold()`**

      - Testar com diferentes níveis de similaridade: 0.96, 0.94, 0.90
      - **Esperado:** ≥0.95 usa Caminho Feliz, <0.95 usa Caminho Real

    - **`test_normalizacao_consistente()`**
      - Validar que normalização é aplicada igualmente em todos os pontos
      - Testar com: tabs, múltiplos espaços, quebras de linha, unicode
      - **Esperado:** Resultados idênticos independente da formatação

3.  **`versiona-ai/tests/test_vinculacao_performance.py`** (novo arquivo)

    - **`test_performance_100_tags_200kb()`**

      - Simular documento com 100 tags e ~200KB de texto
      - Medir tempo de execução
      - **Meta:** < 5 segundos sem otimizações, < 2 segundos com índice n-gramas

    - **`test_performance_tags_aninhadas_profundas()`**
      - Tags com 5+ níveis de aninhamento
      - Validar que offset acumulado não degrada performance
      - **Meta:** Tempo linear O(N), não exponencial

4.  **Fixture de Teste Real** (adicionar aos testes):

    ```python
    @pytest.fixture
    def versao_real_99090886():
        """Fixture com dados reais da versão 99090886."""
        return {
            "versao_id": "99090886-7f43-45c9-bfe4-ec6eddd6cde0",
            "modelo_id": "7e392c2a-9ca7-441e-8d4a-ad1a611294fa",
            "arquivo_com_tags_id": "08c0a84c-baf0-4548-8883-fa4197da7e42",
            "total_modificacoes": 55,
            "meta_minima": 50  # 90%+
        }

    def test_vinculacao_versao_real(versao_real_99090886):
        """Teste de integração com versão real."""
        resultado = processar_versao(versao_real_99090886["versao_id"])

        vinculadas = resultado["vinculadas"]
        total = versao_real_99090886["total_modificacoes"]
        meta = versao_real_99090886["meta_minima"]

        assert len(vinculadas) >= meta, f"Esperado ≥{meta}, obteve {len(vinculadas)}"
        assert all(v["score"] >= 0.7 for v in vinculadas), "Todas devem ter score ≥ 0.7"
    ```

---

## 🧪 Como Testar a Solução

### 1. Executar Testes Unitários

```bash
cd /Users/sidarta/repositorios/docx-compare/versiona-ai
python3 tests/test_vinculacao_formatacao.py
```

**Esperado:** Todos os testes (antigos e novos) devem passar.

### 2. Processar Versão Real

O comando de teste permanece o mesmo, mas esperamos um resultado drasticamente melhor.

```bash
# ... (comandos para reiniciar servidor e processar versão) ...

# Verificar resultado
tail -500 /tmp/flask_server.log | grep "📋 Cláusula vinculada" | wc -l
```

**Meta:**

- ✅ Antes: 8/55 (14.5%)
- 🎯 **Meta: 50+/55 (90%+)**

---

## 📊 Critérios de Sucesso

### Mínimo Aceitável

- [ ] **≥ 90% de modificações vinculadas** em versões reais de teste (vinculadas + revisão manual)
- [ ] Logs claros indicando qual caminho ("Feliz" ou "Real") foi tomado para cada versão
- [ ] Sistema de score de confiança implementado com 3 níveis (alta/média/baixa)
- [ ] Tempo de processamento ≤ 5 segundos para documentos de até 200KB
- [ ] Todos os testes unitários passando (existentes + novos)
- [ ] Taxa de sucesso automático (sem revisão) ≥ 70% em versões reais

### Ideal

- [ ] **~100% de modificações válidas cobertas** (vinculação automática + revisão manual)
- [ ] Taxa de vinculação automática (score ≥ 0.7) ≥ 85%
- [ ] Tempo de processamento < 3 segundos com otimizações (índice n-gramas)
- [ ] Interface web para revisão manual das vinculações de média confiança
- [ ] Métricas detalhadas por versão:
  - Caminho usado (Feliz/Real)
  - Distribuição de scores
  - Taxa de vinculação por tipo de cláusula
- [ ] Documentação completa do algoritmo no README
- [ ] Logs estruturados (JSON) para análise posterior

### Métricas de Validação

**Validar com Múltiplas Versões:**

1. **Versão 99090886 (baseline):**

   - Antes: 8/55 (14.5%)
   - Meta: ≥50/55 (90%+)

2. **Versão com documentos idênticos (Caminho Feliz):**

   - Meta: 100% com score 1.0

3. **Versão com documentos divergentes (Caminho Real):**
   - Meta: ≥85% com score ≥0.7

**Regressão:**

- Nenhuma versão que funcionava antes pode piorar

---

## 🚀 Próximos Passos Sugeridos (Ordem de Implementação)

### Fase 1: Fundação (Estimativa: 4-6 horas)

1. **Criar estruturas de dados:**

   - Classes `TagMapeada` e `ResultadoVinculacao`
   - Função `normalizar_texto()` centralizada
   - ✅ **Validação:** Testes unitários simples para normalização

2. **Implementar função de similaridade:**

   - `_calcular_similaridade_textos()` usando `difflib.SequenceMatcher`
   - ✅ **Validação:** Testar com pares conhecidos (idênticos = 1.0, diferentes = <0.9)

3. **Criar testes básicos:**
   - `test_normalizacao_consistente()`
   - `test_similaridade_threshold()`
   - ✅ **Validação:** Todos os testes passando antes de prosseguir

### Fase 2: Caminho Feliz (Estimativa: 6-8 horas)

4. **Implementar `_mapear_tags_via_offset()`:**

   - Regex para encontrar todas as tags: `r'\{\{/?[^}]+\}\}'`
   - Loop acumulando offsets
   - Recalcular posições das tags
   - ✅ **Validação:** Testar com documento simples (3 tags, não aninhadas)

5. **Criar testes do Caminho Feliz:**

   - `test_caminho_feliz_offset_simples()`
   - `test_caminho_feliz_offset_tags_aninhadas()`
   - ✅ **Validação:** 100% de vinculação nos testes

6. **Integrar no algoritmo principal:**
   - Criar `_vincular_modificacoes_clausulas_unificado()` (versão inicial)
   - Implementar apenas branch do "Caminho Feliz"
   - ✅ **Validação:** Processar versão real com documentos idênticos

### Fase 3: Caminho Real (Estimativa: 8-12 horas)

7. **Implementar `_inferir_posicoes_via_conteudo_com_contexto()`:**

   - Extrair conteúdo + contexto (50 chars antes/depois)
   - Busca com contexto completo → parcial → conteúdo
   - Atribuir score baseado no método
   - ✅ **Validação:** `test_caminho_real_contexto_completo()`

8. **Lidar com ambiguidade:**

   - Implementar detecção de múltiplos candidatos
   - Usar contexto de vizinhança para desambiguar
   - ✅ **Validação:** `test_caminho_real_texto_ambiguo()`

9. **Integrar no algoritmo principal:**
   - Adicionar branch do "Caminho Real"
   - Escolha automática baseada em similaridade (threshold 0.95)
   - ✅ **Validação:** Processar versão 99090886 (meta: ≥50/55)

### Fase 4: Sistema de Score e Categorização (Estimativa: 4-6 horas)

10. **Implementar `_vincular_por_sobreposicao_com_score()`:**

    - Calcular score final: `tag.score × sobreposicao × fator_contexto`
    - Categorizar: alta (≥0.7), média (0.4-0.69), baixa (<0.4)
    - ✅ **Validação:** `test_score_confianca_e_categorizacao()`

11. **Adicionar logs detalhados:**

    - Log de estatísticas (vinculadas/revisão/não vinculadas)
    - Log de qual caminho foi usado
    - Log de scores por modificação
    - ✅ **Validação:** Verificar logs em `/tmp/flask_server.log`

12. **Implementar fila de revisão manual:**
    - Estrutura de dados para modificações pendentes
    - Endpoint API para buscar modificações em revisão (futuro)
    - ✅ **Validação:** Verificar que modificações com score 0.4-0.69 vão para fila

### Fase 5: Casos de Borda e Otimização (Estimativa: 6-8 horas)

13. **Modificações multi-cláusula:**

    - Detectar sobreposição ≥30% em múltiplas cláusulas
    - Vincular a array em vez de single
    - ✅ **Validação:** `test_modificacao_cruzando_fronteiras()`

14. **Otimização de performance (se necessário):**

    - Implementar `_construir_indice_ngramas()` se tempo > 5 segundos
    - Paralelização com `multiprocessing` se tempo > 10 segundos
    - ✅ **Validação:** `test_performance_100_tags_200kb()` (meta: <5s)

15. **Testes de integração completos:**
    - `test_vinculacao_versao_real()` com fixture de produção
    - Validar regressão: versões antigas não podem piorar
    - ✅ **Validação:** ≥90% de cobertura em múltiplas versões

### Fase 6: Documentação e Deploy (Estimativa: 2-4 horas)

16. **Documentar algoritmo:**

    - Atualizar README com explicação detalhada
    - Diagramas de fluxo (Caminho Feliz vs Real)
    - Exemplos de uso

17. **Deploy e validação:**
    - Reiniciar servidor com novo código
    - Processar 5-10 versões reais
    - Monitorar logs e taxas de sucesso
    - ✅ **Critério de aceite:** ≥90% de cobertura (vinculadas + revisão)

---

**Tempo Total Estimado:** 30-44 horas (~1 semana de trabalho)

**Prioridade de Implementação:**

1. 🔴 **Alta:** Fases 1-3 (Fundação + Caminhos)
2. 🟡 **Média:** Fase 4 (Score e categorização)
3. 🟢 **Baixa:** Fases 5-6 (Otimização + Documentação)

**Estratégia de Desenvolvimento:**

- ✅ **TDD:** Escrever testes ANTES de implementar cada função
- ✅ **Incremental:** Validar cada fase antes de prosseguir
- ✅ **Reversível:** Manter código antigo comentado até validação completa

---

## 📈 Estimativa de Taxa de Sucesso

Com a solução proposta, esperamos os seguintes resultados por cenário:

| Cenário                            | Descrição                                    | Taxa de Sucesso Automático | Taxa de Cobertura Total | Observações                                   |
| ---------------------------------- | -------------------------------------------- | -------------------------- | ----------------------- | --------------------------------------------- |
| **Caminho Feliz**                  | Documentos idênticos (similaridade ≥95%)     | **~100%** (score 1.0)      | **100%**                | Cálculo matemático preciso via offset         |
| **Caminho Real - Alta Confiança**  | Documentos diferentes mas com contexto único | **85-95%** (score 0.8-0.9) | **95-100%**             | Inferência com contexto completo funciona bem |
| **Caminho Real - Média Confiança** | Documentos com alguma ambiguidade            | **60-70%** (automático)    | **90-95%** (+ revisão)  | Alguns casos vão para revisão manual          |
| **Caminho Real - Divergente**      | Documentos muito diferentes                  | **50-60%**                 | **70-80%**              | Mais casos para revisão manual                |
| **Média Geral (Produção)**         | Mix de todos os cenários                     | **75-85%**                 | **90-98%**              | Depende da distribuição de casos              |

**Legenda:**

- **Taxa de Sucesso Automático:** Vinculações com score ≥ 0.7 (alta confiança)
- **Taxa de Cobertura Total:** Inclui revisão manual (score 0.4-0.69)

### Comparação com Situação Atual

| Métrica            | Antes (Atual) | Depois (Esperado) | Melhoria                 |
| ------------------ | ------------- | ----------------- | ------------------------ |
| Taxa de Vinculação | 14.5% (8/55)  | 75-85%            | **+500% a +600%**        |
| Taxa de Cobertura  | 14.5%         | 90-98%            | **+520% a +675%**        |
| Confiança          | Desconhecida  | Score 0.0-1.0     | **Sistema de qualidade** |
| Revisão Manual     | Inexistente   | Fila priorizada   | **Fallback robusto**     |

---

## 🔍 Considerações Técnicas Adicionais

### 1. Normalização Unicode

Importante para evitar problemas com acentos e caracteres especiais:

```python
import unicodedata

def normalizar_texto(texto):
    # Normalização NFC: garante forma canônica composta
    # "é" pode ser: U+00E9 (único) OU U+0065 + U+0301 (e + acento)
    # NFC garante sempre U+00E9
    texto = unicodedata.normalize('NFC', texto)

    # Remover variações de espaço (nbsp, thin space, etc)
    texto = re.sub(r'[\u00A0\u1680\u2000-\u200B\u202F\u205F\u3000]', ' ', texto)

    # Normalizar espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)

    return texto.strip()
```

### 2. Tratamento de Tabelas e Listas

Documentos DOCX podem ter estruturas especiais:

```python
def extrair_texto_preservando_estrutura(arquivo_docx):
    """
    Extrai texto mantendo ordem lógica de tabelas e listas.
    """
    doc = Document(arquivo_docx)
    texto_completo = []

    for elemento in doc.element.body:
        if elemento.tag.endswith('p'):  # Parágrafo
            texto_completo.append(elemento.text)
        elif elemento.tag.endswith('tbl'):  # Tabela
            # Processar tabela linha por linha
            for row in elemento.findall('.//w:tr', namespaces):
                row_text = ' | '.join(cell.text for cell in row.findall('.//w:tc', namespaces))
                texto_completo.append(row_text)

    return '\n'.join(texto_completo)
```

### 3. Cache de Resultados

Para evitar reprocessamento desnecessário:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def _calcular_similaridade_cached(texto1_hash, texto2_hash, texto1, texto2):
    """Cache baseado em hash dos textos."""
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()

def calcular_similaridade(texto1, texto2):
    hash1 = hashlib.md5(texto1.encode()).hexdigest()
    hash2 = hashlib.md5(texto2.encode()).hexdigest()
    return _calcular_similaridade_cached(hash1, hash2, texto1, texto2)
```

### 4. Logging Estruturado para Análise

```python
import json
import logging

def log_resultado_vinculacao(resultado: ResultadoVinculacao, versao_id: str, caminho: str):
    """Log estruturado em JSON para análise posterior."""
    log_data = {
        "versao_id": versao_id,
        "timestamp": datetime.now().isoformat(),
        "caminho_usado": caminho,
        "metricas": {
            "total_modificacoes": len(resultado.vinculadas) + len(resultado.nao_vinculadas) + len(resultado.revisao_manual),
            "vinculadas": len(resultado.vinculadas),
            "revisao_manual": len(resultado.revisao_manual),
            "nao_vinculadas": len(resultado.nao_vinculadas),
            "taxa_sucesso": resultado.taxa_sucesso(),
            "taxa_cobertura": resultado.taxa_cobertura()
        },
        "distribuicao_scores": {
            "alta_confianca": sum(1 for _, _, s in resultado.vinculadas if s >= 0.8),
            "media_confianca": sum(1 for _, _, s in resultado.vinculadas if 0.7 <= s < 0.8),
            "baixa_confianca": len(resultado.revisao_manual)
        }
    }

    logging.info(f"RESULTADO_VINCULACAO: {json.dumps(log_data)}")
```

### 5. Detecção de Anomalias

Alertar quando resultados parecem incorretos:

```python
def validar_resultado(resultado: ResultadoVinculacao, tags_totais: int):
    """Validação de sanidade dos resultados."""
    warnings = []

    # Anomalia 1: Taxa de sucesso muito baixa
    if resultado.taxa_sucesso() < 0.30:
        warnings.append(f"⚠️  Taxa de sucesso muito baixa: {resultado.taxa_sucesso():.1%}")

    # Anomalia 2: Muitas modificações sem vinculação
    if len(resultado.nao_vinculadas) > len(resultado.vinculadas):
        warnings.append(f"⚠️  Mais não vinculadas ({len(resultado.nao_vinculadas)}) do que vinculadas ({len(resultado.vinculadas)})")

    # Anomalia 3: Nenhuma vinculação com alta confiança
    alta_confianca = sum(1 for _, _, s in resultado.vinculadas if s >= 0.9)
    if alta_confianca == 0 and len(resultado.vinculadas) > 10:
        warnings.append(f"⚠️  Nenhuma vinculação com alta confiança (score ≥ 0.9)")

    if warnings:
        for w in warnings:
            print(w)
        print("🔍 Considere revisar a qualidade dos dados de entrada.")

    return len(warnings) == 0
```

---

## 🏷️ Tags

`#vinculação` `#cláusulas` `#tags` `#modificações` `#solução-refinada` `#high-priority` `#coordenadas` `#offset` `#inferencia` `#algoritmo-unificado` `#score-confianca` `#revisao-manual` `#performance`

---

## 📚 Referências e Recursos

### Documentação Relacionada

- **Task 001:** Agrupamento posicional de modificações (✅ completa)
- **Task 002:** Integração do processamento de tags (✅ completa)
- **Testes Unitários:** `/versiona-ai/tests/test_vinculacao_formatacao.py`
- **Servidor Flask:** `/versiona-ai/directus_server.py` (linhas 240-920)

### APIs e Bibliotecas Utilizadas

- **Directus API:** https://contract.devix.co

  - Token: `S1okNXYabq9TL1gVj0TxiNEdu0md_F3d` (permissões limitadas)
  - Documentação: https://directus.io/docs/guides/ai/mcp

- **Python difflib:** Para cálculo de similaridade

  - `difflib.SequenceMatcher(None, texto1, texto2).ratio()`
  - Documentação: https://docs.python.org/3/library/difflib.html

- **Python re (regex):** Para processamento de tags
  - Pattern: `r'\{\{/?[^}]+\}\}'` (tags aninhadas)
  - Documentação: https://docs.python.org/3/library/re.html

### Algoritmos e Conceitos

1. **Longest Common Subsequence (LCS):**

   - Usado para inferir posições quando documentos divergem
   - Complexidade: O(n×m) no pior caso
   - Otimização: Índice de n-gramas reduz para O(n) amortizado

2. **Offset Acumulado:**

   - Técnica para mapear coordenadas entre documentos com inserções
   - Similar ao usado em diffs (unified diff format)
   - Complexidade: O(N log N) por ordenação

3. **Score de Confiança (Confidence Score):**
   - Técnica comum em ML/NLP para quantificar incerteza
   - Permite decisões baseadas em threshold
   - Implementação: produto ponderado de múltiplos fatores

### Ferramentas de Desenvolvimento

- **VS Code:** Editor principal
- **Python 3.13:** Runtime
- **pytest:** Framework de testes
- **uv:** Gerenciador de dependências
- **Flask:** Framework web (servidor API)

### Dados de Teste

**Versão Real Principal:** `99090886-7f43-45c9-bfe4-ec6eddd6cde0`

- Contrato: `77b8555b-e40d-4ece-8c8a-88367b36a625`
- Modelo: `7e392c2a-9ca7-441e-8d4a-ad1a611294fa` (Minuta de empreitada)
- Arquivo COM Tags: `08c0a84c-baf0-4548-8883-fa4197da7e42`
- Total modificações: 55
- Resultado atual: 8/55 (14.5%)
- Meta: ≥50/55 (90%+)

### Logs e Monitoramento

- **Servidor:** `localhost:8001`
- **Logs:** `/tmp/flask_server.log`
- **Health Check:** `curl http://localhost:8001/health`
- **Processar Versão:** `curl -X POST http://localhost:8001/api/process -H "Content-Type: application/json" -d '{"versao_id": "..."}'`

### Comandos Úteis

```bash
# Reiniciar servidor
cd /Users/sidarta/repositorios/docx-compare
lsof -ti:8001 | xargs kill -9 2>/dev/null
cd versiona-ai
nohup python3 directus_server.py > /tmp/flask_server.log 2>&1 &

# Verificar taxa de vinculação
tail -500 /tmp/flask_server.log | grep "📋 Cláusula vinculada" | wc -l

# Executar testes
cd versiona-ai
python3 tests/test_vinculacao_formatacao.py

# Executar testes com pytest
uv run pytest tests/ -v

# Verificar erros
tail -100 /tmp/flask_server.log | grep -E "(ERROR|Exception)"
```

---

**Última Atualização:** 2025-10-11 21:30
**Versão do Documento:** 2.0 (Refinado com otimizações e casos de borda)
**Próxima Revisão:** Após implementação das Fases 1-3 (Fundação + Caminhos)

---

## ✅ Checklist de Implementação

### Fase 1: Fundação ⬜ (0/3)

- [ ] Criar estruturas de dados (TagMapeada, ResultadoVinculacao)
- [ ] Implementar função centralizada de normalização
- [ ] Implementar função de cálculo de similaridade

### Fase 2: Caminho Feliz ⬜ (0/3)

- [ ] Implementar `_mapear_tags_via_offset()`
- [ ] Criar testes para Caminho Feliz (simples + aninhado)
- [ ] Integrar branch "Caminho Feliz" no algoritmo principal

### Fase 3: Caminho Real ⬜ (0/3)

- [ ] Implementar `_inferir_posicoes_via_conteudo_com_contexto()`
- [ ] Criar testes para Caminho Real (contexto + ambiguidade)
- [ ] Integrar branch "Caminho Real" no algoritmo principal

### Fase 4: Score e Categorização ⬜ (0/3)

- [ ] Implementar `_vincular_por_sobreposicao_com_score()`
- [ ] Adicionar logs detalhados e estruturados
- [ ] Implementar fila de revisão manual

### Fase 5: Robustez ⬜ (0/3)

- [ ] Implementar detecção de modificações multi-cláusula
- [ ] Otimizar performance (índice n-gramas se necessário)
- [ ] Criar testes de integração com dados reais

### Fase 6: Finalização ⬜ (0/2)

- [ ] Documentar algoritmo no README
- [ ] Deploy e validação em produção (≥90% cobertura)

---

**Progresso Geral:** 0/17 tarefas (0%)

**Meta de Sucesso:**

- ✅ Antes: 8/55 (14.5%)
- 🎯 **Meta: ≥50/55 (90%+)**

---

## 📝 Notas de Implementação

_Esta seção deve ser preenchida durante a implementação com observações importantes, decisões técnicas e aprendizados._

### Decisões Técnicas

- [ ] Threshold de similaridade definido: **\_**%
- [ ] Tamanho do contexto de vizinhança: **\_** caracteres
- [ ] Scores de confiança calibrados: alta (\_**\_), média (\_\_**), baixa (\_\_\_\_)
- [ ] Performance aceitável alcançada: **\_** segundos para **\_** KB

### Problemas Encontrados

_Documentar problemas inesperados e suas soluções aqui._

### Melhorias Futuras

_Ideias para otimização ou features adicionais identificadas durante a implementação._
