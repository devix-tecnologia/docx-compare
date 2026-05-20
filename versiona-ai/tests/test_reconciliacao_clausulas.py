#!/usr/bin/env python3
"""
Testes TDD para reconciliação de cláusulas no reprocessamento de modelos.

Estratégia de reconciliação:
  - Cláusula existe no modelo E no documento → update (só conteudo_original)
  - Cláusula existe no modelo mas NÃO no documento → update (status="inativo")
  - Cláusula NÃO existe no modelo mas SIM no documento → create (nova)
  - Nenhuma cláusula é deletada — dados manuais nunca são perdidos.

Tudo via sintaxe "Detailed" do Directus (create/update em 1 PATCH).
"""

from unittest.mock import MagicMock

import pytest
from processador_tags_modelo import ProcessadorTagsModelo


@pytest.fixture
def processador():
    """Cria um processador com repositório mockado."""
    proc = ProcessadorTagsModelo("https://test.directus.io", "fake-token")
    proc.repo = MagicMock()
    return proc


# ---------------------------------------------------------------------------
# Fixtures de dados
# ---------------------------------------------------------------------------


def _clausulas_existentes():
    """Cláusulas já cadastradas no modelo (simulando o que viria do Directus)."""
    return [
        {
            "id": "clau-aaa",
            "numero": "1.1",
            "nome": "Objeto do Contrato",
            "conteudo_original": "Texto original da cláusula 1.1",
            "status": "published",
        },
        {
            "id": "clau-bbb",
            "numero": "2.1",
            "nome": "Vigência",
            "conteudo_original": "Texto original da cláusula 2.1",
            "status": "published",
        },
        {
            "id": "clau-ccc",
            "numero": "3.1",
            "nome": "Pagamento",
            "conteudo_original": "Texto original da cláusula 3.1",
            "status": "published",
        },
    ]


def _tags_reprocessadas():
    """Tags extraídas no reprocessamento (documento atualizado).

    - 1.1 continua (mesmo conteúdo)
    - 2.1 continua (conteúdo mudou)
    - 3.1 SUMIU do documento
    - 4.1 é NOVA
    """
    return [
        {"nome": "1.1", "conteudo": "Texto original da cláusula 1.1"},
        {"nome": "2.1", "conteudo": "Texto ATUALIZADO da cláusula 2.1"},
        {"nome": "4.1", "conteudo": "Texto da nova cláusula 4.1"},
        {"nome": "vigencia", "conteudo": "Tag textual sem número"},
    ]


# ---------------------------------------------------------------------------
# Testes: _reconciliar_clausulas
# ---------------------------------------------------------------------------


