"""
Framework para Comparação de Algoritmos de Vinculação de Cláusulas

Permite testar diferentes estratégias de:
1. Cálculo de posições de modificações
2. Vinculação de modificações a cláusulas

Com métricas objetivas para comparação A/B.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Metricas:
    """Métricas de avaliação de um algoritmo em uma fixture"""

    taxa_vinculacao: float  # % de modificações vinculadas
    precisao: float  # % de vinculações corretas (de todas vinculadas)
    recall: float  # % de vinculações esperadas encontradas
    f1_score: float  # Média harmônica de precisão e recall
    erro_medio_posicao: float  # Média da diferença em caracteres
    tempo_execucao_ms: float  # Tempo de execução

    @property
    def score_geral(self) -> float:
        """Score geral combinando todas as métricas (0-100)"""
        # Peso: 40% F1, 30% taxa vinculação, 20% erro posição, 10% tempo
        peso_f1 = 0.4
        peso_taxa = 0.3
        peso_erro = 0.2  # Invertido: menor erro = melhor
        peso_tempo = 0.1  # Invertido: menor tempo = melhor

        # Normalizar erro de posição (max 50 chars = 0 pontos)
        erro_normalizado = max(0, 100 - (self.erro_medio_posicao / 50 * 100))

        # Normalizar tempo (max 1000ms = 0 pontos)
        tempo_normalizado = max(0, 100 - (self.tempo_execucao_ms / 1000 * 100))

        return (
            peso_f1 * self.f1_score
            + peso_taxa * self.taxa_vinculacao
            + peso_erro * erro_normalizado
            + peso_tempo * tempo_normalizado
        )

    def __str__(self) -> str:
        return (
            f"Taxa Vinculação: {self.taxa_vinculacao:.1f}% | "
            f"Precisão: {self.precisao:.1f}% | "
            f"Recall: {self.recall:.1f}% | "
            f"F1: {self.f1_score:.1f} | "
            f"Erro Pos: {self.erro_medio_posicao:.1f} chars | "
            f"Tempo: {self.tempo_execucao_ms:.1f}ms | "
            f"⭐ Score: {self.score_geral:.1f}"
        )


class AlgoritmoVinculacao(ABC):
    """Interface para algoritmos de vinculação de cláusulas"""

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome identificador do algoritmo"""
        pass

    @property
    @abstractmethod
    def descricao(self) -> str:
        """Descrição da estratégia do algoritmo"""
        pass

    @abstractmethod
    def calcular_posicoes(self, modificacoes: list[dict], texto: str) -> list[dict]:
        """
        Calcula posicao_inicio e posicao_fim para cada modificação.

        Args:
            modificacoes: Lista de modificações (tipo, conteudo)
            texto: Texto completo do documento

        Returns:
            Lista de modificações com posicao_inicio/posicao_fim preenchidos
        """
        pass

    @abstractmethod
    def vincular_clausulas(
        self, modificacoes: list[dict], tags: list[dict], texto: str
    ) -> list[dict]:
        """
        Vincula modificações às tags (cláusulas).

        Args:
            modificacoes: Lista de modificações COM posições
            tags: Lista de tags com posições
            texto: Texto completo do documento

        Returns:
            Lista de modificações com campo 'tag_vinculada' (dict ou None)
        """
        pass


class Fixture:
    """Carrega e valida fixtures de teste"""

    def __init__(self, path: Path):
        self.path = path
        with open(path) as f:
            self.data = json.load(f)

    @property
    def id(self) -> str:
        return self.data["id"]

    @property
    def descricao(self) -> str:
        return self.data["descricao"]

    @property
    def nivel_complexidade(self) -> str:
        return self.data["nivel_complexidade"]

    @property
    def texto_completo(self) -> str:
        return self.data["documento"]["texto_completo"]

    @property
    def tags(self) -> list[dict]:
        return self.data["documento"]["tags"]

    @property
    def modificacoes(self) -> list[dict]:
        return self.data["modificacoes"]

    @property
    def vinculacoes_esperadas(self) -> list[dict]:
        return self.data["vinculacoes_esperadas"]

    @property
    def metricas_objetivo(self) -> dict:
        return self.data["metricas_objetivo"]


