"""Integração mínima entre a identidade OIDC e a camada de aplicação."""

from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from src.config.runtime import is_local_mode


def _auth_is_configured() -> bool:
    """Verifica se o provedor OIDC local possui as credenciais necessárias."""
    try:
        auth = st.secrets.get("auth", {})
    except StreamlitSecretNotFoundError:
        return False
    required_keys = (
        "redirect_uri",
        "cookie_secret",
        "client_id",
        "client_secret",
        "server_metadata_url",
    )
    return all(str(auth.get(key, "")).strip() for key in required_keys)


def require_login() -> None:
    """Interrompe a execução até que o usuário conclua o login."""
    local_mode = is_local_mode()
    if local_mode and st.session_state.get("plan_local_authenticated", False):
        return
    if not local_mode and st.user.get("is_logged_in", False):
        return

    auth_configured = local_mode or _auth_is_configured()
    left, right = st.columns([1.05, 0.95], gap="large", vertical_alignment="center")
    with left:
        st.markdown(
            """
            <div class="plan-login-copy">
                <div class="plan-login-kicker"><span class="plan-login-dot"></span> PLANO DE ESTUDOS</div>
                <h1>Seu semestre,<br><em>no seu ritmo.</em></h1>
                <p class="plan-login-lead">Organize as aulas, escolha o próximo foco e transforme intenção em constância.</p>
                <div class="plan-login-signals">
                    <div><span class="plan-login-signal-icon">↗</span><span><strong>Clareza</strong><small>saiba o que vem agora</small></span></div>
                    <div><span class="plan-login-signal-icon">◷</span><span><strong>Ritmo</strong><small>planeje sem sobrecarregar</small></span></div>
                    <div><span class="plan-login-signal-icon">✓</span><span><strong>Progresso</strong><small>veja o estudo acontecer</small></span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="plan-login-visual" aria-hidden="true">
                <div class="plan-login-orbit plan-login-orbit-one"></div>
                <div class="plan-login-orbit plan-login-orbit-two"></div>
                <div class="plan-login-week-card">
                    <div class="plan-login-card-top"><span>esta semana</span><b>72%</b></div>
                    <div class="plan-login-card-title">Um pouco por dia<br>já muda tudo.</div>
                    <div class="plan-login-bars"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
                    <div class="plan-login-card-foot"><span>seg</span><span>ter</span><span>qua</span><span>qui</span><span>sex</span><span>sáb</span><span>dom</span></div>
                </div>
                <div class="plan-login-float plan-login-float-check">✓ <span>sessão concluída</span></div>
                <div class="plan-login-float plan-login-float-focus">foco<br><strong>25 min</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if local_mode:
        with left:
            st.markdown(
                '<div class="plan-login-action-label">Conheça seu plano de estudos</div>',
                unsafe_allow_html=True,
            )
            st.caption("Escolha entrar com dados de exemplo ou começar com um plano vazio. Nenhuma conta é necessária.")
            if st.button(
                "Entrar na demonstração",
                type="primary",
                width="stretch",
                key="local_demo_login",
            ):
                st.session_state["plan_local_profile"] = "demo"
                st.session_state["plan_local_authenticated"] = True
                st.rerun()
            if st.button(
                "Começar com plano vazio",
                width="stretch",
                key="local_empty_login",
            ):
                st.session_state["plan_local_profile"] = "empty"
                st.session_state["plan_local_authenticated"] = True
                st.rerun()
        st.stop()
    if not auth_configured:
        st.warning("O login ainda não está configurado neste ambiente.")
        st.caption(
            "Crie `.streamlit/secrets.toml` a partir do arquivo `.streamlit/secrets.toml.example` "
            "e preencha as credenciais do Google."
        )
        st.stop()
    with left:
        st.markdown('<div class="plan-login-action-label">Entre para começar a organizar seu período</div>', unsafe_allow_html=True)
        st.button("Entrar com Google", type="primary", on_click=st.login, width="stretch")
    st.stop()


def get_current_identity() -> dict[str, str]:
    """Converte os claims necessários do OIDC em uma estrutura estável."""
    if is_local_mode():
        if st.session_state.get("plan_local_profile") == "empty":
            return {
                "provider": "local-demo",
                "subject": "local-empty-user",
                "name": "Sofia",
                "email": "novo@plano.test",
            }
        return {
            "provider": "local-demo",
            "subject": "local-demo-user",
            "name": "Estudante local",
            "email": "local@plano.test",
        }
    subject = str(st.user.get("sub", "")).strip()
    if not subject:
        raise RuntimeError("A identidade do provedor não possui um identificador válido.")
    return {
        "provider": "google",
        "subject": subject,
        "name": str(st.user.get("name", "Estudante")).strip() or "Estudante",
        "email": str(st.user.get("email", "")).strip(),
    }
