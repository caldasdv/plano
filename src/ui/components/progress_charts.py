"""Figuras analíticas da tela de progresso."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import plotly.graph_objects as go


CHART_TEXT = "#172529"
CHART_MUTED = "#687679"
CHART_GREEN = "#176b5d"
CHART_GREEN_SOFT = "#afd1bb"
CHART_GRID = "rgba(220, 229, 222, .72)"


def subject_progress_figure(summary: Sequence[dict[str, Any]]) -> go.Figure:
    """Cria comparação de minutos planejados e concluídos por disciplina."""
    labels = [row["disciplina"] for row in summary]
    figure = go.Figure(
        data=[
            go.Bar(
                name="Planejados",
                x=[row["planejados"] for row in summary],
                y=labels,
                orientation="h",
                marker={"color": CHART_GREEN_SOFT, "line": {"width": 0}},
                hovertemplate="%{y}<br>Planejados: %{x} min<extra></extra>",
            ),
            go.Bar(
                name="Concluídos",
                x=[row["concluídos"] for row in summary],
                y=labels,
                orientation="h",
                marker={"color": CHART_GREEN, "line": {"width": 0}},
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
        font={"color": CHART_MUTED, "family": "Inter, ui-sans-serif, system-ui, sans-serif", "size": 11},
        hoverlabel={"bgcolor": "#fcfdf9", "bordercolor": "#dce5de", "font": {"color": CHART_TEXT}},
        xaxis={"showgrid": True, "gridcolor": CHART_GRID, "zeroline": False, "tickfont": {"color": CHART_MUTED}},
        yaxis={"showgrid": False, "tickfont": {"color": CHART_TEXT, "size": 11}},
    )
    return figure


def weekly_progress_figure(summary: Sequence[dict[str, Any]]) -> go.Figure:
    """Cria a evolução diária de minutos planejados e concluídos."""
    figure = go.Figure(
        data=[
            go.Scatter(
                name="Planejados",
                x=[row["dia"] for row in summary],
                y=[row["planejados"] for row in summary],
                mode="lines+markers",
                line={"color": CHART_GREEN_SOFT, "width": 3, "shape": "spline"},
                marker={"color": "#fcfdf9", "line": {"color": CHART_GREEN_SOFT, "width": 2}, "size": 7},
                hovertemplate="%{x}<br>Planejados: %{y} min<extra></extra>",
            ),
            go.Scatter(
                name="Concluídos",
                x=[row["dia"] for row in summary],
                y=[row["concluídos"] for row in summary],
                mode="lines+markers",
                line={"color": CHART_GREEN, "width": 4, "shape": "spline"},
                marker={"color": CHART_GREEN, "line": {"color": "#fcfdf9", "width": 2}, "size": 8},
                fill="tozeroy",
                fillcolor="rgba(23, 107, 93, .08)",
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
        font={"color": CHART_MUTED, "family": "Inter, ui-sans-serif, system-ui, sans-serif", "size": 11},
        hoverlabel={"bgcolor": "#fcfdf9", "bordercolor": "#dce5de", "font": {"color": CHART_TEXT}},
        xaxis={"showgrid": False, "zeroline": False, "tickfont": {"color": CHART_MUTED}},
        yaxis={"showgrid": True, "gridcolor": CHART_GRID, "zeroline": False, "tickfont": {"color": CHART_MUTED}},
    )
    return figure
