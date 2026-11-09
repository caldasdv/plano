"""Tour de boas-vindas, ajuda e "Primeiros passos".

O tour abre sozinho no primeiro acesso, uma vez, e pode ser revisto pela Ajuda.
Pular, terminar ou fechar o tour grava ``onboarding_completed_at`` na conta.
"""

from __future__ import annotations

import streamlit as st

from src.domain.onboarding_rules import OnboardingStep, build_onboarding_steps, next_step
from src.services.container import ApplicationServices
from src.ui.components.session_dialog import open_session_dialog
from src.ui.dialog_state import (
    HELP_DIALOG,
    TOUR_DIALOG,
    active_dialog,
    close_dialog,
    open_dialog,
)
from src.ui.feedback import show_action_error
from src.ui.navigation import PROGRESS, SUBJECTS, TODAY, WEEK
from src.ui.sections.periods import open_periods_dialog


_AUTO_OPENED_KEY = "plan_tour_auto_opened"
_PENDING_COMPLETION_KEY = "plan_tour_pending_completion"

TOUR_STEPS = (
    (
        "Bem-vindo ao Plano",
        "O Plano ajuda você a transformar o semestre em pequenos blocos de estudo. "
        "O caminho é sempre o mesmo:\n\n"
        "1. **Disciplinas**: cadastre o período, as matérias, os conteúdos e as aulas.\n"
        "2. **Semana**: planeje quando vai estudar.\n"
        "3. **Hoje**: veja o que fazer agora e conclua as sessões.\n"
        "4. **Progresso**: acompanhe a meta, a carga por matéria e as notas.",
    ),
    (
        f"{TODAY.title}: o que fazer agora",
        "É a tela inicial. No topo fica o botão **Nova sessão**. Abaixo aparecem a meta "
        "da semana e as sessões do dia escolhido.\n\n"
        "Terminou de estudar? Use **Concluir** no cartão da sessão. Se clicar sem querer, "
        "o aviso no topo traz **Desfazer**.",
    ),
    (
        f"{WEEK.title}: planejar os próximos dias",
        "A agenda mostra suas sessões e as aulas da semana lado a lado, para você achar "
        "horários livres.\n\n"
        "Clique em uma sessão para **Editar** ou **Excluir**. As setas trocam de semana, "
        "e **Ver semana em lista** mostra tudo em texto.",
    ),
    (
        f"{PROGRESS.title}: acompanhar o ritmo",
        "Aqui você ajusta a **meta semanal** e vê quanto estudou de cada disciplina.\n\n"
        "Na parte de **Notas** você registra avaliações e acompanha a média do período.",
    ),
    (
        f"{SUBJECTS.title}: organizar o semestre",
        "Tudo começa aqui. No topo fica o **período acadêmico** (por exemplo, 2026.2), "
        "que você pode trocar ou gerenciar.\n\n"
        "Escolha uma disciplina para cadastrar **conteúdos** e **horários de aula**. "
        "Se ficar com dúvida, o botão **Ajuda** na barra lateral reabre este tour.",
    ),
)

