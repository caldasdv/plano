"""Semana: sessões de estudo e aulas da grade na mesma visão."""

from datetime import date, timedelta

import streamlit as st

from src.domain.session_rules import effective_status
from src.ui.components.page_header import render_page_header
from src.ui.components.session_card import render_session_card
from src.ui.components.session_dialog import open_session_dialog
from src.ui.components.study_agenda import render_study_agenda
from src.ui.components.study_rhythm import render_study_rhythm
from src.ui.context import load_page_context, load_page_sessions
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.sidebar import render_account_sidebar


services, user, subjects = load_page_context()
render_account_sidebar(services, user)

render_page_header(
    "PLANEJAMENTO",
    "Semana",
    "Suas sessões de estudo e aulas da semana. Selecione uma sessão para concluir, editar ou excluir.",
)


def complete_session(session: dict) -> None:
    try:
        services.sessions.complete(session["_id"], user["_id"])
    except Exception as error:
        show_action_error("concluir a sessão", error)
    else:
        set_success_flash("Sessão concluída.", undo_session_id=session["_id"], user_id=user["_id"])
        st.rerun()


if "weekly_week_offset" not in st.session_state:
    st.session_state["weekly_week_offset"] = 0
navigation_columns = st.columns(3)
if navigation_columns[0].button("Semana anterior", icon=":material/chevron_left:", width="stretch"):
    st.session_state["weekly_week_offset"] -= 1
    st.rerun()
if navigation_columns[1].button(
    "Semana atual",
    width="stretch",
    disabled=st.session_state["weekly_week_offset"] == 0,
):
    st.session_state["weekly_week_offset"] = 0
    st.rerun()
if navigation_columns[2].button("Próxima semana", icon=":material/chevron_right:", width="stretch"):
    st.session_state["weekly_week_offset"] += 1
    st.rerun()

week_start = date.today() - timedelta(days=date.today().weekday()) + timedelta(
    weeks=st.session_state["weekly_week_offset"]
)
week_end = week_start + timedelta(days=6)
sessions = load_page_sessions(
    services,
    user,
    subjects,
    start_date=week_start,
    end_date=week_end,
    retry_key="retry_weekly_sessions",
)
try:
    class_meetings = services.class_meetings.list_for_period(
        user["_id"], user.get("current_academic_period_id"), subjects
    )
except Exception as error:
    show_action_error("carregar as aulas da grade", error)
    class_meetings = []
weekdays = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]

planned_minutes = sum(session["duration"] for session in sessions)
pending_sessions = [
    session for session in sessions if effective_status(session) != "Concluída"
]
st.caption(f"{week_start:%d/%m} a {week_end:%d/%m/%Y}")
render_study_rhythm(sessions, week_start)
summary_columns = st.columns(3)
summary_columns[0].metric("Sessões", len(sessions))
summary_columns[1].metric("Tempo planejado", f"{planned_minutes} min")
summary_columns[2].metric("Pendentes", len(pending_sessions))

if not sessions:
    st.info("Sua semana ainda está vazia. Adicione uma sessão para começar a organizar seus estudos.")
    st.button(
        "Adicionar sessão",
        type="primary",
        icon=":material/add:",
        key="weekly_add_session",
        on_click=open_session_dialog,
    )

if class_meetings:
    st.caption("Blocos tracejados são aulas da sua grade. Para alterá-las, use Disciplinas.")

selected_session_id = render_study_agenda(
    sessions,
    week_start,
    key=f"weekly_agenda_{week_start.isoformat()}",
    dark_mode=st.session_state.get("plan_dark_mode", False),
    class_meetings=class_meetings,
)
if selected_session_id:
    st.session_state["weekly_selected_session_id"] = selected_session_id
selected_session = next(
    (
        session
        for session in sessions
        if str(session["_id"]) == st.session_state.get("weekly_selected_session_id")
    ),
    None,
)
if selected_session:
    st.subheader("Sessão selecionada")
    action = render_session_card(
        selected_session, key=f"weekly_selected_session_{selected_session['_id']}"
    )
    if action == "complete":
        complete_session(selected_session)
    session_key = str(selected_session["_id"])
    edit_column, delete_column, _ = st.columns([1, 1, 2])
    edit_column.button(
        "Editar",
        icon=":material/edit:",
        width="stretch",
        key=f"weekly_edit_{session_key}",
        on_click=open_session_dialog,
        args=(selected_session,),
    )
    if delete_column.button(
        "Excluir", icon=":material/delete:", width="stretch", key=f"weekly_delete_{session_key}"
    ):
        st.session_state["weekly_confirm_delete"] = session_key
    if st.session_state.get("weekly_confirm_delete") == session_key:
        st.warning("Excluir esta sessão? A ação não pode ser desfeita.")
        confirm_column, cancel_column, _ = st.columns([1, 1, 2])
        if confirm_column.button(
            "Confirmar exclusão", type="primary", width="stretch", key="weekly_confirm_delete_yes"
        ):
            try:
                services.sessions.delete(selected_session["_id"], user["_id"])
            except Exception as error:
                show_action_error("excluir a sessão", error)
            else:
                st.session_state.pop("weekly_confirm_delete", None)
                st.session_state.pop("weekly_selected_session_id", None)
                set_success_flash("Sessão excluída.")
                st.rerun()
        if cancel_column.button("Cancelar", width="stretch", key="weekly_confirm_delete_no"):
            st.session_state.pop("weekly_confirm_delete", None)
            st.rerun()
elif sessions:
    st.caption("Selecione uma sessão na agenda para ver os detalhes.")

with st.expander("Ver semana em lista", expanded=False):
    for day_offset, weekday in enumerate(weekdays):
        current_day = week_start + timedelta(days=day_offset)
        day_sessions = [
            session for session in sessions if session["study_date"] == current_day.isoformat()
        ]
        st.markdown(f"**{weekday.title()} · {current_day:%d/%m/%Y}**")
        if not day_sessions:
            st.caption("Nenhuma sessão planejada.")
            continue
        for session in day_sessions:
            action = render_session_card(session, key=f"weekly_list_session_{session['_id']}")
            if action == "complete":
                complete_session(session)
