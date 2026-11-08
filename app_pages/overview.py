"""Tela de visão geral."""

from datetime import date, timedelta

import streamlit as st

from src.domain.session_rules import effective_status
from src.ui.components.session_card import render_session_card
from src.ui.components.study_rhythm import render_study_rhythm
from src.ui.components.page_header import render_page_header
from src.ui.components.session_dialog import render_new_session_button
from src.ui.navigation import PERIODS, PROGRESS, SUBJECTS
from src.ui.context import load_current_period_subjects, load_page_context, load_page_sessions
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.sidebar import render_account_sidebar


services, user, subjects = load_page_context()
render_account_sidebar(services, user)

render_page_header(
    "SEMANA DE ESTUDOS",
    f"Olá, {user['name']}",
    "Aqui está o que você planejou para os próximos dias.",
)

if user.get("current_academic_period_id") is None:
    with st.container(border=True):
        st.subheader("Vamos preparar seu plano")
        st.write("Crie um período acadêmico para depois adicionar disciplinas e sessões de estudo.")
        if st.button("Adicionar período acadêmico", type="primary", icon=PERIODS.icon):
            st.switch_page(PERIODS.path)
    st.stop()

current_subjects = load_current_period_subjects(
    services, user, retry_key="retry_overview_subjects"
)
if not current_subjects:
    with st.container(border=True):
        st.subheader("Seu período está pronto")
        st.write("Adicione sua primeira disciplina para começar a planejar sessões de estudo.")
        if st.button("Adicionar disciplina", type="primary", icon=SUBJECTS.icon):
            st.switch_page(SUBJECTS.path)
    st.stop()

render_new_session_button("overview_new_session")

week_start = date.today() - timedelta(days=date.today().weekday())
week_end = week_start + timedelta(days=6)
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
        <div class="plan-overview-orbit plan-overview-orbit-a" aria-hidden="true"></div>
        <div class="plan-overview-orbit plan-overview-orbit-b" aria-hidden="true"></div>
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

with st.container(border=True, key="overview_weekly_goal"):
    goal_heading, goal_value = st.columns([2, 1])
    goal_heading.markdown("#### Meta da semana")
    goal_heading.caption("Seu ritmo de estudo em relação ao objetivo definido.")
    goal_value.metric("Progresso", f"{completed_minutes} / {goal_minutes} min")
    st.progress(goal_progress, text=f"{goal_progress * 100:.0f}% da meta semanal")
    st.page_link(PROGRESS.path, label="Ajustar meta em Progresso", icon=":material/tune:")

if not pending:
    st.success("Tudo em dia por aqui. Você pode planejar a próxima sessão.")
st.markdown('<div class="plan-overview-divider"></div>', unsafe_allow_html=True)

selected_date = st.date_input("Ver dia", value=date.today(), format="DD/MM/YYYY", key="overview_date")

if week_start <= selected_date <= week_end:
    day_sessions = [session for session in week_sessions if session["study_date"] == selected_date.isoformat()]
else:
    day_sessions = load_page_sessions(
        services,
        user,
        subjects,
        start_date=selected_date,
        end_date=selected_date,
        retry_key="retry_overview_day",
    )
weekdays = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]

st.markdown(
    f'<h2 class="plan-overview-day-title">{weekdays[selected_date.weekday()]}, '
    f'{selected_date.day:02d}/{selected_date.month:02d}</h2>',
    unsafe_allow_html=True,
)

if not day_sessions:
    st.info("Nenhuma sessão planejada para este dia. Use \"Nova sessão\" para adicionar uma.")

for row in day_sessions:
    action = render_session_card(row, key=f"overview_session_{row['_id']}")
    if action == "complete":
        try:
            services.sessions.complete(row["_id"], user["_id"])
        except Exception as error:
            show_action_error("concluir a sessão", error)
        else:
            set_success_flash("Sessão concluída.", undo_session_id=row["_id"], user_id=user["_id"])
            st.rerun()
