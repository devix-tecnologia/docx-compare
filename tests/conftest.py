"""Hooks e fixtures compartilhados para a suíte de testes."""

from tests.matching_rinha_metrics import MATCHER_STATS


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Exibe o placar da rinha de matching ao final da execução."""

    if not MATCHER_STATS:
        return

    ordered = sorted(MATCHER_STATS.items(), key=lambda item: item[1].total_time)

    terminalreporter.write_sep("-", "Rinha de Matching")

    for name, stats in ordered:
        total_time_ms = stats.total_time * 1000
        total_calls = stats.total_calls or 1
        avg_time_ms = total_time_ms / total_calls
        best_ms = stats.best_match.time * 1000
        context_ms = stats.context.time * 1000

        terminalreporter.write_line(
            f"{name:10s} | total {total_time_ms:8.2f} ms | "
            f"chamadas {stats.total_calls:3d} | media {avg_time_ms:6.2f} ms"
        )
        terminalreporter.write_line(
            f"  best_match: {stats.best_match.calls:3d} calls / {best_ms:8.2f} ms"
        )
        terminalreporter.write_line(
            f"  context   : {stats.context.calls:3d} calls / {context_ms:8.2f} ms"
        )

    campea = ordered[0][0]
    terminalreporter.write_line(f"Campea da rodada: {campea}")
