"""Conexão compartilhada com o MongoDB Atlas."""

from __future__ import annotations

from calendar import monthrange
from datetime import UTC, date, datetime, timedelta

import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.config.settings import get_settings
from src.config.runtime import is_local_mode
from src.database.indexes import ensure_indexes


def _seed_local_database(database) -> None:
    """Cria um mês de aulas, estudos e avaliações na demonstração local."""
    if database.users.count_documents({}) > 0:
        return
    today = date.today()
    month_start = today.replace(day=1)
    month_days = monthrange(today.year, today.month)[1]
    study_dates = [month_start + timedelta(days=offset) for offset in range(month_days)]
    now = datetime.now(UTC)
    period = database.academic_periods.insert_one(
        {
            "name": "Demonstração local",
            "name_normalized": "demonstracao local",
            "start_date": today.replace(month=1, day=1).isoformat(),
            "end_date": today.replace(month=12, day=31).isoformat(),
            "status": "ACTIVE",
        }
    ).inserted_id
    user_id = database.users.insert_one(
        {
            "identity": {"provider": "local-demo", "subject": "local-demo-user"},
            "name": "Estudante local",
            "email": "local@plano.test",
            "weekly_goal_minutes": 600,
            "current_academic_period_id": period,
        }
    ).inserted_id
    database.academic_periods.update_one({"_id": period}, {"$set": {"user_id": user_id}})
    subjects = [
        {
            "name": "Interação Humano-Computador",
            "color": "#0474c4",
            "topics": (
                ("Heurísticas de usabilidade", ("Visibilidade do sistema", "Consistência e padrões")),
                ("Protótipos e testes com usuários", ("Fluxos de navegação", "Roteiro de teste")),
            ),
            "class_times": ("08:00", "09:30"),
            "study_time": "17:30",
            "duration": 45,
            "location": "Sala 101",
            "difficulty": "MEDIUM",
            "scores": (8.5, 9.0),
        },
        {
            "name": "Banco de Dados",
            "color": "#4b83a6",
            "topics": (
                ("Modelagem entidade-relacionamento", ("Entidades e atributos", "Cardinalidades")),
                ("Consultas SQL e joins", ("INNER JOIN e LEFT JOIN", "Agregação com GROUP BY")),
            ),
            "class_times": ("09:40", "11:10"),
            "study_time": "18:15",
            "duration": 60,
            "location": "Laboratório 02",
            "difficulty": "HIGH",
            "scores": (6.0, 7.0),
        },
        {
            "name": "Engenharia de Software",
            "color": "#5379ae",
            "topics": (
                ("Requisitos funcionais", ("Casos de uso", "Critérios de aceite")),
                ("Testes unitários", ("Partições de equivalência", "Mocks e fixtures")),
            ),
            "class_times": ("11:20", "12:10"),
            "study_time": "19:15",
            "duration": 45,
            "location": "Sala 203",
            "difficulty": "LOW",
            "scores": (9.0, 8.0),
        },
        {
            "name": "Algoritmos",
            "color": "#7158a6",
            "topics": (
                ("Recursão", ("Caso base", "Árvore de chamadas")),
                ("Complexidade de algoritmos", ("Notação Big O", "Análise de laços")),
            ),
            "class_times": ("13:00", "14:20"),
            "study_time": "20:00",
            "duration": 30,
            "location": "Laboratório 01",
            "difficulty": "HIGH",
            "scores": (5.5, 6.5),
        },
        {
            "name": "Estruturas de Dados",
            "color": "#b06d35",
            "topics": (
                ("Pilhas e filas", ("Operações de pilha", "Fila circular")),
                ("Árvores binárias", ("Percursos em árvores", "Árvore de busca")),
            ),
            "class_times": ("14:30", "15:50"),
            "study_time": "20:45",
            "duration": 45,
            "location": "Sala 204",
            "difficulty": "MEDIUM",
            "scores": (7.5, 8.0),
        },
        {
            "name": "Redes de Computadores",
            "color": "#31858a",
            "topics": (
                ("Modelo TCP/IP", ("Camadas e protocolos", "Encapsulamento")),
                ("Endereçamento IP", ("Máscaras de sub-rede", "Cálculo de sub-redes")),
            ),
            "class_times": ("16:00", "17:00"),
            "study_time": "21:30",
            "duration": 30,
            "location": "Laboratório de Redes",
            "difficulty": "MEDIUM",
            "scores": (8.0, 7.5),
        },
    ]
    for index, item in enumerate(subjects):
        subject_id = database.subjects.insert_one(
            {
                "user_id": user_id,
                "academic_period_id": period,
                "name": item["name"],
                "name_normalized": item["name"].lower(),
                "color": item["color"],
            }
        ).inserted_id
        ownership = {
            "user_id": user_id,
            "academic_period_id": period,
            "subject_id": subject_id,
        }
        topic_options = []
        for offset, (title, subtopics) in enumerate(item["topics"]):
            completed = offset == 0 and index < 3
            topic_status = "NOT_STARTED"
            if offset == 0:
                topic_status = "REVIEWED" if completed else "IN_PROGRESS"
                if index == 2:
                    topic_status = "MASTERED"
            topic_id = database.topics.insert_one(
                {
                    **ownership,
                    "title": title,
                    "title_normalized": title.casefold(),
                    "status": topic_status,
                    "difficulty": item["difficulty"],
                    "created_at": now,
                    "updated_at": now,
                }
            ).inserted_id
            topic_options.append((topic_id, title))
            for child_index, subtitle in enumerate(subtopics):
                database.topics.insert_one(
                    {
                        **ownership,
                        "parent_id": topic_id,
                        "title": subtitle,
                        "title_normalized": subtitle.casefold(),
                        "status": topic_status if completed or child_index == 0 else "NOT_STARTED",
                        "difficulty": item["difficulty"],
                        "created_at": now,
                        "updated_at": now,
                    }
                )
        for weekday in range(5):
            database.class_meetings.insert_one(
                {
                    **ownership,
                    "weekday": weekday,
                    "start_time": item["class_times"][0],
                    "end_time": item["class_times"][1],
                    "location": item["location"],
                    "created_at": now,
                    "updated_at": now,
                }
            )
        for study_date in study_dates:
            weekend = study_date.weekday() >= 5
            if weekend and index % 3 != study_date.weekday() - 5:
                continue
            topic_id, title = topic_options[((study_date.day - 1) // 7) % len(topic_options)]
            completed = (
                study_date < today and (study_date.day + index) % 5 != 0
            ) or (study_date == today and index < 3)
            study_time = item["study_time"]
            if weekend:
                study_time = "09:00" if index < 3 else "10:15"
            database.study_sessions.insert_one(
                {
                    **ownership,
                    "topic_id": topic_id,
                    "topic": title,
                    "goal": (
                        "Revisar os pontos de maior dificuldade da semana."
                        if weekend else "Revisar os conceitos da aula e resolver exercícios."
                    ),
                    "study_date": study_date.isoformat(),
                    "study_time": study_time,
                    "duration": item["duration"],
                    "priority": "Alta" if item["difficulty"] == "HIGH" else "Média",
                    "status": "Concluída" if completed else "Pendente",
                }
            )
        for week, evaluation_date in enumerate(study_dates[6::7]):
            if evaluation_date.weekday() >= 5:
                evaluation_date -= timedelta(days=evaluation_date.weekday() - 4)
            evaluation_type = ("Exercício", "Trabalho", "Exercício", "Prova")[week]
            title = f"{evaluation_type} {week + 1} — {item['name']}"
            score = item["scores"][week % 2] if evaluation_date <= today else None
            database.evaluations.insert_one(
                {
                    **ownership,
                    "title": title,
                    "type": evaluation_type,
                    "evaluation_date": evaluation_date.isoformat(),
                    "score": score,
                    "max_score": 10.0,
                }
            )


@st.cache_resource
def get_database():
    if is_local_mode():
        import mongomock

        database = mongomock.MongoClient()["plano_estudos_local"]
        ensure_indexes(database)
        _seed_local_database(database)
        return database
    settings = get_settings()
    client = MongoClient(
        settings.mongodb_uri,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=5000,
    )
    client.admin.command("ping")
    database = client[settings.database_name]
    ensure_indexes(database)
    return database
