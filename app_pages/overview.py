"""Tela de visão geral."""

from datetime import date, timedelta

import streamlit as st

from src.domain.session_rules import effective_status
from src.ui.components.session_card import render_session_card
from src.ui.components.study_rhythm import render_study_rhythm
from src.ui.components.page_header import render_flow_actions, render_page_header
from src.ui.context import load_page_context, load_page_sessions
from src.ui.sidebar import render_account_sidebar


services, user, subjects = load_page_context()
render_account_sidebar(services, user)

render_page_header(
    "SEMANA DE ESTUDOS",
    f"Olá, {user['name']}",
    "Aqui está o que você planejou para os próximos dias.",
)
render_flow_actions("Hoje")

week_start = date.today() - timedelta(days=date.today().weekday())
week_end = week_start + timedelta(days=6)
selected_date = st.date_input("Ver dia", value=date.today(), format="DD/MM/YYYY", key="overview_date")
week_sessions = load_page_sessions(
    services,
    user,
    subjects,
    start_date=week_start,
    end_date=week_end,
    retry_key="retry_overview_sessions",
)

pending = [session for session in week_sessions if effective_status(session) in ("Pendente", "Atrasada")]
completed = [session for session in week_sessions if effective_status(session) == "Concluída"]
completed_minutes = sum(
    session["duration"] for session in week_sessions if effective_status(session) == "Concluída"
)
goal_minutes = int(user.get("weekly_goal_minutes", 300))

st.markdown(
    f"""
    <section class="plan-overview-hero" aria-label="Resumo da semana">
        <div class="plan-overview-hero-copy">
            <span class="plan-overview-hero-kicker">SEU RITMO, SUA SEMANA</span>
            <h2>Pequenos blocos.<br><em>Um semestre inteiro.</em></h2>
            <p>Você já tem um mapa. Agora é só escolher o próximo passo.</p>
        </div>
        <div class="plan-overview-orbit plan-overview-orbit-a"></div>
        <div class="plan-overview-orbit plan-overview-orbit-b"></div>
        <div class="plan-overview-hero-stat">
            <span>pulso da semana</span>
            <strong>{completed_minutes}<small> min</small></strong>
            <div class="plan-overview-hero-track"><i style="width:{min(completed_minutes / goal_minutes * 100, 100) if goal_minutes else 0:.0f}%"></i></div>
            <small>{len(completed)} sessões concluídas</small>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

render_study_rhythm(week_sessions, week_start)
goal_progress = min(completed_minutes / goal_minutes, 1.0) if goal_minutes else 0.0

with st.container(border=True):
    goal_heading, goal_value = st.columns([2, 1])
    goal_heading.markdown("#### Meta da semana")
    goal_value.metric("Progresso", f"{completed_minutes} / {goal_minutes} min")
    st.progress(goal_progress, text=f"{goal_progress * 100:.0f}% da meta semanal")

st.markdown(
    '<section class="plan-quick-actions" aria-label="Ações rápidas">'
    '<span>O que você quer fazer agora?</span></section>',
    unsafe_allow_html=True,
)

quick_columns = st.columns(3)
quick_columns[0].button("Começar uma sessão", icon=":material/play_arrow:", width="stretch", key="overview_quick_session")
quick_columns[1].button("Revisar a semana", icon=":material/calendar_view_week:", width="stretch", key="overview_quick_week")
quick_columns[2].button("Organizar conteúdos", icon=":material/account_tree:", width="stretch", key="overview_quick_topics")

st.success("Tudo em dia por aqui. Você pode planejar a próxima sessão.")
st.markdown('<div class="plan-overview-divider"></div>', unsafe_allow_html=True)

day_sessions = [session for session in week_sessions if session["study_date"] == selected_date.isoformat()]
weekdays = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]

st.markdown(
    f'<h2 class="plan-overview-day-title">{weekdays[selected_date.weekday()]}, '
    f'{selected_date.day:02d}/{selected_date.month:02d}</h2>',
    unsafe_allow_html=True,
)

for row in day_sessions:
    render_session_card(row, key=f"overview_session_{row['_id']}")