"""Cartões de disciplina com pop-ups para conteúdos, horários e edição.

A tela Disciplinas mostra só o resumo de cada matéria. Cadastrar ou editar
acontece em pop-ups, um de cada vez.
"""

from __future__ import annotations

from html import escape
import re
from typing import Any

import streamlit as st
from streamlit.errors import StreamlitAPIException

from src.services.container import ApplicationServices
from src.services.report_service import build_topic_summary
from src.ui.components.session_dialog import open_session_dialog
from src.ui.dialog_state import SUBJECT_DIALOG, active_dialog, close_dialog, open_dialog
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.forms import (
    DIFFICULTY_LABELS,
    STATUS_LABELS,
    WEEKDAYS,
    class_meeting_form,
    new_topic_form,
)


_NOTICE_KEY = "plan_subject_notice"
_EDITING_MEETING_KEY = "plan_editing_meeting_id"
_CONFIRM_DELETE_KEY = "plan_confirm_delete_meeting_id"
SHORT_WEEKDAYS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def safe_color(subject: dict) -> str:
    color = str(subject.get("color", "#787774"))
    return color if re.fullmatch(r"#[0-9A-Fa-f]{6}", color) else "#787774"


def open_subject_dialog(subject_id: Any, view: str) -> None:
    for key in (_NOTICE_KEY, _EDITING_MEETING_KEY, _CONFIRM_DELETE_KEY):
        st.session_state.pop(key, None)
    open_dialog(SUBJECT_DIALOG, {"subject_id": subject_id, "view": view})


def close_subject_dialog() -> None:
    close_dialog(SUBJECT_DIALOG)


def _rerun_dialog() -> None:
    """Recarrega só o pop-up; fora de um fragmento (como nos testes), a página toda."""
    try:
        st.rerun(scope="fragment")
    except StreamlitAPIException:
        st.rerun()


def _saved(message: str) -> None:
    """Mostra a confirmação dentro do pop-up e recarrega só ele."""
    st.session_state[_NOTICE_KEY] = message
    _rerun_dialog()


def _render_notice() -> None:
    message = st.session_state.pop(_NOTICE_KEY, None)
    if message:
        st.success(message)


def _render_topic_list(
    services: ApplicationServices, user: dict, subjects: list[dict], subject_id: Any
) -> list[dict] | None:
    try:
        topics = services.topics.list_for_subject(
            user["_id"], user.get("current_academic_period_id"), subject_id
        )
        sessions = services.sessions.list_for_user(user["_id"], subjects)
    except Exception as error:
        show_action_error("carregar os conteúdos", error)
        return None
    roots = [topic for topic in topics if topic.get("parent_id") is None]
    if not topics:
        st.info("Ainda não há conteúdos. Adicione o primeiro abaixo.")
        return roots
    children: dict[Any, list[dict]] = {topic["_id"]: [] for topic in roots}
    for topic in topics:
        if topic.get("parent_id") in children:
            children[topic["parent_id"]].append(topic)
    summary = build_topic_summary(
        [session for session in sessions if session.get("subject_id") == subject_id], topics
    )
    progress_by_id = {item["topic_id"]: item for item in summary}
    for root in roots:
        with st.container(border=True):
            st.markdown(f"**{escape(root['title'])}**")
            st.caption(
                f"{STATUS_LABELS.get(root['status'], root['status'])} · Dificuldade "
                f"{DIFFICULTY_LABELS.get(root['difficulty'], root['difficulty'])}"
            )
            root_progress = progress_by_id.get(root["_id"])
            if root_progress and root_progress["planned_minutes"]:
                st.progress(
                    root_progress["progress"],
                    text=f"{root_progress['completed_minutes']} de "
                    f"{root_progress['planned_minutes']} min em sessões",
                )
            items = []
            for child in children[root["_id"]]:
                detail = STATUS_LABELS.get(child["status"], child["status"])
                child_progress = progress_by_id.get(child["_id"])
                if child_progress and child_progress["planned_minutes"]:
                    detail = (
                        f"{detail} · {child_progress['completed_minutes']}/"
                        f"{child_progress['planned_minutes']} min"
                    )
                done = " is-done" if child["status"] in {"REVIEWED", "MASTERED"} else ""
                items.append(
                    f'<div class="plan-topic-path-item{done}"><i aria-hidden="true"></i>'
                    f"<strong>{escape(child['title'])}</strong>"
                    f"<small>{escape(detail)}</small></div>"
                )
            if items:
                st.markdown(
                    '<div class="plan-topic-path">' + "".join(items) + "</div>",
                    unsafe_allow_html=True,
                )
    return roots


