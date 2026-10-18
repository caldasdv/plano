"""Tela de gerenciamento de períodos acadêmicos."""

from datetime import date

import streamlit as st

from src.ui.context import load_page_context
from src.ui.components.page_header import render_page_header
from src.ui.feedback import set_success_flash, show_action_error
from src.ui.sidebar import render_account_sidebar


services, user, _subjects = load_page_context()
render_account_sidebar(services, user)

render_page_header(
    "ORGANIZAÇÃO ACADÊMICA",
    "Períodos acadêmicos",
    "Organize semestres ou ciclos de estudo e indique qual está em andamento.",
)

try:
    periods = services.academic_periods.list_for_user(user["_id"])
except Exception as error:
    show_action_error("carregar seus períodos acadêmicos", error)
    if st.button("Tentar novamente", key="retry_academic_periods"):
        st.rerun()
    st.stop()

current_period_id = user.get("current_academic_period_id")
active_periods = [period for period in periods if period.get("status") == "ACTIVE"]
current_period = next(
    (period for period in active_periods if period["_id"] == current_period_id), None
)

if current_period:
    with st.container(border=True):
        st.caption("PERÍODO ATUAL")
        st.subheader(current_period["name"])
        st.write(
            f"{date.fromisoformat(current_period['start_date']):%d/%m/%Y} a "
            f"{date.fromisoformat(current_period['end_date']):%d/%m/%Y}"
        )
else:
    st.info("Você ainda não escolheu um período atual. Crie o primeiro período ou selecione um ativo.")

if active_periods:
    st.subheader("Escolher período atual")
    periods_by_id = {period["_id"]: period for period in active_periods}
    selected_period_id = st.selectbox(
        "Período ativo",
        list(periods_by_id),
        index=(
            list(periods_by_id).index(current_period_id)
            if current_period_id in periods_by_id
            else 0
        ),
        format_func=lambda value: periods_by_id[value]["name"],
        key="current_academic_period",
    )
    if st.button(
        "Definir como período atual",
        type="primary",
        disabled=selected_period_id == current_period_id,
    ):
        try:
            services.academic_periods.set_current(user["_id"], selected_period_id)
        except ValueError as error:
            st.error(str(error))
        except Exception as error:
            show_action_error("alterar o período atual", error)
        else:
            set_success_flash("Período atual atualizado.")
            st.rerun()

st.divider()
st.subheader("Adicionar período")
today = date.today()
default_start = date(today.year, 1 if today.month <= 6 else 7, 1)
default_end = date(today.year, 6, 30) if today.month <= 6 else date(today.year, 12, 31)
with st.form("new_academic_period"):
    name = st.text_input("Nome", placeholder="Ex.: 2026.2")
    date_columns = st.columns(2)
    start_date = date_columns[0].date_input(
        "Data inicial", value=default_start, format="DD/MM/YYYY"
    )
    end_date = date_columns[1].date_input(
        "Data final", value=default_end, format="DD/MM/YYYY"
    )
    submitted = st.form_submit_button("Adicionar período", type="primary", width="stretch")

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
        set_success_flash("Período acadêmico adicionado.")
        st.rerun()

st.divider()
st.subheader("Todos os períodos")
if not periods:
    st.info("Nenhum período cadastrado. Use o formulário acima para começar.")
for period in periods:
    with st.container(border=True):
        status = "Atual" if period["_id"] == current_period_id else (
            "Ativo" if period.get("status") == "ACTIVE" else "Arquivado"
        )
        st.write(f"**{period['name']}** · {status}")
        st.caption(
            f"{date.fromisoformat(period['start_date']):%d/%m/%Y} a "
            f"{date.fromisoformat(period['end_date']):%d/%m/%Y}"
        )
        if period.get("status") == "ACTIVE" and period["_id"] != current_period_id:
            archive_key = f"confirm_archive_period_{period['_id']}"
            if st.button("Arquivar", key=f"archive_period_{period['_id']}"):
                st.session_state[archive_key] = True
                st.rerun()
            if st.session_state.get(archive_key):
                st.warning(f"Arquivar **{period['name']}**? O histórico será preservado.")
                with st.container(horizontal=True):
                    if st.button("Confirmar arquivamento", key=f"confirm_{period['_id']}"):
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
                            set_success_flash("Período arquivado.")
                            st.rerun()
                    if st.button("Cancelar", key=f"cancel_{period['_id']}"):
                        st.session_state.pop(archive_key, None)
                        st.rerun()
