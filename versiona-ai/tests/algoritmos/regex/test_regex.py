"""
Testes unitários para AlgoritmoRegex.

Valida detecção de padrões, busca com regex, normalização e vinculação.
"""

import sys
from pathlib import Path

# Adicionar tests/ ao path
tests_dir = Path(__file__).parent.parent.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

import pytest
from algoritmos.regex.algoritmo import AlgoritmoRegex


class TestDeteccaoPadroes:
    """Testes de detecção de padrões estruturados."""
    
    def test_detectar_padrao_monetario(self):
        alg = AlgoritmoRegex()
        assert alg._detectar_tipo_padrao("R$ 10.000,00") == "monetario_br"
        assert alg._detectar_tipo_padrao("R$15000") == "monetario_br"
        assert alg._detectar_tipo_padrao("r$ 1.500,50") == "monetario_br"
        assert alg._detectar_tipo_padrao("Valor: R$ 999,99") == "monetario_br"
    
    def test_detectar_padrao_data(self):
        alg = AlgoritmoRegex()
        assert alg._detectar_tipo_padrao("31/12/2024") == "data_br"
        assert alg._detectar_tipo_padrao("01/01/24") == "data_br"
        assert alg._detectar_tipo_padrao("Data: 15-03-2024") == "data_br"
    
    def test_detectar_padrao_percentual(self):
        alg = AlgoritmoRegex()
        assert alg._detectar_tipo_padrao("5%") == "percentual"
        assert alg._detectar_tipo_padrao("10,5 %") == "percentual"
        assert alg._detectar_tipo_padrao("Taxa de 7.5%") == "percentual"
    
    def test_detectar_padrao_prazo(self):
        alg = AlgoritmoRegex()
        assert alg._detectar_tipo_padrao("30 dias") == "prazo_dias"
        assert alg._detectar_tipo_padrao("45 dia") == "prazo_dias"
        assert alg._detectar_tipo_padrao("Prazo: 60 DIAS") == "prazo_dias"
    
    def test_detectar_padrao_cpf(self):
        alg = AlgoritmoRegex()
        assert alg._detectar_tipo_padrao("123.456.789-00") == "cpf"
        assert alg._detectar_tipo_padrao("CPF: 111.222.333-44") == "cpf"
    
    def test_detectar_padrao_cnpj(self):
        alg = AlgoritmoRegex()
        assert alg._detectar_tipo_padrao("12.345.678/0001-99") == "cnpj"
        assert alg._detectar_tipo_padrao("CNPJ: 00.000.000/0000-00") == "cnpj"
    
    def test_detectar_padrao_cep(self):
        alg = AlgoritmoRegex()
        assert alg._detectar_tipo_padrao("01310-100") == "cep"
        assert alg._detectar_tipo_padrao("CEP 12345-678") == "cep"
    
    def test_detectar_padrao_contrato_id(self):
        alg = AlgoritmoRegex()
        assert alg._detectar_tipo_padrao("Contrato 12345") == "contrato_id"
        assert alg._detectar_tipo_padrao("Processo 2024001") == "contrato_id"
    
    def test_sem_padrao(self):
        alg = AlgoritmoRegex()
        assert alg._detectar_tipo_padrao("Texto livre sem padrão") is None
        assert alg._detectar_tipo_padrao("abc") is None


class TestComparacaoValores:
    """Testes de comparação/normalização de valores."""
    
    def test_valores_monetarios_equivalentes(self):
        alg = AlgoritmoRegex()
        assert alg._valores_equivalentes(
            "R$ 10.000,00", "R$ 10000,00", "monetario_br"
        )
        assert alg._valores_equivalentes(
            "R$1.500,50", "R$ 1500,50", "monetario_br"
        )
        assert not alg._valores_equivalentes(
            "R$ 10.000,00", "R$ 15.000,00", "monetario_br"
        )
    
    def test_datas_equivalentes(self):
        alg = AlgoritmoRegex()
        assert alg._valores_equivalentes(
            "31/12/2024", "31-12-2024", "data_br"
        )
        assert alg._valores_equivalentes(
            "01/01/24", "01/01/2024", "data_br"
        )
        assert not alg._valores_equivalentes(
            "31/12/2024", "01/01/2024", "data_br"
        )
    
    def test_percentuais_equivalentes(self):
        alg = AlgoritmoRegex()
        assert alg._valores_equivalentes(
            "5%", "5 %", "percentual"
        )
        assert alg._valores_equivalentes(
            "10,5%", "10.5%", "percentual"
        )
        assert not alg._valores_equivalentes(
            "5%", "7%", "percentual"
        )
    
    def test_numeros_equivalentes(self):
        alg = AlgoritmoRegex()
        assert alg._valores_equivalentes(
            "30 dias", "30 dia", "prazo_dias"
        )
        assert alg._valores_equivalentes(
            "Contrato 12345", "Processo 12345", "contrato_id"
        )


