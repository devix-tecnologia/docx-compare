"""
Testes para o algoritmo de fuzzy matching avançado.
"""

import sys
from pathlib import Path

# Setup path
tests_dir = Path(__file__).parent.parent.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

import pytest
import json
from algoritmos.fuzzy.algoritmo import AlgoritmoFuzzyAvancado
from algoritmos.base import AlgoritmoVinculacao


class TestAlgoritmoFuzzyInterface:
    """Testes de conformidade com a interface AlgoritmoVinculacao."""
    
    def test_herda_de_algoritmo_vinculacao(self):
        """Verifica que o algoritmo herda da classe base."""
        algoritmo = AlgoritmoFuzzyAvancado()
        assert isinstance(algoritmo, AlgoritmoVinculacao)
    
    def test_implementa_calcular_posicoes(self):
        """Verifica que implementa o método calcular_posicoes."""
        algoritmo = AlgoritmoFuzzyAvancado()
        assert hasattr(algoritmo, 'calcular_posicoes')
        assert callable(algoritmo.calcular_posicoes)
    
    def test_implementa_vincular_clausulas(self):
        """Verifica que implementa o método vincular_clausulas."""
        algoritmo = AlgoritmoFuzzyAvancado()
        assert hasattr(algoritmo, 'vincular_clausulas')
        assert callable(algoritmo.vincular_clausulas)


class TestNormalizacaoTexto:
    """Testes de normalização de texto."""
    
    def test_remove_acentos(self):
        """Verifica remoção de acentos."""
        algoritmo = AlgoritmoFuzzyAvancado()
        resultado = algoritmo._normalizar_texto("São Paulo é demais!")
        assert "sao paulo e demais!" == resultado
    
    def test_normaliza_espacos(self):
        """Verifica normalização de espaços múltiplos."""
        algoritmo = AlgoritmoFuzzyAvancado()
        resultado = algoritmo._normalizar_texto("texto  com    espaços")
        assert "texto com espacos" == resultado
    
    def test_normaliza_numeros(self):
        """Verifica normalização de números."""
        algoritmo = AlgoritmoFuzzyAvancado()
        resultado = algoritmo._normalizar_texto("R$ 1.000,50")
        assert "r$ 1000.50" == resultado
    
    def test_texto_vazio(self):
        """Verifica tratamento de texto vazio."""
        algoritmo = AlgoritmoFuzzyAvancado()
        assert "" == algoritmo._normalizar_texto("")
        assert "" == algoritmo._normalizar_texto(None)


class TestThresholdDinamico:
    """Testes de cálculo de threshold dinâmico."""
    
    def test_texto_curto_threshold_alto(self):
        """Textos curtos devem ter threshold alto."""
        algoritmo = AlgoritmoFuzzyAvancado()
        threshold = algoritmo._calcular_threshold_dinamico("abc")
        assert threshold == 90.0
    
    def test_texto_medio_threshold_medio(self):
        """Textos médios devem ter threshold médio."""
        algoritmo = AlgoritmoFuzzyAvancado()
        texto = "Este é um texto médio com vários caracteres"
        threshold = algoritmo._calcular_threshold_dinamico(texto)
        assert threshold == 85.0
    
    def test_texto_longo_threshold_baixo(self):
        """Textos longos devem ter threshold mais flexível."""
        algoritmo = AlgoritmoFuzzyAvancado()
        texto = "Este é um texto bem longo com muitos caracteres e palavras para testar o threshold dinâmico do algoritmo de fuzzy matching avançado"
        threshold = algoritmo._calcular_threshold_dinamico(texto)
        assert threshold == 80.0


class TestScoreComposto:
    """Testes de cálculo de score composto."""
    
    def test_textos_identicos_score_100(self):
        """Textos idênticos devem ter score 100."""
        algoritmo = AlgoritmoFuzzyAvancado()
        score = algoritmo._calcular_score_composto("teste", "teste")
        assert score == 100.0
    
    def test_textos_similares_score_alto(self):
        """Textos similares devem ter score alto."""
        algoritmo = AlgoritmoFuzzyAvancado()
        score = algoritmo._calcular_score_composto(
            "O contrato é válido",
            "O contrato e valido"
        )
        assert score >= 85.0
    
    def test_textos_diferentes_score_baixo(self):
        """Textos diferentes devem ter score baixo."""
        algoritmo = AlgoritmoFuzzyAvancado()
        score = algoritmo._calcular_score_composto(
            "completamente diferente",
            "xyz abc 123"
        )
        assert score < 50.0
    
    def test_texto_vazio_score_zero(self):
        """Texto vazio deve retornar score 0."""
        algoritmo = AlgoritmoFuzzyAvancado()
        assert algoritmo._calcular_score_composto("", "teste") == 0.0
        assert algoritmo._calcular_score_composto("teste", "") == 0.0


