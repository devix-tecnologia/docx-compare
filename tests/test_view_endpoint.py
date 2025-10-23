"""
Testes para o endpoint /versao/<versao_id> (Task-004)
Testa a visualização de dados do Directus
"""

import os
import sys

import pytest

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "versiona-ai"))


@pytest.fixture
def mock_versao_completa():
    """Mock de resposta completa do Directus com todos os relacionamentos"""
    return {
        "id": "test-versao-123",
        "status": "concluido",
        "data_hora_processamento": "2025-01-14T15:30:00Z",
        "contrato": {
            "id": "contrato-123",
            "nome": "Contrato de Teste",
            "numero": "2024/001",
            "modelo_contrato": {
                "id": "modelo-123",
                "nome": "Modelo Padrão",
                "versao": "1.0",
            },
        },
        "modificacao": [
            {
                "id": "mod-001",
                "categoria": "modificacao",
                "conteudo": "texto original",
                "alteracao": "texto modificado",
                "posicao_inicio": 100,
                "posicao_fim": 200,
                "caminho_inicio": "/doc/body/p[1]",
                "caminho_fim": "/doc/body/p[1]",
                "clausula": {
                    "id": "clausula-001",
                    "numero": "5.1",
                    "nome": "Cláusula Teste",
                    "tipo": "prazo",
                },
                "metodo_vinculacao": "conteudo",
                "score_vinculacao": 0.95,
                "status_vinculacao": "automatico",
            },
            {
                "id": "mod-002",
                "categoria": "inclusao",
                "conteudo": "novo texto",
                "alteracao": None,
                "posicao_inicio": 300,
                "posicao_fim": 400,
                "caminho_inicio": "/doc/body/p[2]",
                "caminho_fim": "/doc/body/p[2]",
                "clausula": None,
            },
        ],
    }


@pytest.fixture
def mock_versao_sem_contrato():
    """Mock de versão sem contrato (erro de dados)"""
    return {
        "id": "test-versao-456",
        "status": "concluido",
        "contrato": None,
        "modificacao": [],
    }


@pytest.fixture
def mock_versao_nao_processada():
    """Mock de versão ainda não processada"""
    return {
        "id": "test-versao-789",
        "status": "processando",
        "progresso": 45,
        "contrato": {"id": "contrato-123", "modelo_contrato": {"id": "modelo-123"}},
        "modificacao": [],
    }


def test_formatar_para_view_sucesso(mock_versao_completa):
    """Testa formatação de dados completos do Directus"""
    from directus_server import _formatar_para_view

    resultado = _formatar_para_view(
        mock_versao_completa, mock_versao_completa["modificacao"]
    )

    # Verificar estrutura principal
    assert resultado["versao_id"] == "test-versao-123"
    assert resultado["status"] == "concluido"
    assert resultado["data_processamento"] == "2025-01-14T15:30:00Z"

    # Verificar contrato
    assert resultado["contrato"]["id"] == "contrato-123"
    assert resultado["contrato"]["nome"] == "Contrato de Teste"

    # Verificar modelo
    assert resultado["modelo"]["id"] == "modelo-123"
    assert resultado["modelo"]["nome"] == "Modelo Padrão"

    # Verificar modificações
    assert len(resultado["modificacoes"]) == 2

    # Primeira modificação (com cláusula e vinculação)
    mod1 = resultado["modificacoes"][0]
    assert mod1["id"] == "mod-001"
    assert mod1["tipo"] == "ALTERACAO"
    assert mod1["conteudo"]["original"] == "texto original"
    assert mod1["conteudo"]["novo"] == "texto modificado"
    assert mod1["posicao"]["inicio"] == 100
    assert mod1["posicao"]["fim"] == 200
    assert mod1["clausula"]["numero"] == "5.1"
    assert mod1["vinculacao"]["metodo"] == "conteudo"
    assert mod1["vinculacao"]["score"] == 0.95

    # Segunda modificação (sem cláusula)
    mod2 = resultado["modificacoes"][1]
    assert mod2["id"] == "mod-002"
    assert mod2["tipo"] == "INSERCAO"
    assert "clausula" not in mod2
    assert "vinculacao" not in mod2

    # Verificar métricas
    assert resultado["metricas"]["total_modificacoes"] == 2
    assert resultado["metricas"]["vinculadas"] == 1
    assert resultado["metricas"]["nao_vinculadas"] == 1
    assert resultado["metricas"]["taxa_vinculacao"] == 50.0


