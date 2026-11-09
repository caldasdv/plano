"""Formulários curtos de cadastro, usados nos pop-ups e no assistente.

Cada função desenha o formulário, salva e devolve o resultado (``True`` ou o id
criado) quando deu certo. Quem chama decide o que acontece depois: fechar o
pop-up, avançar o assistente ou recarregar a lista.
"""

from __future__ import annotations

from datetime import date, time
from typing import Any

import streamlit as st

from src.services.container import ApplicationServices
from src.ui.feedback import show_action_error


WEEKDAYS = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]
STATUS_LABELS = {
    "NOT_STARTED": "Não iniciado",
    "IN_PROGRESS": "Em andamento",
    "REVIEWED": "Revisado",
    "MASTERED": "Dominado",
}
DIFFICULTY_LABELS = {"LOW": "Baixa", "MEDIUM": "Média", "HIGH": "Alta"}
REQUIRED_NOTE = "Campos com \\* são obrigatórios."


def new_period_form(
    services: ApplicationServices, user: dict, *, key: str, submit_label: str = "Adicionar período"
) -> bool:
    today = date.today()
    default_start = date(today.year, 1 if today.month <= 6 else 7, 1)
    default_end = date(today.year, 6, 30) if today.month <= 6 else date(today.year, 12, 31)
    with st.form(key, border=False):
        name = st.text_input("Nome *", placeholder="Ex.: 2026.2")
        date_columns = st.columns(2)
        start_date = date_columns[0].date_input(
            "Data inicial", value=default_start, format="DD/MM/YYYY"
        )
        end_date = date_columns[1].date_input("Data final", value=default_end, format="DD/MM/YYYY")
        st.caption(REQUIRED_NOTE)
        submitted = st.form_submit_button(submit_label, type="primary", width="stretch")
    if not submitted:
        return False
    try:
        services.academic_periods.create(
            user_id=user["_id"],
            current_period_id=user.get("current_academic_period_id"),
            name=name,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        show_action_error("adicionar o período acadêmico", error)
    else:
        return True
    return False


def new_subject_form(
    services: ApplicationServices,
    user: dict,
    *,
    key: str,
    submit_label: str = "Adicionar disciplina",
) -> Any | None:
    with st.form(key, border=False):
        subject_name = st.text_input("Nome *", placeholder="Ex.: Banco de Dados")
        color = st.color_picker("Cor", "#5E6AD2", help="Ajuda a reconhecer a disciplina na agenda.")
        st.caption(REQUIRED_NOTE)
        submitted = st.form_submit_button(submit_label, type="primary", width="stretch")
    if not submitted:
        return None
    try:
        return services.subjects.create(
            user["_id"], user.get("current_academic_period_id"), subject_name, color
        )
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        show_action_error("adicionar a disciplina", error)
    return None


def class_meeting_form(
    services: ApplicationServices,
    user: dict,
    *,
    subject_id: Any,
    key: str,
    meeting: dict | None = None,
    submit_label: str | None = None,
) -> bool:
    """Cria (sem ``meeting``) ou edita um horário de aula da disciplina."""
    with st.form(key, border=False):
        weekday_name = st.selectbox(
            "Dia da semana *", WEEKDAYS, index=meeting["weekday"] if meeting else 0
        )
        time_columns = st.columns(2)
        start_time = time_columns[0].time_input(
            "Início *",
            value=time.fromisoformat(meeting["start_time"]) if meeting else time(8, 0),
            step=900,
        )
        end_time = time_columns[1].time_input(
            "Fim *",
            value=time.fromisoformat(meeting["end_time"]) if meeting else time(9, 30),
            step=900,
        )
        location = st.text_input(
            "Local (opcional)",
            value=meeting.get("location", "") if meeting else "",
            placeholder="Ex.: Bloco B, sala 204",
        )
        st.caption(REQUIRED_NOTE)
        submitted = st.form_submit_button(
            submit_label or ("Salvar alterações" if meeting else "Adicionar aula"),
            type="primary",
            width="stretch",
        )
    if not submitted:
        return False
    values = dict(
        user_id=user["_id"],
        academic_period_id=user.get("current_academic_period_id"),
        subject_id=subject_id,
        weekday=WEEKDAYS.index(weekday_name),
        start_time=start_time,
        end_time=end_time,
        location=location,
    )
    try:
        if meeting:
            services.class_meetings.update(meeting_id=meeting["_id"], **values)
        else:
            services.class_meetings.create(**values)
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        show_action_error("salvar o horário de aula", error)
    else:
        return True
    return False


def new_topic_form(
    services: ApplicationServices,
    user: dict,
    *,
    subject_id: Any,
    roots: list[dict],
    key: str,
    submit_label: str = "Adicionar conteúdo",
) -> bool:
    with st.form(key, border=False):
        parent_id = None
        if roots:
            roots_by_id = {topic["_id"]: topic for topic in roots}
            parent_id = st.selectbox(
                "Tipo",
                [None, *roots_by_id],
                format_func=lambda value: (
                    "Tópico principal"
                    if value is None
                    else f"Subtópico de {roots_by_id[value]['title']}"
                ),
            )
        title = st.text_input("Nome do conteúdo *", placeholder="Ex.: JOIN e relacionamentos")
        status_column, difficulty_column = st.columns(2)
        status = status_column.selectbox(
            "Status", list(STATUS_LABELS), format_func=lambda value: STATUS_LABELS[value]
        )
        difficulty = difficulty_column.selectbox(
            "Dificuldade",
            list(DIFFICULTY_LABELS),
            index=1,
            format_func=lambda value: DIFFICULTY_LABELS[value],
        )
        st.caption(REQUIRED_NOTE)
        submitted = st.form_submit_button(submit_label, type="primary", width="stretch")
    if not submitted:
        return False
    try:
        services.topics.create(
            user_id=user["_id"],
            academic_period_id=user.get("current_academic_period_id"),
            subject_id=subject_id,
            parent_id=parent_id,
            title=title,
            status=status,
            difficulty=difficulty,
        )
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        show_action_error("adicionar o conteúdo", error)
    else:
        return True
    return False
