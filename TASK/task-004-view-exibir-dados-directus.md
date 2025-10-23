# Task 004: Alterar /view para exibir dados do Directus

## Objetivo

Modificar o endpoint `/view` (visualizador de diferenças) para buscar e exibir os dados processados que foram armazenados no Directus durante o processamento da versão, ao invés de reprocessar ou usar dados temporários.

## Contexto

Atualmente, o endpoint `/view` pode estar:

- Reprocessando a versão toda vez que é acessado
- Ou usando dados temporários/mock
- Não aproveitando os dados já persistidos no Directus (modificações, vinculações, métricas)

Com o processamento agora persistindo todos os dados no Directus (task-003), precisamos que a visualização consuma esses dados já processados.

## Requisitos Funcionais

### 1. Buscar Dados do Directus em Uma Única Requisição

O endpoint `/view/{versao_id}` deve buscar **todos os dados necessários em uma única requisição** ao Directus, utilizando os relacionamentos da versão:

```
GET /items/versao/{versao_id}?fields=*,modificacoes.*,modificacoes.clausula.*,contrato.*,contrato.modelo_contrato.*
```

Esta única requisição retorna:

- **Versão**: dados principais (id, status, data_processamento, etc.)
- **Modificações**: todas as modificações da versão (categoria, conteúdo, alteração, posições) via campo `modificacoes`
- **Cláusulas**: vinculadas a cada modificação (via `modificacoes.clausula.*`)
- **Contrato**: informações do contrato da versão
- **Modelo do Contrato**: estrutura do modelo vinculado ao contrato

**Vantagens:**

- ✅ Performance: 1 request ao invés de 3+ requests
- ✅ Atomicidade: dados consistentes em um único snapshot
- ✅ Menos latência de rede
- ✅ Transações implícitas no Directus

### 2. Estrutura de Dados

Cada modificação retornada deve conter:

- `id`: UUID da modificação
- `categoria`: tipo (modificacao, inclusao, remocao, etc.)
- `conteudo`: texto original (sempre preenchido)
- `alteracao`: texto modificado (quando encontrado)
- `clausula`: FK para cláusula vinculada (quando encontrada)
- `caminho_inicio`, `caminho_fim`: coordenadas no documento
- `posicao_inicio`, `posicao_fim`: offsets reais
- `metodo_vinculacao`, `score_vinculacao`, `status_vinculacao`: **OPCIONAIS** (serão adicionados na task-005)

### 3. Formatação para Visualização

Transformar os dados do Directus no formato esperado pelo frontend:

```json
{
  "versao_id": "...",
  "status": "concluido",
  "modificacoes": [
    {
      "id": "...",
      "tipo": "ALTERACAO",
      "conteudo": {
        "original": "texto original",
        "novo": "texto modificado"
      },
      "posicao": {
        "inicio": 1234,
        "fim": 1456
      },
      "clausula": {
        "id": "...",
        "numero": "5.1",
        "nome": "Prazo de Vigência"
      },
      "vinculacao": {
        "metodo": "conteudo",
        "score": 0.95,
        "status": "automatico"
      }
    }
  ],
  "metricas": {
    "total_modificacoes": 792,
    "vinculadas": 271,
    "nao_vinculadas": 521,
    "taxa_vinculacao": 34.2
  }
}
```

### 4. Fallback

Se a versão não foi processada ainda (status != "concluido"):

- Retornar erro 404 ou 202 (Accepted)
- Ou disparar processamento assíncrono
- Informar que dados ainda não estão disponíveis

## Requisitos Técnicos

### Endpoint Atual

```python
@app.route("/view/<versao_id>")
def view_version(versao_id):
    # Código atual a ser modificado
```

### Nova Implementação (Busca Única)