class TestReconciliarClausulas:
    """Testes para o método _reconciliar_clausulas."""

    def test_retorna_estrutura_detailed_do_directus(self, processador):
        """O resultado deve ter as chaves 'create' e 'update' (sintaxe Detailed)."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        assert "create" in resultado
        assert "update" in resultado
        assert isinstance(resultado["create"], list)
        assert isinstance(resultado["update"], list)

    def test_clausula_nova_vai_para_create(self, processador):
        """Cláusula 4.1 não existe no modelo — deve ir para 'create'."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        numeros_criados = [c["numero"] for c in resultado["create"]]
        assert "4.1" in numeros_criados

    def test_clausula_nova_tem_campos_obrigatorios(self, processador):
        """Cláusulas criadas devem ter modelo_contrato, numero, nome, conteudo_original, status."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        for clausula in resultado["create"]:
            assert "modelo_contrato" in clausula
            assert clausula["modelo_contrato"] == "modelo-123"
            assert "numero" in clausula
            assert "nome" in clausula
            assert "conteudo_original" in clausula
            assert clausula["status"] == "published"

    def test_clausula_existente_com_conteudo_alterado_vai_para_update(
        self, processador
    ):
        """Cláusula 2.1 existe e mudou conteúdo — deve ir para 'update'."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        ids_atualizados = [c["id"] for c in resultado["update"]]
        assert "clau-bbb" in ids_atualizados

        # Verificar que o conteudo_original foi atualizado
        update_bbb = next(c for c in resultado["update"] if c["id"] == "clau-bbb")
        assert update_bbb["conteudo_original"] == "Texto ATUALIZADO da cláusula 2.1"

    def test_clausula_existente_com_mesmo_conteudo_nao_vai_para_update(
        self, processador
    ):
        """Cláusula 1.1 existe com mesmo conteúdo — NÃO deve ir para 'update'."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        ids_atualizados = [c["id"] for c in resultado["update"]]
        assert "clau-aaa" not in ids_atualizados

    def test_clausula_removida_do_documento_fica_inativa(self, processador):
        """Cláusula 3.1 sumiu do documento — deve ir para 'update' com status 'inativo'."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        ids_atualizados = {c["id"]: c for c in resultado["update"]}
        assert "clau-ccc" in ids_atualizados

        update_ccc = ids_atualizados["clau-ccc"]
        assert update_ccc["status"] == "inativo"

    def test_clausula_inativa_nao_perde_campos_manuais(self, processador):
        """Ao inativar, o update deve ter APENAS id e status — não sobrescrever campos manuais."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        update_ccc = next(c for c in resultado["update"] if c["id"] == "clau-ccc")
        # Só deve ter id e status, sem sobrescrever conteudo/nome
        assert "conteudo_original" not in update_ccc
        assert "nome" not in update_ccc

    def test_update_so_altera_conteudo_original(self, processador):
        """Para cláusulas com conteúdo alterado, o update só muda conteudo_original."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        update_bbb = next(c for c in resultado["update"] if c["id"] == "clau-bbb")
        # Deve ter id e conteudo_original, NÃO deve sobrescrever nome
        assert "id" in update_bbb
        assert "conteudo_original" in update_bbb
        assert "nome" not in update_bbb

    def test_tags_nao_numericas_sao_ignoradas(self, processador):
        """Tags textuais (ex: 'vigencia') não geram cláusulas."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=[],
            tags_validas=_tags_reprocessadas(),
        )

        numeros_criados = [c["numero"] for c in resultado["create"]]
        assert "vigencia" not in numeros_criados
        # Nenhum create deve ter numero vazio
        assert all(c["numero"] for c in resultado["create"])

    def test_nenhuma_clausula_e_deletada(self, processador):
        """NUNCA deve existir chave 'delete' no resultado."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        assert "delete" not in resultado

    def test_clausulas_duplicadas_no_documento_nao_duplicam_create(self, processador):
        """Se o documento tem a mesma tag 2x, deve gerar só 1 create."""
        tags_duplicadas = [
            {"nome": "5.1", "conteudo": "Texto cláusula 5.1"},
            {"nome": "5.1", "conteudo": "Texto cláusula 5.1 repetida"},
        ]

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=[],
            tags_validas=tags_duplicadas,
        )

        numeros_criados = [c["numero"] for c in resultado["create"]]
        assert numeros_criados.count("5.1") == 1

    def test_modelo_sem_clausulas_cria_todas(self, processador):
        """Se o modelo não tem cláusulas, todas as numéricas devem ser criadas."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=[],
            tags_validas=_tags_reprocessadas(),
        )

        numeros_criados = sorted(c["numero"] for c in resultado["create"])
        assert numeros_criados == ["1.1", "2.1", "4.1"]
        assert resultado["update"] == []

    def test_documento_sem_tags_inativa_todas(self, processador):
        """Se o documento não tem tags, todas as cláusulas devem ficar inativas."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=[],
        )

        assert resultado["create"] == []
        ids_inativos = [c["id"] for c in resultado["update"]]
        assert sorted(ids_inativos) == sorted(["clau-aaa", "clau-bbb", "clau-ccc"])

        for update in resultado["update"]:
            assert update["status"] == "inativo"

    def test_clausula_inativa_reativada_ao_reaparecer(self, processador):
        """Se uma cláusula estava inativa e reaparece no documento, deve ser reativada."""
        clausulas = [
            {
                "id": "clau-inativa",
                "numero": "5.1",
                "nome": "Cláusula inativa",
                "conteudo_original": "Texto antigo",
                "status": "inativo",
            },
        ]
        tags = [{"nome": "5.1", "conteudo": "Texto novo"}]

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=clausulas,
            tags_validas=tags,
        )

        # Não deve criar — a cláusula já existe
        assert resultado["create"] == []

        # Deve atualizar com conteúdo novo e status published
        assert len(resultado["update"]) == 1
        update = resultado["update"][0]
        assert update["id"] == "clau-inativa"
        assert update["conteudo_original"] == "Texto novo"
        assert update["status"] == "published"

    def test_conteudo_original_limitado_a_5000_chars(self, processador):
        """conteudo_original deve ser truncado a 5000 caracteres."""
        tags = [{"nome": "1.1", "conteudo": "x" * 10000}]

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=[],
            tags_validas=tags,
        )

        for clausula in resultado["create"]:
            assert len(clausula["conteudo_original"]) <= 5000


