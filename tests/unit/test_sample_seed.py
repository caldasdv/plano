from datetime import date

import mongomock

from src.database.indexes import ensure_indexes
from src.database.sample_seed import SAMPLE_KEY, seed_sample_semester


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