def test_categoria_para_tipo():
    """Testa mapeamento de categorias"""
    from directus_server import _categoria_para_tipo

    assert _categoria_para_tipo("modificacao") == "ALTERACAO"
    assert _categoria_para_tipo("inclusao") == "INSERCAO"
    assert _categoria_para_tipo("remocao") == "REMOCAO"
    assert _categoria_para_tipo("comentario") == "COMENTARIO"
    assert _categoria_para_tipo("formatacao") == "FORMATACAO"
    assert _categoria_para_tipo("desconhecido") == "ALTERACAO"  # default


def test_calcular_metricas():
    """Testa cálculo de métricas"""
    from directus_server import _calcular_metricas

    modificacoes = [
        {"id": "1", "clausula": {"id": "c1"}},
        {"id": "2", "clausula": {"id": "c2"}},
        {"id": "3", "clausula": None},
        {"id": "4", "clausula": None},
    ]

    metricas = _calcular_metricas(modificacoes)

    assert metricas["total_modificacoes"] == 4
    assert metricas["vinculadas"] == 2
    assert metricas["nao_vinculadas"] == 2
    assert metricas["taxa_vinculacao"] == 50.0


def test_calcular_metricas_vazio():
    """Testa métricas com lista vazia"""
    from directus_server import _calcular_metricas

    metricas = _calcular_metricas([])

    assert metricas["total_modificacoes"] == 0
    assert metricas["vinculadas"] == 0
    assert metricas["nao_vinculadas"] == 0
    assert metricas["taxa_vinculacao"] == 0


def test_formatar_modificacao_sem_vinculacao():
    """Testa formatação de modificação sem dados de vinculação"""
    from directus_server import _formatar_para_view

    versao = {
        "id": "v1",
        "status": "concluido",
        "contrato": {
            "id": "c1",
            "nome": "Contrato",
            "modelo_contrato": {"id": "m1", "nome": "Modelo"},
        },
        "modificacao": [
            {
                "id": "mod1",
                "categoria": "modificacao",
                "conteudo": "texto",
                "posicao_inicio": 0,
                "posicao_fim": 10,
                "clausula": {"id": "cl1", "numero": "1.1", "nome": "Teste"},
                # SEM metodo_vinculacao, score_vinculacao, status_vinculacao
            }
        ],
    }

    resultado = _formatar_para_view(versao, versao["modificacao"])
    mod = resultado["modificacoes"][0]

    # Verificar que vinculacao não foi adicionada
    assert "vinculacao" not in mod
    # Mas cláusula está presente
    assert "clausula" in mod


def test_formatar_modificacao_com_vinculacao_parcial():
    """Testa formatação quando só alguns campos de vinculação estão presentes"""
    from directus_server import _formatar_para_view

    versao = {
        "id": "v1",
        "status": "concluido",
        "contrato": {
            "id": "c1",
            "nome": "Contrato",
            "modelo_contrato": {"id": "m1", "nome": "Modelo"},
        },
        "modificacao": [
            {
                "id": "mod1",
                "categoria": "modificacao",
                "conteudo": "texto",
                "posicao_inicio": 0,
                "posicao_fim": 10,
                "clausula": {"id": "cl1", "numero": "1.1"},
                "score_vinculacao": 0.85,
                # metodo_vinculacao e status_vinculacao ausentes
            }
        ],
    }

    resultado = _formatar_para_view(versao, versao["modificacao"])
    mod = resultado["modificacoes"][0]

    # Deve adicionar vinculacao porque score_vinculacao está presente
    assert "vinculacao" in mod
    assert mod["vinculacao"]["score"] == 0.85
    assert mod["vinculacao"]["metodo"] == "conteudo"  # default
    assert mod["vinculacao"]["status"] == "automatico"  # default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
