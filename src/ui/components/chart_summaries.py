"""Resumos em texto dos gráficos, para leitores de tela e leitura rápida."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def describe_subject_load(summary: Sequence[dict[str, Any]]) -> str:
    planned = sum(row["planejados"] for row in summary)
    completed = sum(row["concluídos"] for row in summary)
    if not planned:
        return "Nenhuma sessão planejada nesta semana."
    busiest = max(summary, key=lambda row: row["planejados"])
    return (
        f"{completed} de {planned} minutos planejados foram concluídos. "
        f"Maior carga: {busiest['disciplina']}, com {busiest['planejados']} minutos."
    )


def describe_week_rhythm(summary: Sequence[dict[str, Any]]) -> str:
    studied_days = [row for row in summary if row["planejados"]]
    if not studied_days:
        return "Nenhum dia com sessões nesta semana."
    best = max(summary, key=lambda row: row["concluídos"])
    text = f"{len(studied_days)} de 7 dias têm sessões planejadas."
    if best["concluídos"]:
        text += f" Dia com mais estudo concluído: {best['dia']}, com {best['concluídos']} minutos."
    return text


def describe_grades(evaluations: Sequence[dict[str, Any]]) -> str:
    by_subject: dict[str, list[float]] = {}
    for item in evaluations:
        if item.get("score") is None or not item.get("max_score"):
            continue
        by_subject.setdefault(item["subject_name"], []).append(
            item["score"] / item["max_score"] * 10
        )
    if not by_subject:
        return "Nenhuma nota registrada."
    averages = {name: sum(values) / len(values) for name, values in by_subject.items()}
    total = sum(len(values) for values in by_subject.values())
    best = max(averages, key=averages.get)
    if len(averages) == 1:
        return f"{total} notas registradas em {best}, com média {averages[best]:.1f} de 10."
    worst = min(averages, key=averages.get)
    return (
        f"{total} notas registradas. Maior média: {best} ({averages[best]:.1f} de 10). "
        f"Menor média: {worst} ({averages[worst]:.1f} de 10)."
    )
