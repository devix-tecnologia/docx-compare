"""
Algoritmo de vinculação baseado em expressões regulares.

Detecta padrões estruturados comuns em contratos brasileiros:
- Valores monetários (R$)
- Datas (dd/mm/yyyy)
- Percentuais
- Prazos em dias
- IDs de contratos
- CPF/CNPJ
- CEP

Estratégia: Regex para padrões estruturados + fallback fuzzy para texto livre.
"""

import re
from typing import Dict, Pattern, Optional, List, Tuple
from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao


class AlgoritmoRegex(AlgoritmoVinculacao):
    """
    Algoritmo de vinculação usando expressões regulares para padrões estruturados.
    
    Vantagens:
    - Extremamente rápido (< 10ms)
    - Precisão de 100% quando padrão match
    - Determinístico e sem ambiguidade
    
    Limitações:
    - Não lida com texto livre/não estruturado
    - Fraco para sinônimos/paráfrases
    - Precisa conhecer padrões a priori
    """
    
    # Padrões estruturados para contratos brasileiros
    PADROES_ESTRUTURADOS: Dict[str, Pattern] = {
        "monetario_br": re.compile(
            r'R\$\s*[\d.,]+',
            re.IGNORECASE
        ),
        "data_br": re.compile(
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        ),
        "percentual": re.compile(
            r'\b\d+[,.]?\d*\s*%'
        ),
        "prazo_dias": re.compile(
            r'\b\d+\s+dias?\b',
            re.IGNORECASE
        ),
        "contrato_id": re.compile(
            r'\b\d{4,}\b'
        ),
        "cpf": re.compile(
            r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'
        ),
        "cnpj": re.compile(
            r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b'
        ),
        "cep": re.compile(
            r'\b\d{5}-\d{3}\b'
        ),
    }
    
    @property
    def nome(self) -> str:
        return "regex"
    
    @property
    def descricao(self) -> str:
        return "Vinculação baseada em expressões regulares para padrões estruturados"
    
    def __init__(self):
        self._cache_deteccao = {}
    
    def calcular_posicoes(self, modificacoes: List[dict], texto_completo: str) -> List[dict]:
        """
        Calcula posições das modificações no texto usando regex.
        
        Para cada modificação:
        1. Extrai texto de busca
        2. Detecta tipo de padrão estruturado
        3. Busca usando regex apropriada
        4. Retorna posicao_inicio, posicao_fim, _regex_pattern
        
        Args:
            modificacoes: Lista de modificações com conteudo_anterior/novo
            texto_completo: Texto completo do contrato
            
        Returns:
            Lista de modificações com posições calculadas
        """
        resultado = []
        
        for mod in modificacoes:
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
            
            if not texto_busca:
                resultado.append({
                    **mod,
                    "posicao_inicio": None,
                    "posicao_fim": None,
                    "_regex_pattern": None,
                })
                continue
            
            # Detectar tipo de padrão estruturado
            padrao_tipo = self._detectar_tipo_padrao(texto_busca)
            
            if padrao_tipo:
                # Buscar usando regex
                pos = self._buscar_com_regex(texto_busca, texto_completo, padrao_tipo)
                
                if pos:
                    resultado.append({
                        **mod,
                        "posicao_inicio": pos[0],
                        "posicao_fim": pos[1],
                        "_regex_pattern": padrao_tipo,
                    })
                else:
                    # Regex detectou padrão mas não encontrou no texto
                    # Tentar busca literal como fallback
                    pos_literal = texto_completo.find(texto_busca)
                    if pos_literal >= 0:
                        resultado.append({
                            **mod,
                            "posicao_inicio": pos_literal,
                            "posicao_fim": pos_literal + len(texto_busca),
                            "_regex_pattern": f"{padrao_tipo}_literal",
                        })
                    else:
                        resultado.append({
                            **mod,
                            "posicao_inicio": None,
                            "posicao_fim": None,
                            "_regex_pattern": None,
                        })
            else:
                # Sem padrão estruturado: busca literal
                pos_literal = texto_completo.find(texto_busca)
                if pos_literal >= 0:
                    resultado.append({
                        **mod,
                        "posicao_inicio": pos_literal,
                        "posicao_fim": pos_literal + len(texto_busca),
                        "_regex_pattern": "literal",
                    })
                else:
                    resultado.append({
                        **mod,
                        "posicao_inicio": None,
                        "posicao_fim": None,
                        "_regex_pattern": None,
                    })
        
        return resultado
    
    def vincular_clausulas(
        self, 
        modificacoes: List[dict], 
        tags: List[dict], 
        texto_completo: str
    ) -> List[dict]:
        """
        Vincula modificações às tags usando posições calculadas.
        
        Estratégia:
        1. Calcula posições com regex
        2. Busca tag por overlap de posição
        3. Se falhar, tenta fallback fuzzy
        
        Args:
            modificacoes: Lista de modificações
            tags: Lista de tags (cláusulas) com posições
            texto_completo: Texto completo do contrato
            
        Returns:
            Lista de modificações com tag_vinculada (objeto completo)
        """
        # Primeiro calcular posições
        mods_com_posicao = self.calcular_posicoes(modificacoes, texto_completo)
        
        resultado = []
        
        for mod in mods_com_posicao:
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")
            
            if pos_inicio is None or pos_fim is None:
                # Não encontrou posição: tentar fallback fuzzy
                tag = self._fallback_fuzzy(mod, tags)
                resultado.append({
                    **mod,
                    "tag_vinculada": tag,
                    "_metodo_vinculacao": "fuzzy_fallback" if tag else "nao_vinculada",
                })
                continue
            
            # Buscar tag por overlap de posição
            tag = UtilitariosVinculacao.buscar_tag_por_posicao(
                pos_inicio, pos_fim, tags
            )
            
            if tag:
                resultado.append({
                    **mod,
                    "tag_vinculada": tag,
                    "_metodo_vinculacao": "regex_overlap",
                })
            else:
                # Não achou por posição: tentar por estrutura similar
                padrao_tipo = mod.get("_regex_pattern")
                if padrao_tipo and padrao_tipo != "literal":
                    tag = self._buscar_tag_por_estrutura(mod, tags, padrao_tipo)
                
                if not tag:
                    # Último recurso: fallback fuzzy
                    tag = self._fallback_fuzzy(mod, tags)
                
                resultado.append({
                    **mod,
                    "tag_vinculada": tag,
                    "_metodo_vinculacao": (
                        "regex_estrutura" if tag and padrao_tipo != "literal"
                        else "fuzzy_fallback" if tag
                        else "nao_vinculada"
                    ),
                })
        
        return resultado
    
    def _detectar_tipo_padrao(self, texto: str) -> Optional[str]:
        """
        Detecta qual padrão estruturado o texto contém.
        
        Testa cada regex e retorna o nome do primeiro padrão que match.
        Usa cache para otimizar buscas repetidas.
        
        Args:
            texto: Texto a analisar
            
        Returns:
            Nome do padrão (chave de PADROES_ESTRUTURADOS) ou None
        """
        if texto in self._cache_deteccao:
            return self._cache_deteccao[texto]
        
        # Ordem de prioridade (mais específicos primeiro)
        ordem_prioridade = [
            "cnpj",      # Mais específico que contrato_id
            "cpf",       # Mais específico que contrato_id
            "cep",       # Mais específico que contrato_id
            "monetario_br",
            "data_br",
            "percentual",
            "prazo_dias",
            "contrato_id",  # Mais genérico (apenas números)
        ]
        
        for nome in ordem_prioridade:
            padrao = self.PADROES_ESTRUTURADOS[nome]
            if padrao.search(texto):
                self._cache_deteccao[texto] = nome
                return nome
        
        self._cache_deteccao[texto] = None
        return None
    
    def _buscar_com_regex(
        self, 
        texto_busca: str, 
        texto_completo: str, 
        tipo_padrao: str
    ) -> Optional[Tuple[int, int]]:
        """
        Busca texto usando regex do tipo detectado.
        
        Extrai valor estruturado do texto de busca e procura no texto completo,
        usando normalização para comparar valores equivalentes.
        
        Args:
            texto_busca: Texto a buscar
            texto_completo: Texto onde buscar
            tipo_padrao: Tipo de padrão (chave de PADROES_ESTRUTURADOS)
            
        Returns:
            Tupla (inicio, fim) ou None se não encontrar
        """
        padrao = self.PADROES_ESTRUTURADOS[tipo_padrao]
        
        # Extrair valor estruturado do texto de busca
        match_busca = padrao.search(texto_busca)
        if not match_busca:
            return None
        
        valor_busca = match_busca.group(0)
        
        # Buscar todas as ocorrências no texto completo
        for match in padrao.finditer(texto_completo):
            valor_encontrado = match.group(0)
            
            # Comparar com normalização
            if self._valores_equivalentes(valor_busca, valor_encontrado, tipo_padrao):
                # Para ser mais preciso, verificar se contexto é similar
                contexto_busca = texto_busca.replace(valor_busca, "").strip()
                
                # Se não há contexto adicional, aceitar primeira ocorrência
                if not contexto_busca or len(contexto_busca) < 5:
                    return (match.start(), match.end())
                
                # Se há contexto, verificar se está próximo
                inicio = max(0, match.start() - 50)
                fim = min(len(texto_completo), match.end() + 50)
                contexto_encontrado = texto_completo[inicio:fim]
                
                # Busca fuzzy no contexto
                if contexto_busca.lower() in contexto_encontrado.lower():
                    return (match.start(), match.end())
        
        return None
    
    def _valores_equivalentes(self, val1: str, val2: str, tipo: str) -> bool:
        """
        Verifica se dois valores do mesmo tipo são equivalentes.
        
        Normaliza os valores conforme o tipo e compara.
        
        Args:
            val1: Primeiro valor
            val2: Segundo valor
            tipo: Tipo de padrão
            
        Returns:
            True se valores são equivalentes
        """
        # Normalizar
        v1 = val1.strip().lower()
        v2 = val2.strip().lower()
        
        # Comparação exata primeiro
        if v1 == v2:
            return True
        
        # Comparações específicas por tipo
        if tipo == "monetario_br":
            return self._comparar_valores_monetarios(v1, v2)
        elif tipo == "data_br":
            return self._comparar_datas(v1, v2)
        elif tipo == "percentual":
            return self._comparar_percentuais(v1, v2)
        elif tipo in ["prazo_dias", "contrato_id"]:
            return self._comparar_numeros(v1, v2)
        
        # Para CPF, CNPJ, CEP: comparação exata
        return v1 == v2
    
    def _comparar_valores_monetarios(self, v1: str, v2: str) -> bool:
        """Compara valores monetários normalizando formato."""
        def extrair_numero(v):
            # Remove R$, espaços, pontos de milhar
            v = re.sub(r'[rR]\$\s*', '', v)
            v = v.replace('.', '')  # Remove pontos de milhar
            v = v.replace(',', '.')  # Vírgula vira ponto decimal
            try:
                return float(v)
            except ValueError:
                return None
        
        n1 = extrair_numero(v1)
        n2 = extrair_numero(v2)
        
        if n1 is None or n2 is None:
            return False
        
        return abs(n1 - n2) < 0.01
    
    def _comparar_datas(self, v1: str, v2: str) -> bool:
        """Compara datas normalizando separadores."""
        # Normalizar separadores
        d1 = v1.replace('-', '/').replace('.', '/')
        d2 = v2.replace('-', '/').replace('.', '/')
        
        # Tentar normalizar anos de 2 dígitos
        partes1 = d1.split('/')
        partes2 = d2.split('/')
        
        if len(partes1) == 3 and len(partes2) == 3:
            # Normalizar ano
            if len(partes1[2]) == 2:
                partes1[2] = '20' + partes1[2] if int(partes1[2]) < 50 else '19' + partes1[2]
            if len(partes2[2]) == 2:
                partes2[2] = '20' + partes2[2] if int(partes2[2]) < 50 else '19' + partes2[2]
            
            return partes1 == partes2
        
        return d1 == d2
    
    def _comparar_percentuais(self, v1: str, v2: str) -> bool:
        """Compara percentuais extraindo valor numérico."""
        def extrair_numero(v):
            v = v.replace('%', '').strip()
            v = v.replace(',', '.')
            try:
                return float(v)
            except ValueError:
                return None
        
        n1 = extrair_numero(v1)
        n2 = extrair_numero(v2)
        
        if n1 is None or n2 is None:
            return False
        
        return abs(n1 - n2) < 0.001
    
    def _comparar_numeros(self, v1: str, v2: str) -> bool:
        """Compara números extraindo apenas dígitos."""
        try:
            n1_match = re.search(r'\d+', v1)
            n2_match = re.search(r'\d+', v2)
            
            if n1_match and n2_match:
                return int(n1_match.group()) == int(n2_match.group())
            
            return False
        except (ValueError, AttributeError):
            return False
    
    def _buscar_tag_por_estrutura(
        self, 
        mod: dict, 
        tags: List[dict], 
        tipo_padrao: str
    ) -> Optional[dict]:
        """
        Busca tag que contenha estrutura similar ao padrão.
        
        Útil quando a modificação tem padrão estruturado mas não foi
        encontrada por posição exata.
        
        Args:
            mod: Modificação com _regex_pattern
            tags: Lista de tags
            tipo_padrao: Tipo de padrão regex
            
        Returns:
            Tag encontrada ou None
        """
        if tipo_padrao.endswith("_literal"):
            tipo_padrao = tipo_padrao.replace("_literal", "")
        
        if tipo_padrao not in self.PADROES_ESTRUTURADOS:
            return None
        
        padrao = self.PADROES_ESTRUTURADOS[tipo_padrao]
        texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
        
        # Extrair valor da modificação
        match_mod = padrao.search(texto_busca)
        if not match_mod:
            return None
        
        valor_mod = match_mod.group(0)
        
        # Buscar em tags
        for tag in tags:
            tag_texto = tag.get("texto", "")
            
            for match_tag in padrao.finditer(tag_texto):
                valor_tag = match_tag.group(0)
                
                if self._valores_equivalentes(valor_mod, valor_tag, tipo_padrao):
                    return tag
        
        return None
    
    def _fallback_fuzzy(self, mod: dict, tags: List[dict]) -> Optional[dict]:
        """
        Fallback para busca fuzzy quando regex falha.
        
        Usa normalização de texto e busca por substring.
        
        Args:
            mod: Modificação
            tags: Lista de tags
            
        Returns:
            Tag encontrada ou None
        """
        texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)
        if not texto_busca or len(texto_busca) < 5:
            return None
        
        texto_norm = UtilitariosVinculacao.normalizar_texto(texto_busca)
        
        # Buscar substring normalizada
        melhor_tag = None
        melhor_score = 0.0
        
        for tag in tags:
            tag_texto = tag.get("texto", "")
            tag_norm = UtilitariosVinculacao.normalizar_texto(tag_texto)
            
            # Verificar substring
            if texto_norm in tag_norm:
                # Score baseado em proporção de match
                score = len(texto_norm) / len(tag_norm)
                if score > melhor_score:
                    melhor_score = score
                    melhor_tag = tag
        
        # Exigir pelo menos 20% de match para considerar válido
        return melhor_tag if melhor_score >= 0.20 else None
