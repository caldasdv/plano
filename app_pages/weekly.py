"""Visão semanal com ações rápidas."""

from datetime import date, timedelta

import streamlit as st

from src.domain.session_rules import effective_status
from src.ui.components.session_card import render_session_card
from src.ui.components.study_agenda import render_study_agenda
from src.ui.context import load_page_context, load_page_sessions
from src.ui.components.page_header import render_flow_actions, render_page_header
from src.ui.feedback import show_action_error
from src.ui.feedback import set_success_flash
from src.ui.sidebar import render_account_sidebar


services, user, subjects = load_page_context()
render_account_sidebar(services, user)

render_page_header("PLANEJAMENTO", "Visão semanal", "Revise sua carga de estudos e conclua sessões rapidamente.")
render_flow_actions("Semana")

if "weekly_week_offset" not in st.session_state:
    st.session_state["weekly_week_offset"] = 0
navigation_columns = st.columns(3)
if navigation_columns[0].button("Semana anterior", icon=":material/chevron_left:", width="stretch"):
    st.session_state["weekly_week_offset"] -= 1
    st.rerun()
if navigation_columns[1].button("Semana atual", width="stretch"):
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
summary_columns = st.columns(3)
summary_columns[0].metric("Sessões", len(sessions))
summary_columns[1].metric("Tempo planejado", f"{planned_minutes} min")
summary_columns[2].metric("Pendentes", len(pending_sessions))

if not sessions:
    st.info("Sua semana ainda está vazia. Crie uma sessão para começar a organizar seus estudos.")
    if st.button("Criar nova sessão", type="primary", icon=":material/add_circle:"):
        st.switch_page("app_pages/new_session.py")

selected_session_id = render_study_agenda(
    sessions,
    week_start,
    key=f"weekly_agenda_{week_start.isoformat()}",
    dark_mode=st.session_state.get("plan_dark_mode", False),
)
selected_session = next(
    (session for session in sessions if str(session["_id"]) == selected_session_id),
    None,
)
if selected_session:
    st.subheader("Sessão selecionada")
    action = render_session_card(
        selected_session, key=f"weekly_selected_session_{selected_session['_id']}"
    )
    if action == "complete":
        try:
            services.sessions.complete(selected_session["_id"], user["_id"])
        except Exception as error:
            show_action_error("concluir a sessão", error)
        else:
            set_success_flash("Sessão concluída.")
            st.rerun()
else:
    st.caption("Selecione uma sessão na grade para ver os detalhes e concluir o estudo.")

with st.expander("Abrir lista detalhada", expanded=False):
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
                try:
                    services.sessions.complete(session["_id"], user["_id"])
                except Exception as error:
                    show_action_error("concluir a sessão", error)
                else:
                    set_success_flash("Sessão concluída.")
                    st.rerun()
