"""Carga demonstrativa do modo local (mongomock em memória)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta


SUBJECTS = (
    ("Interação Humano-Computador", "#176b5d", ("Heurísticas", "Acessibilidade", "Avaliação prática")),
    ("Banco de Dados", "#4b83a6", ("Entidades", "Relacionamentos", "Consultas SQL")),
    ("Engenharia de Software", "#c58b22", ("Scrum", "Backlog", "Testes")),
)
CLASS_MEETINGS = (
    (0, 0, "08:00", "10:00", "Sala 204"),
    (1, 1, "14:00", "16:00", "Laboratório 3"),
    (2, 2, "10:00", "12:00", "Sala 108"),
    (3, 1, "14:00", "16:00", "Laboratório 3"),
    (4, 0, "08:00", "10:00", "Sala 204"),
)
EVALUATIONS = (
    (0, "Prova 1", "Prova", -45, 8.5),
    (1, "Lista de exercícios", "Exercício", -40, 6.0),
    (2, "Trabalho de requisitos", "Trabalho", -35, 9.0),
    (0, "Trabalho de usabilidade", "Trabalho", -20, 7.5),
    (1, "Prova 1", "Prova", -12, 5.5),
    (2, "Prova 1", "Prova", -6, 7.0),
)


def seed_local_database(database, today: date | None = None) -> None:
    """Cria um semestre de exemplo na primeira execução local."""
    if database.users.count_documents({}) > 0:
        return
    today = today or date.today()
    now = datetime.now(UTC)
    period_id = database.academic_periods.insert_one(
        {
            "name": "Demonstração local",
            "name_normalized": "demonstracao local",
            "start_date": (today - timedelta(days=60)).isoformat(),
            "end_date": (today + timedelta(days=60)).isoformat(),
            "status": "ACTIVE",
        }
    ).inserted_id
    user_id = database.users.insert_one(
        {
            "identity": {"provider": "local-demo", "subject": "local-demo-user"},
            "name": "Estudante local",
            "email": "local@plano.test",
            "weekly_goal_minutes": 300,
            "current_academic_period_id": period_id,
        }
    ).inserted_id
    database.academic_periods.update_one({"_id": period_id}, {"$set": {"user_id": user_id}})
    scope = {"user_id": user_id, "academic_period_id": period_id}

    subject_ids = []
    topic_titles = []
    for name, color, topics in SUBJECTS:
        subject_id = database.subjects.insert_one(
            {**scope, "name": name, "name_normalized": name.lower(), "color": color}
        ).inserted_id
        subject_ids.append(subject_id)
        topic_titles.append(topics)
        for index, title in enumerate(topics):
            database.topics.insert_one(
                {
                    **scope,
                    "subject_id": subject_id,
                    "parent_id": None,
                    "title": title,
                    "title_normalized": title.lower(),
                    "status": ("MASTERED", "IN_PROGRESS", "NOT_STARTED")[index],
                    "difficulty": ("LOW", "MEDIUM", "HIGH")[index],
                    "created_at": now,
                    "updated_at": now,
                }
            )

    sessions = []
    for offset in range(-28, 15):
        study_date = today + timedelta(days=offset)
        if study_date.weekday() >= 5:
            continue
        for slot, study_time in enumerate(("09:00", "19:00")):
            index = (study_date.toordinal() + slot) % len(subject_ids)
            duration = (30, 45, 60)[(study_date.toordinal() + slot) % 3]
            completed = offset < 0 and (study_date.toordinal() + slot) % 4 != 0
            sessions.append(
                {
                    **scope,
                    "subject_id": subject_ids[index],
                    "topic": topic_titles[index][slot % 3],
                    "study_date": study_date.isoformat(),
                    "study_time": study_time,
                    "duration": duration,
                    "priority": "Alta" if duration == 60 else "Média",
                    "status": "Concluída" if completed else "Pendente",
                    "goal": "Avançar uma etapa e registrar o que ficou claro.",
                }
            )
    database.study_sessions.insert_many(sessions)

    database.class_meetings.insert_many(
        [
            {
                **scope,
                "subject_id": subject_ids[index],
                "weekday": weekday,
                "start_time": start,
                "end_time": end,
                "location": location,
                "created_at": now,
                "updated_at": now,
            }
            for weekday, index, start, end, location in CLASS_MEETINGS
        ]
    )
    database.evaluations.insert_many(
        [
            {
                **scope,
                "subject_id": subject_ids[index],
                "title": title,
                "type": evaluation_type,
                "evaluation_date": (today + timedelta(days=offset)).isoformat(),
                "score": score,
                "max_score": 10.0,
            }
            for index, title, evaluation_type, offset, score in EVALUATIONS
        ]
    )