```python
@app.route("/view/<versao_id>")
def view_version(versao_id):
    """
    Visualiza diferenças de uma versão usando dados do Directus.
    Busca todos os dados em uma única requisição para máxima performance.
    """
    try:
        directus = DirectusAPI()

        # Buscar versão COM TODOS os relacionamentos em UMA requisição
        versao_completa = directus.get_item("versao", versao_id, params={
            "fields": "*,modificacao.*,modificacao.clausula.*,contrato.*,contrato.modelo_contrato.*"
        })

        if not versao_completa:
            return jsonify({"error": "Versão não encontrada"}), 404

        if versao_completa.get("status") != "concluido":
            return jsonify({
                "error": "Versão ainda não processada",
                "status": versao_completa.get("status"),
                "progresso": versao_completa.get("progresso")
            }), 202

        # Validar que contrato e modelo estão presentes (obrigatórios)
        if not versao_completa.get("contrato"):
            logger.error(f"Versão {versao_id} sem contrato vinculado")
            return jsonify({"error": "Dados inconsistentes: versão sem contrato"}), 500

        if not versao_completa["contrato"].get("modelo_contrato"):
            logger.error(f"Contrato da versão {versao_id} sem modelo vinculado")
            return jsonify({"error": "Dados inconsistentes: contrato sem modelo"}), 500

        # Modificações já vêm no objeto versao_completa["modificacao"]
        modificacoes = versao_completa.get("modificacao", [])

        # Formatar dados para visualização
        dados_view = _formatar_para_view(versao_completa, modificacoes)

        # Renderizar template ou retornar JSON
        if request.args.get("format") == "json":
            return jsonify(dados_view)
        else:
            return render_template("view.html", dados=dados_view)

    except Exception as e:
        logger.error(f"Erro ao carregar view para versão {versao_id}: {e}")
        return jsonify({"error": str(e)}), 500
```

### Função Auxiliar

```python
def _formatar_para_view(versao_completa: dict, modificacoes: list[dict]) -> dict:
    """
    Formata dados do Directus para o formato esperado pelo frontend.

    Args:
        versao_completa: Objeto versão com todos os relacionamentos carregados
        modificacoes: Lista de modificações (já vem em versao_completa["modificacao"])

    Returns:
        Dicionário formatado para o frontend
    """
    modificacoes_formatadas = []

    for mod in modificacoes:
        mod_formatada = {
            "id": mod["id"],
            "tipo": _categoria_para_tipo(mod["categoria"]),
            "conteudo": {
                "original": mod.get("conteudo", ""),
                "novo": mod.get("alteracao", "")
            },
            "posicao": {
                "inicio": mod.get("posicao_inicio", 0),
                "fim": mod.get("posicao_fim", 0)
            },
            "caminho": {
                "inicio": mod.get("caminho_inicio"),
                "fim": mod.get("caminho_fim")
            }
        }

        # Adicionar cláusula se vinculada (já vem em mod["clausula"])
        if mod.get("clausula"):
            clausula = mod["clausula"]
            mod_formatada["clausula"] = {
                "id": clausula.get("id"),
                "numero": clausula.get("numero"),
                "nome": clausula.get("nome"),
                "tipo": clausula.get("tipo")
            }

            # Dados de vinculação (OPCIONAIS - serão adicionados na task-005)
            # Estes campos ainda não estão na coleção modificacao do Directus
            if mod.get("metodo_vinculacao") or mod.get("score_vinculacao") or mod.get("status_vinculacao"):
                mod_formatada["vinculacao"] = {
                    "metodo": mod.get("metodo_vinculacao", "conteudo"),
                    "score": mod.get("score_vinculacao"),
                    "status": mod.get("status_vinculacao", "automatico")
                }

        modificacoes_formatadas.append(mod_formatada)

    # Dados do contrato e modelo (OBRIGATÓRIOS - sempre devem estar presentes)
    contrato = versao_completa["contrato"]  # Não usa .get() - deve existir
    modelo = contrato["modelo_contrato"]     # Não usa .get() - deve existir

    return {
        "versao_id": versao_completa["id"],
        "status": versao_completa["status"],
        "data_processamento": versao_completa.get("data_hora_processamento"),
        "contrato": {
            "id": contrato["id"],
            "nome": contrato["nome"],
            "numero": contrato.get("numero")  # número pode ser opcional
        },
        "modelo": {
            "id": modelo["id"],
            "nome": modelo["nome"],
            "versao": modelo.get("versao")  # versão pode ser opcional
        },
        "modificacoes": modificacoes_formatadas,
        "metricas": _calcular_metricas(modificacoes)
    }

def _categoria_para_tipo(categoria: str) -> str:
    """Mapeia categoria do Directus para tipo do frontend."""
    mapa = {
        "modificacao": "ALTERACAO",
        "inclusao": "INSERCAO",
        "remocao": "REMOCAO",
        "comentario": "COMENTARIO",
        "formatacao": "FORMATACAO"
    }
    return mapa.get(categoria, "ALTERACAO")

def _calcular_metricas(modificacoes: list[dict]) -> dict:
    """Calcula métricas agregadas das modificações."""
    total = len(modificacoes)
    vinculadas = sum(1 for m in modificacoes if m.get("clausula"))

    return {
        "total_modificacoes": total,
        "vinculadas": vinculadas,
        "nao_vinculadas": total - vinculadas,
        "taxa_vinculacao": (vinculadas / total * 100) if total > 0 else 0
    }
```

