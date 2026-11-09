"""Tela de progresso e dashboard analítico."""

from datetime import date, timedelta

import streamlit as st

from src.services.report_service import build_subject_summary, build_week_summary
from src.ui.components.page_header import render_page_header
from src.ui.components.chart_summaries import describe_subject_load, describe_week_rhythm
from src.ui.components.progress_charts import subject_progress_figure, weekly_progress_figure
from src.ui.components.progress_summary import render_subject_progress_summary
from src.ui.context import load_current_period_subjects, load_page_context, load_page_sessions
from src.ui.sections.grades import render_grades_section
from src.ui.sections.weekly_goal import render_weekly_goal_section
from src.ui.sidebar import render_account_sidebar


services, user, subjects = load_page_context()
render_account_sidebar(services, user)

render_page_header(
    "ACOMPANHAMENTO",
    "Progresso",
    "Sua meta da semana, o que já foi estudado e como estão as notas.",
)
render_weekly_goal_section(services, user, subjects)

st.header("Estudo da semana", anchor="estudo-da-semana")
filter_week, filter_subject = st.columns(2)
selected_week_day = filter_week.date_input(
    "Escolha um dia da semana",
    value=date.today() - timedelta(days=date.today().weekday()),
    format="DD/MM/YYYY",
    key="progress_week_start",
)
week_start = selected_week_day - timedelta(days=selected_week_day.weekday())
week_end = week_start + timedelta(days=6)
if selected_week_day != week_start:
    st.caption(f"A semana exibida começa na segunda-feira, {week_start:%d/%m/%Y}.")
progress_sessions = load_page_sessions(
    services,
    user,
    subjects,
    start_date=week_start,
    end_date=week_end,
    retry_key="retry_progress_sessions",
)
subjects_by_id = {subject["_id"]: subject for subject in subjects}
subject_options = [None, *subjects_by_id]
selected_subject_id = filter_subject.selectbox(
    "Disciplina",
    subject_options,
    format_func=lambda value: (
        "Todas as disciplinas" if value is None else subjects_by_id[value]["name"]
    ),
    key="progress_subject",
)
selected_subject_name = (
    "Todas as disciplinas"
    if selected_subject_id is None
    else subjects_by_id[selected_subject_id]["name"]
)
st.caption(
    f"Filtros ativos: semana de {week_start:%d/%m/%Y} a {week_end:%d/%m/%Y} "
    f"· {selected_subject_name}."
)
filtered_week_sessions = [
    session for session in progress_sessions
    if selected_subject_id is None or session["subject_id"] == selected_subject_id
]
filtered_subjects = [
    subject for subject in subjects
    if selected_subject_id is None or subject["_id"] == selected_subject_id
]
week_summary = build_week_summary(filtered_week_sessions, week_start)
subject_summary = build_subject_summary(filtered_week_sessions, filtered_subjects)
planned_minutes = sum(row["planejados"] for row in week_summary)
completed_minutes = sum(row["concluídos"] for row in week_summary)
pending_count = sum(row["pendentes"] for row in week_summary)
overdue_count = sum(row["atrasadas"] for row in week_summary)

if not filtered_week_sessions:
    st.info(
        "Não há sessões para os filtros selecionados. Escolha outra semana ou disciplina, "
        "ou adicione uma nova sessão."
    )
else:
    metric_cols = st.columns(4)
    metric_cols[0].metric("Planejados", f"{planned_minutes} min", border=True)
    metric_cols[1].metric("Concluídos", f"{completed_minutes} min", border=True)
    metric_cols[2].metric("Pendências", pending_count, border=True)
    metric_cols[3].metric("Atrasadas", overdue_count, border=True)

    chart_col, table_col = st.columns(2)
    with chart_col:
        with st.container(border=True):
            st.subheader("Carga por disciplina")
            st.caption(describe_subject_load(subject_summary))
            st.plotly_chart(
                subject_progress_figure(
                    subject_summary, dark_mode=bool(user.get("dark_mode", False))
                ),
                width="stretch",
                config={"displayModeBar": False},
            )
    with table_col:
        with st.container(border=True):
            st.subheader("Ritmo ao longo da semana")
            st.caption(describe_week_rhythm(week_summary))
            st.plotly_chart(
                weekly_progress_figure(
                    week_summary, dark_mode=bool(user.get("dark_mode", False))
                ),
                width="stretch",
                config={"displayModeBar": False},
            )

    with st.expander("Ver dados da semana em tabela"):
        st.table(
            [
                {
                    "Dia": row["dia"],
                    "Planejados (min)": row["planejados"],
                    "Concluídos (min)": row["concluídos"],
                    "Pendências": row["pendentes"],
                    "Atrasadas": row["atrasadas"],
                }
                for row in week_summary
            ],
            hide_index=True,
            width="stretch",
        )

st.subheader("Detalhamento por disciplina")
render_subject_progress_summary(subject_summary)

current_subjects = load_current_period_subjects(
    services, user, retry_key="retry_progress_current_subjects"
)
render_grades_section(services, user, current_subjects, selected_subject_id)