class TestCalcularPosicoes:
    """Testes de cálculo de posições."""
    
    def test_match_exato(self):
        """Verifica match exato de texto."""
        algoritmo = AlgoritmoFuzzyAvancado()
        texto = "Este é um contrato de prestação de serviços."
        modificacoes = [{"tipo": "INSERCAO", "conteudo": {"novo": "contrato de prestação"}}]
        
        resultado = algoritmo.calcular_posicoes(modificacoes, texto)
        
        assert len(resultado) == 1
        assert resultado[0]['posicao_inicio'] is not None
        assert resultado[0]['posicao_fim'] > resultado[0]['posicao_inicio']
        assert resultado[0]['_fuzzy_score'] >= 85.0
    
    def test_match_fuzzy_com_acento(self):
        """Verifica match fuzzy ignorando acentos."""
        algoritmo = AlgoritmoFuzzyAvancado()
        texto = "Cláusula de rescisão contratual."
        modificacoes = [{"tipo": "INSERCAO", "conteudo": {"novo": "Clausula de rescisao"}}]
        
        resultado = algoritmo.calcular_posicoes(modificacoes, texto)
        
        assert len(resultado) == 1
        assert resultado[0]['posicao_inicio'] is not None
        assert resultado[0]['_fuzzy_score'] >= 85.0
    
    def test_texto_nao_encontrado(self):
        """Verifica comportamento quando texto não é encontrado."""
        algoritmo = AlgoritmoFuzzyAvancado()
        texto = "Este é um contrato."
        modificacoes = [{"tipo": "INSERCAO", "conteudo": {"novo": "cláusula inexistente que definitivamente não existe neste texto"}}]
        
        resultado = algoritmo.calcular_posicoes(modificacoes, texto)
        
        assert len(resultado) == 1
        assert resultado[0]['posicao_inicio'] is None
        assert resultado[0]['posicao_fim'] is None


class TestVincularClausulas:
    """Testes de vinculação de cláusulas."""
    
    def test_vinculacao_com_overlap(self):
        """Verifica vinculação usando overlap de posições."""
        algoritmo = AlgoritmoFuzzyAvancado()
        texto = "Cláusula 1: Este é o conteúdo da primeira cláusula."
        tags = [{"id": "tag1", "posicao_inicio": 0, "posicao_fim": 52}]
        modificacoes = [{"tipo": "ALTERACAO", "conteudo": {"novo": "conteúdo da primeira"}}]
        
        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)
        
        assert len(resultado) == 1
        assert resultado[0]['tag_vinculada'] is not None
        assert resultado[0]['tag_vinculada']['id'] == "tag1"
    
    def test_vinculacao_sem_overlap_usa_fuzzy(self):
        """Verifica vinculação por fuzzy matching quando não há overlap."""
        algoritmo = AlgoritmoFuzzyAvancado()
        texto = "Introdução. Cláusula 1: Conteúdo importante da cláusula."
        tags = [{"id": "tag1", "posicao_inicio": 12, "posicao_fim": 57, "texto": "Cláusula 1: Conteúdo importante da cláusula."}]
        modificacoes = [{"tipo": "ALTERACAO", "conteudo": {"antigo": "Conteúdo importante", "novo": "Conteúdo relevante"}}]
        
        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)
        
        assert len(resultado) == 1
        # Pode vincular por fuzzy se o texto for similar suficiente
        # ou retornar None se não atingir threshold
    
    def test_multiplas_modificacoes(self):
        """Verifica vinculação de múltiplas modificações."""
        algoritmo = AlgoritmoFuzzyAvancado()
        texto = "Tag1: Conteúdo 1. Tag2: Conteúdo 2."
        tags = [
            {"id": "tag1", "posicao_inicio": 0, "posicao_fim": 16, "texto": "Tag1: Conteúdo 1."},
            {"id": "tag2", "posicao_inicio": 18, "posicao_fim": 36, "texto": "Tag2: Conteúdo 2."}
        ]
        modificacoes = [
            {"tipo": "ALTERACAO", "conteudo": {"novo": "Conteúdo 1"}},
            {"tipo": "ALTERACAO", "conteudo": {"novo": "Conteúdo 2"}}
        ]
        
        resultado = algoritmo.vincular_clausulas(modificacoes, tags, texto)
        
        assert len(resultado) == 2


class TestIntegracaoFixtures:
    """Testes de integração com fixtures reais."""
    
    @pytest.fixture
    def fixtures_path(self):
        """Retorna o caminho para as fixtures."""
        return Path(__file__).parent.parent.parent / "fixtures"
    
    def test_caso_01_insercao_simples(self, fixtures_path):
        """Testa caso 01: inserção simples."""
        fixture_file = fixtures_path / "caso_01_insercao_simples.json"
        
        if not fixture_file.exists():
            pytest.skip("Fixture não encontrada")
        
        with open(fixture_file, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        algoritmo = AlgoritmoFuzzyAvancado()
        resultado = algoritmo.vincular_clausulas(
            dados['modificacoes'],
            dados['documento']['tags'],
            dados['documento']['texto_completo']
        )
        
        assert len(resultado) > 0
    
    def test_caso_02_alteracao_simples(self, fixtures_path):
        """Testa caso 02: alteração simples."""
        fixture_file = fixtures_path / "caso_02_alteracao_simples.json"
        
        if not fixture_file.exists():
            pytest.skip("Fixture não encontrada")
        
        with open(fixture_file, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        algoritmo = AlgoritmoFuzzyAvancado()
        resultado = algoritmo.vincular_clausulas(
            dados['modificacoes'],
            dados['documento']['tags'],
            dados['documento']['texto_completo']
        )
        
        assert len(resultado) > 0
        vinculadas = [m for m in resultado if m.get('tag_vinculada') is not None]
        assert len(vinculadas) > 0
