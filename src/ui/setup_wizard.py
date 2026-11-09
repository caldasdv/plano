"""Assistente "Montar meu plano": as missões de Primeiros passos num pop-up só.

O passo atual sai dos dados do usuário (o primeiro que falta), então o
assistente sempre retoma de onde a pessoa parou. Horário de aula e conteúdo
podem ser pulados; período, disciplina e sessão não.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.domain.onboarding_rules import OnboardingStep
from src.services.container import ApplicationServices
from src.ui.components.session_dialog import render_session_form
from src.ui.dialog_state import SETUP_DIALOG, active_dialog, close_dialog, open_dialog
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.forms import class_meeting_form, new_period_form, new_subject_form, new_topic_form
from src.ui.navigation import WEEK


WIZARD_STEPS = ("period", "subject", "class", "topic", "session")
OPTIONAL_STEPS = {"class", "topic"}
STEP_COPY = {
    "period": (
        "Qual é o seu período?",
        "O período agrupa disciplinas, sessões e notas. Pode ser o semestre atual, como 2026.2.",
    ),
    "subject": (
        "Qual disciplina você quer organizar primeiro?",
        "Comece por uma. Depois você adiciona as outras em Disciplinas.",
    ),
    "class": (
        "Quando são as aulas de {subject}?",
        "Os horários aparecem na Semana e ajudam a achar tempo livre para estudar.",
    ),
    "topic": (
        "O que você precisa estudar em {subject}?",
        "Cadastre um conteúdo, como um capítulo ou assunto da prova.",
    ),
    "session": (
        "Quando você vai estudar {subject}?",
        "Marque um bloco curto de estudo. Você conclui a sessão em Hoje quando terminar.",
    ),
}


def open_setup_wizard() -> None:
    open_dialog(SETUP_DIALOG, {"skipped": [], "finished": False, "subject_id": None})


def close_setup_wizard() -> None:
    close_dialog(SETUP_DIALOG)


def _state() -> dict:
    return st.session_state[SETUP_DIALOG]


def _skip(step_key: str) -> None:
    _state()["skipped"].append(step_key)


def _finish_session() -> None:
    _state()["finished"] = True
    st.rerun()


def _current_step(steps: list[OnboardingStep], skipped: list[str]) -> str | None:
    done = {step.key for step in steps if step.done}
    return next(
        (key for key in WIZARD_STEPS if key not in done and key not in skipped),
        None,
    )


def _choose_subject(subjects: list[dict], state: dict) -> dict:
    subjects_by_id = {subject["_id"]: subject for subject in subjects}
    if len(subjects) > 1:
        chosen = st.selectbox(
            "Disciplina",
            list(subjects_by_id),
            index=list(subjects_by_id).index(state["subject_id"])
            if state.get("subject_id") in subjects_by_id
            else 0,
            format_func=lambda value: subjects_by_id[value]["name"],
            key="setup_subject",
        )
        state["subject_id"] = chosen
    return subjects_by_id.get(state.get("subject_id")) or subjects[0]


def _render_finished(user: dict) -> None:
    st.subheader("Seu plano está pronto!", anchor=False)
    st.markdown(
        "Sua primeira sessão já aparece na **Semana** e em **Hoje**. "
        "Quando terminar de estudar, use **Concluir** no cartão da sessão."
    )
    close_column, week_column = st.columns(2)
    if close_column.button("Fechar", width="stretch", key="setup_close"):
        close_setup_wizard()
        st.rerun()
    if week_column.button(
        "Ver na Semana", type="primary", icon=WEEK.icon, width="stretch", key="setup_go_week"
    ):
        close_setup_wizard()
        st.switch_page(WEEK.path)


@st.dialog("Montar meu plano", width="medium", on_dismiss=close_setup_wizard)
def _setup_dialog(
    services: ApplicationServices,
    user: dict,
    steps: list[OnboardingStep],
    subjects: list[dict],
) -> None:
    state = _state()
    if state.get("finished"):
        _render_finished(user)
        return
    step_key = _current_step(steps, state["skipped"])
    if step_key is None:
        close_setup_wizard()
        set_success_flash("Seu plano está montado.")
        st.rerun()
    position = WIZARD_STEPS.index(step_key) + 1
    st.caption(f"Passo {position} de {len(WIZARD_STEPS)}")
    st.progress(position / len(WIZARD_STEPS))

    subject: dict[str, Any] | None = None
    if step_key in ("class", "topic", "session"):
        subject = _choose_subject(subjects, state)
    title, help_text = STEP_COPY[step_key]
    subject_name = subject["name"] if subject else ""
    st.subheader(title.format(subject=subject_name), anchor=False)
    st.caption(help_text)

    saved = False
    if step_key == "period":
        saved = new_period_form(services, user, key="setup_period", submit_label="Salvar e continuar")
    elif step_key == "subject":
        new_id = new_subject_form(services, user, key="setup_subject_form", submit_label="Salvar e continuar")
        if new_id is not None:
            state["subject_id"] = new_id
            saved = True
    elif step_key == "class":
        saved = class_meeting_form(
            services,
            user,
            subject_id=subject["_id"],
            key=f"setup_class_{subject['_id']}",
            submit_label="Salvar e continuar",
        )
    elif step_key == "topic":
        saved = new_topic_form(
            services,
            user,
            subject_id=subject["_id"],
            roots=[],
            key=f"setup_topic_{subject['_id']}",
            submit_label="Salvar e continuar",
        )
    else:
        render_session_form(
            services,
            user,
            session=None,
            key="setup_session",
            preset_subject_id=subject["_id"],
            on_saved=_finish_session,
        )
    if saved:
        st.rerun()

    if step_key in OPTIONAL_STEPS:
        st.button(
            "Pular este passo",
            width="stretch",
            key=f"setup_skip_{step_key}",
            on_click=_skip,
            args=(step_key,),
        )
    st.caption("Você pode fechar e continuar depois pelos Primeiros passos, em Hoje.")


def render_setup_wizard(services: ApplicationServices, user: dict) -> None:
    if active_dialog() != SETUP_DIALOG:
        return
    from src.ui.onboarding import load_onboarding_steps

    try:
        subjects = (
            services.subjects.list_for_period(user["_id"], user.get("current_academic_period_id"))
            if user.get("current_academic_period_id") is not None
            else []
        )
        steps = load_onboarding_steps(services, user, subjects)
    except Exception as error:
        show_action_error("carregar o assistente", error)
        return
    _setup_dialog(services, user, steps, subjects)