def _topics_view(
    services: ApplicationServices, user: dict, subjects: list[dict], subject: dict
) -> None:
    roots = _render_topic_list(services, user, subjects, subject["_id"])
    if roots is None:
        return
    st.markdown("**Adicionar conteúdo**")
    if new_topic_form(
        services, user, subject_id=subject["_id"], roots=roots, key=f"new_topic_{subject['_id']}"
    ):
        _saved("Conteúdo adicionado.")


def _meeting_label(meeting: dict) -> str:
    location = f" · {meeting['location']}" if meeting.get("location") else ""
    return (
        f"**{WEEKDAYS[meeting['weekday']]}** · "
        f"{meeting['start_time']}–{meeting['end_time']}{location}"
    )


def _classes_view(
    services: ApplicationServices, user: dict, subjects: list[dict], subject: dict
) -> None:
    period_id = user.get("current_academic_period_id")
    try:
        meetings = [
            meeting
            for meeting in services.class_meetings.list_for_period(user["_id"], period_id, subjects)
            if meeting["subject_id"] == subject["_id"]
        ]
    except Exception as error:
        show_action_error("carregar os horários de aula", error)
        return
    meetings.sort(key=lambda meeting: (meeting["weekday"], meeting["start_time"]))
    st.caption("As aulas aparecem na Semana, ao lado das sessões de estudo.")
    if not meetings:
        st.info("Ainda não há horários. Adicione o primeiro abaixo.")
    editing_id = st.session_state.get(_EDITING_MEETING_KEY)
    confirm_id = st.session_state.get(_CONFIRM_DELETE_KEY)
    for meeting in meetings:
        meeting_id = str(meeting["_id"])
        with st.container(border=True):
            text_column, edit_column, delete_column = st.columns(
                [3, 1, 1], vertical_alignment="center"
            )
            text_column.markdown(_meeting_label(meeting))
            if edit_column.button(
                "Editar", icon=":material/edit:", width="stretch", key=f"edit_meeting_{meeting_id}"
            ):
                st.session_state[_EDITING_MEETING_KEY] = meeting_id
                st.session_state.pop(_CONFIRM_DELETE_KEY, None)
                _rerun_dialog()
            if delete_column.button(
                "Excluir",
                icon=":material/delete:",
                width="stretch",
                key=f"delete_meeting_{meeting_id}",
            ):
                st.session_state[_CONFIRM_DELETE_KEY] = meeting_id
                st.session_state.pop(_EDITING_MEETING_KEY, None)
                _rerun_dialog()
            if confirm_id == meeting_id:
                st.warning("Excluir este horário? A ação não pode ser desfeita.")
                confirm_column, cancel_column = st.columns(2)
                if confirm_column.button(
                    "Confirmar exclusão",
                    type="primary",
                    width="stretch",
                    key=f"confirm_delete_meeting_{meeting_id}",
                ):
                    try:
                        services.class_meetings.delete(user["_id"], period_id, meeting["_id"])
                    except Exception as error:
                        show_action_error("remover o horário", error)
                    else:
                        st.session_state.pop(_CONFIRM_DELETE_KEY, None)
                        _saved("Horário removido.")
                if cancel_column.button(
                    "Cancelar", width="stretch", key=f"cancel_delete_meeting_{meeting_id}"
                ):
                    st.session_state.pop(_CONFIRM_DELETE_KEY, None)
                    _rerun_dialog()
            if editing_id == meeting_id:
                if class_meeting_form(
                    services,
                    user,
                    subject_id=subject["_id"],
                    meeting=meeting,
                    key=f"edit_meeting_form_{meeting_id}",
                ):
                    st.session_state.pop(_EDITING_MEETING_KEY, None)
                    _saved("Horário atualizado.")
                if st.button("Cancelar edição", key=f"cancel_edit_meeting_{meeting_id}"):
                    st.session_state.pop(_EDITING_MEETING_KEY, None)
                    _rerun_dialog()
    st.markdown("**Adicionar horário de aula**")
    if class_meeting_form(
        services, user, subject_id=subject["_id"], key=f"new_meeting_{subject['_id']}"
    ):
        _saved("Horário adicionado.")


