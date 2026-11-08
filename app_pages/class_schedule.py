"""Tela da grade semanal de aulas."""

from datetime import time

import streamlit as st

from src.ui.context import load_current_period_subjects, load_page_context
from src.ui.components.class_timetable import (
    render_class_timetable,
    render_class_timetable_fallback,
)
from src.ui.components.page_header import render_page_header
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.sidebar import render_account_sidebar


services, user, _subjects = load_page_context()
render_account_sidebar(services, user)

WEEKDAYS = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]

render_page_header(
    "ORGANIZAÇÃO ACADÊMICA",
    "Grade de aulas",
    "Cadastre os horários recorrentes das disciplinas do período atual.",
)

current_period_id = user.get("current_academic_period_id")
subjects = load_current_period_subjects(services, user, retry_key="retry_class_schedule_subjects")

if current_period_id is None:
    st.info("Defina um período acadêmico atual antes de montar sua grade.")
    if st.button("Gerenciar períodos acadêmicos", icon=":material/date_range:"):
        st.switch_page("app_pages/academic_periods.py")
    st.stop()

if not subjects:
    st.info("Cadastre ao menos uma disciplina no período atual antes de adicionar aulas.")
    if st.button("Gerenciar disciplinas", icon=":material/menu_book:"):
        st.switch_page("app_pages/subjects.py")
    st.stop()

try:
    meetings = services.class_meetings.list_for_period(
        user["_id"], current_period_id, subjects
    )
except Exception as error:
    show_action_error("carregar sua grade de aulas", error)
    if st.button("Tentar novamente", key="retry_class_schedule"):
        st.rerun()
    st.stop()

subjects_by_id = {subject["_id"]: subject for subject in subjects}
st.divider()
st.subheader("Sua semana")
if not meetings:
    st.info("Sua grade ainda está vazia. Adicione o primeiro horário abaixo.")

timetable_result = render_class_timetable(
    meetings,
    WEEKDAYS,
    key=(
        f"class_timetable_{current_period_id}_"
        f"{st.session_state.get('selected_class_meeting_id', 'none')}_"
        f"{st.session_state.get('class_timetable_reset', 0)}"
    ),
    selected_id=st.session_state.get("selected_class_meeting_id"),
    dark_mode=st.session_state.get("plan_dark_mode", False),
)
deleted_meeting_id = timetable_result[0] if len(timetable_result) > 0 else None
edited_meeting_id = timetable_result[1] if len(timetable_result) > 1 else None
selected_meeting_id = timetable_result[2] if len(timetable_result) > 2 else None
if deleted_meeting_id:
    meeting_by_id = {str(meeting["_id"]): meeting for meeting in meetings}
    deleted_meeting = meeting_by_id.get(str(deleted_meeting_id))
    if deleted_meeting is None:
        st.error("Esse horário não está mais disponível. Atualize a grade e tente novamente.")
        st.stop()
    try:
        services.class_meetings.delete(
            user["_id"], current_period_id, deleted_meeting["_id"]
        )
    except Exception as error:
        show_action_error("remover a aula", error)
    else:
        set_success_flash("Horário removido da grade.")
        st.rerun()

if edited_meeting_id:
    st.session_state["editing_class_meeting_id"] = edited_meeting_id

if selected_meeting_id is not None:
    if selected_meeting_id:
        st.session_state["selected_class_meeting_id"] = str(selected_meeting_id)
    else:
        st.session_state.pop("selected_class_meeting_id", None)
        st.session_state.pop("confirm_delete_class_meeting_id", None)

