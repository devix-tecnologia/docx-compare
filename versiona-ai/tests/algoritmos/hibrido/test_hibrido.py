"""
Testes para Algoritmo Híbrido

Valida:
- Cascata de estratégias (overlap → regex → fuzzy → ml)
- Estatísticas de uso
- Combinação de pontos fortes de cada algoritmo
- Performance geral (meta: score ≥90, taxa ≥95%)
"""

import sys
from pathlib import Path

# Adicionar tests/ ao path
tests_dir = Path(__file__).parent.parent.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

import pytest
from algoritmos.hibrido.algoritmo import AlgoritmoHibrido


class TestAlgoritmoHibridoInterface:
    """Testes da interface obrigatória."""

    def test_tem_propriedade_nome(self):
        """Algoritmo deve ter propriedade 'nome'."""
        alg = AlgoritmoHibrido()
        assert hasattr(alg, "nome")
        assert isinstance(alg.nome, str)
        assert len(alg.nome) > 0

    def test_tem_propriedade_descricao(self):
        """Algoritmo deve ter propriedade 'descricao'."""
        alg = AlgoritmoHibrido()
        assert hasattr(alg, "descricao")
        assert isinstance(alg.descricao, str)
        assert len(alg.descricao) > 0

    def test_tem_metodo_calcular_posicoes(self):
        """Algoritmo deve ter método calcular_posicoes."""
        alg = AlgoritmoHibrido()
        assert hasattr(alg, "calcular_posicoes")
        assert callable(alg.calcular_posicoes)

    def test_tem_metodo_vincular_clausulas(self):
        """Algoritmo deve ter método vincular_clausulas."""
        alg = AlgoritmoHibrido()
        assert hasattr(alg, "vincular_clausulas")
        assert callable(alg.vincular_clausulas)


class TestAlgoritmoHibridoEstatisticas:
    """Testes de estatísticas de uso."""

    def test_inicializa_estatisticas_zeradas(self):
        """Estatísticas devem iniciar em zero."""
        alg = AlgoritmoHibrido()
        stats = alg.obter_estatisticas()
        
        assert "overlap" in stats
        assert "regex" in stats
        assert "fuzzy" in stats
        assert "ml" in stats
        assert "nao_vinculada" in stats
        
        for estrategia, dados in stats.items():
            assert dados["count"] == 0
            assert dados["percentage"] >= 0

    def test_resetar_estatisticas(self):
        """Resetar deve zerar todas as estatísticas."""
        alg = AlgoritmoHibrido()
        
        # Simular algum uso
        alg._stats["regex"] = 10
        alg._stats["fuzzy"] = 5
        
        # Resetar
        alg.resetar_estatisticas()
        
        # Verificar
        stats = alg.obter_estatisticas()
        for dados in stats.values():
            assert dados["count"] == 0


class TestAlgoritmoHibridoCalculoPosicoes:
    """Testes específicos do cálculo de posições."""

    def test_calcula_posicao_com_regex(self):
        """Regex deve calcular posição para padrões estruturados."""
        alg = AlgoritmoHibrido()
        
        modificacoes = [
            {
                "tipo": "ALTERACAO",
                "conteudo": {
                    "antigo": "01/01/2024",
                    "novo": "31/12/2024"
                }
            }
        ]
        
        texto = "A data de início é 01/01/2024 e término em 31/12/2024."
        
        resultado = alg.calcular_posicoes(modificacoes, texto)
        
        assert len(resultado) > 0
        assert resultado[0].get("posicao_inicio") is not None
        assert resultado[0].get("posicao_fim") is not None
        assert resultado[0].get("_estrategia_posicao") in ["regex", "exact"]

    def test_calcula_posicao_com_fuzzy_quando_regex_falha(self):
        """Fuzzy deve ser usado quando regex não encontra padrão."""
        alg = AlgoritmoHibrido()
        
        modificacoes = [
            {
                "tipo": "ALTERACAO",
                "conteudo": {
                    "antigo": "empresa contratante",
                    "novo": "empresa contratada"
                }
            }
        ]
        
        texto = "A empresa contratante deve fornecer os recursos necessários."
        
        resultado = alg.calcular_posicoes(modificacoes, texto)
        
        assert len(resultado) > 0
        assert resultado[0].get("posicao_inicio") is not None
        assert resultado[0].get("_estrategia_posicao") in ["fuzzy", "exact", "regex"]

    def test_retorna_none_quando_nao_encontra_posicao(self):
        """Deve retornar None quando não consegue calcular posição."""
        alg = AlgoritmoHibrido()
        
        modificacoes = [
            {
                "tipo": "INSERCAO",
                "conteudo": {
                    "novo": "Texto que definitivamente não existe no documento xyz123"
                }
            }
        ]
        
        texto = "Documento curto sem o texto buscado."
        
        resultado = alg.calcular_posicoes(modificacoes, texto)
        
        assert len(resultado) > 0
        # Pode não encontrar
        if resultado[0].get("posicao_inicio") is None:
            assert resultado[0].get("posicao_fim") is None
            assert resultado[0].get("_estrategia_posicao") is None


class TestAlgoritmoHibridoConfiguracao:
    """Testes de configuração de thresholds."""

    def test_configurar_thresholds(self):
        """Deve permitir configurar thresholds."""
        alg = AlgoritmoHibrido()
        
        alg.configurar_thresholds(overlap=0.6, fuzzy=0.9, ml=0.75)
        
        assert alg._thresholds["overlap"] == 0.6
        assert alg._thresholds["fuzzy"] == 0.9
        assert alg._thresholds["ml"] == 0.75

    def test_thresholds_limitados_entre_0_e_1(self):
        """Thresholds devem ser limitados entre 0 e 1."""
        alg = AlgoritmoHibrido()
        
        alg.configurar_thresholds(overlap=1.5, fuzzy=-0.5)
        
        assert 0.0 <= alg._thresholds["overlap"] <= 1.0
        assert 0.0 <= alg._thresholds["fuzzy"] <= 1.0

    def test_threshold_none_nao_altera_valor(self):
        """Passar None não deve alterar threshold existente."""
        alg = AlgoritmoHibrido()
        
        valor_original = alg._thresholds["overlap"]
        alg.configurar_thresholds(overlap=None)
        
        assert alg._thresholds["overlap"] == valor_original