## Benefícios

1. **Performance**:

   - ✅ Uma única requisição HTTP ao Directus
   - ✅ Não reprocessa a versão a cada visualização
   - ✅ Reduz latência de rede (1 request vs 3+ requests)

2. **Consistência**:

   - ✅ Exibe exatamente o que foi processado e persistido
   - ✅ Dados carregados atomicamente (snapshot consistente)

3. **Rastreabilidade**:

   - ✅ Dados vêm diretamente do banco de dados
   - ✅ Contrato e modelo disponíveis para contexto

4. **Escalabilidade**:

   - ✅ Múltiplos usuários podem visualizar sem sobrecarregar processamento
   - ✅ Menos carga no servidor Directus

5. **Cache**:
   - ✅ Possibilidade de cache adicional na camada de visualização
   - ✅ Directus pode cachear relacionamentos

## Exemplo de Resposta do Directus

Com a requisição:

```
GET /items/versao/99090886-7f43-45c9-bfe4-ec6eddd6cde0?fields=*,modificacao.*,modificacao.clausula.*,contrato.*,contrato.modelo_contrato.*
```

O Directus retorna algo como:

```json
{
  "data": {
    "id": "99090886-7f43-45c9-bfe4-ec6eddd6cde0",
    "status": "concluido",
    "data_hora_processamento": "2025-01-14T15:30:00Z",
    "contrato": {
      "id": "abc123",
      "nome": "Contrato de Prestação de Serviços",
      "numero": "2024/001",
      "modelo_contrato": {
        "id": "modelo-001",
        "nome": "Modelo Padrão v2",
        "versao": "2.1"
      }
    },
    "modificacao": [
      {
        "id": "mod-001",
        "categoria": "modificacao",
        "conteudo": "prazo de 30 dias",
        "alteracao": "prazo de 45 dias",
        "posicao_inicio": 1234,
        "posicao_fim": 1256,
        "metodo_vinculacao": "conteudo",
        "score_vinculacao": 0.95,
        "clausula": {
          "id": "clausula-001",
          "numero": "5.1",
          "nome": "Prazo de Vigência",
          "tipo": "prazo"
        }
      },
      {
        "id": "mod-002",
        "categoria": "inclusao",
        "conteudo": "nova cláusula de confidencialidade",
        "posicao_inicio": 2345,
        "posicao_fim": 2389,
        "clausula": null
      }
    ]
  }
}
```

## Validação

### Testes