HELP_ITEMS = (
    (
        "O que é uma sessão de estudo?",
        "É um bloco curto de estudo com disciplina, data, horário e duração. Você pode "
        "ligar a sessão a um conteúdo para acompanhar o que já estudou.",
    ),
    (
        "O que é o período acadêmico?",
        "É o semestre ou ciclo em andamento, como 2026.2. Disciplinas, sessões e notas "
        "ficam ligadas a ele. Você troca ou cria períodos no topo de **Disciplinas**.",
    ),
    (
        "Como planejo uma sessão?",
        "Use **Nova sessão** no topo de **Hoje** ou de **Semana**. Os campos com \\* são "
        "obrigatórios. Se faltar período ou disciplina, o próprio diálogo leva você até lá.",
    ),
    (
        "Como concluo ou desfaço uma sessão?",
        "Em **Hoje**, use **Concluir** no cartão da sessão. O aviso que aparece no topo "
        "tem **Desfazer**, caso tenha sido sem querer.",
    ),
    (
        "Como edito ou excluo uma sessão?",
        "Em **Semana**, clique na sessão na agenda e use **Editar** ou **Excluir**. "
        "A exclusão pede confirmação.",
    ),
    (
        "Como cadastro conteúdos e horários de aula?",
        "Em **Disciplinas**, escolha a disciplina na lista e use as seções de conteúdos "
        "e de horários logo abaixo.",
    ),
    (
        "Por que a meta sugeriu este número?",
        "Em **Progresso**, o plano de foco divide a meta semanal pela carga das suas "
        "disciplinas. Você pode ajustar a meta a qualquer momento em **Ajustar meta semanal**.",
    ),
    (
        "Onde estou e como volto?",
        "A barra lateral mostra os quatro lugares do Plano: **Hoje**, **Semana**, "
        "**Progresso** e **Disciplinas**. O lugar atual fica destacado, e o período "
        "atual aparece no seu cartão, no topo da barra.",
    ),
)


def open_tour() -> None:
    open_dialog(TOUR_DIALOG, 0)


def _dismiss_tour() -> None:
    """Fechar no X ou com Esc também conta como "já vi o tour"."""
    close_dialog(TOUR_DIALOG)
    st.session_state[_PENDING_COMPLETION_KEY] = True


def _set_tour_step(step: int) -> None:
    st.session_state[TOUR_DIALOG] = step


def _complete_tour(services: ApplicationServices, user: dict) -> None:
    st.session_state.pop(_PENDING_COMPLETION_KEY, None)
    if user.get("onboarding_completed_at"):
        return
    try:
        services.users.complete_onboarding(user["_id"])
    except Exception as error:
        show_action_error("salvar que você já viu o tour", error)


@st.dialog("Conheça o Plano", width="medium", on_dismiss=_dismiss_tour)
def _tour_dialog(services: ApplicationServices, user: dict) -> None:
    step = min(max(int(st.session_state.get(TOUR_DIALOG, 0)), 0), len(TOUR_STEPS) - 1)
    title, body = TOUR_STEPS[step]
    st.caption(f"Passo {step + 1} de {len(TOUR_STEPS)}")
    st.progress((step + 1) / len(TOUR_STEPS))
    st.subheader(title)
    st.markdown(body)

    is_last = step == len(TOUR_STEPS) - 1
    back_column, skip_column, next_column = st.columns(3)
    back_column.button(
        "Anterior",
        icon=":material/arrow_back:",
        width="stretch",
        disabled=step == 0,
        key="tour_back",
        on_click=_set_tour_step,
        args=(step - 1,),
    )
    if not is_last:
        if skip_column.button("Pular tour", width="stretch", key="tour_skip"):
            close_dialog(TOUR_DIALOG)
            _complete_tour(services, user)
            st.rerun()
        next_column.button(
            "Próximo",
            icon=":material/arrow_forward:",
            type="primary",
            width="stretch",
            key="tour_next",
            on_click=_set_tour_step,
            args=(step + 1,),
        )
        return

    needs_period = user.get("current_academic_period_id") is None
    if needs_period:
        st.info("Para começar, adicione o seu período acadêmico atual.")
    if next_column.button(
        "Adicionar período" if needs_period else "Começar",
        type="primary",
        width="stretch",
        key="tour_finish",
    ):
        close_dialog(TOUR_DIALOG)
        _complete_tour(services, user)
        if needs_period:
            open_periods_dialog()
        st.rerun()


def _close_help() -> None:
    close_dialog(HELP_DIALOG)


def open_help() -> None:
    open_dialog(HELP_DIALOG)


@st.dialog("Ajuda", width="medium", on_dismiss=_close_help)
def _help_dialog() -> None:
    st.caption("Respostas rápidas para as dúvidas mais comuns.")
    for question, answer in HELP_ITEMS:
        with st.expander(question):
            st.markdown(answer)
    if st.button(
        "Ver o tour de novo",
        icon=":material/tour:",
        width="stretch",
        key="help_replay_tour",
    ):
        open_tour()
        st.rerun()


