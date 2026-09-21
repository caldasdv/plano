"""Cabeçalho consistente para páginas do produto."""

from __future__ import annotations

from html import escape

import streamlit as st


def render_page_header(eyebrow: str, title: str, description: str) -> None:
    """Apresenta contexto, título e objetivo da tela na mesma ordem."""
    st.markdown(
        f'<div class="plan-eyebrow">{escape(eyebrow.capitalize())}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<h1 class="plan-page-title">{escape(title)}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="plan-page-description">{escape(description)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="plan-header-motif" aria-hidden="true">'
        '<span class="plan-header-motif-long"></span>'
        '<span class="plan-header-motif-short"></span>'
        '<i></i></div>',
        unsafe_allow_html=True,
    )


def render_flow_actions(current: str) -> None:
    """Oferece navegação contextual para o fluxo principal sem depender da sidebar."""
    pages = {
        "Hoje": ("app_pages/overview.py", ":material/home:", "flow_today"),
        "Metas": ("app_pages/goals.py", ":material/track_changes:", "flow_goals"),
        "Nova sessão": ("app_pages/new_session.py", ":material/add_circle:", "flow_session"),
        "Semana": ("app_pages/weekly.py", ":material/calendar_view_week:", "flow_week"),
        "Progresso": ("app_pages/progress.py", ":material/insights:", "flow_progress"),
        "Avaliações": ("app_pages/evaluations.py", ":material/assignment:", "flow_evaluations"),
    }
    labels = [label for label in pages if label != current]
    columns = st.columns(len(labels))
    for column, label in zip(columns, labels):
        page, icon, key = pages[label]
        if column.button(label, icon=icon, width="stretch", key=key):
            st.switch_page(page)
