"""Boas-vindas, balões de explicação, ajuda e "Primeiros passos".

No primeiro acesso aparece uma tela curta de boas-vindas. Dela o usuário segue
para os balões, que apontam para os lugares reais da tela, ou pula. Pular,
terminar ou fechar grava ``onboarding_completed_at`` na conta. A Ajuda reabre os
balões a qualquer momento.
"""

from __future__ import annotations

import streamlit as st

from src.domain.onboarding_rules import OnboardingStep, build_onboarding_steps, next_step
from src.services.container import ApplicationServices
from src.ui.components.coach_marks import render_coach_marks
from src.ui.dialog_state import (
    HELP_DIALOG,
    SETUP_DIALOG,
    TOUR_DIALOG,
    active_dialog,
    close_dialog,
    open_dialog,
)
from src.ui.feedback import show_action_error
from src.ui.navigation import PROGRESS, SUBJECTS, TODAY, WEEK
from src.ui.setup_wizard import WIZARD_STEPS, open_setup_wizard, render_setup_wizard


_AUTO_OPENED_KEY = "plan_tour_auto_opened"
_PENDING_COMPLETION_KEY = "plan_tour_pending_completion"
COACH_STATE_KEY = "plan_coach_run"

WELCOME_TEXT = (
    "O Plano ajuda você a transformar o semestre em pequenos blocos de estudo. "
    "O caminho é sempre o mesmo:\n\n"
    "1. **Disciplinas**: cadastre o período, as matérias, os horários de aula e os conteúdos.\n"
    "2. **Semana** ou **Hoje**: planeje sessões de estudo com **Nova sessão**.\n"
    "3. **Hoje**: conclua as sessões quando terminar de estudar.\n"
    "4. **Progresso**: acompanhe a meta, a carga por matéria e as notas."
)

COACH_STEPS = [
    {
        "nav": SUBJECTS.title,
        "title": "Comece por Disciplinas",
        "body": "Cadastre aqui o período, suas matérias e, em cada uma, os horários de aula "
        "e os conteúdos. Dentro de cada disciplina há o botão Planejar sessão.",
    },
    {
        "nav": WEEK.title,
        "title": "Planeje a semana",
        "body": "A agenda mostra suas sessões e as aulas lado a lado, para achar horários "
        "livres. Clique numa sessão para editar ou excluir.",
    },
    {
        "nav": TODAY.title,
        "title": "Estude no dia",
        "body": "Hoje mostra o que fazer agora. Quando terminar de estudar, use Concluir "
        "no cartão da sessão. Se errar, o aviso traz Desfazer.",
    },
    {
        "nav": PROGRESS.title,
        "title": "Acompanhe o ritmo",
        "body": "Ajuste a meta semanal, veja quanto estudou de cada disciplina e registre "
        "suas notas.",
    },
    {
        "selector": ".st-key-overview_first_steps",
        "title": "Seu próximo passo",
        "body": "Esta lista mostra o que falta para o plano ficar pronto. O botão leva "
        "direto ao próximo passo.",
    },
    {
        "selector": ".st-key-overview_new_session, .st-key-weekly_new_session",
        "title": "Nova sessão",
        "body": "Use este botão sempre que quiser planejar um bloco de estudo.",
    },
    {
        "selector": ".st-key-open_help",
        "title": "Ficou com dúvida?",
        "body": "A Ajuda tem respostas rápidas e mostra estes balões de novo.",
    },
]


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
        "Use **Nova sessão** no topo de **Hoje** ou de **Semana**, ou **Planejar sessão** "
        "dentro de cada disciplina. Os campos com \\* são obrigatórios. Se faltar período "
        "ou disciplina, o próprio diálogo leva você até lá.",
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
        "Em **Disciplinas**, cada matéria tem um cartão com os botões **Conteúdos** e "
        "**Horários**. Cada um abre um pop-up para ver, adicionar e editar.",
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
    """Abre a tela de boas-vindas."""
    open_dialog(TOUR_DIALOG, 0)


def start_coach_marks() -> None:
    """Começa (ou recomeça) os balões, fechando qualquer diálogo aberto."""
    for key in (TOUR_DIALOG, HELP_DIALOG):
        close_dialog(key)
    st.session_state[COACH_STATE_KEY] = int(st.session_state.get(COACH_STATE_KEY, 0)) + 1


def _coach_done() -> None:
    st.session_state.pop(COACH_STATE_KEY, None)
    st.session_state[_PENDING_COMPLETION_KEY] = True