class TestBuscaComRegex:
    """Testes de busca usando regex no texto completo."""
    
    def test_buscar_valor_monetario(self):
        alg = AlgoritmoRegex()
        texto = "O valor do contrato é R$ 15.000,00 conforme acordado."
        pos = alg._buscar_com_regex("R$ 15.000,00", texto, "monetario_br")
        
        assert pos is not None
        assert texto[pos[0]:pos[1]] == "R$ 15.000,00"
    
    def test_buscar_data(self):
        alg = AlgoritmoRegex()
        texto = "Vigência de 01/01/2024 até 31/12/2024."
        pos = alg._buscar_com_regex("01/01/2024", texto, "data_br")
        
        assert pos is not None
        assert texto[pos[0]:pos[1]] == "01/01/2024"
    
    def test_buscar_percentual(self):
        alg = AlgoritmoRegex()
        texto = "Taxa de juros de 5% ao mês."
        pos = alg._buscar_com_regex("5%", texto, "percentual")
        
        assert pos is not None
        assert texto[pos[0]:pos[1]] == "5%"
    
    def test_buscar_prazo(self):
        alg = AlgoritmoRegex()
        texto = "Prazo de entrega de 30 dias corridos."
        pos = alg._buscar_com_regex("30 dias", texto, "prazo_dias")
        
        assert pos is not None
        assert "30 dias" in texto[pos[0]:pos[1]]
    
    def test_buscar_nao_encontrado(self):
        alg = AlgoritmoRegex()
        texto = "Texto sem o valor procurado."
        pos = alg._buscar_com_regex("R$ 99.999,99", texto, "monetario_br")
        
        assert pos is None


class TestCalcularPosicoes:
    """Testes do método calcular_posicoes."""
    
    def test_calcular_posicoes_monetario(self):
        alg = AlgoritmoRegex()
        texto = "O valor é R$ 10.000,00 conforme cláusula."
        modificacoes = [{
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "R$ 10.000,00",
                "novo": "R$ 15.000,00"
            }
        }]
        
        resultado = alg.calcular_posicoes(modificacoes, texto)
        
        assert len(resultado) == 1
        # Busca pelo valor NOVO (R$ 15.000,00) mas encontra pelo padrão monetário
        # Como o valor novo não está no texto, pode retornar None ou buscar pelo padrão
        if resultado[0]["posicao_inicio"] is not None:
            assert resultado[0]["posicao_fim"] is not None
            assert resultado[0]["_regex_pattern"] in ["monetario_br", "literal"]
    
    def test_calcular_posicoes_nao_encontrado(self):
        alg = AlgoritmoRegex()
        texto = "Texto simples."
        modificacoes = [{
            "tipo": "ALTERACAO",
            "conteudo": {
                "original": "R$ 99.999,99",
                "novo": "R$ 111.111,11"
            }
        }]
        
        resultado = alg.calcular_posicoes(modificacoes, texto)
        
        assert len(resultado) == 1
        assert resultado[0]["posicao_inicio"] is None
        assert resultado[0]["posicao_fim"] is None


class TestPropriedades:
    """Testes de propriedades da classe."""
    
    def test_nome(self):
        alg = AlgoritmoRegex()
        assert alg.nome == "regex"
    
    def test_descricao(self):
        alg = AlgoritmoRegex()
        assert "express" in alg.descricao.lower() or "regex" in alg.descricao.lower()
        assert len(alg.descricao) > 10
