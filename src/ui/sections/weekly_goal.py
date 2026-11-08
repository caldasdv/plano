"""Seção de meta semanal e plano de foco (antiga tela Metas)."""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from src.services.container import ApplicationServices
from src.services.report_service import build_adaptive_goal_plan
from src.ui.context import load_page_sessions
from src.ui.feedback import set_success_flash, show_action_error


def render_weekly_goal_section(
    services: ApplicationServices, user: dict, subjects: list[dict]
) -> None:
    st.header("Meta da semana", anchor="meta-da-semana")
    week_start = date.today() - timedelta(days=date.today().weekday())
    week_end = week_start + timedelta(days=6)
    sessions = load_page_sessions(
        services,
        user,
        subjects,
        start_date=week_start,
        end_date=week_end,
        retry_key="retry_goals_sessions",
    )
    completed_minutes = sum(
        int(session["duration"]) for session in sessions if session.get("status") == "Concluída"
    )
    goal_minutes = int(user.get("weekly_goal_minutes", 300))
    progress = min(completed_minutes / goal_minutes, 1.0) if goal_minutes else 0.0

    metric_columns = st.columns(3)
    metric_columns[0].metric(
        "Meta semanal", f"{goal_minutes // 60}h {goal_minutes % 60:02d}", border=True
    )
    metric_columns[1].metric("Concluído", f"{completed_minutes} min", border=True)
    metric_columns[2].metric("Progresso", f"{progress * 100:.0f}%", border=True)
    st.progress(progress, text=f"{completed_minutes} de {goal_minutes} minutos da meta")

    with st.popover("Ajustar meta semanal", icon=":material/tune:"):
        st.caption("Quantas horas você quer estudar por semana? Fica salvo na sua conta.")
        with st.form("weekly_goal_form", border=False):
            goal_hours = st.number_input(
                "Horas por semana",
                min_value=1.0,
                max_value=80.0,
                value=goal_minutes / 60,
                step=0.5,
            )
            submitted = st.form_submit_button("Salvar meta", type="primary", width="stretch")
        if submitted:
            try:
                services.users.update_weekly_goal(user["_id"], goal_hours)
            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                show_action_error("atualizar sua meta", error)
            else:
                set_success_flash("Meta semanal atualizada.")
                st.rerun()

    try:
        evaluations = services.evaluations.list_for_period(
            user["_id"], user.get("current_academic_period_id"), subjects
        )
        topics_by_subject = {
            subject["_id"]: services.topics.list_for_subject(
                user["_id"], user.get("current_academic_period_id"), subject["_id"]
            )
            for subject in subjects
        }
    except Exception as error:
        show_action_error("calcular suas prioridades", error)
        evaluations = []
        topics_by_subject = {}

    st.subheader("Plano de foco")
    st.caption("Uma sugestão de como distribuir a meta, com base em notas, dificuldade e pendências.")
    strategy = st.selectbox(
        "O que deve pesar mais?",
        ["Equilibrada", "Priorizar notas", "Priorizar dificuldade", "Priorizar pendências"],
        key="goal_strategy",
    )
    adaptive_plan = build_adaptive_goal_plan(
        subjects, topics_by_subject, evaluations, sessions, goal_minutes, strategy
    )
    if adaptive_plan:
        st.table(
            [
                {
                    "Disciplina": row["disciplina"],
                    "Foco sugerido": f"{row['minutos']} min",
                    "Por quê": row["motivo"],
                }
                for row in adaptive_plan
            ],
            hide_index=True,
            width="stretch",
        )
