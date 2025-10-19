"""
Documentação Swagger/OpenAPI para a API do Versiona.ai

Este módulo configura o Flask-RESTX para gerar documentação interativa
acessível em /docs/
"""

from flask import Blueprint
from flask_restx import Api, Namespace, Resource, fields

# Blueprint para documentação
docs_blueprint = Blueprint("docs", __name__)

# Configurar API Swagger
api = Api(
    docs_blueprint,
    version="1.0",
    title="Versiona.ai API",
    description="""
# API de Processamento de Documentos DOCX

API para comparação e análise de documentos contratuais com detecção automática de modificações.

## 🎯 Recursos Principais

- **Processamento AST (Pandoc)**: 59.3% de precisão
- **Integração Directus**: Persistência automática
- **Detecção Inteligente**: Alterações, inserções e remoções
- **Vinculação de Cláusulas**: Mapeamento automático

## 📋 Endpoints Principais

### Processamento
- `POST /api/process` - Processa versão individual
- `POST /api/process-modelo` - Processa modelo completo

### Visualização
- `GET /view/{diff_id}` - Interface HTML do diff
- `GET /api/data/{diff_id}` - Dados JSON do diff

### Utilidades
- `GET /health` - Status da aplicação
    """,
    doc="/docs/",
)

# Namespace
ns = Namespace("api", description="Operações da API")

# ===== MODELS =====

# Model: Request de Versão
versao_request = api.model(
    "VersaoRequest",
    {
        "versao_id": fields.String(
            required=True,
            description="UUID da versão",
            example="322e56c0-4b38-4e62-b563-8f29a131889c",
        ),
        "use_ast": fields.Boolean(
            default=True, description="Usar AST (true) ou método original (false)"
        ),
        "mock": fields.Boolean(default=False, description="Usar dados mockados"),
    },
)

# Model: Request de Modelo
modelo_request = api.model(
    "ModeloRequest",
    {
        "modelo_id": fields.String(
            required=True,
            description="UUID do modelo",
            example="d2699a57-b0ff-472b-a130-626f5fc2852b",
        ),
        "use_ast": fields.Boolean(default=True, description="Usar processamento AST"),
        "process_tags": fields.Boolean(
            default=True, description="Processar tags do modelo"
        ),
        "process_versions": fields.Boolean(
            default=True, description="Processar versões automaticamente"
        ),
        "dry_run": fields.Boolean(
            default=False, description="Simular sem gravar no Directus"
        ),
    },
)

# Model: Modificação
modificacao_model = api.model(
    "Modificacao",
    {
        "id": fields.Integer(description="ID da modificação"),
        "tipo": fields.String(
            description="Tipo", enum=["ALTERACAO", "REMOCAO", "INSERCAO"]
        ),
        "confianca": fields.Float(description="Confiança (0.0-1.0)"),
        "clausula_original": fields.String(description="Cláusula original"),
        "clausula_modificada": fields.String(description="Cláusula modificada"),
        "conteudo": fields.Raw(
            description="Conteúdo original e novo", example={"original": "...", "novo": "..."}
        ),
    },
)

# Model: Response de Versão
versao_response = api.model(
    "VersaoResponse",
    {
        "success": fields.Boolean(description="Sucesso"),
        "diff_id": fields.String(description="UUID do diff"),
        "url": fields.String(description="URL de visualização"),
        "modificacoes": fields.List(
            fields.Nested(modificacao_model), description="Lista de modificações"
        ),
        "metricas": fields.Raw(
            description="Métricas",
            example={
                "total_modificacoes": 8,
                "alteracoes": 4,
                "remocoes": 2,
                "insercoes": 2,
            },
        ),
        "metodo": fields.String(
            description="Método usado", enum=["AST_PANDOC", "SEQUENCE_MATCHER"]
        ),
    },
)

# Model: Response de Modelo
modelo_response = api.model(
    "ModeloResponse",
    {
        "status": fields.String(description="Status", enum=["sucesso", "erro"]),
        "modelo_id": fields.String(description="UUID do modelo"),
        "use_ast": fields.Boolean(description="Usou AST"),
        "tags_encontradas": fields.Integer(description="Tags encontradas"),
        "tags_criadas": fields.Integer(description="Tags criadas"),
        "versoes_processadas": fields.Integer(description="Versões processadas"),
        "versoes_com_erro": fields.Integer(description="Versões com erro"),
        "total_modificacoes": fields.Integer(description="Total de modificações"),
    },
)

# Model: Erro
error_model = api.model(
    "Error",
    {
        "error": fields.String(description="Mensagem de erro"),
        "details": fields.String(description="Detalhes"),
    },
)

# ===== RESOURCES (ENDPOINTS DOCUMENTADOS) =====


@ns.route("/process")
class ProcessVersao(Resource):
    @api.doc("process_versao")
    @api.expect(versao_request)
    @api.response(200, "Sucesso", versao_response)
    @api.response(400, "Erro", error_model)
    def post(self):
        """
        Processa uma versão de contrato

        Detecta modificações comparando documento original com modificado.
        Usa AST (Pandoc) por padrão para 59.3% de precisão.
        """
        pass  # Implementação no directus_server.py


@ns.route("/process-modelo")
class ProcessModelo(Resource):
    @api.doc("process_modelo")
    @api.expect(modelo_request)
    @api.response(200, "Sucesso", modelo_response)
    @api.response(400, "Erro", error_model)
    def post(self):
        """
        Processa modelo completo com todas as versões

        1. Extrai tags do modelo ({{tag}})
        2. Busca todas as versões vinculadas
        3. Processa cada versão com AST
        4. Grava no Directus automaticamente
        """
        pass  # Implementação no directus_server.py


api.add_namespace(ns, path="/api")
