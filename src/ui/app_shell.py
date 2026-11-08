"""Shell único da aplicação para execução local e no Community Cloud."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.ui.auth import require_login
from src.ui.styles import apply_styles
from src.ui.feedback import render_flash
from src.ui.navigation import MAIN_PLACES, SETTINGS, TODAY


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
            "": [
                st.Page(place.path, title=place.title, icon=place.icon, default=place is TODAY)
                for place in MAIN_PLACES
            ],
            "Ajustes": [
                st.Page(item.path, title=item.title, icon=item.icon) for item in SETTINGS
            ],
        },
        position="sidebar",
    )
    page.run()
