"""Casos de uso da grade semanal de aulas."""

from __future__ import annotations

from datetime import time
from typing import Any

from src.domain.class_meeting_rules import (
    class_meetings_conflict,
    validate_class_meeting,
)


class ClassMeetingService:
    def __init__(
        self,
        repository,
        subject_repository,
        academic_period_repository,
    ) -> None:
        self.repository = repository
        self.subject_repository = subject_repository
        self.academic_period_repository = academic_period_repository

    def list_for_period(
        self,
        user_id: Any,
        academic_period_id: Any | None,
        subjects: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if academic_period_id is None:
            return []
        subjects_by_id = {subject["_id"]: subject for subject in subjects}
        meetings = self.repository.list_by_period(user_id, academic_period_id)
        for meeting in meetings:
            subject = subjects_by_id.get(
                meeting["subject_id"], {"name": "Disciplina indisponível", "color": "#787774"}
            )
            meeting["subject_name"] = subject["name"]
            meeting["subject_color"] = subject.get("color", "#787774")
        return meetings

    def create(
        self,
        *,
        user_id: Any,
        academic_period_id: Any | None,
        subject_id: Any,
        weekday: int,
        start_time: time,
        end_time: time,
        location: str,
    ) -> Any:
        validate_class_meeting(weekday, start_time, end_time)
        if academic_period_id is None or not self.academic_period_repository.is_active_owned_by(
            user_id, academic_period_id
        ):
            raise ValueError("Defina um período acadêmico ativo para cadastrar aulas.")
        if not self.subject_repository.belongs_to_user_period(
            user_id, subject_id, academic_period_id
        ):
            raise ValueError("Selecione uma disciplina válida do período atual.")
        existing = self.repository.list_by_weekday(
            user_id, academic_period_id, weekday
        )
        if class_meetings_conflict(start_time, end_time, existing):
            raise ValueError("Esse horário conflita com outra aula da sua grade.")
        return self.repository.create(
            {
                "user_id": user_id,
                "academic_period_id": academic_period_id,
                "subject_id": subject_id,
                "weekday": weekday,
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "location": " ".join(location.split()),
            }
        )

    def delete(
        self, user_id: Any, academic_period_id: Any, meeting_id: Any
    ) -> None:
        self.repository.delete(user_id, academic_period_id, meeting_id)

    def update(
        self,
        *,
        user_id: Any,
        academic_period_id: Any | None,
        meeting_id: Any,
        subject_id: Any,
        weekday: int,
        start_time: time,
        end_time: time,
        location: str,
    ) -> None:
        validate_class_meeting(weekday, start_time, end_time)
        if academic_period_id is None or not self.academic_period_repository.is_active_owned_by(
            user_id, academic_period_id
        ):
            raise ValueError("Defina um período acadêmico ativo para editar aulas.")
        if not self.subject_repository.belongs_to_user_period(
            user_id, subject_id, academic_period_id
        ):
            raise ValueError("Selecione uma disciplina válida do período atual.")
        existing = [
            meeting
            for meeting in self.repository.list_by_weekday(
                user_id, academic_period_id, weekday
            )
            if meeting.get("_id") != meeting_id
        ]
        if class_meetings_conflict(start_time, end_time, existing):
            raise ValueError("Esse horário conflita com outra aula da sua grade.")
        self.repository.update(
            user_id,
            academic_period_id,
            meeting_id,
            {
                "subject_id": subject_id,
                "weekday": weekday,
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "location": " ".join(location.split()),
            },
        )
