"""Diálogos de criar e editar sessão, abertos a partir de Hoje e Semana."""

from __future__ import annotations

from datetime import date, time
from typing import Any

import streamlit as st

from src.services.container import ApplicationServices
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.navigation import SUBJECTS


DURATIONS = [25, 45, 60, 90, 120]
PRIORITIES = ["Baixa", "Média", "Alta"]


def _load_subjects(services: ApplicationServices, user: dict) -> list[dict] | None:
    try:
        return services.subjects.list_for_period(
            user["_id"], user.get("current_academic_period_id")
        )
    except Exception as error:
        show_action_error("carregar as disciplinas do período atual", error)
        return None


def _missing_setup(user: dict, subjects: list[dict]) -> bool:
    """Explica o pré-requisito que falta e leva direto até ele (recuperação apoiada)."""
    if user.get("current_academic_period_id") is None:
        st.info("Para criar sessões, primeiro adicione um período acadêmico em Disciplinas.")
        st.page_link(SUBJECTS.path, label="Ir para Disciplinas", icon=SUBJECTS.icon)
        return True
    if not subjects:
        st.info("Para criar sessões, primeiro adicione uma disciplina ao período atual.")
        st.page_link(SUBJECTS.path, label="Ir para Disciplinas", icon=SUBJECTS.icon)
        return True
    return False


def _session_form(
    services: ApplicationServices,
    user: dict,
    *,
    session: dict[str, Any] | None,
    key: str,
) -> None:
    subjects = _load_subjects(services, user)
    if subjects is None or _missing_setup(user, subjects):
        return
    period_id = user["current_academic_period_id"]
    subjects_by_id = {subject["_id"]: subject for subject in subjects}
    subject_ids = list(subjects_by_id)
    default_subject = session.get("subject_id") if session else None
    subject_id = st.selectbox(
        "Disciplina",
        subject_ids,
        index=subject_ids.index(default_subject) if default_subject in subjects_by_id else 0,
        format_func=lambda value: subjects_by_id[value]["name"],
        key=f"{key}_subject",
    )
    try:
        topics = services.topics.list_for_subject(user["_id"], period_id, subject_id)
    except Exception as error:
        show_action_error("carregar os conteúdos da disciplina", error)
        topics = []
    topics_by_id = {topic["_id"]: topic for topic in topics}
    topic_options = [None, *topics_by_id]
    default_topic = session.get("topic_id") if session else None
    with st.form(f"{key}_form", border=False):
        topic_id = st.selectbox(
            "Conteúdo relacionado (opcional)",
            topic_options,
            index=topic_options.index(default_topic) if default_topic in topics_by_id else 0,
            format_func=lambda value: (
                "Sem conteúdo específico" if value is None else topics_by_id[value]["title"]
            ),
            help="Vincule a sessão a um tópico para acompanhar o progresso por conteúdo.",
        )
        topic = st.text_input(
            "O que você vai estudar? *",
            value=session.get("topic", "") if session else "",
            placeholder="Ex.: Heurísticas de Nielsen",
        )
        goal = st.text_area(
            "Objetivo da sessão (opcional)",
            value=session.get("goal", "") if session else "",
            placeholder="Ex.: revisar as heurísticas e anotar exemplos",
        )
        date_column, time_column = st.columns(2)
        study_date = date_column.date_input(
            "Data *",
            value=date.fromisoformat(session["study_date"]) if session else date.today(),
            format="DD/MM/YYYY",
        )
        study_time = time_column.time_input(
            "Horário *",
            value=time.fromisoformat(session["study_time"]) if session else time(14, 0),
            step=900,
        )
        duration_column, priority_column = st.columns(2)
        current_duration = int(session["duration"]) if session else 60
        durations = sorted({*DURATIONS, current_duration})
        duration = duration_column.selectbox(
            "Duração",
            durations,
            index=durations.index(current_duration),
            format_func=lambda value: f"{value} minutos",
        )
        current_priority = session.get("priority", "Média") if session else "Média"
        priority = priority_column.selectbox(
            "Prioridade",
            PRIORITIES,
            index=PRIORITIES.index(current_priority) if current_priority in PRIORITIES else 1,
        )
        st.caption("Campos com \\* são obrigatórios.")
        submitted = st.form_submit_button(
            "Salvar alterações" if session else "Adicionar sessão",
            type="primary",
            width="stretch",
        )
    if not submitted:
        return
    values = dict(
        user_id=user["_id"],
        academic_period_id=period_id,
        subject_id=subject_id,
        topic=topic,
        goal=goal,
        study_date=study_date,
        study_time=study_time,
        duration=duration,
        priority=priority,
        topic_id=topic_id,
    )
    try:
        if session:
            services.sessions.update(session_id=session["_id"], **values)
        else:
            services.sessions.create(**values)
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        show_action_error("salvar a sessão", error)
    else:
        close_session_dialog()
        set_success_flash("Sessão atualizada." if session else "Sessão adicionada ao seu plano.")
        st.rerun()


_DIALOG_STATE_KEY = "plan_session_dialog"


def open_session_dialog(session: dict | None = None) -> None:
    """Abre o diálogo de criar (sem ``session``) ou editar sessão.

    O estado fica na sessão do Streamlit para o diálogo continuar aberto entre
    reruns e fechar só quando o usuário salva ou dispensa.
    """
    st.session_state[_DIALOG_STATE_KEY] = {"session": session}


def render_new_session_button(key: str) -> None:
    """Botão principal da tela, logo abaixo do cabeçalho, alinhado à direita."""
    _, button_column = st.columns([3, 1])
    button_column.button(
        "Nova sessão",
        type="primary",
        icon=":material/add:",
        width="stretch",
        key=key,
        on_click=open_session_dialog,
    )


def close_session_dialog() -> None:
    st.session_state.pop(_DIALOG_STATE_KEY, None)


@st.dialog("Nova sessão", width="medium", on_dismiss=close_session_dialog)
def _new_session_dialog(services: ApplicationServices, user: dict) -> None:
    st.caption("Defina uma sessão pequena e objetiva para facilitar o início do estudo.")
    _session_form(services, user, session=None, key="new_session")


@st.dialog("Editar sessão", width="medium", on_dismiss=close_session_dialog)
def _edit_session_dialog(services: ApplicationServices, user: dict, session: dict) -> None:
    _session_form(services, user, session=session, key=f"edit_session_{session['_id']}")


def render_session_dialog(services: ApplicationServices, user: dict) -> None:
    """Mostra o diálogo pedido, se houver. Chamado uma vez por execução, na sidebar."""
    state = st.session_state.get(_DIALOG_STATE_KEY)
    if state is None:
        return
    if state["session"] is None:
        _new_session_dialog(services, user)
    else:
        _edit_session_dialog(services, user, state["session"])
