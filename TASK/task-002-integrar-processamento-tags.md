# Task 002: Integrar Processamento de Tags ao Fluxo Versiona-AI

## 🎯 Objetivo

Integrar a rotina de processamento de modelo de contrato (que cria tags em `modelo_contrato_tag`) ao fluxo atual de processamento de versões no `versiona-ai`.

## 📋 Problema Identificado

1. ✅ O código de vinculação de modificações a cláusulas **existe e está correto** em `directus_server.py`
2. ❌ O código **nunca é executado** porque não existem tags em `modelo_contrato_tag`
3. ❌ A rotina que **criava as tags** foi implementada no projeto antigo mas **não migrada para versiona-ai**

## 🔍 Código Histórico Encontrado

### Commit: `8879b59` - feat: implementa processador de modelo de contrato com extração de tags

**Arquivo**: `processador_modelo_contrato.py` (972 linhas)

**Fluxo de Processamento**:

```python
def processar_modelo_contrato(modelo_data, dry_run=False):
    """
    1. Baixa arquivo_original e arquivo_com_tags do Directus
    2. Converte ambos para HTML usando pandoc
    3. Converte HTML para texto limpo
    4. Analisa diferenças entre os documentos
    5. Extrai tags das diferenças usando regex patterns
    6. Salva tags na coleção modelo_contrato_tag
    """

    # 1. Download de arquivos
    original_path = download_file_from_directus(arquivo_original_id)
    tagged_path = download_file_from_directus(arquivo_com_tags_id)

    # 2-3. Conversão para texto
    original_text = html_to_text(pandoc_convert(original_path))
    tagged_text = html_to_text(pandoc_convert(tagged_path))

    # 4. Análise de diferenças
    modifications = analyze_differences_detailed(original_text, tagged_text)

    # 5. Extração de tags
    tags_encontradas = extract_tags_from_differences(modifications)

    # 6. Salvamento no Directus
    salvar_tags_modelo_contrato(modelo_id, tags_encontradas, dry_run)
```

### Função de Extração de Tags

```python
def extract_tags_from_differences(modifications: List[Dict]) -> List[Dict]:
    """
    Extrai tags das modificações encontradas entre os documentos.

    Padrões suportados:
    - {{tag}} ou {{ tag }} - tags textuais
    - {{1}}, {{1.1}}, {{1.2.3}} - tags numéricas
    - {{tag /}} ou {{ tag /}} - tags auto-fechadas
    - {{TAG-nome}}...{{/TAG-nome}} - tags com prefixo
    """

    tag_patterns = [
        r'(?<!\{)\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})',      # {{tag}}
        r'(?<!\{)\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*/\s*\}\}(?!\})',  # {{tag /}}
        r'(?<!\{)\{\{\s*/\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}(?!\})',  # {{/tag}}
        r'(?<!\{)\{\{\s*(\d+(?:\.\d+)*)\s*\}\}(?!\})',               # {{1.2.3}}
        r'(?<!\{)\{\{\s*(\d+(?:\.\d+)*)\s*/\s*\}\}(?!\})',           # {{1 /}}
        r'(?<!\{)\{\{\s*/\s*(\d+(?:\.\d+)*)\s*\}\}(?!\})',           # {{/1}}
    ]

    tags_encontradas = {}

    for modification in modifications:
        for fonte, texto in [("original", modification.get("conteudo")),
                             ("alteracao", modification.get("alteracao"))]:
            for pattern in tag_patterns:
                matches = re.finditer(pattern, texto, re.IGNORECASE)
                for match in matches:
                    tag_nome = match.group(1).strip()
                    pos_inicio = match.start()
                    pos_fim = match.end()

                    tags_encontradas[tag_nome] = {
                        'nome': tag_nome,
                        'texto_completo': match.group(0),
                        'posicao_inicio': pos_inicio,
                        'posicao_fim': pos_fim,
                        'contexto': texto[max(0, pos_inicio-100):pos_fim+100],
                        'caminho_tag_inicio': f"modificacao_{idx}_linha_{linha}_pos_{pos_inicio}",
                        'caminho_tag_fim': f"modificacao_{idx}_linha_{linha}_pos_{pos_fim}"
                    }

    return list(tags_encontradas.values())
```

### Função de Salvamento

