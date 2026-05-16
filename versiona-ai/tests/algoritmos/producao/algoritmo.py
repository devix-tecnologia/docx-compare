"""
Adapter do algoritmo de produção (directus_server.py) para interface comum.

Este algoritmo serve como BASELINE para comparação com novas estratégias.
"""

import sys
from pathlib import Path

# Adicionar paths necessários
tests_dir = Path(__file__).parent.parent.parent
versiona_dir = tests_dir.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))
if str(versiona_dir) not in sys.path:
    sys.path.insert(0, str(versiona_dir))

from rapidfuzz import fuzz

from algoritmos.base import AlgoritmoVinculacao, UtilitariosVinculacao


class AlgoritmoProducao(AlgoritmoVinculacao):
    """
    Algoritmo atualmente em produção (directus_server.py) - ATUALIZADO.

    Estratégia:
    - Busca simples de texto com str.find()
    - Fuzzy matching com RapidFuzz (threshold dinâmico 80-90%)
    - Múltiplas métricas: ratio, partial_ratio, token_sort_ratio, token_set_ratio
    - Método baseado em conteúdo (não offset)
    
    Nota: Atualizado para usar RapidFuzz ao invés de difflib para melhor
    comparação de templates com placeholders vs. valores reais.
    """

    @property
    def nome(self) -> str:
        return "producao"

    @property
    def descricao(self) -> str:
        return "Algoritmo de produção atualizado (baseline) - busca simples + RapidFuzz com múltiplas métricas"

    def calcular_posicoes(self, modificacoes: list[dict], texto: str) -> list[dict]:
        """
        Implementação baseada em _calcular_posicoes_modificacoes() do directus_server.py
        """
        for mod in modificacoes:
            tipo = mod.get("tipo")
            texto_busca = UtilitariosVinculacao.extrair_texto_busca(mod)

            if not texto_busca:
                continue

            # Para INSERCAO/ALTERACAO: buscar no texto modificado
            if tipo in ["INSERCAO", "ALTERACAO"]:
                pos = texto.find(texto_busca)
                if pos != -1:
                    mod["posicao_inicio"] = pos
                    mod["posicao_fim"] = pos + len(texto_busca)

            # Para REMOCAO: não está no texto modificado
            # (algoritmo atual retorna None)

        return modificacoes

    def vincular_clausulas(
        self, modificacoes: list[dict], tags: list[dict], texto: str
    ) -> list[dict]:
        """
        Implementação baseada em _vincular_modificacoes_clausulas_novo() do directus_server.py

        Usa método de conteúdo com fuzzy matching.
        
        Atualizado para fazer fuzzy matching mesmo sem posição calculada
        (útil para comparar templates com valores reais).
        """
        # Primeiro calcular posições
        mods_com_posicao = self.calcular_posicoes(modificacoes, texto)
        
        for mod in mods_com_posicao:
            pos_inicio = mod.get("posicao_inicio")
            pos_fim = mod.get("posicao_fim")

            # Extrair texto da modificação
            texto_modificacao = UtilitariosVinculacao.extrair_texto_busca(mod)
            if not texto_modificacao:
                mod["tag_vinculada"] = None
                continue

            # Se TEM posição: buscar por overlap + fuzzy
            if pos_inicio is not None and pos_fim is not None:
                melhor_tag = self._buscar_melhor_tag_fuzzy(
                    texto_modificacao, pos_inicio, pos_fim, tags
                )
                mod["tag_vinculada"] = melhor_tag
            else:
                # Se NÃO TEM posição: usar APENAS fuzzy matching
                # (útil para templates vs valores reais)
                melhor_tag = self._buscar_melhor_tag_apenas_fuzzy(
                    texto_modificacao, tags
                )
                mod["tag_vinculada"] = melhor_tag

        return mods_com_posicao

    def _calcular_threshold_dinamico(self, texto: str) -> float:
        """
        Calcula threshold dinâmico baseado no tamanho do texto.
        
        Textos curtos precisam de threshold mais alto para evitar falsos positivos.
        
        Args:
            texto: Texto para análise
            
        Returns:
            Threshold entre 0 e 100
        """
        tamanho = len(texto)
        
        if tamanho < 20:
            return 90.0  # Muito curto: alta precisão
        elif tamanho < 100:
            return 85.0  # Médio: balanceado
        else:
            return 80.0  # Longo: mais flexível

    def _calcular_score_composto(self, texto1: str, texto2: str) -> float:
        """
        Calcula score usando múltiplas métricas do RapidFuzz e retorna o máximo.
        
        Usa 4 métricas:
        - ratio: Similaridade caractere por caractere
        - partial_ratio: Melhor substring
        - token_sort_ratio: Tokens ordenados
        - token_set_ratio: Conjunto de tokens (ignora duplicatas e ordem)
        
        Args:
            texto1: Primeiro texto
            texto2: Segundo texto
            
        Returns:
            Score entre 0 e 100
        """
        if not texto1 or not texto2:
            return 0.0
        
        # Calcular múltiplas métricas
        scores = [
            fuzz.ratio(texto1, texto2),
            fuzz.partial_ratio(texto1, texto2),
            fuzz.token_sort_ratio(texto1, texto2),
            fuzz.token_set_ratio(texto1, texto2)  # Melhor para templates vs valores
        ]
        
        # Retornar o melhor score
        return max(scores)

    def _buscar_melhor_tag_apenas_fuzzy(
        self,
        texto_modificacao: str,
        tags: list[dict],
    ) -> dict | None:
        """
        Busca melhor tag usando APENAS fuzzy matching (sem overlap de posição).
        
        Útil quando a modificação não foi encontrada no texto (ex: template vs valores).
        
        Args:
            texto_modificacao: Texto da modificação
            tags: Lista de tags disponíveis
            
        Returns:
            Tag com melhor score acima do threshold, ou None
        """
        melhor_tag = None
        melhor_score = 0.0
        threshold = self._calcular_threshold_dinamico(texto_modificacao)

        for tag in tags:
            tag_texto = tag.get("texto", "")
            
            if not tag_texto:
                continue

            # Checar substring primeiro
            if texto_modificacao in tag_texto:
                return tag  # Match perfeito
            
            # Calcular score composto
            score = self._calcular_score_composto(texto_modificacao, tag_texto)

            if score > melhor_score and score >= threshold:
                melhor_score = score
                melhor_tag = tag

        return melhor_tag

    def _buscar_melhor_tag_fuzzy(
        self,
        texto_modificacao: str,
        pos_inicio: int,
        pos_fim: int,
        tags: list[dict],
    ) -> dict | None:
        """
        Busca melhor tag usando fuzzy matching (threshold dinâmico) E validação de overlap.

        Baseado em _vincular_modificacoes_clausulas_novo() do directus_server.py
        Atualizado para usar RapidFuzz com múltiplas métricas.
        
        CORREÇÃO CRÍTICA:
        - Fuzzy matching tem PRIORIDADE sobre overlap
        - Overlap só é usado se passar em validação fuzzy também
        - Evita falsos positivos quando posições são de referências diferentes
        """
        melhor_tag = None
        melhor_score = 0.0
        threshold = self._calcular_threshold_dinamico(texto_modificacao)

        for tag in tags:
            tag_texto = tag.get("texto", "")
            tag_inicio = tag.get("posicao_inicio")
            tag_fim = tag.get("posicao_fim")

            # Método 1: Fuzzy matching de conteúdo com múltiplas métricas
            # Checar se a modificação está DENTRO do texto da tag
            if tag_texto and texto_modificacao in tag_texto:
                # Se texto modificação é substring, é match perfeito
                melhor_tag = tag
                melhor_score = 100.0
                break
            elif tag_texto:
                # Usar score composto com múltiplas métricas
                similarity = self._calcular_score_composto(texto_modificacao, tag_texto)

                if similarity > melhor_score:
                    melhor_score = similarity
                    if similarity >= threshold:
                        melhor_tag = tag

            # Método 2: Overlap de posição (fallback COM VALIDAÇÃO)
            # CRÍTICO: Só usa overlap se fuzzy também validar!
            if tag_inicio is not None and tag_fim is not None:
                overlap = UtilitariosVinculacao.calcular_overlap(
                    pos_inicio, pos_fim, tag_inicio, tag_fim
                )

                # Overlap significativo (>50%) E fuzzy não encontrou melhor
                if overlap > 0.5 and melhor_score < threshold:
                    # VALIDAÇÃO: Calcular fuzzy do overlap também
                    # Evita vincular quando posições são de referências diferentes
                    if tag_texto:
                        overlap_score = self._calcular_score_composto(texto_modificacao, tag_texto)
                        
                        # Só aceita overlap se fuzzy também for razoável (>= threshold)
                        # Se fuzzy é muito baixo, overlap é falso positivo
                        if overlap_score >= threshold:
                            melhor_tag = tag
                            melhor_score = overlap_score
                        # else: overlap falso - ignora
                    else:
                        # Tag sem texto: usa overlap sem validação (fallback)
                        melhor_tag = tag
                        melhor_score = overlap * 100

        return melhor_tag


# Para importação direta
__all__ = ["AlgoritmoProducao"]
