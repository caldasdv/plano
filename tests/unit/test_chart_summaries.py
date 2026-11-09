from src.ui.components.chart_summaries import (
    describe_grades,
    describe_subject_load,
    describe_week_rhythm,
)


def test_subject_load_names_busiest_subject():
    summary = [
        {"disciplina": "IHC", "planejados": 90, "concluídos": 60},
        {"disciplina": "BD", "planejados": 120, "concluídos": 0},
    ]
    assert describe_subject_load(summary) == (
        "60 de 210 minutos planejados foram concluídos. Maior carga: BD, com 120 minutos."
    )
    assert describe_subject_load([]) == "Nenhuma sessão planejada nesta semana."


def test_week_rhythm_names_best_day():
    summary = [
        {"dia": "segunda 02/11", "planejados": 60, "concluídos": 60},
        {"dia": "terça 03/11", "planejados": 90, "concluídos": 30},
    ] + [{"dia": f"d{i}", "planejados": 0, "concluídos": 0} for i in range(5)]
    assert describe_week_rhythm(summary) == (
        "2 de 7 dias têm sessões planejadas. "
        "Dia com mais estudo concluído: segunda 02/11, com 60 minutos."
    )


def test_grades_compare_subject_averages_and_skip_pending():
    evaluations = [
        {"subject_name": "IHC", "score": 9, "max_score": 10},
        {"subject_name": "BD", "score": 3, "max_score": 5},
        {"subject_name": "BD", "score": None, "max_score": 10},
    ]
    assert describe_grades(evaluations) == (
        "2 notas registradas. Maior média: IHC (9.0 de 10). Menor média: BD (6.0 de 10)."
    )
    assert describe_grades([]) == "Nenhuma nota registrada."