```python
def salvar_tags_modelo_contrato(modelo_id: str, tags_encontradas: List[Dict], dry_run=False):
    """Salva as tags encontradas na coleção modelo_contrato_tag"""

    for tag_info in sorted(tags_encontradas, key=lambda x: x['nome']):
        tag_data = {
            "modelo_contrato": modelo_id,
            "tag_nome": tag_info['nome'],
            "caminho_tag_inicio": tag_info.get('caminho_tag_inicio', ''),
            "caminho_tag_fim": tag_info.get('caminho_tag_fim', ''),
            "conteudo": tag_info.get('conteudo', ''),  # ✅ Campo importante!
            "contexto": tag_info.get('contexto', '')[:500],
            "linha_aproximada": tag_info.get('linha_aproximada', 0),
            "posicao_inicio": tag_info.get('posicao_inicio', 0),
            "posicao_fim": tag_info.get('posicao_fim', 0),
            "status": "published"
        }

        response = requests.post(
            f"{DIRECTUS_BASE_URL}/items/modelo_contrato_tag",
            headers=DIRECTUS_HEADERS,
            json=tag_data,
            timeout=request_timeout
        )
```

## 🏗️ Arquitetura Atual vs Necessária

### Fluxo Atual (Incompleto)

```
1. Usuario cria modelo_contrato no Directus
2. Usuario upload arquivo_original e arquivo_com_tags
3. [FALTA] Processamento automático para criar tags
4. Usuario cria contrato vinculado ao modelo
5. Usuario cria versão do contrato
6. directus_server.py processa versão:
   ✅ Extrai modificações
   ✅ Busca tags do modelo (retorna vazio!)
   ❌ Vinculação não acontece (sem tags)
```

### Fluxo Completo (Necessário)

```
1. Usuario cria modelo_contrato no Directus
2. Usuario upload arquivo_original e arquivo_com_tags
3. [NOVO] Processador de tags detecta modelo com status "processar"
4. [NOVO] Processador extrai tags e salva em modelo_contrato_tag
5. [NOVO] Modelo status atualizado para "concluido"
6. Usuario cria contrato vinculado ao modelo
7. Usuario cria versão do contrato
8. directus_server.py processa versão:
   ✅ Extrai modificações
   ✅ Busca tags do modelo (encontra tags!)
   ✅ Vinculação acontece corretamente
```

## 📝 Tarefas de Implementação

### Fase 1: Portar Código para versiona-ai

- [ ] **Criar arquivo**: `versiona-ai/processador_tags_modelo.py`
  - [ ] Portar `extract_tags_from_differences()` do commit histórico
  - [ ] Portar `salvar_tags_modelo_contrato()` do commit histórico
  - [ ] Portar funções auxiliares necessárias
  - [ ] Adaptar para usar estrutura do versiona-ai

### Fase 2: Integração com DirectusAPI

- [ ] **Atualizar**: `versiona-ai/directus_server.py`
  - [ ] Adicionar método `process_modelo_contrato(modelo_id)`
  - [ ] Adicionar endpoint `/api/process-modelo/<modelo_id>`
  - [ ] Integrar com processador de tags

### Fase 3: Endpoint para Processamento Manual

- [ ] **Criar endpoint**: `POST /api/process-modelo`
  - [ ] Aceitar `modelo_id` no body
  - [ ] Buscar dados do modelo no Directus
  - [ ] Baixar arquivos (original e com tags)
  - [ ] Processar e extrair tags
  - [ ] Salvar tags no Directus
  - [ ] Atualizar status do modelo

### Fase 4: Processamento Automático (Opcional)

- [ ] **Criar serviço**: Background worker para processar modelos
  - [ ] Buscar modelos com status "processar"
  - [ ] Processar automaticamente
  - [ ] Atualizar status

### Fase 5: Testes e Validação

- [ ] **Testar fluxo completo**:
  1. Criar modelo de contrato no Directus
  2. Upload de arquivos
  3. Processar modelo (via endpoint)
  4. Verificar tags criadas em `modelo_contrato_tag`
  5. Criar contrato vinculado
  6. Criar versão
  7. Processar versão
  8. Verificar vinculação de modificações a cláusulas

## 🔧 Implementação Sugerida

### Arquivo: `versiona-ai/processador_tags_modelo.py`

