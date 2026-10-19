"""Conexão compartilhada com o MongoDB Atlas."""

from __future__ import annotations

import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.config.settings import get_settings
from src.config.runtime import is_local_mode
from src.database.indexes import ensure_indexes
from src.database.local_seed import seed_local_database


@st.cache_resource
def get_database():
    if is_local_mode():
        import mongomock

        database = mongomock.MongoClient()["plano_estudos_local"]
        ensure_indexes(database)
        seed_local_database(database)
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
