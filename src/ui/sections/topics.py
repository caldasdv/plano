"""Seção de conteúdos (tópicos e subtópicos) de uma disciplina."""

from __future__ import annotations

from html import escape

import streamlit as st

from src.services.container import ApplicationServices
from src.services.report_service import build_topic_summary
from src.ui.feedback import set_success_flash, show_action_error


STATUS_LABELS = {"NOT_STARTED": "Não iniciado", "IN_PROGRESS": "Em andamento", "REVIEWED": "Revisado", "MASTERED": "Dominado"}
DIFFICULTY_LABELS = {"LOW": "Baixa", "MEDIUM": "Média", "HIGH": "Alta"}


def render_topics_section(
    services: ApplicationServices, user: dict, subjects: list[dict], subject_id
) -> None:
    """Lista e cadastra conteúdos da disciplina escolhida."""
    topics_service = services.topics
    try:
        topics = topics_service.list_for_subject(
            user["_id"], user.get("current_academic_period_id"), subject_id
        )
        all_sessions = services.sessions.list_for_user(user["_id"], subjects)
    except Exception as error:
        show_action_error("carregar os conteúdos", error)
        return

    roots = [topic for topic in topics if topic.get("parent_id") is None]
    children = {topic["_id"]: [] for topic in roots}
    for topic in topics:
        if topic.get("parent_id") in children:
            children[topic["parent_id"]].append(topic)

    topic_summary = build_topic_summary(
        [session for session in all_sessions if session.get("subject_id") == subject_id],
        topics,
    )
    if not topics:
        st.info("Esta disciplina ainda não tem conteúdos. Adicione o primeiro abaixo.")
    else:
        for root in roots:
            with st.container(border=True):
                st.markdown(f"**{escape(root['title'])}**")
                st.caption(f"{STATUS_LABELS.get(root['status'], root['status'])} · Dificuldade {DIFFICULTY_LABELS.get(root['difficulty'], root['difficulty'])}")
                root_progress = next((item for item in topic_summary if item["topic_id"] == root["_id"]), None)
                if root_progress and root_progress["planned_minutes"]:
                    st.progress(root_progress["progress"], text=f"{root_progress['completed_minutes']} de {root_progress['planned_minutes']} min em sessões")
                path_items = []
                for child in children[root["_id"]]:
                    child_progress = next((item for item in topic_summary if item["topic_id"] == child["_id"]), None)
                    is_done = child["status"] in {"REVIEWED", "MASTERED"}
                    detail = STATUS_LABELS.get(child["status"], child["status"])
                    if child_progress and child_progress["planned_minutes"]:
                        detail = f"{detail} · {child_progress['completed_minutes']}/{child_progress['planned_minutes']} min"
                    path_items.append(
                        f'<div class="plan-topic-path-item {"is-done" if is_done else ""}" '
                        'style="align-items:center;display:flex;gap:.65rem;min-height:1.8rem;">'
                        '<i aria-hidden="true" style="display:block;flex:0 0 auto;"></i>'
                        f'<strong style="color:var(--plan-text);font-size:.88rem;">{escape(child["title"])}</strong>'
                        f'<small style="color:var(--plan-muted);margin-left:auto;white-space:nowrap;">{escape(detail)}</small></div>'
                    )
                if path_items:
                    st.markdown(
                        '<div class="plan-topic-path">' + "".join(path_items) + "</div>",
                        unsafe_allow_html=True,
                    )

    with st.expander("Adicionar conteúdo", icon=":material/add:", expanded=not topics):
        with st.form(f"new_topic_{subject_id}"):
            parent_options = [None, *[topic["_id"] for topic in roots]]
            parent_id = st.selectbox(
                "Tipo",
                parent_options,
                format_func=lambda value: "Tópico principal" if value is None else f"Subtópico de {next(topic['title'] for topic in roots if topic['_id'] == value)}",
            )
            title = st.text_input("Nome do conteúdo", placeholder="Ex.: JOIN e relacionamentos")
            status = st.selectbox("Status", list(STATUS_LABELS), format_func=lambda value: STATUS_LABELS[value])
            difficulty = st.selectbox("Dificuldade", list(DIFFICULTY_LABELS), index=1, format_func=lambda value: DIFFICULTY_LABELS[value])
            submitted = st.form_submit_button("Adicionar conteúdo", type="primary", width="stretch")
        if submitted:
            try:
                topics_service.create(
                    user_id=user["_id"],
                    academic_period_id=user.get("current_academic_period_id"),
                    subject_id=subject_id,
                    parent_id=parent_id,
                    title=title,
                    status=status,
                    difficulty=difficulty,
                )
            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                show_action_error("adicionar o conteúdo", error)
            else:
                set_success_flash("Conteúdo adicionado.")
                st.rerun()