def _dismiss_tour() -> None:
    """Fechar no X ou com Esc também conta como "já vi o tour"."""
    close_dialog(TOUR_DIALOG)
    st.session_state[_PENDING_COMPLETION_KEY] = True


def _complete_tour(services: ApplicationServices, user: dict) -> None:
    st.session_state.pop(_PENDING_COMPLETION_KEY, None)
    if user.get("onboarding_completed_at"):
        return
    try:
        services.users.complete_onboarding(user["_id"])
    except Exception as error:
        show_action_error("salvar que você já viu o tour", error)


@st.dialog("Bem-vindo ao Plano", width="medium", on_dismiss=_dismiss_tour)
def _tour_dialog(services: ApplicationServices, user: dict) -> None:
    st.markdown(WELCOME_TEXT)
    if user.get("current_academic_period_id") is None:
        st.markdown("Comece montando seu plano agora: leva uns dois minutos.")
        if st.button(
            "Montar meu plano agora",
            type="primary",
            icon=":material/rocket_launch:",
            width="stretch",
            key="tour_setup",
        ):
            _complete_tour(services, user)
            open_setup_wizard()
            st.rerun()
    skip_column, start_column = st.columns(2)
    if skip_column.button("Agora não", width="stretch", key="tour_skip"):
        close_dialog(TOUR_DIALOG)
        _complete_tour(services, user)
        st.rerun()
    if start_column.button(
        "Mostrar onde fica cada coisa",
        icon=":material/tour:",
        width="stretch",
        key="tour_start",
    ):
        start_coach_marks()
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
        "Mostrar os balões de novo",
        icon=":material/tour:",
        width="stretch",
        key="help_replay_tour",
    ):
        start_coach_marks()
        st.rerun()


def render_help_button() -> None:
    st.sidebar.button(
        "Ajuda",
        icon=":material/help:",
        width="stretch",
        key="open_help",
        help="Perguntas frequentes e os balões que mostram onde fica cada coisa.",
        on_click=open_help,
    )


def render_onboarding_dialogs(services: ApplicationServices, user: dict) -> None:
    """Abre as boas-vindas no primeiro acesso e desenha o que estiver pedido."""
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
    elif current == SETUP_DIALOG:
        render_setup_wizard(services, user)
    elif st.session_state.get(COACH_STATE_KEY):
        with st.sidebar:
            render_coach_marks(
                run=int(st.session_state[COACH_STATE_KEY]),
                steps=COACH_STEPS,
                on_done=_coach_done,
                key="plan_coach_marks",
            )


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
        heading_column.subheader("Primeiros passos", anchor=False)
        count_column.markdown(f"**{done_count} de {len(steps)}** feitos")
        st.progress(done_count / len(steps))
        st.markdown(
            "  \n".join(
                f"{'✓' if step.done else '○'} {step.label}" for step in steps
            )
        )
        _render_next_step_action(upcoming, done_count)
    return True


def _render_next_step_action(step: OnboardingStep, done_count: int) -> None:
    if step.key in WIZARD_STEPS:
        st.button(
            "Montar meu plano" if done_count == 0 else f"Continuar: {step.label.lower()}",
            type="primary",
            icon=":material/rocket_launch:",
            key="overview_setup",
            on_click=open_setup_wizard,
        )
    else:
        st.caption(
            "Quando terminar de estudar, use **Concluir** no cartão da sessão, logo abaixo."
        )


def render_subjects_next_step(
    services: ApplicationServices, user: dict, subjects: list[dict]
) -> None:
    """Em Disciplinas, lembra o que falta e retoma o assistente num clique."""
    if user.get("current_academic_period_id") is None:
        return
    try:
        upcoming = next_step(load_onboarding_steps(services, user, subjects))
    except Exception:
        return
    if upcoming is None:
        return
    hint_column, action_column = st.columns([3, 1], vertical_alignment="center")
    if upcoming.key in WIZARD_STEPS:
        hint_column.info(
            f"Seu plano ainda não está pronto. Falta: {upcoming.label.lower()}.",
            icon=":material/flag:",
        )
        action_column.button(
            "Continuar montando",
            type="primary",
            icon=":material/rocket_launch:",
            width="stretch",
            key="subjects_setup",
            on_click=open_setup_wizard,
        )
    else:
        hint_column.info(
            "Sessão planejada. Quando terminar de estudar, conclua a sessão em **Hoje**.",
            icon=":material/flag:",
        )
        with action_column:
            st.page_link(TODAY.path, label="Ir para Hoje", icon=TODAY.icon)