```python
"""
Processador de Tags para Modelos de Contrato
Extrai tags dos arquivos tagged e salva no Directus
"""

import re
import requests
from typing import List, Dict

class ProcessadorTagsModelo:
    def __init__(self, directus_base_url: str, directus_token: str):
        self.base_url = directus_base_url
        self.headers = {
            "Authorization": f"Bearer {directus_token}",
            "Content-Type": "application/json"
        }

    def processar_modelo(self, modelo_id: str) -> Dict:
        """
        Processa um modelo de contrato e extrai suas tags

        Args:
            modelo_id: ID do modelo de contrato

        Returns:
            dict com resultado do processamento
        """
        # 1. Buscar dados do modelo
        modelo_data = self._buscar_modelo(modelo_id)

        # 2. Baixar arquivos
        arquivo_original = self._baixar_arquivo(modelo_data['arquivo_original'])
        arquivo_tagged = self._baixar_arquivo(modelo_data['arquivo_com_tags'])

        # 3. Converter para texto
        texto_original = self._converter_docx_para_texto(arquivo_original)
        texto_tagged = self._converter_docx_para_texto(arquivo_tagged)

        # 4. Analisar diferenças
        modificacoes = self._analisar_diferencas(texto_original, texto_tagged)

        # 5. Extrair tags
        tags_encontradas = self._extrair_tags(modificacoes, texto_tagged)

        # 6. Salvar tags
        tags_criadas = self._salvar_tags(modelo_id, tags_encontradas)

        # 7. Atualizar status do modelo
        self._atualizar_status_modelo(modelo_id, "concluido", len(tags_criadas))

        return {
            "modelo_id": modelo_id,
            "tags_encontradas": len(tags_encontradas),
            "tags_criadas": len(tags_criadas),
            "status": "sucesso"
        }

    def _extrair_tags(self, modificacoes: List[Dict], texto_completo: str) -> List[Dict]:
        """Extrai tags das modificações"""
        # Implementar lógica de extração de tags
        pass

    def _salvar_tags(self, modelo_id: str, tags: List[Dict]) -> List[str]:
        """Salva tags no Directus"""
        # Implementar salvamento
        pass
```

### Integração no directus_server.py

```python
@app.route("/api/process-modelo", methods=["POST"])
def process_modelo():
    """Processa um modelo de contrato e extrai suas tags"""
    try:
        data = request.get_json()
        modelo_id = data.get("modelo_id")

        if not modelo_id:
            return jsonify({"error": "modelo_id é obrigatório"}), 400

        # Criar processador
        processador = ProcessadorTagsModelo(
            directus_base_url=DIRECTUS_BASE_URL,
            directus_token=DIRECTUS_TOKEN
        )

        # Processar modelo
        resultado = processador.processar_modelo(modelo_id)

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## 🧪 Como Testar

### 1. Processar Modelo Manualmente

```bash
curl -X POST https://ignai-contract-ia.paas.node10.de.vix.br/api/process-modelo \
  -H "Content-Type: application/json" \
  -d '{"modelo_id": "7e392c2a-9ca7-441e-8d4a-ad1a611294fa"}'
```

### 2. Verificar Tags Criadas

```bash
curl "https://contract.devix.co/items/modelo_contrato_tag?filter[modelo_contrato][_eq]=7e392c2a-9ca7-441e-8d4a-ad1a611294fa" \
  -H "Authorization: Bearer S1okNXYabq9TL1gVj0TxiNEdu0md_F3d"
```

### 3. Processar Versão (deve vincular agora)

```bash
curl -X POST https://ignai-contract-ia.paas.node10.de.vix.br/api/process \
  -H "Content-Type: application/json" \
  -d '{"versao_id": "966bae5c-b1a0-462e-80f1-2386670e6b95", "mock": false}'
```

## 📊 Resultado Esperado

Após implementação:

1. ✅ Endpoint `/api/process-modelo` disponível
2. ✅ Processamento extrai tags do arquivo tagged
3. ✅ Tags salvas em `modelo_contrato_tag` com:
   - `tag_nome`
   - `conteudo` (texto entre tags)
   - `caminho_tag_inicio` / `caminho_tag_fim`
   - `posicao_inicio` / `posicao_fim`
   - `clausulas` (vinculação manual posterior)
4. ✅ Processamento de versão vincula modificações a cláusulas
5. ✅ Campo `clausula` preenchido nas modificações

## 📚 Referências

- Commit histórico: `8879b59`
- Arquivo original: `processador_modelo_contrato.py` (972 linhas)
- Documentação: `IMPLEMENTACAO_CONTEUDO_TAGS.md`
- Schema Directus: `config/directus-schema.json`

## ⚠️ Importante

- O processador histórico usa **pandoc** para conversão DOCX → HTML → Texto
- O versiona-ai já tem `docx_utils.py` com função `convert_docx_to_text()`
- **Reutilizar** a conversão existente em vez de instalar pandoc
- **Adaptar** padrões de regex para o formato atual de tags
