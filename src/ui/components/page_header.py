"""Cabeçalho consistente para páginas do produto."""

from __future__ import annotations

from html import escape

import streamlit as st


def render_page_header(eyebrow: str, title: str, description: str) -> None:
    """Apresenta contexto, título e objetivo da tela na mesma ordem."""
    # Adicionado style="font-size: 1rem;" para igualar ao tamanho da descrição
    st.markdown(
        f'<div class="plan-eyebrow" style="font-size: 1.5rem;">{escape(eyebrow.capitalize())}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<h1 class="plan-page-title">{escape(title)}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="plan-page-description">{escape(description)}</div>',
        unsafe_allow_html=True,
    )
    # O bloco "plan-header-motif" que gerava a linha com o ponto foi removido daqui
