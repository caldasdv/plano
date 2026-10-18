"""Shell único da aplicação para execução local e no Community Cloud."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.ui.auth import require_login
from src.ui.styles import apply_styles
from src.ui.feedback import render_flash


PROJECT_DIR = Path(__file__).resolve().parents[2]


def run_app() -> None:
    """Configura e executa a navegação principal do produto."""
    load_dotenv(PROJECT_DIR / ".env")
    st.set_page_config(
        page_title="Plano",
        page_icon=str(PROJECT_DIR / "assets" / "plan-logo.svg"),
        layout="wide",
    )
    apply_styles()
    st.logo(str(PROJECT_DIR / "assets" / "plan-wordmark.svg"), size="large")

    require_login()

    render_flash()
    page = st.navigation(
        {
            "Plano": [
                st.Page("app_pages/overview.py", title="Hoje", icon=":material/home:"),
                st.Page("app_pages/goals.py", title="Metas", icon=":material/track_changes:"),
                st.Page(
                    "app_pages/new_session.py",
                    title="Nova sessão",
                    icon=":material/add_circle:",
                ),
                st.Page(
                    "app_pages/weekly.py",
                    title="Semana",
                    icon=":material/calendar_view_week:",
                ),
            ],
            "Acompanhar": [
                st.Page("app_pages/progress.py", title="Progresso", icon=":material/analytics:"),
                st.Page("app_pages/evaluations.py", title="Avaliações", icon=":material/assignment:"),
            ],
            "Organizar": [
                st.Page("app_pages/subjects.py", title="Disciplinas", icon=":material/menu_book:"),
                st.Page(
                    "app_pages/class_schedule.py",
                    title="Grade de aulas",
                    icon=":material/calendar_view_week:",
                ),
                st.Page(
                    "app_pages/topics.py",
                    title="Conteúdos",
                    icon=":material/account_tree:",
                ),
                st.Page(
                    "app_pages/academic_periods.py",
                    title="Períodos acadêmicos",
                    icon=":material/date_range:",
                ),
            ],
        },
        position="sidebar",
    )
    page.run()