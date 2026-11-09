"""Tela de disciplinas."""

from html import escape
import re

import streamlit as st

from src.ui.context import load_current_period_subjects, load_legacy_subjects, load_page_context
from src.ui.components.page_header import render_page_header
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.sections.class_schedule import render_class_schedule_section
from src.ui.sections.periods import render_period_bar
from src.ui.sections.topics import render_topics_section
from src.ui.onboarding import render_plan_session_footer, render_subjects_next_step
from src.ui.sidebar import render_account_sidebar


@st.dialog("Adicionar disciplina", width="small")
def new_subject_dialog(period_id) -> None:
    with st.form("new_subject", border=False):
        subject_name = st.text_input("Nome *", placeholder="Ex.: Banco de Dados")
        color = st.color_picker("Cor", "#5E6AD2", help="Ajuda a reconhecer a disciplina na agenda.")
        st.caption("Campos com \\* são obrigatórios.")
        submitted = st.form_submit_button("Adicionar disciplina", type="primary", width="stretch")
    if submitted:
        try:
            services.subjects.create(user["_id"], period_id, subject_name, color)
        except ValueError as error:
            st.error(str(error))
        except Exception as error:
            show_action_error("adicionar a disciplina", error)
        else:
            set_success_flash("Disciplina adicionada.")
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
heading_column.header("Suas disciplinas", anchor="suas-disciplinas")
if action_column.button(
    "Adicionar disciplina",
    type="primary" if not subjects else "secondary",
    icon=":material/add:",
    width="stretch",
    key="subjects_add",
):
    new_subject_dialog(current_period_id)
if not subjects:
    st.info("Nenhuma disciplina no período atual. Use \"Adicionar disciplina\" para começar.")
else:
    subjects_by_id = {subject["_id"]: subject for subject in subjects}
    detail_subject_id = st.pills(
        "Escolha uma disciplina para ver os conteúdos e os horários de aula",
        list(subjects_by_id),
        format_func=lambda value: subjects_by_id[value]["name"],
        default=next(iter(subjects_by_id)),
        key="subjects_detail",
    )
    if detail_subject_id is None:
        detail_subject_id = next(iter(subjects_by_id))
    subject = subjects_by_id[detail_subject_id]
    color = subject.get("color", "#787774")
    safe_color = color if re.fullmatch(r"#[0-9A-Fa-f]{6}", str(color)) else "#787774"

    with st.container(border=True):
        title_column, edit_column = st.columns([3, 1], vertical_alignment="center")
        title_column.markdown(
            f'<h2 class="plan-subject-title"><span class="subject-dot" '
            f'style="background:{safe_color}" aria-hidden="true"></span>'
            f"{escape(subject['name'])}</h2>",
            unsafe_allow_html=True,
        )
        with edit_column.popover("Editar disciplina", icon=":material/edit:", width="stretch"):
            with st.form(f"edit_subject_{subject['_id']}", border=False):
                edited_name = st.text_input("Nome da disciplina", value=subject["name"])
                edited_color = st.color_picker("Cor da disciplina", safe_color)
                save_edit = st.form_submit_button(
                    "Salvar alterações", type="primary", width="stretch"
                )
            if save_edit:
                try:
                    services.subjects.update(
                        user["_id"], subject["_id"], current_period_id, edited_name, edited_color
                    )
                except ValueError as error:
                    st.error(str(error))
                except Exception as error:
                    show_action_error("salvar a disciplina", error)
                else:
                    set_success_flash("Disciplina atualizada.")
                    st.rerun()

        st.subheader("Conteúdos")
        render_topics_section(services, user, subjects, detail_subject_id)
        st.subheader("Horários de aula")
        st.caption("As aulas também aparecem na Semana, junto com as sessões de estudo.")
        render_class_schedule_section(services, user, subjects, detail_subject_id)
        render_plan_session_footer(subject)


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
