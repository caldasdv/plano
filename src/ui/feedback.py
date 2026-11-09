"""Feedback consistente para falhas de interação na UI."""

from __future__ import annotations

import logging
from typing import Any

import streamlit as st


logger = logging.getLogger(__name__)


def set_success_flash(
    message: str,
    *,
    undo_session_id: Any | None = None,
    user_id: Any | None = None,
    link: tuple[str, str, str] | None = None,
) -> None:
    """Preserva uma confirmação para a próxima execução após um rerun.

    Quando ``undo_session_id`` é informado, a confirmação oferece "Desfazer",
    que devolve a sessão concluída para pendente (controle e liberdade).
    """
    st.session_state["flash_message"] = message
    if link is not None:
        st.session_state["flash_link"] = link
    else:
        st.session_state.pop("flash_link", None)
    if undo_session_id is not None:
        st.session_state["flash_undo"] = {"session_id": undo_session_id, "user_id": user_id}
    else:
        st.session_state.pop("flash_undo", None)


def _undo_completion(session_id: Any, user_id: Any) -> None:
    from src.services.container import get_application_services

    try:
        get_application_services().sessions.reopen(session_id, user_id)
    except Exception:
        logger.exception("Falha ao desfazer a conclusão da sessão")
        st.session_state["flash_error"] = "Não foi possível desfazer. Tente novamente."
    else:
        st.session_state["flash_message"] = "Conclusão desfeita. A sessão voltou para pendente."


def render_flash() -> None:
    """Exibe e consome a confirmação pendente da execução anterior."""
    error = st.session_state.pop("flash_error", None)
    if error:
        st.error(error)
    message = st.session_state.pop("flash_message", None)
    undo = st.session_state.pop("flash_undo", None)
    link = st.session_state.pop("flash_link", None)
    if not message:
        return
    if link is not None:
        message_column, link_column = st.columns([4, 1], vertical_alignment="center")
        message_column.success(message)
        path, label, icon = link
        with link_column:
            st.page_link(path, label=label, icon=icon)
        return
    if undo is None:
        st.success(message)
        return
    message_column, undo_column = st.columns([5, 1], vertical_alignment="center")
    message_column.success(message)
    undo_column.button(
        "Desfazer",
        icon=":material/undo:",
        key="flash_undo_button",
        width="stretch",
        on_click=_undo_completion,
        args=(undo["session_id"], undo["user_id"]),
    )


def show_action_error(action: str, error: Exception) -> None:
    """Registra detalhes técnicos sem expor infraestrutura ao usuário."""
    logger.exception("Falha ao %s", action)
    st.error(f"Não foi possível {action}.")
    st.caption("Verifique os dados e tente novamente. Se o problema continuar, tente mais tarde.")
