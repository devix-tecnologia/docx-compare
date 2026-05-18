# Prompt para Geração de Blueprint Visual - Sistema Versiona AI

## Contexto

Crie um **diagrama blueprint técnico tradicional** (estilo engenharia/arquitetura) ilustrando o sistema **Versiona AI** - um sistema de comparação e versionamento inteligente de contratos jurídicos em formato DOCX.

---

## Elementos do Sistema a Serem Representados

### 1. MODELO DE CONTRATO (Template Base)

**Representar como**: Documento blueprint com duas camadas

**Elementos**:

- **Arquivo Original** (sem tags)
  - Documento DOCX puro
  - Conteúdo: texto corrido do contrato template

- **Arquivo com Tags** (taggeado)
  - Mesmo documento com delimitadores especiais
  - Tags no formato: `{{TAG-nome_unico}}...{{/TAG-nome_unico}}`
  - Exemplo visual de tags: `{{TAG-responsavel}}`, `{{TAG-prazo}}`, `{{TAG-valor}}`

**Estados do Modelo**:

- draft → processar → em_processamento → concluido → publicado

---

### 2. TAGS (modelo_contrato_tag)

**Representar como**: Marcadores/âncoras estruturais no documento

**Propriedades**:

- `tag_nome`: identificador único (ex: "responsavel", "prazo")
- `caminho_tag_inicio`: coordenada estrutural inicial no documento
- `caminho_tag_fim`: coordenada estrutural final no documento
- `conteudo`: texto extraído entre as tags

**Visual sugerido**:

- Tags como "clips" ou "marcadores" coloridos delimitando blocos de texto
- Mostrar coordenadas/posições numéricas (ex: posição 1234 a 1567)

---

### 3. CLÁUSULAS

**Representar como**: Blocos lógicos vinculados às tags

**Propriedades**:

- `numero`: identificação hierárquica (ex: "1.1", "2.3", "4.5.2")
- `nome`: título da cláusula (ex: "Identificação das Partes")
- `conteudo`: texto completo da cláusula
- `objetivo`: propósito/finalidade da cláusula
- `tag`: referência à tag que delimita este bloco

**Visual sugerido**:

- Caixas organizadas hierarquicamente
- Linha conectando cada cláusula à sua tag correspondente
- Numeração visível

---

### 4. REFERÊNCIAS (Orientações/Ações)

**Representar como**: Anotações/notas técnicas vinculadas às cláusulas

**Propriedades**:

- `orientacao_retorno`: tipo de ação necessária
- `descricao`: instruções detalhadas para o analista

**Visual sugerido**:

- Pequenos ícones ou símbolos (⚠️, ℹ️, ✓) ao lado das cláusulas
- Balões de texto com instruções
- Diferentes cores por tipo de orientação

---

### 5. VERSÕES (Documentos Modificados)

**Representar como**: Linha do tempo de versões do contrato

**Elementos**:

- **Versão Base** (primeira): comparada com Template
- **Versões Subsequentes**: comparadas com versão anterior

**Propriedades**:

- `status`: a_processar → processando → concluido
- `arquivo_preenchido`: arquivo DOCX da versão
- `versao_anterior`: referência à versão prévia

**Visual sugerido**:

- Timeline horizontal com marcos/milestones
- Setas indicando progressão temporal
- Template → V1.0 → V1.1 → V2.0

---

### 6. MODIFICAÇÕES (Mudanças Detectadas)

**Representar como**: Marcações/anotações sobre diferenças

**Tipos** (usar cores distintas):

- 🟢 **INSERCAO**: texto adicionado (verde)
- 🔴 **REMOCAO**: texto removido (vermelho)
- 🟡 **ALTERACAO**: texto modificado (amarelo/laranja)

**Propriedades**:

- `conteudo_original`: texto antes da mudança
- `conteudo_modificado`: texto após a mudança
- `posicao`: coordenada no documento
- `similaridade`: percentual de semelhança (0-100%)
- `clausula_vinculada`: referência à cláusula afetada

**Visual sugerido**:

- Setas ou destacamentos no texto
- Código de cores por tipo
- Linhas conectando modificação → cláusula → referências

---

### 7. PROCESSO DE DETECÇÃO DE MUDANÇAS (Pipeline)

**Representar como**: Fluxo de processamento técnico (flowchart blueprint)

**Etapas Sequenciais**:

1. **Download dos Arquivos DOCX**
   - Versão Nova (arquivo_preenchido.docx)
   - Versão Anterior OU Template (comparação.docx)

2. **Conversão para Pandoc AST**
   - Transformação DOCX → Abstract Syntax Tree (JSON)
   - Representação estruturada hierárquica do documento

3. **Comparação Estrutural AST vs AST**
   - Análise nó-a-nó da árvore sintática
   - Detecção de diferenças estruturais

4. **Extração de Modificações**
   - Identificação de INSERCAO, REMOCAO, ALTERACAO
   - Cálculo de posições e similaridade

5. **Vinculação com Cláusulas (via Tags)**
   - Matching de posições: modificação.posicao ∈ [tag.inicio, tag.fim]
   - Fuzzy matching de conteúdo textual (threshold 80%)
   - Associação modificação → tag → cláusula

6. **Agrupamento em Blocos**
   - Modificações próximas (mesma região) agrupadas
   - Facilita visualização e análise

