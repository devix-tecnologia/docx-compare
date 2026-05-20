"""Utilitários para instrumentar a rinha de matching."""

import time
from collections import defaultdict
from dataclasses import dataclass, field

from matching import MatchingStrategy, MatchResult


@dataclass
class CallStats:
    calls: int = 0
    time: float = 0.0


@dataclass
class StrategyStats:
    total_time: float = 0.0
    total_calls: int = 0
    best_match: CallStats = field(default_factory=CallStats)
    context: CallStats = field(default_factory=CallStats)


MATCHER_STATS: defaultdict[str, StrategyStats] = defaultdict(StrategyStats)


class InstrumentedMatcher(MatchingStrategy):
    """Decorator que coleta métricas de tempo para compararmos as estratégias."""

    def __init__(self, inner: MatchingStrategy):
        self._inner = inner
        self._stats = MATCHER_STATS[inner.name]

    @property
    def name(self) -> str:
        return self._inner.name

    def find_best_match(
        self,
        needle: str,
        haystack: str,
        threshold: float = 0.85,
    ) -> MatchResult:
        start = time.perf_counter()
        result = self._inner.find_best_match(needle, haystack, threshold)
        duration = time.perf_counter() - start

        self._stats.total_time += duration
        self._stats.total_calls += 1
        self._stats.best_match.calls += 1
        self._stats.best_match.time += duration

        return result

    def find_with_context(
        self,
        needle: str,
        context_before: str,
        context_after: str,
        haystack: str,
        threshold: float = 0.85,
    ) -> MatchResult:
        start = time.perf_counter()
        result = self._inner.find_with_context(
            needle, context_before, context_after, haystack, threshold
        )
        duration = time.perf_counter() - start

        self._stats.total_time += duration
        self._stats.total_calls += 1
        self._stats.context.calls += 1
        self._stats.context.time += duration

        return result
