from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path
import json
import sys

import pytest
from streamlit.testing.v1 import AppTest

from src.database.connection import get_database
from src.services.user_service import UserService


APP_PATH = Path(__file__).resolve().parents[2] / "app.py"
FLOW_PAGES = {
    "overview": ("flow_today", "Olá, Estudante local"),
    "goals": ("flow_goals", "Metas"),
    "new_session": ("flow_session", "Nova sessão"),
    "weekly": ("flow_week", "Visão semanal"),
    "progress": ("flow_progress", "Seu progresso"),
    "evaluations": ("flow_evaluations", "Avaliações"),
}


@pytest.fixture
def local_app(monkeypatch):
    monkeypatch.setenv("PLANO_LOCAL_MODE", "true")
    components = (
        "src.ui.components.study_agenda",
        "src.ui.components.class_timetable",
    )
    # Cada AppTest tem um Runtime próprio para registrar os componentes v2.
    for name in components:
        sys.modules.pop(name, None)
    get_database.clear()
    app = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    app.button(key="local_demo_login").click().run()
    assert not app.exception
    try:
        yield app
    finally:
        get_database.clear()
        for name in components:
            sys.modules.pop(name, None)


def assert_page_and_theme(app, title, dark_mode):
    assert not app.exception
    assert not app.error
    assert any(f">{title}</h1>" in item.value for item in app.markdown)
    assert app.session_state["plan_dark_mode"] is dark_mode
    assert bool(get_database().users.find_one().get("dark_mode", False)) is dark_mode
    assert any(
        item.value.startswith('<span class="plan-dark-mode-marker"')
        for item in app.markdown
    ) is dark_mode


@pytest.mark.parametrize("dark_mode", [False, True])
def test_navigation_buttons_reach_their_pages_without_changing_theme(
    local_app, monkeypatch, dark_mode
):
    app = local_app
    if dark_mode:
        app.button(key="toggle_plan_theme").click().run()

    def unexpected_theme_change(*args, **kwargs):
        raise AssertionError("Navegação não deve alterar a preferência de tema.")

    monkeypatch.setattr(UserService, "update_dark_mode", unexpected_theme_change)
    for origin in FLOW_PAGES:
        for destination, (key, title) in FLOW_PAGES.items():
            if origin == destination:
                continue
            app.switch_page(f"app_pages/{origin}.py").run()
            app.button(key=key).click().run()
            assert_page_and_theme(app, title, dark_mode)

    for key, title in (
        ("overview_quick_session", "Nova sessão"),
        ("overview_quick_week", "Visão semanal"),
        ("overview_quick_topics", "Conteúdos"),
    ):
        app.switch_page("app_pages/overview.py").run()
        app.button(key=key).click().run()
        assert_page_and_theme(app, title, dark_mode)

    for destination, title in (
        ("subjects", "Disciplinas"),
        ("class_schedule", "Grade de aulas"),
        ("topics", "Conteúdos"),
        ("academic_periods", "Períodos acadêmicos"),
    ):
        app.switch_page(f"app_pages/{destination}.py").run()
        assert_page_and_theme(app, title, dark_mode)


@pytest.mark.parametrize("dark_mode", [False, True])
def test_navigation_uses_saved_theme_instead_of_old_session_value(local_app, dark_mode):
    database = get_database()
    user = database.users.find_one()
    database.users.update_one({"_id": user["_id"]}, {"$set": {"dark_mode": dark_mode}})
    local_app.session_state["plan_dark_mode"] = not dark_mode

    local_app.switch_page("app_pages/goals.py").run()

    assert_page_and_theme(local_app, "Metas", dark_mode)


def test_completing_session_updates_current_week_goal_and_day_filter_keeps_it(local_app):
    app = local_app
    database = get_database()
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    completed = sum(
        session["duration"]
        for session in database.study_sessions.find(
            {
                "status": "Concluída",
                "study_date": {"$gte": week_start.isoformat(), "$lte": week_end.isoformat()},
            }
        )
    )
    pending = database.study_sessions.find_one(
        {"study_date": today.isoformat(), "status": "Pendente"}
    )
    goal = database.users.find_one()["weekly_goal_minutes"]

    app.button(key=f"overview_session_{pending['_id']}_complete").click().run()

    assert not app.exception
    assert database.study_sessions.find_one({"_id": pending["_id"]})["status"] == "Concluída"
    expected = f"{completed + pending['duration']} / {goal} min"
    assert app.metric[0].value == expected

    other_day = today.replace(day=1 if today.day > 7 else monthrange(today.year, today.month)[1])
    app.date_input(key="overview_date").set_value(other_day).run()

    assert not app.exception
    assert app.metric[0].value == expected
    assert any('<div class="plan-session-topic">' in item.value for item in app.markdown)


@pytest.mark.parametrize("dark_mode", [False, True])
def test_saving_weekly_goal_updates_home_without_changing_theme(local_app, dark_mode):
    app = local_app
    if dark_mode:
        app.button(key="toggle_plan_theme").click().run()
    app.button(key="flow_goals").click().run()
    assert_page_and_theme(app, "Metas", dark_mode)
    app.switch_page("app_pages/goals.py").run()
    app.number_input[0].set_value(12.0)
    next(button for button in app.button if button.label == "Salvar meta").click().run()

    assert_page_and_theme(app, "Metas", dark_mode)
    assert get_database().users.find_one()["weekly_goal_minutes"] == 720

    app.button(key="flow_today").click().run()

    assert_page_and_theme(app, "Olá, Estudante local", dark_mode)
    assert app.metric[0].value.endswith("/ 720 min")


@pytest.mark.parametrize("dark_mode", [False, True])
def test_evaluation_filter_updates_chart_and_summary_for_selected_subject(local_app, dark_mode):
    app = local_app
    if dark_mode:
        app.button(key="toggle_plan_theme").click().run()
    app.switch_page("app_pages/evaluations.py").run()
    database = get_database()
    subject = database.subjects.find_one({"name": "Banco de Dados"})

    app.selectbox(key="evaluation_subject_filter").set_value(subject["_id"]).run()

    assert_page_and_theme(app, "Avaliações", dark_mode)
    rows = list(database.evaluations.find({"subject_id": subject["_id"]}))
    graded = [row for row in rows if row["score"] is not None]
    assert app.metric[0].value == str(len(rows))
    assert app.metric[1].value == str(len(graded))
    chart = json.loads(app.get("plotly_chart")[0].proto.spec)
    assert len(chart["data"]) == 1
    assert chart["data"][0]["name"] == subject["name"]
    assert len(chart["data"][0]["x"]) == len(graded)

    app.selectbox(key="evaluation_subject_filter").set_value(None).run()

    assert_page_and_theme(app, "Avaliações", dark_mode)
    assert app.metric[0].value == str(database.evaluations.count_documents({}))
