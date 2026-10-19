"""Tela de progresso e dashboard analítico."""

from datetime import date, timedelta

import streamlit as st

from src.services.report_service import (
    build_evaluation_summary,
    build_subject_summary,
    build_week_summary,
)
from src.ui.components.page_header import render_flow_actions, render_page_header
from src.ui.components.progress_charts import subject_progress_figure, weekly_progress_figure
from src.ui.components.progress_summary import render_subject_progress_summary
from src.ui.context import load_page_context, load_page_sessions
from src.ui.feedback import show_action_error
from src.ui.sidebar import render_account_sidebar


services, user, subjects = load_page_context()
render_account_sidebar(services, user)

render_page_header("ACOMPANHAMENTO", "Seu progresso", "Entenda sua carga de estudos e o que já foi concluído.")
render_flow_actions("Progresso")
selected_week_day = st.date_input(
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
try:
    evaluations = services.evaluations.list_for_period(
        user["_id"], user.get("current_academic_period_id"), subjects
    )
except Exception as error:
    show_action_error("carregar sua análise de avaliações", error)
    evaluations = []
subjects_by_id = {subject["_id"]: subject for subject in subjects}
subject_options = [None, *subjects_by_id]
selected_subject_id = st.selectbox(
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
            st.caption("Minutos planejados e concluídos. Passe o cursor para ver os valores.")
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
            st.caption("Compare a carga planejada com o que foi concluído em cada dia.")
            st.plotly_chart(
                weekly_progress_figure(
                    week_summary, dark_mode=bool(user.get("dark_mode", False))
                ),
                width="stretch",
                config={"displayModeBar": False},
            )

    with st.expander("Ver dados da semana em tabela"):
        st.dataframe(
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

st.subheader("Análise de avaliações")
evaluation_summary = build_evaluation_summary(evaluations, filtered_subjects)
if not evaluation_summary:
    st.info("Registre provas, trabalhos ou exercícios para visualizar sua análise de notas.")
else:
    st.dataframe(
        [
            {
                "Disciplina": row["disciplina"],
                "Avaliações": row["avaliacoes"],
                "Média": f"{row['media']:.1f}/10",
                "Aproveitamento": f"{row['aproveitamento'] * 100:.0f}%",
            }
            for row in evaluation_summary
        ],
        hide_index=True,
        width="stretch",
    )

st.subheader("Detalhamento por disciplina")
render_subject_progress_summary(subject_summary)