- [ ] Versão processada com sucesso retorna dados corretos
- [ ] Versão não processada retorna erro apropriado (status 202)
- [ ] Versão inexistente retorna 404
- [ ] **Versão sem contrato retorna erro 500** ⚠️
- [ ] **Contrato sem modelo retorna erro 500** ⚠️
- [ ] Modificações são formatadas corretamente
- [ ] Cláusulas vinculadas aparecem na visualização
- [ ] Métricas são calculadas corretamente
- [ ] Performance: < 1s para versões com ~800 modificações
- [ ] Logs apropriados para erros de dados inconsistentes

### Checklist de Implementação

- [x] Modificar endpoint `/view/{versao_id}` para usar busca única
- [x] Adicionar parâmetro `fields` com todos os relacionamentos na chamada ao Directus
- [x] **Adicionar validação obrigatória de contrato e modelo** ⚠️
- [x] Implementar função `_formatar_para_view()` com suporte a contrato e modelo
- [x] Criar função `_calcular_metricas()`
- [ ] Atualizar template HTML para exibir dados de contrato/modelo (se necessário)
- [x] Adicionar tratamento de erros para relacionamentos ausentes
- [x] Adicionar logging com tempo de resposta da requisição única
- [x] **Adicionar logging específico para erros de dados inconsistentes** ⚠️
- [x] Atualizar documentação da API
- [x] Escrever testes unitários (mock da resposta única do Directus)
- [ ] **Escrever testes para cenários de erro (sem contrato, sem modelo)** ⚠️
- [ ] Escrever testes de integração (com Directus real)
- [ ] Testar com versão real em produção
- [ ] Benchmark de performance: comparar 1 request vs múltiplos requests

## Arquivos Afetados

- `versiona-ai/directus_server.py` (endpoint `/view`)
- `versiona-ai/templates/view.html` (se usar templates)
- `tests/test_view_endpoint.py` (novos testes)
- `API_DOCUMENTATION.md` (documentar mudança)

## Prioridade

**ALTA** - Completa o ciclo de persistência + visualização dos dados processados.

## Dependências

- ✅ Task 003 concluída (vinculação e persistência funcionando)
- Directus com dados de versão processada disponível
- ⏳ Task 005 (adicionar campos de vinculação) - **opcional**, view funciona sem estes dados

## Observações

### Performance Esperada

Com busca única:

- **1 request HTTP** ao invés de 3+ requests separados
- Latência típica: 50-200ms (dependendo de quantidade de modificações)
- Para 800 modificações: ~150-300ms esperados
- Cache do Directus pode reduzir para <50ms em acessos subsequentes

### Melhorias Futuras

- Adicionar filtros no frontend (por tipo, por cláusula, etc.)
- Paginação para versões com muitas modificações (>1000)
- Cache em Redis ou similar para performance adicional
- WebSocket para atualização em tempo real durante processamento
- Compressão gzip/brotli para reduzir payload da resposta

### Relacionamentos Directus

A estrutura de relacionamentos usada:

```
versao (1) -> (N) modificacoes         ⚠️ Campo: modificacoes (plural)
modificacoes (N) -> (1) clausula
versao (N) -> (1) contrato              ⚠️ OBRIGATÓRIO
contrato (N) -> (1) modelo_contrato     ⚠️ OBRIGATÓRIO
```

**Regra de Integridade:**

- Toda versão DEVE ter um contrato vinculado
- Todo contrato DEVE ter um modelo_contrato vinculado
- Se qualquer um destes relacionamentos estiver ausente, é um erro de dados inconsistentes (HTTP 500)

Query otimizada com `fields=*,modificacoes.*,modificacoes.clausula.*,contrato.*,contrato.modelo_contrato.*` carrega todos de uma vez.

**Tratamento de Erro:**

```python
# Sem contrato
if not versao_completa.get("contrato"):
    return jsonify({"error": "Dados inconsistentes: versão sem contrato"}), 500

# Sem modelo
if not versao_completa["contrato"].get("modelo_contrato"):
    return jsonify({"error": "Dados inconsistentes: contrato sem modelo"}), 500
```