class ComparadorAlgoritmos:
    """Avalia e compara algoritmos usando fixtures"""

    def __init__(self, fixtures_dir: Path = None):
        if fixtures_dir is None:
            fixtures_dir = Path(__file__).parent / "fixtures"
        self.fixtures_dir = fixtures_dir

    def carregar_fixtures(
        self, nivel: str = None, ids: list[str] = None
    ) -> list[Fixture]:
        """
        Carrega fixtures para teste.

        Args:
            nivel: Filtrar por nível ('simples', 'medio', 'complexo')
            ids: Filtrar por IDs específicos

        Returns:
            Lista de fixtures
        """
        fixtures = []
        for path in sorted(self.fixtures_dir.glob("caso_*.json")):
            fixture = Fixture(path)

            # Filtros
            if nivel and fixture.nivel_complexidade != nivel:
                continue
            if ids and fixture.id not in ids:
                continue

            fixtures.append(fixture)

        return fixtures

    def avaliar(self, algoritmo: AlgoritmoVinculacao, fixture: Fixture) -> Metricas:
        """
        Avalia um algoritmo em uma fixture.

        Returns:
            Métricas de performance
        """
        import time

        # 1. Calcular posições
        inicio = time.time()
        modificacoes_com_posicoes = algoritmo.calcular_posicoes(
            fixture.modificacoes.copy(), fixture.texto_completo
        )

        # 2. Vincular cláusulas
        modificacoes_vinculadas = algoritmo.vincular_clausulas(
            modificacoes_com_posicoes, fixture.tags, fixture.texto_completo
        )
        tempo_ms = (time.time() - inicio) * 1000

        # 3. Calcular métricas
        return self._calcular_metricas(
            modificacoes_vinculadas, fixture.vinculacoes_esperadas, tempo_ms
        )

    def _calcular_metricas(
        self,
        modificacoes_vinculadas: list[dict],
        vinculacoes_esperadas: list[dict],
        tempo_ms: float,
    ) -> Metricas:
        """Calcula métricas comparando resultado com ground truth"""

        total_modificacoes = len(modificacoes_vinculadas)
        total_esperadas = len(vinculacoes_esperadas)

        # Taxa de vinculação: % de modificações que foram vinculadas
        vinculadas = [m for m in modificacoes_vinculadas if m.get("tag_vinculada")]
        taxa_vinculacao = (
            len(vinculadas) / total_modificacoes * 100 if total_modificacoes > 0 else 0
        )

        # Criar mapa de vinculações esperadas
        esperadas_map = {v["modificacao_index"]: v for v in vinculacoes_esperadas}

        # Analisar cada vinculação
        true_positives = 0  # Vinculou corretamente
        false_positives = 0  # Vinculou errado
        false_negatives = 0  # Deveria vincular mas não vinculou

        erros_posicao = []

        for idx, mod in enumerate(modificacoes_vinculadas):
            esperada = esperadas_map.get(idx)
            vinculada = mod.get("tag_vinculada")

            if esperada:
                # Deveria estar vinculada
                if vinculada and vinculada["id"] == esperada["tag_id"]:
                    # ✅ Vinculou corretamente
                    true_positives += 1

                    # Calcular erro de posição (se disponível)
                    pos_inicio = mod.get("posicao_inicio")
                    pos_fim = mod.get("posicao_fim")

                    if pos_inicio is not None and pos_fim is not None:
                        erro_inicio = abs(
                            pos_inicio - esperada["posicao_inicio_esperada"]
                        )
                        erro_fim = abs(pos_fim - esperada["posicao_fim_esperada"])
                        erros_posicao.append((erro_inicio + erro_fim) / 2)
                elif vinculada:
                    # ❌ Vinculou mas para tag errada
                    false_positives += 1
                    false_negatives += 1
                else:
                    # ❌ Não vinculou quando deveria
                    false_negatives += 1
            else:
                # Não deveria estar vinculada
                if vinculada:
                    # ❌ Vinculou quando não deveria
                    false_positives += 1

        # Cálculo de métricas
        precisao = (
            true_positives / (true_positives + false_positives) * 100
            if (true_positives + false_positives) > 0
            else 0
        )
        recall = (
            true_positives / (true_positives + false_negatives) * 100
            if (true_positives + false_negatives) > 0
            else 0
        )
        f1_score = (
            2 * (precisao * recall) / (precisao + recall)
            if (precisao + recall) > 0
            else 0
        )
        erro_medio = sum(erros_posicao) / len(erros_posicao) if erros_posicao else 0

        return Metricas(
            taxa_vinculacao=taxa_vinculacao,
            precisao=precisao,
            recall=recall,
            f1_score=f1_score,
            erro_medio_posicao=erro_medio,
            tempo_execucao_ms=tempo_ms,
        )

    def comparar(
        self, algoritmos: list[AlgoritmoVinculacao], fixtures: list[Fixture] = None
    ) -> dict[str, dict[str, Metricas]]:
        """
        Compara múltiplos algoritmos em múltiplas fixtures.

        Returns:
            {algoritmo_nome: {fixture_id: Metricas}}
        """
        if fixtures is None:
            fixtures = self.carregar_fixtures()

        resultados = {}

        for algoritmo in algoritmos:
            resultados[algoritmo.nome] = {}
            for fixture in fixtures:
                print(
                    f"🔬 Testando {algoritmo.nome} em {fixture.id}... ",
                    end="",
                    flush=True,
                )
                metricas = self.avaliar(algoritmo, fixture)
                resultados[algoritmo.nome][fixture.id] = metricas
                print(f"✅ Score: {metricas.score_geral:.1f}")

        return resultados

    def gerar_relatorio(
        self, resultados: dict[str, dict[str, Metricas]], formato: str = "console"
    ):
        """
        Gera relatório comparativo.

        Args:
            resultados: Saída de comparar()
            formato: 'console', 'html', 'markdown'
        """
        if formato == "console":
            self._relatorio_console(resultados)
        elif formato == "markdown":
            return self._relatorio_markdown(resultados)
        elif formato == "html":
            return self._relatorio_html(resultados)

    def _relatorio_console(self, resultados: dict[str, dict[str, Metricas]]):
        """Imprime relatório no console"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO COMPARATIVO DE ALGORITMOS")
        print("=" * 80)

        # Calcular scores gerais
        scores_gerais = {}
        for alg_nome, fixtures_metricas in resultados.items():
            scores = [m.score_geral for m in fixtures_metricas.values()]
            scores_gerais[alg_nome] = sum(scores) / len(scores) if scores else 0

        # Ordenar por score
        ranking = sorted(scores_gerais.items(), key=lambda x: x[1], reverse=True)

        print("\n🏆 RANKING GERAL:")
        for pos, (alg_nome, score) in enumerate(ranking, 1):
            emoji = (
                "🥇" if pos == 1 else "🥈" if pos == 2 else "🥉" if pos == 3 else "  "
            )
            print(f"{emoji} {pos}. {alg_nome}: {score:.1f} pontos")

        print("\n📋 DETALHAMENTO POR FIXTURE:")
        for fixture_id in sorted(
            set(fid for metricas in resultados.values() for fid in metricas.keys())
        ):
            print(f"\n  {fixture_id}:")
            for alg_nome in ranking:
                alg_nome = alg_nome[0]  # tupla (nome, score)
                if fixture_id in resultados[alg_nome]:
                    metricas = resultados[alg_nome][fixture_id]
                    print(f"    {alg_nome}: {metricas}")

    def _relatorio_markdown(self, resultados: dict[str, dict[str, Metricas]]) -> str:
        """Gera relatório em Markdown"""
        md = ["# Relatório Comparativo de Algoritmos", ""]

        # Ranking
        scores_gerais = {}
        for alg_nome, fixtures_metricas in resultados.items():
            scores = [m.score_geral for m in fixtures_metricas.values()]
            scores_gerais[alg_nome] = sum(scores) / len(scores) if scores else 0

        ranking = sorted(scores_gerais.items(), key=lambda x: x[1], reverse=True)

        md.append("## 🏆 Ranking Geral")
        md.append("")
        md.append("| Posição | Algoritmo | Score |")
        md.append("|---------|-----------|-------|")
        for pos, (alg_nome, score) in enumerate(ranking, 1):
            emoji = "🥇" if pos == 1 else "🥈" if pos == 2 else "🥉"
            md.append(f"| {emoji} {pos} | {alg_nome} | {score:.1f} |")

        # Detalhes
        md.append("")
        md.append("## 📊 Métricas Detalhadas")
        md.append("")

        for fixture_id in sorted(
            set(fid for metricas in resultados.values() for fid in metricas.keys())
        ):
            md.append(f"### {fixture_id}")
            md.append("")
            md.append(
                "| Algoritmo | Taxa Vinc | Precisão | Recall | F1 | Erro Pos | Tempo | Score |"
            )
            md.append(
                "|-----------|-----------|----------|--------|----|-----------|---------|----|"
            )

            for alg_nome, _ in ranking:
                if fixture_id in resultados[alg_nome]:
                    m = resultados[alg_nome][fixture_id]
                    md.append(
                        f"| {alg_nome} | {m.taxa_vinculacao:.1f}% | "
                        f"{m.precisao:.1f}% | {m.recall:.1f}% | {m.f1_score:.1f} | "
                        f"{m.erro_medio_posicao:.1f} | {m.tempo_execucao_ms:.1f}ms | "
                        f"{m.score_geral:.1f} |"
                    )
            md.append("")

        return "\n".join(md)

    def _relatorio_html(self, resultados: dict[str, dict[str, Metricas]]) -> str:
        """Gera relatório em HTML"""
        # Implementação simplificada - pode ser expandida
        md = self._relatorio_markdown(resultados)
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Relatório Comparativo de Algoritmos</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <pre>{md}</pre>
</body>
</html>
"""
        return html
