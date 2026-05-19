"""
Testes TDD para consolidação de vinculação com cláusulas inválidas.

CONTEXTO DO BUG ENCONTRADO:
- Tag 2.5.2 tinha múltiplas cláusulas associadas
- A primeira cláusula tinha ID inválido (não existia no banco)
- A segunda cláusula tinha ID válido (status=published)
- O código antigo pegava sempre a primeira → erro "Invalid foreign key"

SOLUÇÃO IMPLEMENTADA:
- Iterar por todas as cláusulas da tag
- Pegar a primeira que tenha status válido (draft ou published)
- Se nenhuma for válida, deixar sem clausula_id

Este teste valida essa lógica.
"""

from dataclasses import dataclass

import pytest


@dataclass
class TagMapeada:
    """Representa uma tag mapeada do modelo para o documento original."""

    tag_nome: str
    posicao_inicio_original: int
    posicao_fim_original: int
    score_inferencia: float = 1.0
    metodo: str = "conteudo"
    clausulas: list[dict] | None = None


@dataclass
class ResultadoVinculacao:
    """Resultado da vinculação de modificações a cláusulas."""

    vinculadas: list[dict]
    nao_vinculadas: list[dict]
    revisao_manual: list[dict]


class TestConsolidacaoClausulasInvalidas:
    """
    Testes para garantir que cláusulas inválidas são ignoradas
    e apenas cláusulas válidas (com status) são usadas.
    """

    @pytest.fixture
    def processor(self):
        """Mock simplificado do processador para testar _consolidar_modificacoes_vinculacao."""
        import sys
        from pathlib import Path

        # Adicionar versiona-ai ao path
        versiona_ai_path = Path(__file__).parent.parent / "versiona-ai"
        if str(versiona_ai_path) not in sys.path:
            sys.path.insert(0, str(versiona_ai_path))

        from directus_server import DirectusAPI

        # Criar instância mock sem necessidade de configuração completa
        processor = DirectusAPI.__new__(DirectusAPI)
        return processor

    def test_tag_com_clausula_invalida_primeira_e_valida_segunda(self, processor):
        """
        CENÁRIO: Tag tem 2 cláusulas, primeira sem status (inválida), segunda com status=published
        ESPERADO: Deve pegar a segunda (válida) e ignorar a primeira (inválida)
        """
        # Arrange: Tag com cláusula inválida primeiro, válida depois
        tag = TagMapeada(
            tag_nome="2.5.2",
            posicao_inicio_original=69333,
            posicao_fim_original=69811,
            clausulas=[
                {
                    "id": "92eb8f9e-c7ff-41fb-af8c-5a05d94a1556",  # ID que causou o bug real
                    "numero": "2.5.2",
                    "nome": "Cláusula órfã (sem status)",
                    "status": None,  # ❌ Inválida
                },
                {
                    "id": "4c81459b-d380-4325-b578-d03a5f7f8c40",  # ID válido do banco
                    "numero": "2.5.2",
                    "nome": "A CONTRATADA não terá direito de indenização",
                    "status": "published",  # ✅ Válida
                },
            ],
        )

        resultado = ResultadoVinculacao(
            vinculadas=[
                {
                    "modificacao": {
                        "tipo": "INSERCAO",
                        "posicao_inicio": 69570,
                        "posicao_fim": 69637,
                        "conteudo": {"novo": "a) Multa de 2%"},
                    },
                    "tag": tag,
                    "score": 0.85,
                }
            ],
            nao_vinculadas=[],
            revisao_manual=[],
        )

        # Act
        modificacoes = processor._consolidar_modificacoes_vinculacao(resultado)

        # Assert
        assert len(modificacoes) == 1
        mod = modificacoes[0]

        # ✅ Deve ter pegado a cláusula VÁLIDA (segunda)
        assert mod["clausula_id"] == "4c81459b-d380-4325-b578-d03a5f7f8c40"
        assert mod["clausula_numero"] == "2.5.2"
        assert mod["clausula_nome"] == "A CONTRATADA não terá direito de indenização"

        # ❌ NÃO deve ter pegado a cláusula INVÁLIDA (primeira)
        assert mod["clausula_id"] != "92eb8f9e-c7ff-41fb-af8c-5a05d94a1556"

    def test_tag_com_clausula_draft_eh_valida(self, processor):
        """
        CENÁRIO: Tag tem cláusula com status=draft
        ESPERADO: Deve aceitar (draft é válido)
        """
        tag = TagMapeada(
            tag_nome="3.1",
            posicao_inicio_original=69653,
            posicao_fim_original=70357,
            clausulas=[
                {
                    "id": "draft-clausula-id",
                    "numero": "3.1",
                    "nome": "Cláusula em rascunho",
                    "status": "draft",  # ✅ Draft é válido
                }
            ],
        )

        resultado = ResultadoVinculacao(
            vinculadas=[
                {
                    "modificacao": {"tipo": "ALTERACAO", "posicao_inicio": 69700},
                    "tag": tag,
                }
            ],
            nao_vinculadas=[],
            revisao_manual=[],
        )

        modificacoes = processor._consolidar_modificacoes_vinculacao(resultado)

        assert len(modificacoes) == 1
        assert modificacoes[0]["clausula_id"] == "draft-clausula-id"
        assert modificacoes[0]["clausula_numero"] == "3.1"

    def test_tag_com_todas_clausulas_invalidas(self, processor):
        """
        CENÁRIO: Tag tem 3 cláusulas, todas sem status (inválidas)
        ESPERADO: Modificação não deve ter clausula_id
        """
        tag = TagMapeada(
            tag_nome="10.7",
            posicao_inicio_original=100000,
            posicao_fim_original=105000,
            clausulas=[
                {"id": "invalid-1", "numero": "10.7", "status": None},
                {"id": "invalid-2", "numero": "10.7", "status": None},
                {
                    "id": "invalid-3",
                    "numero": "10.7",
                    "status": "archived",
                },  # archived não é válido
            ],
        )

        resultado = ResultadoVinculacao(
            vinculadas=[
                {
                    "modificacao": {"tipo": "REMOCAO", "posicao_inicio": 102000},
                    "tag": tag,
                }
            ],
            nao_vinculadas=[],
            revisao_manual=[],
        )

        modificacoes = processor._consolidar_modificacoes_vinculacao(resultado)

        assert len(modificacoes) == 1
        mod = modificacoes[0]

        # Não deve ter clausula_id pois todas são inválidas
        assert mod.get("clausula_id") is None or mod.get("clausula_id") == ""

    def test_tag_com_clausula_string_id_direto(self, processor):
        """
        CENÁRIO: Tag tem lista de IDs simples (strings) ao invés de dicts
        ESPERADO: Deve aceitar o primeiro ID (não tem como validar status)
        """
        tag = TagMapeada(
            tag_nome="5.2",
            posicao_inicio_original=80000,
            posicao_fim_original=85000,
            clausulas=[
                "clausula-id-string-1",
                "clausula-id-string-2",
            ],  # Lista de strings
        )

        resultado = ResultadoVinculacao(
            vinculadas=[
                {
                    "modificacao": {"tipo": "INSERCAO", "posicao_inicio": 82000},
                    "tag": tag,
                }
            ],
            nao_vinculadas=[],
            revisao_manual=[],
        )

        modificacoes = processor._consolidar_modificacoes_vinculacao(resultado)

        assert len(modificacoes) == 1
        # Como são strings diretas, pega a primeira
        assert modificacoes[0]["clausula_id"] == "clausula-id-string-1"

    def test_tag_com_clausula_aninhada_via_juncao(self, processor):
        """
        CENÁRIO: Cláusula vem aninhada via tabela de junção (clausula.clausula_id)
        ESPERADO: Deve extrair o ID corretamente
        """
        tag = TagMapeada(
            tag_nome="12.6",
            posicao_inicio_original=110000,
            posicao_fim_original=115000,
            clausulas=[
                {
                    "clausula": {
                        "id": "nested-clausula-id",
                        "numero": "12.6",
                        "nome": "Cláusula aninhada",
                        "status": "published",
                    }
                }
            ],
        )

        resultado = ResultadoVinculacao(
            vinculadas=[
                {
                    "modificacao": {"tipo": "ALTERACAO", "posicao_inicio": 112000},
                    "tag": tag,
                }
            ],
            nao_vinculadas=[],
            revisao_manual=[],
        )

        modificacoes = processor._consolidar_modificacoes_vinculacao(resultado)

        assert len(modificacoes) == 1
        assert modificacoes[0]["clausula_id"] == "nested-clausula-id"
        assert modificacoes[0]["clausula_numero"] == "12.6"

    def test_modificacao_nao_vinculada_sem_clausula(self, processor):
        """
        CENÁRIO: Modificação que não foi vinculada a nenhuma tag
        ESPERADO: Não deve ter clausula_id
        """
        resultado = ResultadoVinculacao(
            vinculadas=[],
            nao_vinculadas=[
                {
                    "modificacao": {
                        "tipo": "INSERCAO",
                        "posicao_inicio": 50000,
                        "posicao_fim": 50100,
                    },
                    "motivo": "sem_sobreposicao",
                }
            ],
            revisao_manual=[],
        )

        modificacoes = processor._consolidar_modificacoes_vinculacao(resultado)

        assert len(modificacoes) == 1
        mod = modificacoes[0]
        assert mod.get("clausula_id") is None or mod.get("clausula_id") == ""
        assert mod["status_vinculacao"] == "nao_vinculada"
        assert mod["motivo_vinculacao"] == "sem_sobreposicao"

    def test_revisao_manual_com_clausula_valida(self, processor):
        """
        CENÁRIO: Modificação marcada para revisão manual, tag tem cláusula válida
        ESPERADO: Deve incluir clausula_id mesmo sendo revisão manual
        """
        tag = TagMapeada(
            tag_nome="16.3",
            posicao_inicio_original=120000,
            posicao_fim_original=125000,
            clausulas=[
                {
                    "id": "valid-clausula-review",
                    "numero": "16.3",
                    "nome": "Força maior",
                    "status": "published",
                }
            ],
        )

        resultado = ResultadoVinculacao(
            vinculadas=[],
            nao_vinculadas=[],
            revisao_manual=[
                {
                    "modificacao": {"tipo": "ALTERACAO", "posicao_inicio": 122000},
                    "tag": tag,
                    "score": 0.65,
                    "motivo": "score_medio",
                }
            ],
        )

        modificacoes = processor._consolidar_modificacoes_vinculacao(resultado)

        assert len(modificacoes) == 1
        mod = modificacoes[0]
        assert mod["clausula_id"] == "valid-clausula-review"
        assert mod["status_vinculacao"] == "revisao_manual"
        assert mod["score_vinculacao"] == 0.65

    def test_multiplas_modificacoes_mesma_tag(self, processor):
        """
        CENÁRIO: Várias modificações vinculadas à mesma tag
        ESPERADO: Todas devem receber o mesmo clausula_id válido
        """
        tag = TagMapeada(
            tag_nome="2.5.2",
            posicao_inicio_original=69333,
            posicao_fim_original=69811,
            clausulas=[
                {
                    "id": "shared-clausula-id",
                    "numero": "2.5.2",
                    "nome": "Cláusula compartilhada",
                    "status": "published",
                }
            ],
        )

        resultado = ResultadoVinculacao(
            vinculadas=[
                {
                    "modificacao": {"tipo": "INSERCAO", "posicao_inicio": 69570},
                    "tag": tag,
                },
                {
                    "modificacao": {"tipo": "INSERCAO", "posicao_inicio": 69639},
                    "tag": tag,
                },
            ],
            nao_vinculadas=[],
            revisao_manual=[],
        )

        modificacoes = processor._consolidar_modificacoes_vinculacao(resultado)

        assert len(modificacoes) == 2
        # Ambas devem ter o mesmo clausula_id
        assert modificacoes[0]["clausula_id"] == "shared-clausula-id"
        assert modificacoes[1]["clausula_id"] == "shared-clausula-id"

    def test_cenario_real_bug_producao(self, processor):
        """
        REPRODUÇÃO EXATA DO BUG REAL:
        - Versão 2573b998-63d0-4471-ad85-db6f860c3721
        - 2 modificações de INSERCAO
        - Tag 2.5.2 com cláusula inválida primeiro
        - Erro: "Invalid foreign key 92eb8f9e-..."
        """
        # Tag EXATA do bug real
        tag_252 = TagMapeada(
            tag_nome="2.5.2",
            posicao_inicio_original=69333,
            posicao_fim_original=69811,
            clausulas=[
                {
                    "id": "92eb8f9e-c7ff-41fb-af8c-5a05d94a1556",  # BUG: ID não existe
                    "numero": "2.5.2",
                    "nome": "A CONTRATADA não terá direito de indenização de qualquer natureza em",
                    "status": None,  # ❌ Sem status
                },
                {
                    "id": "4c81459b-d380-4325-b578-d03a5f7f8c40",  # ✅ ID válido
                    "numero": "2.5.2",
                    "nome": "A CONTRATADA não terá direito de indenização",
                    "status": "published",
                },
            ],
        )

        resultado = ResultadoVinculacao(
            vinculadas=[
                {
                    "modificacao": {
                        "tipo": "INSERCAO",
                        "posicao_inicio": 69570,
                        "posicao_fim": 69637,
                        "conteudo": {"novo": "a) Multa de 2% (dois por cento)"},
                    },
                    "tag": tag_252,
                    "score": 0.85,
                },
                {
                    "modificacao": {
                        "tipo": "INSERCAO",
                        "posicao_inicio": 69639,
                        "posicao_fim": 69825,
                        "conteudo": {"novo": "b) Juros de mora, pro rata die"},
                    },
                    "tag": tag_252,
                    "score": 0.85,
                },
            ],
            nao_vinculadas=[],
            revisao_manual=[],
        )

        # Act
        modificacoes = processor._consolidar_modificacoes_vinculacao(resultado)

        # Assert: Ambas modificações devem usar ID VÁLIDO
        assert len(modificacoes) == 2

        for i, mod in enumerate(modificacoes):
            # ✅ Deve pegar ID válido
            assert mod["clausula_id"] == "4c81459b-d380-4325-b578-d03a5f7f8c40", (
                f"Modificação {i} pegou ID errado: {mod.get('clausula_id')}"
            )

            # ❌ NÃO deve pegar ID inválido
            assert mod["clausula_id"] != "92eb8f9e-c7ff-41fb-af8c-5a05d94a1556", (
                f"Modificação {i} pegou ID inválido que causou o bug!"
            )

            assert mod["clausula_numero"] == "2.5.2"
            assert mod["status_vinculacao"] == "automatico"