7. **Persistência no Directus**
   - Salvar modificações vinculadas
   - Criar registros modificacao_referencia

8. **Geração de Relatório HTML**
   - Diff visual colorido
   - Destaque de modificações por tipo
   - Links para cláusulas e referências

**Visual sugerido**:

- Diagrama de fluxo com caixas retangulares numeradas (1 a 8)
- Setas indicando sequência
- Ícones representando cada tipo de operação
- Destaque para etapa 5 (vinculação) como ponto crítico

---

## Relacionamentos Importantes a Destacar

### Hierarquia Principal:

```
MODELO_CONTRATO
  ↓ possui
TAGS (modelo_contrato_tag)
  ↓ delimita
BLOCOS DE TEXTO
  ↓ associados a
CLÁUSULAS
  ↓ possuem
REFERÊNCIAS (orientações)
```

### Fluxo de Versionamento:

```
VERSÃO_NOVA.docx + VERSÃO_ANTERIOR.docx
  ↓ processamento
MODIFICAÇÕES detectadas
  ↓ vinculação via tags
CLÁUSULAS afetadas
  ↓ acionam
REFERÊNCIAS relevantes
  ↓ exibição para
ANALISTA/USUÁRIO
```

### Vinculação por Posição:

```
MODIFICAÇÃO (pos: 1234-1567)
  ↓ overlap detectado
TAG (pos: 1000-2000)
  ↓ referencia
CLÁUSULA "1.1 - Partes"
  ↓ ativa
REFERÊNCIA "Verificar identidade das partes"
```

---

## Estilo Visual Solicitado

- **Estilo**: Blueprint técnico tradicional (fundo azul escuro, linhas brancas)
- **Elementos**: Precisos, técnicos, com medidas e coordenadas
- **Tipografia**: Fonte mono-espaçada para dados técnicos
- **Cores**: Azul e branco predominantes, com toques de verde/vermelho/amarelo para modificações
- **Anotações**: Notas explicativas estilo "callouts" de engenharia
- **Escala**: Indicar relações de tamanho/volume (ex: "294 tags", "55 modificações")

---

## Detalhes Técnicos a Incluir

- **Formato de arquivos**: DOCX (Office Open XML)
- **Parser utilizado**: Pandoc (conversão para AST JSON)
- **Algoritmo de matching**: Fuzzy matching (RapidFuzz) com threshold 80%
- **Normalização**: Case-insensitive, remoção de espaços extras
- **Métricas**:
  - Similaridade: 0-100%
  - Posições: coordenadas numéricas (caracteres)
  - Taxa de vinculação: X/Y modificações vinculadas

---

## Casos de Uso a Ilustrar (Exemplos Reais)

1. **Tag de Identificação**:
   - Tag: `{{TAG-responsavel}}`
   - Conteúdo original: "Nome: João Silva"
   - Modificação: ALTERACAO → "Nome: Maria Santos"
   - Cláusula: "1.1 - Identificação do Responsável"
   - Referência: "⚠️ Verificar documentação da nova pessoa responsável"

2. **Tag de Multa**:
   - Tag: `{{TAG-penalidades}}`
   - Conteúdo original: vazio
   - Modificação: INSERCAO → "a) Multa de 2% sobre o valor em atraso"
   - Cláusula: "4.2 - Penalidades"
   - Posição: 69570-69637
   - Problema: Tag SEM posição definida → vinculação falha

3. **Múltiplas Modificações Agrupadas**:
   - Bloco 1: 3 modificações na região 5000-6000
   - Todas vinculadas à Cláusula "2.1 - Prazo de Vigência"
   - Acionam 2 referências diferentes

---

## Elementos Obrigatórios no Diagrama

✅ **Título Principal**: "Versiona AI - Sistema de Versionamento Inteligente de Contratos"

✅ **Legenda**:

- Cores das modificações (verde, vermelho, amarelo)
- Símbolos de status (processando, concluído, erro)
- Tipos de conexões (vinculação, herança, fluxo)

✅ **Escala/Métricas**:

- Exemplo: "Template com 294 tags"
- Exemplo: "55 modificações detectadas"
- Exemplo: "Taxa de vinculação: 48/55 (87%)"

✅ **Anotações Técnicas**:

- "AST = Abstract Syntax Tree (JSON)"
- "Threshold fuzzy matching: 80%"
- "Vinculação por overlap de posições: mod.pos ∈ [tag.inicio, tag.fim]"

✅ **Problemas Comuns** (destacar em vermelho):

- "❌ Tags sem posições definidas → vinculação falha"
- "⚠️ Modificações curtas vs cláusulas longas → baixa similaridade"

---

## Objetivo Final

O blueprint deve permitir que um desenvolvedor ou arquiteto de sistemas compreenda visualmente:

1. Como os contratos são estruturados com tags
2. Como as versões são comparadas (processo técnico)
3. Como as modificações são detectadas e categorizadas
4. Como funciona a vinculação modificações → cláusulas → referências
5. Qual o fluxo completo desde upload até visualização
6. Quais os pontos críticos onde a vinculação pode falhar

**Público-alvo**: Desenvolvedores técnicos, arquitetos de sistemas, analistas de produto

**Uso**: Documentação técnica, apresentações, onboarding de equipe
