from calendar import monthrange
from datetime import date, time, timedelta
from pathlib import Path
import json
import sys

import pytest
from streamlit.testing.v1 import AppTest

from src.database.connection import get_database
from src.services.user_service import UserService
from src.ui.navigation import MAIN_PLACES


APP_PATH = Path(__file__).resolve().parents[2] / "app.py"
PAGES = {
    "overview": "Olá, Estudante local",
    "weekly": "Semana",
    "progress": "Progresso",
    "subjects": "Disciplinas",
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


def metric_value(app, label):
    return next(item.value for item in app.metric if item.label == label)


def grade_chart(app):
    return next(
        chart for chart in app.get("plotly_chart") if "evaluation_grade_chart" in chart.proto.id
    )


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


def test_navigation_has_four_main_places_in_cycle_order():
    assert [place.title for place in MAIN_PLACES] == ["Hoje", "Semana", "Progresso", "Disciplinas"]
    assert all((APP_PATH.parent / place.path).exists() for place in MAIN_PLACES)


@pytest.mark.parametrize("dark_mode", [False, True])
def test_every_page_renders_without_changing_theme(local_app, monkeypatch, dark_mode):
    app = local_app
    if dark_mode:
        app.button(key="toggle_plan_theme").click().run()

    def unexpected_theme_change(*args, **kwargs):
        raise AssertionError("Navegação não deve alterar a preferência de tema.")

    monkeypatch.setattr(UserService, "update_dark_mode", unexpected_theme_change)
    for page, title in PAGES.items():
        app.switch_page(f"app_pages/{page}.py").run()
        assert_page_and_theme(app, title, dark_mode)


def test_new_session_dialog_adds_session(local_app):
    app = local_app
    database = get_database()
    before = database.study_sessions.count_documents({})
    app.switch_page("app_pages/weekly.py").run()

    app.button(key="weekly_new_session").click().run()
    assert not app.exception
    app.text_input[0].input("Revisar normalização")
    next(button for button in app.button if button.label == "Adicionar sessão").click().run()

    assert not app.exception
    assert database.study_sessions.count_documents({}) == before + 1
    assert database.study_sessions.find_one({"topic": "Revisar normalização"})["status"] == "Pendente"
    assert "plan_session_dialog" not in app.session_state


@pytest.mark.parametrize(("page", "key"), [("overview", "overview_new_session"), ("weekly", "weekly_new_session")])
def test_planning_pages_show_new_session_button_that_opens_dialog(local_app, page, key):
    app = local_app
    app.switch_page(f"app_pages/{page}.py").run()

    app.button(key=key).click().run()

    assert not app.exception
    assert app.text_input[0].label == "O que você vai estudar? *"


def test_completing_session_can_be_undone(local_app):
    app = local_app
    database = get_database()
    pending = database.study_sessions.find_one(
        {"study_date": date.today().isoformat(), "status": "Pendente"}
    )
    app.button(key=f"overview_session_{pending['_id']}_complete").click().run()
    assert database.study_sessions.find_one({"_id": pending["_id"]})["status"] == "Concluída"

    app.button(key="flash_undo_button").click().run()

    assert not app.exception
    assert database.study_sessions.find_one({"_id": pending["_id"]})["status"] == "Pendente"


@pytest.mark.parametrize("dark_mode", [False, True])
def test_navigation_uses_saved_theme_instead_of_old_session_value(local_app, dark_mode):
    database = get_database()
    user = database.users.find_one()
    database.users.update_one({"_id": user["_id"]}, {"$set": {"dark_mode": dark_mode}})
    local_app.session_state["plan_dark_mode"] = not dark_mode

    local_app.switch_page("app_pages/progress.py").run()

    assert_page_and_theme(local_app, "Progresso", dark_mode)


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
    app.switch_page("app_pages/progress.py").run()
    assert_page_and_theme(app, "Progresso", dark_mode)
    app.number_input[0].set_value(12.0)
    next(button for button in app.button if button.label == "Salvar meta").click().run()

    assert_page_and_theme(app, "Progresso", dark_mode)
    assert get_database().users.find_one()["weekly_goal_minutes"] == 720

    app.switch_page("app_pages/overview.py").run()

    assert_page_and_theme(app, "Olá, Estudante local", dark_mode)
    assert app.metric[0].value.endswith("/ 720 min")


@pytest.mark.parametrize("dark_mode", [False, True])
def test_evaluation_filter_updates_chart_and_summary_for_selected_subject(local_app, dark_mode):
    app = local_app
    if dark_mode:
        app.button(key="toggle_plan_theme").click().run()
    app.switch_page("app_pages/progress.py").run()
    database = get_database()
    subject = database.subjects.find_one({"name": "Banco de Dados"})

    app.selectbox(key="progress_subject").set_value(subject["_id"]).run()

    assert_page_and_theme(app, "Progresso", dark_mode)
    rows = list(database.evaluations.find({"subject_id": subject["_id"]}))
    graded = [row for row in rows if row["score"] is not None]
    assert metric_value(app, "Avaliações") == str(len(rows))
    assert metric_value(app, "Com nota") == str(len(graded))
    chart = json.loads(grade_chart(app).proto.spec)
    assert len(chart["data"]) == 1
    assert chart["data"][0]["name"] == subject["name"]
    assert len(chart["data"][0]["x"]) == len(graded)

    app.selectbox(key="progress_subject").set_value(None).run()

    assert_page_and_theme(app, "Progresso", dark_mode)
    assert metric_value(app, "Avaliações") == str(database.evaluations.count_documents({}))


def test_period_is_managed_from_subjects_and_shown_in_sidebar(local_app):
    app = local_app
    database = get_database()
    app.switch_page("app_pages/subjects.py").run()
    assert any("Período: " in item.value for item in app.sidebar.markdown)

    app.button(key="subjects_manage_period").click().run()
    next(item for item in app.text_input if item.label == "Nome *").input("2027.1")
    next(button for button in app.button if button.label == "Adicionar período").click().run()

    assert not app.exception
    assert database.academic_periods.find_one({"name": "2027.1"})
    assert "plan_periods_dialog" not in app.session_state


def test_welcome_opens_on_first_access_and_skip_is_saved(local_app):
    app = local_app
    assert app.session_state["plan_tour_dialog"] == 0
    assert app.button(key="tour_start")

    app.button(key="tour_skip").click().run()
    assert not app.exception
    assert "plan_tour_dialog" not in app.session_state
    assert "plan_coach_run" not in app.session_state
    assert get_database().users.find_one().get("onboarding_completed_at")

    # Uma nova sessão do navegador não abre as boas-vindas de novo.
    fresh = AppTest.from_file(str(APP_PATH), default_timeout=20).run()
    fresh.button(key="local_demo_login").click().run()
    assert not fresh.exception
    assert "plan_tour_dialog" not in fresh.session_state


def test_welcome_starts_balloons_and_help_restarts_them(local_app):
    app = local_app
    app.button(key="tour_start").click().run()
    assert not app.exception
    assert "plan_tour_dialog" not in app.session_state
    assert app.session_state["plan_coach_run"] == 1

    app.button(key="open_help").click().run()
    assert not app.exception
    assert app.session_state["plan_help_dialog"] is True
    assert len(app.expander) >= 8
    app.button(key="help_replay_tour").click().run()
    assert not app.exception
    assert "plan_help_dialog" not in app.session_state
    assert app.session_state["plan_coach_run"] == 2


def test_subject_card_leads_to_planning_a_session(local_app):
    app = local_app
    app.button(key="tour_skip").click().run()
    app.switch_page("app_pages/subjects.py").run()
    assert not app.exception
    subject_id = app.pills(key="subjects_detail").value
    app.button(key="subjects_plan_session").click().run()
    assert not app.exception
    assert app.session_state["plan_session_dialog"]["subject_id"] == subject_id
    assert app.selectbox(key="new_session_subject").value == subject_id

    next(
        item for item in app.text_input if item.label == "O que você vai estudar? *"
    ).input("Revisar a matéria da última aula")
    # Horário tarde para não conflitar com as sessões da demonstração.
    next(item for item in app.time_input if item.label == "Horário *").set_value(time(23, 0))
    next(
        button for button in app.button if button.label == "Adicionar sessão"
    ).click().run()
    assert not app.exception
    assert "plan_session_dialog" not in app.session_state
    assert any("Quando estudar" in item.value for item in app.success)


def test_opening_another_dialog_closes_the_tour(local_app):
    app = local_app
    app.button(key="overview_new_session").click().run()
    assert "plan_tour_dialog" not in app.session_state
    assert "plan_session_dialog" in app.session_state