selected_class_meeting_id = st.session_state.get("selected_class_meeting_id")
selected_meeting = next(
    (meeting for meeting in meetings if str(meeting["_id"]) == str(selected_class_meeting_id)),
    None,
)
if selected_meeting:
    st.subheader("Aula selecionada")
    with st.container(border=True):
        st.markdown(f"### {selected_meeting['subject_name']}")
        detail_columns = st.columns(3)
        detail_columns[0].caption("Dia")
        detail_columns[0].write(WEEKDAYS[selected_meeting["weekday"]])
        detail_columns[1].caption("Horário")
        detail_columns[1].write(
            f"{selected_meeting['start_time']}–{selected_meeting['end_time']}"
        )
        detail_columns[2].caption("Local")
        detail_columns[2].write(selected_meeting.get("location") or "Não informado")
        action_columns = st.columns(2)
        if action_columns[0].button(
            "Editar aula", icon=":material/edit:", width="stretch", key="selected_edit_class"
        ):
            st.session_state["editing_class_meeting_id"] = str(selected_meeting["_id"])
            st.rerun()
        if action_columns[1].button(
            "Excluir aula", icon=":material/delete:", width="stretch", key="selected_delete_class"
        ):
            st.session_state["confirm_delete_class_meeting_id"] = str(selected_meeting["_id"])
            st.rerun()
        if st.session_state.get("confirm_delete_class_meeting_id") == str(selected_meeting["_id"]):
            st.warning("Excluir este horário recorrente? A ação não pode ser desfeita.")
            confirm_columns = st.columns(2)
            if confirm_columns[0].button(
                "Confirmar exclusão", type="primary", width="stretch", key="confirm_selected_delete"
            ):
                try:
                    services.class_meetings.delete(
                        user["_id"], current_period_id, selected_meeting["_id"]
                    )
                except Exception as error:
                    show_action_error("remover a aula", error)
                else:
                    st.session_state.pop("selected_class_meeting_id", None)
                    st.session_state.pop("confirm_delete_class_meeting_id", None)
                    set_success_flash("Horário removido da grade.")
                    st.rerun()
            if confirm_columns[1].button(
                "Cancelar", width="stretch", key="cancel_selected_delete"
            ):
                st.session_state.pop("confirm_delete_class_meeting_id", None)
                st.rerun()

editing_meeting_id = st.session_state.get("editing_class_meeting_id")
editing_meeting = next(
    (meeting for meeting in meetings if str(meeting["_id"]) == editing_meeting_id),
    None,
)
if editing_meeting:
    st.subheader("Editar horário")
    with st.container(border=True):
        with st.form(f"edit_class_meeting_{editing_meeting_id}"):
            edit_subject_id = st.selectbox(
                "Disciplina",
                list(subjects_by_id),
                index=list(subjects_by_id).index(editing_meeting["subject_id"]),
                format_func=lambda value: subjects_by_id[value]["name"],
            )
            edit_weekday = st.selectbox(
                "Dia da semana", WEEKDAYS, index=editing_meeting["weekday"]
            )
            edit_time_columns = st.columns(2)
            edit_start_time = edit_time_columns[0].time_input(
                "Início", value=time.fromisoformat(editing_meeting["start_time"]), step=900
            )
            edit_end_time = edit_time_columns[1].time_input(
                "Fim", value=time.fromisoformat(editing_meeting["end_time"]), step=900
            )
            edit_location = st.text_input(
                "Local (opcional)", value=editing_meeting.get("location", "")
            )
            save_col, cancel_col = st.columns(2)
            save_edit = save_col.form_submit_button(
                "Salvar horário", type="primary", width="stretch"
            )
            cancel_edit = cancel_col.form_submit_button("Cancelar", width="stretch")
        if cancel_edit:
            st.session_state.pop("editing_class_meeting_id", None)
            st.rerun()
        if save_edit:
            try:
                services.class_meetings.update(
                    user_id=user["_id"],
                    academic_period_id=current_period_id,
                    meeting_id=editing_meeting["_id"],
                    subject_id=edit_subject_id,
                    weekday=WEEKDAYS.index(edit_weekday),
                    start_time=edit_start_time,
                    end_time=edit_end_time,
                    location=edit_location,
                )
            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                show_action_error("salvar o horário", error)
            else:
                st.session_state.pop("editing_class_meeting_id", None)
                set_success_flash("Horário atualizado na grade.")
                st.rerun()

render_class_timetable_fallback(meetings, WEEKDAYS)

st.divider()
with st.expander("Adicionar aula recorrente", expanded=not meetings):
    with st.form("new_class_meeting"):
        subject_id = st.selectbox(
            "Disciplina",
            list(subjects_by_id),
            format_func=lambda value: subjects_by_id[value]["name"],
            key="class_schedule_subject",
        )
        weekday_name = st.selectbox("Dia da semana", WEEKDAYS, key="class_schedule_weekday")
        time_columns = st.columns(2)
        start_time = time_columns[0].time_input(
            "Início", value=time(8, 0), step=900, key="class_schedule_start"
        )
        end_time = time_columns[1].time_input(
            "Fim", value=time(9, 30), step=900, key="class_schedule_end"
        )
        location = st.text_input("Local (opcional)", placeholder="Ex.: Bloco B, sala 204")
        submitted = st.form_submit_button(
            "Adicionar à grade", type="primary", width="stretch"
        )

if submitted:
    try:
        services.class_meetings.create(
            user_id=user["_id"],
            academic_period_id=current_period_id,
            subject_id=subject_id,
            weekday=WEEKDAYS.index(weekday_name),
            start_time=start_time,
            end_time=end_time,
            location=location,
        )
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        show_action_error("adicionar a aula", error)
    else:
        set_success_flash("Aula adicionada à grade semanal.")
        st.rerun()
