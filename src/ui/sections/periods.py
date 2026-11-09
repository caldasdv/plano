"""Período acadêmico: resumo no topo de Disciplinas e diálogo para trocar ou gerenciar."""

from __future__ import annotations

from datetime import date
from html import escape

import streamlit as st

from src.services.container import ApplicationServices
from src.ui.dialog_state import PERIODS_DIALOG, active_dialog, close_dialog, open_dialog
from src.ui.feedback import set_success_flash, show_action_error


def open_periods_dialog() -> None:
    open_dialog(PERIODS_DIALOG)


def close_periods_dialog() -> None:
    close_dialog(PERIODS_DIALOG)


def _date_range(period: dict) -> str:
    return (
        f"{date.fromisoformat(period['start_date']):%d/%m/%Y} a "
        f"{date.fromisoformat(period['end_date']):%d/%m/%Y}"
    )


def find_current_period(services: ApplicationServices, user: dict) -> dict | None:
    current_period_id = user.get("current_academic_period_id")
    if current_period_id is None:
        return None
    try:
        periods = services.academic_periods.list_for_user(user["_id"])
    except Exception:
        return None
    return next((period for period in periods if period["_id"] == current_period_id), None)


def _finish(message: str) -> None:
    close_periods_dialog()
    set_success_flash(message)
    st.rerun()


@st.dialog("Períodos acadêmicos", width="medium", on_dismiss=close_periods_dialog)
def _periods_dialog(services: ApplicationServices, user: dict) -> None:
    try:
        periods = services.academic_periods.list_for_user(user["_id"])
    except Exception as error:
        show_action_error("carregar seus períodos acadêmicos", error)
        return
    current_period_id = user.get("current_academic_period_id")
    active_periods = [period for period in periods if period.get("status") == "ACTIVE"]

    if active_periods:
        st.markdown("**Período atual**")
        periods_by_id = {period["_id"]: period for period in active_periods}
        period_ids = list(periods_by_id)
        selected_period_id = st.selectbox(
            "Período em andamento",
            period_ids,
            index=period_ids.index(current_period_id) if current_period_id in periods_by_id else 0,
            format_func=lambda value: (
                f"{periods_by_id[value]['name']} · {_date_range(periods_by_id[value])}"
            ),
            key="current_academic_period",
        )
        if st.button(
            "Usar este período",
            type="primary",
            width="stretch",
            disabled=selected_period_id == current_period_id,
            key="periods_set_current",
        ):
            try:
                services.academic_periods.set_current(user["_id"], selected_period_id)
            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                show_action_error("alterar o período atual", error)
            else:
                _finish("Período atual atualizado.")

    with st.expander("Adicionar período", icon=":material/add:", expanded=not periods):
        today = date.today()
        default_start = date(today.year, 1 if today.month <= 6 else 7, 1)
        default_end = date(today.year, 6, 30) if today.month <= 6 else date(today.year, 12, 31)
        with st.form("new_academic_period", border=False):
            name = st.text_input("Nome *", placeholder="Ex.: 2026.2")
            date_columns = st.columns(2)
            start_date = date_columns[0].date_input(
                "Data inicial", value=default_start, format="DD/MM/YYYY"
            )
            end_date = date_columns[1].date_input(
                "Data final", value=default_end, format="DD/MM/YYYY"
            )
            st.caption("Campos com \\* são obrigatórios.")
            submitted = st.form_submit_button(
                "Adicionar período", type="primary", width="stretch"
            )
        if submitted:
            try:
                services.academic_periods.create(
                    user_id=user["_id"],
                    current_period_id=current_period_id,
                    name=name,
                    start_date=start_date,
                    end_date=end_date,
                )
            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                show_action_error("adicionar o período acadêmico", error)
            else:
                _finish("Período acadêmico adicionado.")

    archivable = [
        period
        for period in active_periods
        if period["_id"] != current_period_id
    ]
    archived = [period for period in periods if period.get("status") != "ACTIVE"]
    if not archivable and not archived:
        return
    with st.expander("Arquivar ou ver períodos antigos", icon=":material/inventory_2:"):
        for period in archivable:
            archive_key = f"confirm_archive_period_{period['_id']}"
            name_column, action_column = st.columns([3, 1], vertical_alignment="center")
            name_column.markdown(f"**{escape(period['name'])}** · {_date_range(period)}")
            if action_column.button(
                "Arquivar", key=f"archive_period_{period['_id']}", width="stretch"
            ):
                st.session_state[archive_key] = True
            if st.session_state.get(archive_key):
                st.warning(f"Arquivar **{period['name']}**? O histórico será preservado.")
                confirm_column, cancel_column = st.columns(2)
                if confirm_column.button(
                    "Confirmar arquivamento", key=f"confirm_{period['_id']}", width="stretch"
                ):
                    try:
                        services.academic_periods.archive(
                            user["_id"], period["_id"], current_period_id
                        )
                    except ValueError as error:
                        st.error(str(error))
                    except Exception as error:
                        show_action_error("arquivar o período", error)
                    else:
                        st.session_state.pop(archive_key, None)
                        _finish("Período arquivado.")
                if cancel_column.button(
                    "Cancelar", key=f"cancel_{period['_id']}", width="stretch"
                ):
                    st.session_state.pop(archive_key, None)
                    st.rerun(scope="fragment")
        for period in archived:
            st.caption(f"{period['name']} · {_date_range(period)} · arquivado")


def render_periods_dialog(services: ApplicationServices, user: dict) -> None:
    if active_dialog() == PERIODS_DIALOG:
        _periods_dialog(services, user)


def render_period_bar(services: ApplicationServices, user: dict) -> dict | None:
    """Mostra o período atual no topo de Disciplinas com a ação de trocar ou gerenciar."""
    current_period = find_current_period(services, user)
    with st.container(border=True):
        info_column, action_column = st.columns([3, 1], vertical_alignment="center")
        if current_period:
            info_column.markdown(
                f"**Período: {escape(current_period['name'])}**  \n"
                f"{_date_range(current_period)}"
            )
            action_column.button(
                "Trocar ou gerenciar",
                icon=":material/date_range:",
                width="stretch",
                key="subjects_manage_period",
                on_click=open_periods_dialog,
            )
        else:
            info_column.markdown(
                "**Nenhum período em andamento.** Adicione um período, como um semestre, "
                "para organizar suas disciplinas."
            )
            action_column.button(
                "Adicionar período",
                type="primary",
                icon=":material/add:",
                width="stretch",
                key="subjects_manage_period",
                on_click=open_periods_dialog,
            )
    return current_period
