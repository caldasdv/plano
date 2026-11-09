"""Tela de disciplinas."""

import streamlit as st

from src.ui.context import load_current_period_subjects, load_legacy_subjects, load_page_context
from src.ui.components.page_header import render_page_header
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.forms import new_subject_form
from src.ui.sections.periods import render_period_bar
from src.ui.sections.subject_cards import render_subject_cards, render_subject_dialog
from src.ui.onboarding import render_subjects_next_step
from src.ui.sidebar import render_account_sidebar


@st.dialog("Adicionar disciplina", width="small")
def new_subject_dialog() -> None:
    if new_subject_form(services, user, key="new_subject") is not None:
        set_success_flash("Disciplina adicionada. Agora cadastre os horários e os conteúdos dela.")
        st.rerun()


services, user, _subjects = load_page_context()
render_account_sidebar(services, user)
render_page_header(
    "ORGANIZAÇÃO",
    "Disciplinas",
    "Cadastre as disciplinas do período e, em cada uma, os conteúdos e os horários de aula.",
)
render_period_bar(services, user)

current_period_id = user.get("current_academic_period_id")
subjects = load_current_period_subjects(services, user, retry_key="retry_subjects_loading")
legacy_subjects = load_legacy_subjects(services, user, retry_key="retry_legacy_subjects_loading")
if current_period_id is None:
    if legacy_subjects:
        st.subheader("Disciplinas sem período")
        st.caption(
            "Estes registros antigos foram preservados e não serão associados automaticamente."
        )
        for subject in legacy_subjects:
            st.write(f"- {subject['name']}")
    st.stop()

render_subjects_next_step(services, user, subjects)
heading_column, action_column = st.columns([3, 1], vertical_alignment="bottom")
heading_column.header("Suas disciplinas", anchor=False)
if action_column.button(
    "Adicionar disciplina",
    type="primary" if not subjects else "secondary",
    icon=":material/add:",
    width="stretch",
    key="subjects_add",
):
    new_subject_dialog()
if not subjects:
    st.info("Nenhuma disciplina no período atual. Use \"Adicionar disciplina\" para começar.")
else:
    render_subject_cards(services, user, subjects)
    render_subject_dialog(services, user, subjects)


if legacy_subjects:
    st.divider()
    st.subheader("Disciplinas sem período")
    st.caption(
        "Estes registros antigos continuam preservados e identificando sessões existentes. "
        "Eles não foram associados automaticamente para evitar colocá-los no semestre errado."
    )
    try:
        periods = services.academic_periods.list_for_user(user["_id"])
    except Exception as error:
        show_action_error("carregar os períodos para associação", error)
        if st.button("Tentar novamente", key="retry_subject_assignment_periods"):
            st.rerun()
        st.stop()
    active_periods = [period for period in periods if period.get("status") == "ACTIVE"]
    periods_by_id = {period["_id"]: period for period in active_periods}
    if not active_periods:
        st.info("Crie um período ativo para associar estas disciplinas.")
    for subject in legacy_subjects:
        with st.container(border=True):
            st.write(f"**{subject['name']}**")
            if not active_periods:
                continue
            with st.form(f"assign_legacy_subject_{subject['_id']}"):
                destination_period_id = st.selectbox(
                    "Período de destino",
                    list(periods_by_id),
                    format_func=lambda value: periods_by_id[value]["name"],
                    key=f"legacy_subject_period_{subject['_id']}",
                )
                confirmed = st.checkbox(
                    "Confirmo que esta disciplina pertence ao período escolhido.",
                    key=f"confirm_legacy_subject_{subject['_id']}",
                )
                assign_submitted = st.form_submit_button(
                    "Associar ao período", type="primary"
                )
            if assign_submitted:
                if not confirmed:
                    st.error("Confirme o período escolhido antes de associar.")
                    continue
                try:
                    services.subjects.assign_legacy_to_period(
                        user["_id"], subject["_id"], destination_period_id
                    )
                except ValueError as error:
                    st.error(str(error))
                except Exception as error:
                    show_action_error("associar a disciplina ao período", error)
                else:
                    set_success_flash("Disciplina associada ao período escolhido.")
                    st.rerun()
