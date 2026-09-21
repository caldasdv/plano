"""Tela de disciplinas."""

from html import escape
import re

import streamlit as st

from src.ui.context import (
    load_current_period_subjects,
    load_legacy_subjects,
    load_page_context,
)
from src.ui.components.page_header import render_page_header
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.sidebar import render_account_sidebar


services, user, _all_subjects = load_page_context()
render_account_sidebar(services, user)

current_period_id = user.get("current_academic_period_id")
subjects = load_current_period_subjects(
    services, user, retry_key="retry_current_period_subjects"
)
legacy_subjects = load_legacy_subjects(
    services, user, retry_key="retry_legacy_subjects"
)

render_page_header(
    "ORGANIZAÇÃO",
    "Disciplinas",
    "Organize as disciplinas do período atual e use cores para reconhecê-las rapidamente.",
)
if current_period_id is None:
    st.info("Defina um período acadêmico atual antes de adicionar disciplinas.")
    if st.button("Gerenciar períodos acadêmicos", icon=":material/date_range:"):
        st.switch_page("app_pages/academic_periods.py")
    if legacy_subjects:
        st.subheader("Disciplinas sem período")
        st.caption(
            "Estes registros antigos foram preservados e não serão associados automaticamente."
        )
        for subject in legacy_subjects:
            st.write(f"- {subject['name']}")
    st.stop()

st.subheader("Disciplinas do período atual")
if not subjects:
    st.info("Nenhuma disciplina cadastrada no período atual. Adicione a primeira abaixo.")
else:
    subject_columns = st.columns(2)
    for index, subject in enumerate(subjects):
        color = subject.get("color", "#787774")
        safe_color = color if re.fullmatch(r"#[0-9A-Fa-f]{6}", color) else "#787774"
        with subject_columns[index % 2]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="plan-subject-swatch" style="background:{safe_color}" '
                    f'aria-label="Cor da disciplina {escape(safe_color)}"></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{escape(subject['name'])}**")
                st.caption(f"Cor {safe_color}")
                if st.button(
                    "Editar disciplina",
                    key=f"edit_subject_{subject['_id']}",
                    icon=":material/edit:",
                    width="stretch",
                ):
                    st.session_state["editing_subject_id"] = subject["_id"]
                    st.rerun()

editing_subject_id = st.session_state.get("editing_subject_id")
editing_subject = next(
    (subject for subject in subjects if subject["_id"] == editing_subject_id), None
)
if editing_subject:
    st.divider()
    with st.container(border=True):
        st.subheader(f"Editar {editing_subject['name']}")
        with st.form(f"edit_subject_{editing_subject['_id']}"):
            edited_name = st.text_input("Nome da disciplina", value=editing_subject["name"])
            edited_color = st.color_picker(
                "Cor da disciplina", editing_subject.get("color", "#787774")
            )
            save_col, cancel_col = st.columns(2)
            save_edit = save_col.form_submit_button(
                "Salvar alterações", type="primary", width="stretch"
            )
            cancel_edit = cancel_col.form_submit_button("Cancelar", width="stretch")
        if cancel_edit:
            st.session_state.pop("editing_subject_id", None)
            st.rerun()
        if save_edit:
            try:
                services.subjects.update(
                    user["_id"],
                    editing_subject["_id"],
                    current_period_id,
                    edited_name,
                    edited_color,
                )
            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                show_action_error("salvar a disciplina", error)
            else:
                st.session_state.pop("editing_subject_id", None)
                set_success_flash("Disciplina atualizada.")
                st.rerun()

st.divider()
with st.form("new_subject"):
    subject_name = st.text_input("Nome da nova disciplina")
    color = st.color_picker("Cor", "#5E6AD2")
    if st.form_submit_button("Adicionar disciplina", type="primary", width="stretch"):
        try:
            services.subjects.create(
                user["_id"], current_period_id, subject_name, color
            )
        except ValueError as error:
            st.error(str(error))
        except Exception as error:
            show_action_error("adicionar a disciplina", error)
        else:
            set_success_flash("Disciplina adicionada.")
            st.rerun()

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
