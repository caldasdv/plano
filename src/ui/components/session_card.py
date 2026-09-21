"""Card visual de uma sessão de estudo."""

from __future__ import annotations

import re
from html import escape

import streamlit as st

from src.domain.session_rules import effective_status
from src.ui.components.status_badge import render_status


def render_session_card(row: dict, *, key: str) -> str | None:
    """Renderiza uma sessão e retorna a ação solicitada pelo usuário."""
    with st.container(border=True):
        info_col, status_col = st.columns([5, 1])
        subject_color = row.get("subject_color", "#787774")
        if isinstance(subject_color, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", subject_color):
            safe_subject_name = escape(str(row["subject_name"]))
            subject_markup = (
                f'<span class="subject-dot" style="background:{subject_color}" '
                f'aria-label="Cor da disciplina {subject_color}"></span>{safe_subject_name}'
            )
        else:
            subject_markup = escape(str(row["subject_name"]))
        goal_markup = (
            f'<div class="plan-session-goal">{escape(str(row["goal"]))}</div>'
            if row.get("goal")
            else ""
        )
        info_col.markdown(
            f'<div class="plan-session-content">'
            f'<div class="plan-session-meta">{escape(str(row["study_time"]))} · '
            f'{escape(str(row["duration"]))} minutos</div>'
            f'<div class="plan-session-subject">{subject_markup}</div>'
            f'<div class="plan-session-topic">{escape(str(row["topic"]))}</div>'
            f'{goal_markup}</div>',
            unsafe_allow_html=True,
        )
        status = effective_status(row)
        with status_col:
            render_status(status)
        if status != "Concluída" and info_col.button(
            "Concluir sessão",
            key=f"{key}_complete",
            type="primary",
            icon=":material/check:",
            width="content",
        ):
            return "complete"
    return None
