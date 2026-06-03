"""
Sistema de Registro de Algoritmos de Vinculação

Permite descoberta automática e comparação de múltiplos algoritmos.

Uso:
    # Registrar algoritmo
    @register_algorithm
    class MeuAlgoritmo(AlgoritmoVinculacao):
        ...

    # Listar todos
    algoritmos = get_registered_algorithms()

    # Executar comparação
    runner = AlgorithmBenchmarkRunner()
    resultados = runner.compare_all(modificacoes, tags, texto)
"""


from framework_comparacao import AlgoritmoVinculacao

# Registry global de algoritmos
_ALGORITHM_REGISTRY: dict[str, type[AlgoritmoVinculacao]] = {}


def register_algorithm(cls: type[AlgoritmoVinculacao]) -> type[AlgoritmoVinculacao]:
    """
    Decorator para registrar automaticamente um algoritmo.

    Uso:
        @register_algorithm
        class MeuAlgoritmo(AlgoritmoVinculacao):
            @property
            def nome(self) -> str:
                return "meu_algo"
    """
    # Instancia temporariamente para obter nome
    instance = cls()
    nome = instance.nome

    if nome in _ALGORITHM_REGISTRY:
        print(f"⚠️  Algoritmo '{nome}' já registrado, sobrescrevendo com {cls.__name__}")

    _ALGORITHM_REGISTRY[nome] = cls
    return cls


def get_registered_algorithms() -> dict[str, type[AlgoritmoVinculacao]]:
    """
    Retorna dicionário com todos os algoritmos registrados.

    Returns:
        dict: {nome_algoritmo: ClasseAlgoritmo}
    """
    return _ALGORITHM_REGISTRY.copy()


def get_algorithm(nome: str) -> type[AlgoritmoVinculacao] | None:
    """
    Retorna classe de algoritmo por nome.

    Args:
        nome: Nome do algoritmo (ex: 'fuzzy', 'regex', 'hibrido')

    Returns:
        Classe do algoritmo ou None se não encontrado
    """
    return _ALGORITHM_REGISTRY.get(nome)


def list_algorithms() -> list[str]:
    """
    Lista nomes de todos os algoritmos registrados.

    Returns:
        Lista de nomes dos algoritmos
    """
    return list(_ALGORITHM_REGISTRY.keys())


def clear_registry():
    """Limpa o registry (útil para testes)."""
    _ALGORITHM_REGISTRY.clear()


__all__ = [
    "register_algorithm",
    "get_registered_algorithms",
    "get_algorithm",
    "list_algorithms",
    "clear_registry",
]
