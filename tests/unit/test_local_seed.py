from datetime import date

import mongomock

from src.database.indexes import ensure_indexes
from src.database.local_seed import SAMPLE_KEY, seed_local_database, seed_sample_semester


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


def test_sample_semester_goes_into_an_existing_account() -> None:
    database = mongomock.MongoClient()["plano"]
    ensure_indexes(database)
    user_id = database.users.insert_one(
        {"identity": {"provider": "google", "subject": "123"}, "email": "a@b.c"}
    ).inserted_id

    period_id = seed_sample_semester(database, user_id, today=date(2026, 10, 19))

    assert database.users.find_one({"_id": user_id})["current_academic_period_id"] == period_id
    assert database.academic_periods.find_one({"_id": period_id})["name"] == "Semestre de exemplo"
    sample = {"user_id": user_id, "sample_key": SAMPLE_KEY}
    assert database.subjects.count_documents(sample) == 3
    assert database.study_sessions.count_documents(sample) > 0
