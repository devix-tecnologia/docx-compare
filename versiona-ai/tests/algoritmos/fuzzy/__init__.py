"""
Algoritmos de Fuzzy Matching - Auto-registro

Todos os algoritmos nesta pasta são automaticamente registrados
para comparação via benchmark_fuzzy_runner.py

Para adicionar novo algoritmo:
1. Crie arquivo algoritmo_*.py
2. Herde de AlgoritmoVinculacao
3. Decore com @register_algorithm
4. Execute: python tests/benchmark_fuzzy_runner.py
"""

# Import registry system
import sys
from pathlib import Path

tests_dir = Path(__file__).parent.parent.parent
if str(tests_dir) not in sys.path:
    sys.path.insert(0, str(tests_dir))

from algoritmos.registry import register_algorithm  # noqa: E402

# Import e registro automático de todos os algoritmos
from .algoritmo import AlgoritmoFuzzyAvancado  # noqa: E402

# Registra baseline
AlgoritmoFuzzyAvancadoRegistrado = register_algorithm(AlgoritmoFuzzyAvancado)

# Tenta importar algoritmo otimizado (pode não estar completo ainda)
try:
    from .algoritmo_otimizado import AlgoritmoFuzzyAvancadoOtimizado  # noqa: E402

    AlgoritmoFuzzyAvancadoOtimizadoRegistrado = register_algorithm(
        AlgoritmoFuzzyAvancadoOtimizado
    )
except ImportError:
    pass

__all__ = [
    "AlgoritmoFuzzyAvancado",
    "register_algorithm",
]
