"""Figuras analíticas da tela de progresso."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import plotly.graph_objects as go


LIGHT_COLORS = {
    "text": "#262b40",
    "muted": "#5379ae",
    "accent": "#0474c4",
    "soft": "#a8c4ec",
    "surface": "#ffffff",
    "grid": "rgba(83, 121, 174, .28)",
}
DARK_COLORS = {
    "text": "#ffffff",
    "muted": "#a8c4ec",
    "accent": "#a8c4ec",
    "soft": "#5379ae",
    "surface": "#2c444c",
    "grid": "rgba(168, 196, 236, .22)",
}


def subject_progress_figure(
    summary: Sequence[dict[str, Any]], *, dark_mode: bool = False
) -> go.Figure:
    """Cria comparação de minutos planejados e concluídos por disciplina."""
    colors = DARK_COLORS if dark_mode else LIGHT_COLORS
    labels = [row["disciplina"] for row in summary]
    figure = go.Figure(
        data=[
            go.Bar(
                name="Planejados",
                x=[row["planejados"] for row in summary],
                y=labels,
                orientation="h",
                marker={"color": colors["soft"], "line": {"width": 0}},
                hovertemplate="%{y}<br>Planejados: %{x} min<extra></extra>",
            ),
            go.Bar(
                name="Concluídos",
                x=[row["concluídos"] for row in summary],
                y=labels,
                orientation="h",
                marker={"color": colors["accent"], "line": {"width": 0}},
                hovertemplate="%{y}<br>Concluídos: %{x} min<extra></extra>",
            ),
        ]
    )
    figure.update_layout(
        barmode="group",
        bargap=.34,
        bargroupgap=.16,
        height=max(260, 70 * len(summary)),
        margin={"l": 8, "r": 8, "t": 12, "b": 12},
        legend={"orientation": "h", "y": 1.08, "x": 0, "font": {"size": 11}},
        xaxis_title="Minutos",
        yaxis_title="Minutos",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": colors["muted"], "family": "Inter, ui-sans-serif, system-ui, sans-serif", "size": 11},
        hoverlabel={"bgcolor": colors["surface"], "bordercolor": colors["muted"], "font": {"color": colors["text"]}},
        xaxis={"showgrid": True, "gridcolor": colors["grid"], "zeroline": False, "tickfont": {"color": colors["muted"]}},
        yaxis={"showgrid": False, "tickfont": {"color": colors["text"], "size": 11}},
    )
    return figure


def weekly_progress_figure(
    summary: Sequence[dict[str, Any]], *, dark_mode: bool = False
) -> go.Figure:
    """Cria a evolução diária de minutos planejados e concluídos."""
    colors = DARK_COLORS if dark_mode else LIGHT_COLORS
    figure = go.Figure(
        data=[
            go.Scatter(
                name="Planejados",
                x=[row["dia"] for row in summary],
                y=[row["planejados"] for row in summary],
                mode="lines+markers",
                line={"color": colors["soft"], "width": 3, "shape": "spline"},
                marker={"color": colors["surface"], "line": {"color": colors["soft"], "width": 2}, "size": 7},
                hovertemplate="%{x}<br>Planejados: %{y} min<extra></extra>",
            ),
            go.Scatter(
                name="Concluídos",
                x=[row["dia"] for row in summary],
                y=[row["concluídos"] for row in summary],
                mode="lines+markers",
                line={"color": colors["accent"], "width": 4, "shape": "spline"},
                marker={"color": colors["accent"], "line": {"color": colors["surface"], "width": 2}, "size": 8},
                fill="tozeroy",
                fillcolor="rgba(4, 116, 196, .10)",
                hovertemplate="%{x}<br>Concluídos: %{y} min<extra></extra>",
            ),
        ]
    )
    figure.update_layout(
        height=320,
        margin={"l": 8, "r": 8, "t": 12, "b": 12},
        legend={"orientation": "h", "y": 1.08, "x": 0, "font": {"size": 11}},
        yaxis_title="Minutos",
        xaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": colors["muted"], "family": "Inter, ui-sans-serif, system-ui, sans-serif", "size": 11},
        hoverlabel={"bgcolor": colors["surface"], "bordercolor": colors["muted"], "font": {"color": colors["text"]}},
        xaxis={"showgrid": False, "zeroline": False, "tickfont": {"color": colors["muted"]}},
        yaxis={"showgrid": True, "gridcolor": colors["grid"], "zeroline": False, "tickfont": {"color": colors["muted"]}},
    )
    return figure


def evaluation_progress_figure(
    evaluations: Sequence[dict[str, Any]], *, dark_mode: bool = False
) -> go.Figure:
    """Compara notas proporcionais sem descartar avaliações realizadas no mesmo dia."""
    colors = DARK_COLORS if dark_mode else LIGHT_COLORS
    by_subject: dict[Any, list[dict[str, Any]]] = {}
    for evaluation in evaluations:
        if evaluation.get("score") is not None and evaluation.get("max_score"):
            by_subject.setdefault(evaluation["subject_id"], []).append(evaluation)
    figure = go.Figure()
    for rows in by_subject.values():
        rows = sorted(rows, key=lambda row: (row["evaluation_date"], row["title"]))
        figure.add_trace(
            go.Scatter(
                name=rows[0]["subject_name"],
                x=[row["evaluation_date"] for row in rows],
                y=[row["score"] / row["max_score"] * 10 for row in rows],
                mode="lines+markers",
                marker={"size": 9},
                line={"width": 3},
                customdata=[[row["title"], row["score"], row["max_score"]] for row in rows],
                hovertemplate=(
                    "%{customdata[0]}<br>%{x|%d/%m/%Y}<br>"
                    "Nota: %{customdata[1]}/%{customdata[2]}<br>"
                    "Proporcional: %{y:.1f}/10<extra>%{fullData.name}</extra>"
                ),
            )
        )
    figure.update_layout(
        height=320,
        margin={"l": 8, "r": 8, "t": 12, "b": 12},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": colors["text"], "family": "Inter, ui-sans-serif, system-ui, sans-serif"},
        colorway=[colors["accent"], "#b06d35", "#7158a6", "#31858a", "#4b83a6", colors["soft"]],
        hoverlabel={"bgcolor": colors["surface"], "font": {"color": colors["text"]}},
        legend={"orientation": "h", "y": -0.25, "x": 0},
        xaxis={"title": "Data da avaliação", "type": "date", "tickformat": "%d/%m", "showgrid": False},
        yaxis={"title": "Nota proporcional", "range": [0, 10.5], "gridcolor": colors["grid"], "zeroline": False},
    )
    return figure