def _edit_view(services: ApplicationServices, user: dict, subject: dict) -> None:
    with st.form(f"edit_subject_{subject['_id']}", border=False):
        name = st.text_input("Nome *", value=subject["name"])
        color = st.color_picker("Cor", safe_color(subject))
        st.caption("Campos com \\* são obrigatórios.")
        submitted = st.form_submit_button("Salvar alterações", type="primary", width="stretch")
    if not submitted:
        return
    try:
        services.subjects.update(
            user["_id"], subject["_id"], user.get("current_academic_period_id"), name, color
        )
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        show_action_error("salvar a disciplina", error)
    else:
        close_subject_dialog()
        set_success_flash("Disciplina atualizada.")
        st.rerun()


_VIEWS = {
    "topics": "Conteúdos",
    "classes": "Horários de aula",
    "edit": "Editar disciplina",
}


@st.dialog("Disciplina", width="medium", on_dismiss=close_subject_dialog)
def _subject_dialog(
    services: ApplicationServices, user: dict, subjects: list[dict], subject: dict, view: str
) -> None:
    st.markdown(
        f'<h3 class="plan-subject-title"><span class="subject-dot" '
        f'style="background:{safe_color(subject)}" aria-hidden="true"></span>'
        f"{escape(subject['name'])} · {_VIEWS[view]}</h3>",
        unsafe_allow_html=True,
    )
    _render_notice()
    if view == "topics":
        _topics_view(services, user, subjects, subject)
    elif view == "classes":
        _classes_view(services, user, subjects, subject)
    else:
        _edit_view(services, user, subject)


def render_subject_dialog(services: ApplicationServices, user: dict, subjects: list[dict]) -> None:
    if active_dialog() != SUBJECT_DIALOG:
        return
    state = st.session_state[SUBJECT_DIALOG]
    subject = next((item for item in subjects if item["_id"] == state["subject_id"]), None)
    if subject is None or state.get("view") not in _VIEWS:
        close_subject_dialog()
        return
    _subject_dialog(services, user, subjects, subject, state["view"])


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def render_subject_cards(services: ApplicationServices, user: dict, subjects: list[dict]) -> None:
    """Um cartão por disciplina: resumo e as ações em pop-up."""
    period_id = user.get("current_academic_period_id")
    try:
        meetings = services.class_meetings.list_for_period(user["_id"], period_id, subjects)
        topic_counts = {
            subject["_id"]: len(
                services.topics.list_for_subject(user["_id"], period_id, subject["_id"])
            )
            for subject in subjects
        }
    except Exception as error:
        show_action_error("carregar o resumo das disciplinas", error)
        return
    for subject in subjects:
        subject_id = subject["_id"]
        subject_meetings = sorted(
            (meeting for meeting in meetings if meeting["subject_id"] == subject_id),
            key=lambda meeting: (meeting["weekday"], meeting["start_time"]),
        )
        topic_count = topic_counts.get(subject_id, 0)
        with st.container(border=True, key=f"subject_card_{subject_id}"):
            st.markdown(
                f'<h3 class="plan-subject-title"><span class="subject-dot" '
                f'style="background:{safe_color(subject)}" aria-hidden="true"></span>'
                f"{escape(subject['name'])}</h3>",
                unsafe_allow_html=True,
            )
            summary = [
                _plural(topic_count, "conteúdo", "conteúdos") if topic_count else "Sem conteúdos",
                _plural(len(subject_meetings), "aula por semana", "aulas por semana")
                if subject_meetings
                else "Sem horários de aula",
            ]
            st.caption(" · ".join(summary))
            if subject_meetings:
                st.caption(
                    "Aulas: "
                    + ", ".join(
                        f"{SHORT_WEEKDAYS[meeting['weekday']]} {meeting['start_time']}"
                        for meeting in subject_meetings
                    )
                )
            topics_column, classes_column, plan_column, edit_column = st.columns(4)
            topics_column.button(
                "Conteúdos",
                icon=":material/list:",
                width="stretch",
                key=f"subject_topics_{subject_id}",
                on_click=open_subject_dialog,
                args=(subject_id, "topics"),
            )
            classes_column.button(
                "Horários",
                icon=":material/schedule:",
                width="stretch",
                key=f"subject_classes_{subject_id}",
                on_click=open_subject_dialog,
                args=(subject_id, "classes"),
            )
            plan_column.button(
                "Planejar sessão",
                icon=":material/event:",
                width="stretch",
                key=f"subject_plan_{subject_id}",
                on_click=open_session_dialog,
                args=(None, subject_id),
            )
            edit_column.button(
                "Editar",
                icon=":material/edit:",
                width="stretch",
                key=f"subject_edit_{subject_id}",
                on_click=open_subject_dialog,
                args=(subject_id, "edit"),
            )
