from datetime import date

import mongomock

from src.database.indexes import ensure_indexes
from src.database.local_seed import seed_local_database


def test_local_seed_fills_every_screen_once() -> None:
    database = mongomock.MongoClient()["plano_estudos_local"]
    ensure_indexes(database)

    seed_local_database(database, today=date(2026, 10, 19))
    seed_local_database(database, today=date(2026, 10, 19))

    user = database.users.find_one({})
    period = database.academic_periods.find_one({"user_id": user["_id"]})
    assert database.users.count_documents({}) == 1
    assert user["current_academic_period_id"] == period["_id"]
    assert period["start_date"] <= "2026-10-19" <= period["end_date"]
    scope = {"user_id": user["_id"], "academic_period_id": period["_id"]}
    assert database.subjects.count_documents(scope) == 3
    assert database.topics.count_documents(scope) == 9
    assert database.class_meetings.count_documents(scope) == 5
    assert database.evaluations.count_documents(scope) == 6
    assert database.study_sessions.count_documents({**scope, "status": "Concluída"}) > 0
    assert database.study_sessions.count_documents(
        {**scope, "study_date": {"$gte": "2026-10-19"}, "status": "Pendente"}
    ) > 0