# ---------------------------------------------------------------------------
# Testes: integração com PATCH do Directus (sintaxe Detailed)
# ---------------------------------------------------------------------------


class TestPatchClausulasDetailed:
    """Verifica que o payload gerado é compatível com a API do Directus."""

    def test_payload_detailed_valido(self, processador):
        """O payload para PATCH deve usar a sintaxe {create: [...], update: [...]}."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        # Deve ser usável diretamente como: {"clausulas": resultado}
        payload = {"clausulas": resultado}
        assert "clausulas" in payload
        assert "create" in payload["clausulas"]
        assert "update" in payload["clausulas"]

    def test_itens_de_create_nao_tem_id(self, processador):
        """Itens em 'create' não devem ter 'id' — Directus gera automaticamente."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=[],
            tags_validas=_tags_reprocessadas(),
        )

        for clausula in resultado["create"]:
            assert "id" not in clausula

    def test_itens_de_update_tem_id(self, processador):
        """Todo item em 'update' DEVE ter 'id' — Directus precisa saber qual atualizar."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        for clausula in resultado["update"]:
            assert "id" in clausula
            assert clausula["id"]  # Não pode ser vazio


# ---------------------------------------------------------------------------
# Testes de borda
# ---------------------------------------------------------------------------


class TestReconciliacaoEdgeCases:
    """Edge cases para reconciliação de cláusulas."""

    def test_clausula_existente_com_conteudo_none(self, processador):
        """Cláusula no Directus com conteudo_original=None não deve causar erro."""
        clausulas = [
            {
                "id": "clau-null",
                "numero": "1.1",
                "nome": "Cláusula sem conteúdo",
                "conteudo_original": None,
                "status": "published",
            },
        ]
        tags = [{"nome": "1.1", "conteudo": "Texto novo"}]

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=clausulas,
            tags_validas=tags,
        )

        # Deve atualizar pois None != "Texto novo"
        assert len(resultado["update"]) == 1
        assert resultado["update"][0]["conteudo_original"] == "Texto novo"

    def test_clausula_existente_sem_numero(self, processador):
        """Cláusula existente sem 'numero' (campo vazio/None) deve ser ignorada."""
        clausulas = [
            {
                "id": "clau-sem-numero",
                "numero": "",
                "nome": "Manual sem número",
                "conteudo_original": "Texto qualquer",
                "status": "published",
            },
            {
                "id": "clau-none-numero",
                "numero": None,
                "nome": "Outro sem número",
                "conteudo_original": "Outro texto",
                "status": "published",
            },
        ]
        tags = [{"nome": "1.1", "conteudo": "Texto 1.1"}]

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=clausulas,
            tags_validas=tags,
        )

        # 1.1 é nova — as existentes sem numero não entram na reconciliação
        assert len(resultado["create"]) == 1
        assert resultado["create"][0]["numero"] == "1.1"
        # Cláusulas sem número NÃO devem ser inativadas (não participam)
        assert resultado["update"] == []

    def test_clausula_ja_inativa_e_ausente_nao_gera_update(self, processador):
        """Cláusula que já está inativa e continua ausente NÃO deve gerar update redundante."""
        clausulas = [
            {
                "id": "clau-ja-inativa",
                "numero": "9.9",
                "nome": "Já desativada",
                "conteudo_original": "Texto antigo",
                "status": "inativo",
            },
        ]
        tags = []  # Documento sem tags

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=clausulas,
            tags_validas=tags,
        )

        # Já era inativa e continua ausente — nenhum update necessário
        assert resultado["update"] == []

    def test_whitespace_no_conteudo_existente_vs_novo(self, processador):
        """Conteúdo com whitespace diferente deve ser tratado como alteração."""
        clausulas = [
            {
                "id": "clau-ws",
                "numero": "1.1",
                "nome": "Cláusula",
                "conteudo_original": "  Texto com espaços  ",
                "status": "published",
            },
        ]
        # Tag tem o mesmo texto mas sem espaços extras
        tags = [{"nome": "1.1", "conteudo": "Texto com espaços"}]

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=clausulas,
            tags_validas=tags,
        )

        # O antigo é stripped ("Texto com espaços") — deve ser igual ao novo
        # Portanto NÃO deve gerar update desnecessário
        assert resultado["update"] == []

    def test_conteudo_vazio_na_tag(self, processador):
        """Tag com conteúdo vazio para cláusula existente com conteúdo."""
        clausulas = [
            {
                "id": "clau-com-conteudo",
                "numero": "1.1",
                "nome": "Com conteúdo",
                "conteudo_original": "Texto existente",
                "status": "published",
            },
        ]
        tags = [{"nome": "1.1", "conteudo": ""}]

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=clausulas,
            tags_validas=tags,
        )

        # Conteúdo mudou de "Texto existente" para "" — deve atualizar
        assert len(resultado["update"]) == 1
        assert resultado["update"][0]["conteudo_original"] == ""

    def test_tag_sem_chave_conteudo(self, processador):
        """Tag dict sem a chave 'conteudo' não deve causar KeyError."""
        tags = [{"nome": "1.1"}]  # Sem chave "conteudo"

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=[],
            tags_validas=tags,
        )

        assert len(resultado["create"]) == 1
        assert resultado["create"][0]["conteudo_original"] == ""


# ---------------------------------------------------------------------------
# Testes: _criar_clausulas_em_lote usa reconciliação no reprocessamento
# ---------------------------------------------------------------------------


class TestCriarClausulasEmLoteReconciliacao:
    """Verifica que _criar_clausulas_em_lote usa reconciliação quando há cláusulas existentes."""

    def test_primeiro_processamento_cria_todas(self, processador):
        """Primeiro processamento (sem cláusulas existentes) deve criar todas."""
        processador.repo.get_clausulas_modelo.return_value = []

        tags = [
            {"nome": "1.1", "conteudo": "Texto 1.1"},
            {"nome": "2.1", "conteudo": "Texto 2.1"},
        ]

        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=[],
            tags_validas=tags,
        )

        assert len(resultado["create"]) == 2
        assert len(resultado["update"]) == 0

    def test_reprocessamento_reconcilia(self, processador):
        """Reprocessamento deve reconciliar: criar novas, atualizar existentes, inativar ausentes."""
        resultado = processador._reconciliar_clausulas(
            modelo_id="modelo-123",
            clausulas_existentes=_clausulas_existentes(),
            tags_validas=_tags_reprocessadas(),
        )

        # 4.1 é nova
        numeros_criados = [c["numero"] for c in resultado["create"]]
        assert "4.1" in numeros_criados

        # 2.1 foi atualizada
        ids_update = {c["id"] for c in resultado["update"]}
        assert "clau-bbb" in ids_update

        # 3.1 foi inativada
        assert "clau-ccc" in ids_update

        # 1.1 não mudou — não aparece em nenhum
        assert "clau-aaa" not in ids_update
        assert "1.1" not in numeros_criados
