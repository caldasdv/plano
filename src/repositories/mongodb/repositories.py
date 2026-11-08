"""Implementações MongoDB dos repositories do MVP."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from src.domain.exceptions import (
    DuplicateAcademicPeriodError,
    DuplicateSubjectError,
    EntityNotFoundError,
)


class MongoUserRepository:
    def __init__(self, database) -> None:
        self.collection = database.users

    def find_or_create_by_identity(self, identity: dict[str, str]) -> dict[str, Any]:
        return self.collection.find_one_and_update(
            {
                "identity.provider": identity["provider"],
                "identity.subject": identity["subject"],
            },
            {
                "$setOnInsert": {
                    "identity": {
                        "provider": identity["provider"],
                        "subject": identity["subject"],
                    },
                    "name": identity["name"],
                    "email": identity["email"],
                    "weekly_goal_minutes": 300,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def update_weekly_goal(self, user_id: Any, minutes: int) -> None:
        self.collection.update_one({"_id": user_id}, {"$set": {"weekly_goal_minutes": minutes}})

    def update_current_academic_period(self, user_id: Any, period_id: Any) -> None:
        result = self.collection.update_one(
            {"_id": user_id}, {"$set": {"current_academic_period_id": period_id}}
        )
        if result.matched_count == 0:
            raise EntityNotFoundError("O usuário autenticado não foi encontrado.")

    def update_dark_mode(self, user_id: Any, enabled: bool) -> None:
        result = self.collection.update_one(
            {"_id": user_id}, {"$set": {"dark_mode": bool(enabled)}}
        )
        if result.matched_count == 0:
            raise EntityNotFoundError("O usuário autenticado não foi encontrado.")


class MongoAcademicPeriodRepository:
    def __init__(self, database) -> None:
        self.collection = database.academic_periods

    def list_by_user(self, user_id: Any) -> list[dict[str, Any]]:
        return list(
            self.collection.find({"user_id": user_id}).sort(
                [("start_date", -1), ("name", 1)]
            )
        )

    def exists_by_normalized_name(self, user_id: Any, normalized_name: str) -> bool:
        return self.collection.find_one(
            {"user_id": user_id, "name_normalized": normalized_name}, {"_id": 1}
        ) is not None

    def create(
        self,
        user_id: Any,
        name: str,
        normalized_name: str,
        start_date: date,
        end_date: date,
    ) -> Any:
        now = datetime.now(UTC)
        try:
            return self.collection.insert_one(
                {
                    "user_id": user_id,
                    "name": name,
                    "name_normalized": normalized_name,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "status": "ACTIVE",
                    "created_at": now,
                    "updated_at": now,
                }
            ).inserted_id
        except DuplicateKeyError as error:
            raise DuplicateAcademicPeriodError(
                "Você já possui um período acadêmico com esse nome."
            ) from error

    def is_active_owned_by(self, user_id: Any, period_id: Any) -> bool:
        return self.collection.find_one(
            {"_id": period_id, "user_id": user_id, "status": "ACTIVE"}, {"_id": 1}
        ) is not None

    def archive(self, user_id: Any, period_id: Any) -> None:
        result = self.collection.update_one(
            {"_id": period_id, "user_id": user_id, "status": "ACTIVE"},
            {"$set": {"status": "ARCHIVED", "updated_at": datetime.now(UTC)}},
        )
        if result.matched_count == 0:
            raise EntityNotFoundError("O período não foi encontrado ou já está arquivado.")


class MongoSubjectRepository:
    def __init__(self, database) -> None:
        self.collection = database.subjects

    def list_by_user(self, user_id: Any) -> list[dict[str, Any]]:
        return list(self.collection.find({"user_id": user_id}).sort("name", 1))

    def list_by_period(self, user_id: Any, academic_period_id: Any) -> list[dict[str, Any]]:
        return list(
            self.collection.find(
                {"user_id": user_id, "academic_period_id": academic_period_id}
            ).sort("name", 1)
        )

    def list_without_period(self, user_id: Any) -> list[dict[str, Any]]:
        return list(
            self.collection.find(
                {"user_id": user_id, "academic_period_id": {"$exists": False}}
            ).sort("name", 1)
        )

    def find_legacy_owned(
        self, user_id: Any, subject_id: Any
    ) -> dict[str, Any] | None:
        return self.collection.find_one(
            {
                "_id": subject_id,
                "user_id": user_id,
                "academic_period_id": {"$exists": False},
            }
        )

    def belongs_to_user_period(
        self, user_id: Any, subject_id: Any, academic_period_id: Any
    ) -> bool:
        return self.collection.find_one(
            {
                "_id": subject_id,
                "user_id": user_id,
                "academic_period_id": academic_period_id,
            },
            {"_id": 1},
        ) is not None

    def exists_by_normalized_name(
        self, user_id: Any, academic_period_id: Any, normalized_name: str
    ) -> bool:
        return self.collection.find_one(
            {
                "user_id": user_id,
                "academic_period_id": academic_period_id,
                "name_normalized": normalized_name,
            },
            {"_id": 1},
        ) is not None

    def create(
        self,
        user_id: Any,
        academic_period_id: Any,
        name: str,
        normalized_name: str,
        color: str,
    ) -> Any:
        try:
            return self.collection.insert_one(
                {
                    "user_id": user_id,
                    "academic_period_id": academic_period_id,
                    "name": name,
                    "name_normalized": normalized_name,
                    "color": color,
                }
            ).inserted_id
        except DuplicateKeyError as error:
            raise DuplicateSubjectError("Você já possui uma disciplina com esse nome.") from error

    def update(
        self,
        user_id: Any,
        subject_id: Any,
        academic_period_id: Any,
        name: str,
        normalized_name: str,
        color: str,
    ) -> None:
        try:
            result = self.collection.update_one(
                {
                    "_id": subject_id,
                    "user_id": user_id,
                    "academic_period_id": academic_period_id,
                },
                {
                    "$set": {
                        "name": name,
                        "name_normalized": normalized_name,
                        "color": color,
                        "updated_at": datetime.now(UTC),
                    }
                },
            )
        except DuplicateKeyError as error:
            raise DuplicateSubjectError("Você já possui uma disciplina com esse nome.") from error
        if result.matched_count == 0:
            raise EntityNotFoundError("A disciplina não foi encontrada ou não pertence ao período atual.")

    def assign_legacy_to_period(
        self,
        user_id: Any,
        subject_id: Any,
        academic_period_id: Any,
        normalized_name: str,
    ) -> None:
        try:
            result = self.collection.update_one(
                {
                    "_id": subject_id,
                    "user_id": user_id,
                    "academic_period_id": {"$exists": False},
                },
                {
                    "$set": {
                        "academic_period_id": academic_period_id,
                        "name_normalized": normalized_name,
                        "updated_at": datetime.now(UTC),
                    }
                },
            )
        except DuplicateKeyError as error:
            raise DuplicateSubjectError(
                "O período escolhido já possui uma disciplina com esse nome."
            ) from error
        if result.matched_count == 0:
            raise EntityNotFoundError(
                "A disciplina sem período não foi encontrada ou já foi associada."
            )


class MongoClassMeetingRepository:
    def __init__(self, database) -> None:
        self.collection = database.class_meetings

    def list_by_period(
        self, user_id: Any, academic_period_id: Any
    ) -> list[dict[str, Any]]:
        return list(
            self.collection.find(
                {"user_id": user_id, "academic_period_id": academic_period_id}
            ).sort([("weekday", 1), ("start_time", 1), ("subject_id", 1)])
        )

    def list_by_weekday(
        self, user_id: Any, academic_period_id: Any, weekday: int
    ) -> list[dict[str, Any]]:
        return list(
            self.collection.find(
                {
                    "user_id": user_id,
                    "academic_period_id": academic_period_id,
                    "weekday": weekday,
                },
                {"start_time": 1, "end_time": 1},
            ).sort("start_time", 1)
        )

    def create(self, data: dict[str, Any]) -> Any:
        now = datetime.now(UTC)
        document = {**data, "created_at": now, "updated_at": now}
        return self.collection.insert_one(document).inserted_id

    def update(
        self, user_id: Any, academic_period_id: Any, meeting_id: Any, data: dict[str, Any]
    ) -> None:
        result = self.collection.update_one(
            {
                "_id": meeting_id,
                "user_id": user_id,
                "academic_period_id": academic_period_id,
            },
            {"$set": {**data, "updated_at": datetime.now(UTC)}},
        )
        if result.matched_count == 0:
            raise EntityNotFoundError("A aula não foi encontrada ou não está mais disponível.")

    def delete(
        self, user_id: Any, academic_period_id: Any, meeting_id: Any
    ) -> None:
        result = self.collection.delete_one(
            {
                "_id": meeting_id,
                "user_id": user_id,
                "academic_period_id": academic_period_id,
            }
        )
        if result.deleted_count == 0:
            raise EntityNotFoundError("A aula não foi encontrada ou não está mais disponível.")


class MongoTopicRepository:
    def __init__(self, database) -> None:
        self.collection = database.topics

    def list_for_subject(self, user_id: Any, academic_period_id: Any, subject_id: Any) -> list[dict[str, Any]]:
        return list(self.collection.find({"user_id": user_id, "academic_period_id": academic_period_id, "subject_id": subject_id}).sort("title", 1))

    def belongs_to_subject(self, user_id: Any, academic_period_id: Any, subject_id: Any, topic_id: Any) -> bool:
        return self.collection.find_one({"_id": topic_id, "user_id": user_id, "academic_period_id": academic_period_id, "subject_id": subject_id}, {"_id": 1}) is not None

    def exists_by_title(self, user_id: Any, academic_period_id: Any, subject_id: Any, parent_id: Any | None, title_normalized: str) -> bool:
        query = {"user_id": user_id, "academic_period_id": academic_period_id, "subject_id": subject_id, "title_normalized": title_normalized, "parent_id": parent_id}
        return self.collection.find_one(query, {"_id": 1}) is not None

    def create(self, user_id: Any, academic_period_id: Any, subject_id: Any, parent_id: Any | None, title: str, title_normalized: str, status: str, difficulty: str) -> Any:
        from datetime import UTC, datetime
        document = {"user_id": user_id, "academic_period_id": academic_period_id, "subject_id": subject_id, "title": title, "title_normalized": title_normalized, "status": status, "difficulty": difficulty, "created_at": datetime.now(UTC), "updated_at": datetime.now(UTC)}
        if parent_id is not None:
            document["parent_id"] = parent_id
        return self.collection.insert_one(document).inserted_id


class MongoStudySessionRepository:
    def __init__(self, database) -> None:
        self.collection = database.study_sessions

    def list_by_user(
        self, user_id: Any, start_date: date | None = None, end_date: date | None = None
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"user_id": user_id}
        if start_date is not None or end_date is not None:
            date_range: dict[str, str] = {}
            if start_date is not None:
                date_range["$gte"] = start_date.isoformat()
            if end_date is not None:
                date_range["$lte"] = end_date.isoformat()
            query["study_date"] = date_range
        return list(self.collection.find(query).sort([("study_date", 1), ("study_time", 1)]))

    def list_pending_by_date(self, user_id: Any, study_date: date) -> list[dict[str, Any]]:
        return list(
            self.collection.find(
                {"user_id": user_id, "study_date": study_date.isoformat(), "status": "Pendente"},
                {"study_time": 1, "duration": 1},
            )
        )

    def create(self, data: dict[str, Any]) -> Any:
        return self.collection.insert_one(data).inserted_id

    def update(self, session_id: Any, user_id: Any, data: dict[str, Any]) -> None:
        result = self.collection.update_one({"_id": session_id, "user_id": user_id}, {"$set": data})
        if result.matched_count == 0:
            raise EntityNotFoundError("A sessão não foi encontrada ou não está mais disponível.")

    def mark_completed(self, session_id: Any, user_id: Any) -> None:
        result = self.collection.update_one(
            {"_id": session_id, "user_id": user_id}, {"$set": {"status": "Concluída"}}
        )
        if result.matched_count == 0:
            raise EntityNotFoundError("A sessão não foi encontrada ou não está mais disponível.")

    def mark_pending(self, session_id: Any, user_id: Any) -> None:
        result = self.collection.update_one(
            {"_id": session_id, "user_id": user_id}, {"$set": {"status": "Pendente"}}
        )
        if result.matched_count == 0:
            raise EntityNotFoundError("A sessão não foi encontrada ou não está mais disponível.")

    def delete(self, session_id: Any, user_id: Any) -> None:
        result = self.collection.delete_one({"_id": session_id, "user_id": user_id})
        if result.deleted_count == 0:
            raise EntityNotFoundError("A sessão não foi encontrada ou não está mais disponível.")


class MongoEvaluationRepository:
    def __init__(self, database) -> None:
        self.collection = database.evaluations

    def list_by_period(self, user_id: Any, academic_period_id: Any, subjects: list[dict[str, Any]]) -> list[dict[str, Any]]:
        names = {subject["_id"]: subject["name"] for subject in subjects}
        rows = list(self.collection.find({"user_id": user_id, "academic_period_id": academic_period_id}).sort("evaluation_date", 1))
        for row in rows:
            row["subject_name"] = names.get(row["subject_id"], "Disciplina indisponível")
        return rows

    def create(self, data: dict[str, Any]) -> Any:
        return self.collection.insert_one(data).inserted_id
