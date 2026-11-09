from pathlib import Path

import streamlit as st
from streamlit.testing.v1 import AppTest

from src.database import connection
from src.ui import auth


APP_PATH = Path(__file__).resolve().parents[2] / "app.py"


def test_local_demo_starts_at_login_and_returns_after_logout(monkeypatch):
    monkeypatch.setenv("PLANO_LOCAL_MODE", "true")

    def external_access(*args, **kwargs):
        raise AssertionError("A demonstração não deve acessar autenticação ou banco externos.")

    monkeypatch.setattr(auth, "_auth_is_configured", external_access)
    monkeypatch.setattr(st, "login", external_access)
    monkeypatch.setattr(st, "logout", external_access)
    monkeypatch.setattr(connection, "get_settings", external_access)
    monkeypatch.setattr(connection, "MongoClient", external_access)
    connection.get_database.clear()
    try:
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()

        assert not app.exception
        assert app.button(key="local_demo_login").label == "Entrar na demonstração"
        assert not app.date_input
        assert not app.warning

        app.button(key="local_demo_login").click().run()

        assert not app.exception
        assert app.session_state["plan_local_authenticated"]
        assert app.date_input(key="overview_date")
        assert app.button(key="local_demo_logout")

        app.switch_page("app_pages/weekly.py").run()
        assert not app.exception
        assert app.button(key="local_demo_logout")

        app.button(key="local_demo_logout").click().run()

        assert not app.exception
        assert "plan_local_authenticated" not in app.session_state
        assert app.button(key="local_demo_login")
        assert not app.date_input

        app.button(key="local_demo_login").click().run()
        assert not app.exception
        assert app.button(key="local_demo_logout")
    finally:
        connection.get_database.clear()


def test_real_mode_keeps_google_login_and_logout(monkeypatch):
    monkeypatch.setenv("PLANO_LOCAL_MODE", "false")
    user = {"is_logged_in": False}
    monkeypatch.setattr(st, "user", user)
    monkeypatch.setattr(auth, "_auth_is_configured", lambda: True)
    monkeypatch.setattr(st, "login", lambda: user.update(is_logged_in=True))
    monkeypatch.setattr(st, "logout", lambda: user.update(is_logged_in=False))
    app = AppTest.from_string(
        """
from types import SimpleNamespace
import streamlit as st
from src.ui.auth import require_login
from src.ui.sidebar import render_account_sidebar

require_login()
render_account_sidebar(SimpleNamespace(), {"name": "Estudante", "email": "aluno@example.com"})
st.write("Seu plano")
"""
    )
    app.session_state["plan_local_authenticated"] = True
    app.run()

    assert not app.exception
    assert app.button[0].label == "Entrar com Google"

    app.button[0].click().run()
    assert not app.exception
    assert user["is_logged_in"]
    logout = next(button for button in app.sidebar.button if button.label == "Sair")

    logout.click().run()
    assert not app.exception
    assert not user["is_logged_in"]

    app.run()
    assert not app.exception
    assert app.button[0].label == "Entrar com Google"


def test_real_mode_without_oidc_still_requires_configuration(monkeypatch):
    monkeypatch.setenv("PLANO_LOCAL_MODE", "false")
    monkeypatch.setattr(st, "user", {"is_logged_in": False})
    monkeypatch.setattr(auth, "_auth_is_configured", lambda: False)

    app = AppTest.from_string("from src.ui.auth import require_login\nrequire_login()").run()

    assert not app.exception
    assert app.warning[0].value == "O login ainda não está configurado neste ambiente."
    assert not app.button


def test_empty_login_keeps_sample_data_in_a_separate_account(monkeypatch):
    monkeypatch.setenv("PLANO_LOCAL_MODE", "true")
    connection.get_database.clear()
    try:
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        app.button(key="local_empty_login").click().run()
        assert not app.exception
        assert any(header.value == "Primeiros passos" for header in app.subheader)
        assert app.button(key="overview_add_period")
        database = connection.get_database()
        empty_user = database.users.find_one({"identity.subject": "local-empty-user"})
        demo_user = database.users.find_one({"identity.subject": "local-demo-user"})
        for collection in ("academic_periods", "subjects", "topics", "study_sessions", "evaluations"):
            assert database[collection].count_documents({"user_id": empty_user["_id"]}) == 0
        assert database.subjects.count_documents({"user_id": demo_user["_id"]}) == 6

        app.button(key="local_demo_logout").click().run()
        app.button(key="local_demo_login").click().run()

        assert not app.exception
        assert app.session_state["plan_local_profile"] == "demo"
        assert app.date_input(key="overview_date")
        assert database.subjects.count_documents({"user_id": demo_user["_id"]}) == 6
    finally:
        connection.get_database.clear()


def test_new_user_adds_first_period_from_home(monkeypatch):
    monkeypatch.setenv("PLANO_LOCAL_MODE", "true")
    connection.get_database.clear()
    try:
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        app.button(key="local_empty_login").click().run()

        app.button(key="overview_add_period").click().run()
        app.text_input[0].input("2026.2")
        next(button for button in app.button if button.label == "Adicionar período").click().run()
        assert not app.exception
        assert app.button(key="overview_next_step").label == "Adicionar disciplina"
        assert any("1 de 6" in item.value for item in app.markdown)
    finally:
        connection.get_database.clear()


def test_new_user_is_guided_from_period_to_subjects(monkeypatch):
    monkeypatch.setenv("PLANO_LOCAL_MODE", "true")
    connection.get_database.clear()
    try:
        app = AppTest.from_file(str(APP_PATH), default_timeout=15).run()
        app.button(key="local_empty_login").click().run()
        app.button(key="tour_skip").click().run()
        user = connection.get_database().users.find_one({"identity.subject": "local-empty-user"})
        assert user.get("onboarding_completed_at")

        app.button(key="overview_add_period").click().run()
        app.text_input[0].input("2026.2")
        next(button for button in app.button if button.label == "Adicionar período").click().run()
        app.switch_page("app_pages/subjects.py").run()
        assert not app.exception
        assert any("primeira disciplina" in item.value for item in app.info)
    finally:
        connection.get_database.clear()
