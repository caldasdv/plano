"""Casos de uso de sessões de estudo."""

from __future__ import annotations

from datetime import date, time
from typing import Any

from src.domain.session_rules import sessions_conflict, validate_new_session


class SessionService:
    def __init__(self, repository, subject_repository, topic_repository=None) -> None:
        self.repository = repository
        self.subject_repository = subject_repository
        self.topic_repository = topic_repository

    def list_for_user(
        self,
        user_id: Any,
        subjects: list[dict[str, Any]],
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, Any]]:
        subjects_by_id = {subject["_id"]: subject for subject in subjects}
        sessions = self.repository.list_by_user(user_id, start_date, end_date)
        for session in sessions:
            subject = subjects_by_id.get(session["subject_id"], {"name": "Sem disciplina", "color": "#787774"})
            session["subject_name"] = subject["name"]
            session["subject_color"] = subject["color"]
        return sessions

    def create(
        self,
        *,
        user_id: Any,
        academic_period_id: Any,
        subject_id: Any,
        topic: str,
        goal: str,
        study_date: date,
        study_time: time,
        duration: int,
        priority: str,
        topic_id: Any | None = None,
    ) -> Any:
        validate_new_session(topic=topic, study_date=study_date, duration=duration)
        self._validate_subject_ownership(user_id, subject_id, academic_period_id)
        self._validate_topic_ownership(user_id, topic_id, subject_id, academic_period_id)
        existing = self.repository.list_pending_by_date(user_id, study_date)
        if sessions_conflict(study_time, duration, existing):
            raise ValueError("Esse horário conflita com outra sessão pendente.")
        data = {
            "user_id": user_id,
            "academic_period_id": academic_period_id,
            "subject_id": subject_id,
            "topic": topic.strip(),
            "study_date": study_date.isoformat(),
            "study_time": study_time.strftime("%H:%M"),
            "duration": duration,
            "priority": priority,
            "status": "Pendente",
            "goal": goal.strip(),
        }
        if topic_id is not None:
            data["topic_id"] = topic_id
        return self.repository.create(data)

    def complete(self, session_id: Any, user_id: Any) -> None:
        self.repository.mark_completed(session_id, user_id)

    def update(
        self,
        *,
        session_id: Any,
        user_id: Any,
        academic_period_id: Any,
        subject_id: Any,
        topic: str,
        goal: str,
        study_date: date,
        study_time: time,
        duration: int,
        priority: str,
        topic_id: Any | None = None,
    ) -> None:
        """Edita uma sessão e revalida conflito, ignorando a própria sessão."""
        validate_new_session(topic=topic, study_date=study_date, duration=duration)
        self._validate_subject_ownership(user_id, subject_id, academic_period_id)
        self._validate_topic_ownership(user_id, topic_id, subject_id, academic_period_id)
        existing = [
            item
            for item in self.repository.list_pending_by_date(user_id, study_date)
            if item.get("_id") != session_id
        ]
        if sessions_conflict(study_time, duration, existing):
            raise ValueError("Esse horário conflita com outra sessão pendente.")
        self.repository.update(
            session_id,
            user_id,
            {
                "subject_id": subject_id,
                "academic_period_id": academic_period_id,
                "topic": topic.strip(),
                "study_date": study_date.isoformat(),
                "study_time": study_time.strftime("%H:%M"),
                "duration": duration,
                "priority": priority,
                "goal": goal.strip(),
                "topic_id": topic_id,
            },
        )

    def delete(self, session_id: Any, user_id: Any) -> None:
        self.repository.delete(session_id, user_id)

    def _validate_subject_ownership(
        self, user_id: Any, subject_id: Any, academic_period_id: Any
    ) -> None:
        if not self.subject_repository.belongs_to_user_period(
            user_id, subject_id, academic_period_id
        ):
            raise ValueError("Selecione uma disciplina válida do período acadêmico atual.")

    def _validate_topic_ownership(
        self, user_id: Any, topic_id: Any | None, subject_id: Any, academic_period_id: Any
    ) -> None:
        if topic_id is None:
            return
        if self.topic_repository is None or not self.topic_repository.belongs_to_subject(
            user_id, academic_period_id, subject_id, topic_id
        ):
            raise ValueError("Selecione um conteúdo válido da disciplina.")
