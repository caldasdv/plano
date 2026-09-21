"""Conexão compartilhada com o MongoDB Atlas."""

from __future__ import annotations

import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.config.settings import get_settings
from src.config.runtime import is_local_mode
from src.database.indexes import ensure_indexes


def _seed_local_database(database) -> None:
    """Cria um contexto mínimo para a primeira execução local."""
    if database.users.count_documents({}) > 0:
        return
    period = database.academic_periods.insert_one(
        {
            "name": "Demonstração local",
            "name_normalized": "demonstracao local",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "status": "ACTIVE",
        }
    ).inserted_id
    user_id = database.users.insert_one(
        {
            "identity": {"provider": "local-demo", "subject": "local-demo-user"},
            "name": "Estudante local",
            "email": "local@plano.test",
            "weekly_goal_minutes": 300,
            "current_academic_period_id": period,
        }
    ).inserted_id
    database.academic_periods.update_one({"_id": period}, {"$set": {"user_id": user_id}})
    subjects = [
        {"name": "Interação Humano-Computador", "color": "#176b5d"},
        {"name": "Banco de Dados", "color": "#4b83a6"},
        {"name": "Engenharia de Software", "color": "#c58b22"},
    ]
    for item in subjects:
        database.subjects.insert_one(
            {
                "user_id": user_id,
                "academic_period_id": period,
                "name": item["name"],
                "name_normalized": item["name"].lower(),
                "color": item["color"],
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
