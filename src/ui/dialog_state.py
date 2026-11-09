"""Estado dos diálogos: só um fica aberto por vez.

Cada diálogo guarda seu pedido em ``st.session_state``. Abrir um diálogo
descarta os outros pedidos, e a barra lateral desenha apenas o ativo, na ordem
de prioridade abaixo (a ação que o usuário acabou de pedir vem primeiro).
"""

from __future__ import annotations

from typing import Any

import streamlit as st


SESSION_DIALOG = "plan_session_dialog"
PERIODS_DIALOG = "plan_periods_dialog"
SUBJECT_DIALOG = "plan_subject_dialog"
SETUP_DIALOG = "plan_setup_dialog"
HELP_DIALOG = "plan_help_dialog"
TOUR_DIALOG = "plan_tour_dialog"
DIALOG_KEYS = (
    SESSION_DIALOG,
    PERIODS_DIALOG,
    SUBJECT_DIALOG,
    SETUP_DIALOG,
    HELP_DIALOG,
    TOUR_DIALOG,
)


def open_dialog(key: str, value: Any = True) -> None:
    for other in DIALOG_KEYS:
        st.session_state.pop(other, None)
    st.session_state[key] = value


def close_dialog(key: str) -> None:
    st.session_state.pop(key, None)


def active_dialog() -> str | None:
    return next((key for key in DIALOG_KEYS if key in st.session_state), None)
