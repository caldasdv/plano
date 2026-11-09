from datetime import date

from src.services.report_service import (
    build_adaptive_goal_plan,
    build_evaluation_summary,
    build_subject_summary,
    build_topic_summary,
    build_week_summary,
)


SUBJECTS = [{"_id": "ihc", "name": "IHC"}, {"_id": "bd", "name": "Banco de Dados"}]


def test_evaluation_summary_calculates_average_by_subject():
    result = build_evaluation_summary(
        [
            {"subject_id": "ihc", "score": 8, "max_score": 10},
            {"subject_id": "ihc", "score": 6, "max_score": 10},
            {"subject_id": "bd", "score": 15, "max_score": 20},
        ],
        SUBJECTS,
    )

    assert result == [
        {"disciplina": "IHC", "avaliacoes": 2, "media": 7.0, "aproveitamento": 0.7},
        {"disciplina": "Banco de Dados", "avaliacoes": 1, "media": 7.5, "aproveitamento": 0.75},
    ]


def test_adaptive_goal_plan_prioritizes_low_scores():
    result = build_adaptive_goal_plan(
        SUBJECTS,
        {"ihc": [{"difficulty": "LOW"}], "bd": [{"difficulty": "HIGH"}]},
        [
            {"subject_id": "ihc", "score": 4, "max_score": 10},
            {"subject_id": "bd", "score": 9, "max_score": 10},
        ],
        [],
        100,
        "Priorizar notas",
    )

    assert result[0]["disciplina"] == "IHC"
    assert result[0]["minutos"] > result[1]["minutos"]


def test_subject_summary_separates_planned_and_completed_minutes():
    today = date(2026, 8, 30)
    sessions = [
        {"subject_id": "ihc", "study_date": "2026-08-30", "duration": 60, "status": "Concluída"},
        {"subject_id": "ihc", "study_date": "2026-08-31", "duration": 30, "status": "Pendente"},
        {"subject_id": "bd", "study_date": "2026-08-31", "duration": 45, "status": "Pendente"},
    ]

    result = build_subject_summary(sessions, SUBJECTS, today=today)

    assert result == [
        {"disciplina": "IHC", "planejados": 90, "concluídos": 60, "pendentes": 1, "atrasadas": 0},
        {"disciplina": "Banco de Dados", "planejados": 45, "concluídos": 0, "pendentes": 1, "atrasadas": 0},
    ]


def test_week_summary_always_has_seven_days_and_marks_overdue():
    sessions = [
        {"study_date": "2026-08-24", "duration": 60, "status": "Concluída", "subject_id": "ihc"},
        {"study_date": "2026-08-25", "duration": 30, "status": "Pendente", "subject_id": "ihc"},
    ]

    result = build_week_summary(sessions, date(2026, 8, 24), today=date(2026, 8, 25))

    assert len(result) == 7
    assert result[0]["concluídos"] == 60
    assert result[1]["pendentes"] == 1
    assert result[6]["data"] == "2026-08-30"


def test_subject_summary_can_be_limited_to_the_selected_week():
    sessions = [
        {"study_date": "2026-08-24", "duration": 60, "status": "Pendente", "subject_id": "ihc"},
        {"study_date": "2026-09-01", "duration": 45, "status": "Pendente", "subject_id": "ihc"},
    ]

    selected_week = [session for session in sessions if "2026-08-24" <= session["study_date"] <= "2026-08-30"]

    result = build_subject_summary(selected_week, SUBJECTS, today=date(2026, 8, 30))

    assert result[0]["planejados"] == 60
    assert result[0]["atrasadas"] == 1


def test_topic_summary_calculates_completed_minutes():
    result = build_topic_summary(
        [
            {"topic_id": "topic-1", "duration": 60, "status": "Concluída", "study_date": "2026-09-15"},
            {"topic_id": "topic-1", "duration": 30, "status": "Pendente", "study_date": "2026-09-16"},
        ],
        [{"_id": "topic-1", "title": "Funções"}, {"_id": "topic-2", "title": "Listas"}],
        today=date(2026, 9, 15),
    )

    assert result[0]["completed_minutes"] == 60
    assert result[0]["planned_minutes"] == 90
    assert result[0]["progress"] == 60 / 90
    assert result[1]["session_count"] == 0