def render_help_button() -> None:
    st.sidebar.button(
        "Ajuda",
        icon=":material/help:",
        width="stretch",
        key="open_help",
        help="Perguntas frequentes e o tour de boas-vindas.",
        on_click=open_help,
    )


def render_onboarding_dialogs(services: ApplicationServices, user: dict) -> None:
    """Abre o tour no primeiro acesso e desenha o tour ou a ajuda, se pedidos."""
    if st.session_state.get(_PENDING_COMPLETION_KEY):
        _complete_tour(services, user)
    if (
        not user.get("onboarding_completed_at")
        and not st.session_state.get(_AUTO_OPENED_KEY)
        and active_dialog() is None
    ):
        st.session_state[_AUTO_OPENED_KEY] = True
        open_tour()
    current = active_dialog()
    if current == TOUR_DIALOG:
        _tour_dialog(services, user)
    elif current == HELP_DIALOG:
        _help_dialog()


def load_onboarding_steps(
    services: ApplicationServices, user: dict, subjects: list[dict]
) -> list[OnboardingStep]:
    """Conta o que o usuário já cadastrou no período atual."""
    period_id = user.get("current_academic_period_id")
    if period_id is None:
        return build_onboarding_steps(
            has_period=False,
            subject_count=0,
            class_meeting_count=0,
            topic_count=0,
            session_count=0,
            completed_session_count=0,
        )
    meetings = services.class_meetings.list_for_period(user["_id"], period_id, subjects)
    topic_count = 0
    for subject in subjects:
        if services.topics.list_for_subject(user["_id"], period_id, subject["_id"]):
            topic_count += 1
            break
    sessions = services.sessions.list_for_user(user["_id"], subjects)
    return build_onboarding_steps(
        has_period=True,
        subject_count=len(subjects),
        class_meeting_count=len(meetings),
        topic_count=topic_count,
        session_count=len(sessions),
        completed_session_count=sum(
            1 for session in sessions if session.get("status") == "Concluída"
        ),
    )


def render_first_steps(services: ApplicationServices, user: dict, subjects: list[dict]) -> bool:
    """Mostra "Primeiros passos" com um único botão para o próximo passo.

    Retorna ``False`` quando tudo já foi feito e nada foi mostrado.
    """
    try:
        steps = load_onboarding_steps(services, user, subjects)
    except Exception as error:
        show_action_error("carregar seus primeiros passos", error)
        return False
    upcoming = next_step(steps)
    if upcoming is None:
        return False
    done_count = sum(step.done for step in steps)
    with st.container(border=True, key="overview_first_steps"):
        heading_column, count_column = st.columns([3, 1], vertical_alignment="center")
        heading_column.subheader("Primeiros passos")
        count_column.markdown(f"**{done_count} de {len(steps)}** feitos")
        st.progress(done_count / len(steps))
        st.markdown(
            "  \n".join(
                f"{'✓' if step.done else '○'} {step.label}" for step in steps
            )
        )
        _render_next_step_action(upcoming)
    return True


def _render_next_step_action(step: OnboardingStep) -> None:
    if step.key == "period":
        st.button(
            "Adicionar período acadêmico",
            type="primary",
            icon=":material/date_range:",
            key="overview_add_period",
            on_click=open_periods_dialog,
        )
    elif step.key in ("subject", "class", "topic"):
        labels = {
            "subject": "Adicionar disciplina",
            "class": "Cadastrar horário de aula",
            "topic": "Cadastrar conteúdo",
        }
        if st.button(
            labels[step.key], type="primary", icon=SUBJECTS.icon, key="overview_next_step"
        ):
            st.switch_page(SUBJECTS.path)
    elif step.key == "session":
        st.button(
            "Planejar sessão",
            type="primary",
            icon=":material/add:",
            key="overview_next_step",
            on_click=open_session_dialog,
        )
    else:
        st.caption(
            "Quando terminar de estudar, use **Concluir** no cartão da sessão, logo abaixo."
        )
