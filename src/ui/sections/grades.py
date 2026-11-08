"""Seção de notas e avaliações (antiga tela Avaliações)."""

from __future__ import annotations

from datetime import date

import streamlit as st

from src.domain.evaluation_rules import EVALUATION_TYPES
from src.services.container import ApplicationServices
from src.ui.components.progress_charts import evaluation_progress_figure
from src.ui.feedback import set_success_flash, show_action_error


@st.dialog("Adicionar avaliação", width="medium")
def new_evaluation_dialog(
    services: ApplicationServices, user: dict, subjects: list[dict]
) -> None:
    subjects_by_id = {subject["_id"]: subject for subject in subjects}
    with st.form("new_evaluation", border=False):
        subject_id = st.selectbox(
            "Disciplina",
            list(subjects_by_id),
            format_func=lambda value: subjects_by_id[value]["name"],
        )
        title = st.text_input("Nome *", placeholder="Ex.: Prova de consultas SQL")
        evaluation_type = st.selectbox("Tipo", EVALUATION_TYPES)
        form_cols = st.columns(3)
        evaluation_date = form_cols[0].date_input("Data", value=date.today(), format="DD/MM/YYYY")
        score = form_cols[1].number_input("Nota obtida", min_value=0.0, value=0.0, step=0.5)
        max_score = form_cols[2].number_input("Nota máxima", min_value=0.5, value=10.0, step=0.5)
        st.caption("Campos com \\* são obrigatórios.")
        submitted = st.form_submit_button("Adicionar avaliação", type="primary", width="stretch")
    if submitted:
        try:
            services.evaluations.create(
                user_id=user["_id"],
                academic_period_id=user.get("current_academic_period_id"),
                subject_id=subject_id,
                title=title,
                evaluation_type=evaluation_type,
                evaluation_date=evaluation_date,
                score=score,
                max_score=max_score,
            )
        except ValueError as error:
            st.error(str(error))
        except Exception as error:
            show_action_error("adicionar a avaliação", error)
        else:
            set_success_flash("Avaliação adicionada.")
            st.rerun()


def render_grades_section(
    services: ApplicationServices,
    user: dict,
    subjects: list[dict],
    selected_subject_id,
) -> None:
    heading_column, action_column = st.columns([3, 1], vertical_alignment="bottom")
    heading_column.header("Notas", anchor="notas")
    period_id = user.get("current_academic_period_id")
    if period_id is None or not subjects:
        st.info("Adicione um período e uma disciplina para registrar avaliações.")
        return
    if action_column.button(
        "Adicionar avaliação", icon=":material/add:", width="stretch", key="progress_add_evaluation"
    ):
        new_evaluation_dialog(services, user, subjects)
    try:
        evaluations = services.evaluations.list_for_period(user["_id"], period_id, subjects)
    except Exception as error:
        show_action_error("carregar suas avaliações", error)
        return

    filtered = [
        item
        for item in evaluations
        if selected_subject_id is None or item["subject_id"] == selected_subject_id
    ]
    graded = [
        item for item in filtered if item.get("score") is not None and item.get("max_score")
    ]
    average = (
        sum(item["score"] / item["max_score"] for item in graded) / len(graded) * 10
        if graded
        else 0
    )
    metric_cols = st.columns(3)
    metric_cols[0].metric("Avaliações", len(filtered), border=True)
    metric_cols[1].metric("Com nota", len(graded), border=True)
    metric_cols[2].metric("Média proporcional", f"{average:.1f}/10" if graded else "—", border=True)

    if not filtered:
        st.info("Ainda não há avaliações aqui. Use \"Adicionar avaliação\" para registrar provas e trabalhos.")
        return
    if graded:
        st.subheader("Evolução das notas")
        st.caption("Notas proporcionais de 0 a 10. Avaliações sem nota ficam fora do gráfico.")
        st.plotly_chart(
            evaluation_progress_figure(graded, dark_mode=bool(user.get("dark_mode", False))),
            width="stretch",
            config={"displayModeBar": False},
            key="evaluation_grade_chart",
        )
    else:
        st.info("As avaliações selecionadas ainda não têm notas registradas.")

    with st.expander(f"Ver histórico de avaliações ({len(filtered)})"):
        for item in filtered:
            with st.container(border=True):
                heading, detail = st.columns([2, 1])
                heading.markdown(f"**{item['title']}**")
                heading.caption(f"{item['type']} · {item['subject_name']}")
                if item.get("score") is None or not item.get("max_score"):
                    detail.metric("Nota", "Pendente")
                    st.caption(f"{item['evaluation_date']} · nota ainda não registrada")
                else:
                    percentage = item["score"] / item["max_score"] * 100
                    detail.metric("Nota", f"{item['score']:g}/{item['max_score']:g}")
                    st.progress(
                        min(percentage / 100, 1.0),
                        text=f"{item['evaluation_date']} · {percentage:.0f}%",
                    )
