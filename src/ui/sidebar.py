"""Elementos compartilhados da barra lateral."""

from __future__ import annotations

from html import escape

import streamlit as st

from src.services.container import ApplicationServices
from src.config.runtime import is_local_mode
from src.ui.components.session_dialog import render_session_dialog
from src.ui.sections.periods import find_current_period, render_periods_dialog
from src.ui.feedback import show_action_error


def _toggle_theme(services: ApplicationServices, user: dict) -> None:
    next_mode = not bool(user.get("dark_mode", False))
    try:
        services.users.update_dark_mode(user["_id"], next_mode)
    except Exception as error:
        show_action_error("salvar a preferência visual", error)
    else:
        st.session_state["plan_dark_mode"] = next_mode


def render_account_sidebar(services: ApplicationServices, user: dict) -> None:
    current_period = find_current_period(services, user) if hasattr(services, "academic_periods") else None
    period_line = (
        f'<span>Período: {escape(str(current_period["name"]))}</span>' if current_period else ""
    )
    st.sidebar.markdown(
        f'<div class="plan-sidebar-user"><strong>{escape(str(user["name"]))}</strong>'
        f'<span>{escape(str(user["email"]))}</span>{period_line}</div>',
        unsafe_allow_html=True,
    )
    if not is_local_mode() and st.sidebar.button("Sair", width="stretch"):
        st.logout()
    if is_local_mode():
        st.sidebar.caption("Ambiente local · dados temporários")
        if st.sidebar.button(
            "Sair da demonstração", width="stretch", key="local_demo_logout"
        ):
            st.session_state.pop("plan_local_authenticated", None)
            st.session_state.pop("plan_local_profile", None)
            st.rerun()
    st.sidebar.divider()
    dark_mode = bool(user.get("dark_mode", False))
    st.session_state["plan_dark_mode"] = dark_mode
    st.sidebar.button(
        "Usar modo claro" if dark_mode else "Usar modo escuro",
        icon=":material/light_mode:" if dark_mode else ":material/dark_mode:",
        width="stretch",
        key="toggle_plan_theme",
        on_click=_toggle_theme,
        args=(services, user),
    )
    if dark_mode:
        st.sidebar.markdown(
            '<span class="plan-dark-mode-marker" aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )
    render_session_dialog(services, user)
    render_periods_dialog(services, user)
