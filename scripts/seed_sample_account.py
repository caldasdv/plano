"""Carrega um semestre de exemplo na conta de um usuário do MongoDB Atlas.

O usuário precisa ter entrado no app ao menos uma vez com o Google.
Sem `--apply`, apenas mostra o que seria feito.

    python scripts/seed_sample_account.py --email voce@exemplo.com
    python scripts/seed_sample_account.py --email voce@exemplo.com --apply
    python scripts/seed_sample_account.py --email voce@exemplo.com --remove --apply
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.config.settings import get_settings
from src.database.indexes import ensure_indexes
from src.database.local_seed import SAMPLE_KEY, seed_sample_semester

COLLECTIONS = (
    "study_sessions",
    "evaluations",
    "class_meetings",
    "topics",
    "subjects",
    "academic_periods",
)


def _sample_counts(database, user_id) -> dict[str, int]:
    query = {"user_id": user_id, "sample_key": SAMPLE_KEY}
    return {name: database[name].count_documents(query) for name in COLLECTIONS}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--email", required=True, help="e-mail da conta Google no app")
    parser.add_argument("--remove", action="store_true", help="remove o semestre de exemplo")
    parser.add_argument("--apply", action="store_true", help="grava no banco")
    args = parser.parse_args()

    load_dotenv(PROJECT_DIR / ".env")
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri, server_api=ServerApi("1"), serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    database = client[settings.database_name]
    print(f"Banco: {settings.database_name}")

    users = list(database.users.find({"email": args.email}, {"_id": 1, "name": 1}))
    if len(users) != 1:
        print(f"Esperava 1 usuário com {args.email}, encontrei {len(users)}. Entre no app antes.")
        return 1
    user = users[0]
    existing = _sample_counts(database, user["_id"])
    print(f"Usuário: {user.get('name')} ({user['_id']})")
    print(f"Documentos de exemplo existentes: {existing}")

    if args.remove:
        if not args.apply:
            print("Simulação: rode com --apply para remover.")
            return 0
        query = {"user_id": user["_id"], "sample_key": SAMPLE_KEY}
        period_ids = [period["_id"] for period in database.academic_periods.find(query, {"_id": 1})]
        for name in COLLECTIONS:
            database[name].delete_many(query)
        database.users.update_one(
            {"_id": user["_id"], "current_academic_period_id": {"$in": period_ids}},
            {"$unset": {"current_academic_period_id": ""}},
        )
        print("Semestre de exemplo removido.")
        return 0

    if any(existing.values()):
        print("Esta conta já tem o semestre de exemplo. Use --remove antes de carregar de novo.")
        return 1
    if not args.apply:
        print("Simulação: rode com --apply para gravar.")
        return 0
    ensure_indexes(database)
    seed_sample_semester(database, user["_id"])
    print(f"Semestre de exemplo criado: {_sample_counts(database, user['_id'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
