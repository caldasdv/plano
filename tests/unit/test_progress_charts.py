from src.ui.components.progress_charts import (
    evaluation_progress_figure,
    subject_progress_figure,
    weekly_progress_figure,
)


def test_subject_progress_figure_contains_minutes_series():
    figure = subject_progress_figure(
        [{"disciplina": "IHC", "planejados": 90, "concluídos": 60}]
    )

    assert [trace.name for trace in figure.data] == ["Planejados", "Concluídos"]
    assert figure.data[0].x == (90,)
    assert figure.layout.xaxis.title.text == "Minutos"


def test_weekly_progress_figure_contains_daily_series():
    figure = weekly_progress_figure(
        [{"dia": "segunda 24/08", "planejados": 60, "concluídos": 30}]
    )

    assert len(figure.data) == 2
    assert figure.data[1].y == (30,)
    assert figure.layout.yaxis.title.text == "Minutos"


def test_evaluation_chart_keeps_same_day_grades_and_excludes_pending_scores():
    figure = evaluation_progress_figure(
        [
            {"subject_id": "ihc", "subject_name": "IHC", "title": "Prova", "evaluation_date": "2026-10-07", "score": 8, "max_score": 10},
            {"subject_id": "ihc", "subject_name": "IHC", "title": "Trabalho", "evaluation_date": "2026-10-07", "score": 6, "max_score": 10},
            {"subject_id": "bd", "subject_name": "Banco de Dados", "title": "Prova", "evaluation_date": "2026-10-07", "score": 15, "max_score": 20},
            {"subject_id": "bd", "subject_name": "Banco de Dados", "title": "Trabalho", "evaluation_date": "2026-10-21", "score": None, "max_score": 10},
        ]
    )

    assert [trace.name for trace in figure.data] == ["IHC", "Banco de Dados"]
    assert figure.data[0].y == (8.0, 6.0)
    assert figure.data[0].x == ("2026-10-07", "2026-10-07")
    assert figure.data[1].y == (7.5,)
