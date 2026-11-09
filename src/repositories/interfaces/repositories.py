"""Contratos mínimos usados pelos services."""

from __future__ import annotations

from datetime import date
from typing import Any, Iterable, Protocol


class UserRepository(Protocol):
    def find_or_create_by_identity(self, identity: dict[str, str]) -> dict[str, Any]: ...

    def update_weekly_goal(self, user_id: Any, minutes: int) -> None: ...

    def update_current_academic_period(self, user_id: Any, period_id: Any) -> None: ...

    def update_dark_mode(self, user_id: Any, enabled: bool) -> None: ...

    def mark_onboarding_completed(self, user_id: Any) -> None: ...


class AcademicPeriodRepository(Protocol):
    def list_by_user(self, user_id: Any) -> list[dict[str, Any]]: ...

    def exists_by_normalized_name(self, user_id: Any, normalized_name: str) -> bool: ...

    def create(
        self,
        user_id: Any,
        name: str,
        normalized_name: str,
        start_date: date,
        end_date: date,
    ) -> Any: ...

    def is_active_owned_by(self, user_id: Any, period_id: Any) -> bool: ...

    def archive(self, user_id: Any, period_id: Any) -> None: ...


class SubjectRepository(Protocol):
    def list_by_user(self, user_id: Any) -> list[dict[str, Any]]: ...

    def list_by_period(self, user_id: Any, academic_period_id: Any) -> list[dict[str, Any]]: ...

    def list_without_period(self, user_id: Any) -> list[dict[str, Any]]: ...

    def find_legacy_owned(
        self, user_id: Any, subject_id: Any
    ) -> dict[str, Any] | None: ...

    def belongs_to_user_period(
        self, user_id: Any, subject_id: Any, academic_period_id: Any
    ) -> bool: ...

    def exists_by_normalized_name(
        self, user_id: Any, academic_period_id: Any, normalized_name: str
    ) -> bool: ...

    def create(
        self,
        user_id: Any,
        academic_period_id: Any,
        name: str,
        normalized_name: str,
        color: str,
    ) -> Any: ...

    def update(
        self,
        user_id: Any,
        subject_id: Any,
        academic_period_id: Any,
        name: str,
        normalized_name: str,
        color: str,
    ) -> None: ...

    def assign_legacy_to_period(
        self,
        user_id: Any,
        subject_id: Any,
        academic_period_id: Any,
        normalized_name: str,
    ) -> None: ...


class ClassMeetingRepository(Protocol):
    def list_by_period(
        self, user_id: Any, academic_period_id: Any
    ) -> list[dict[str, Any]]: ...

    def list_by_weekday(
        self, user_id: Any, academic_period_id: Any, weekday: int
    ) -> list[dict[str, Any]]: ...

    def create(self, data: dict[str, Any]) -> Any: ...

    def update(
        self, user_id: Any, academic_period_id: Any, meeting_id: Any, data: dict[str, Any]
    ) -> None: ...

    def delete(
        self, user_id: Any, academic_period_id: Any, meeting_id: Any
    ) -> None: ...


class TopicRepository(Protocol):
    def list_for_subject(self, user_id: Any, academic_period_id: Any, subject_id: Any) -> list[dict[str, Any]]: ...
    def belongs_to_subject(self, user_id: Any, academic_period_id: Any, subject_id: Any, topic_id: Any) -> bool: ...
    def exists_by_title(self, user_id: Any, academic_period_id: Any, subject_id: Any, parent_id: Any | None, title_normalized: str) -> bool: ...
    def create(self, user_id: Any, academic_period_id: Any, subject_id: Any, parent_id: Any | None, title: str, title_normalized: str, status: str, difficulty: str) -> Any: ...


class StudySessionRepository(Protocol):
    def list_by_user(
        self, user_id: Any, start_date: date | None = None, end_date: date | None = None
    ) -> list[dict[str, Any]]: ...

    def list_pending_by_date(self, user_id: Any, study_date: date) -> Iterable[dict[str, Any]]: ...

    def create(self, data: dict[str, Any]) -> Any: ...

    def update(self, session_id: Any, user_id: Any, data: dict[str, Any]) -> None: ...

    def mark_completed(self, session_id: Any, user_id: Any) -> None: ...

    def mark_pending(self, session_id: Any, user_id: Any) -> None: ...

    def delete(self, session_id: Any, user_id: Any) -> None: ...


class EvaluationRepository(Protocol):
    def list_by_period(self, user_id: Any, academic_period_id: Any, subjects: list[dict[str, Any]]) -> list[dict[str, Any]]: ...
    def create(self, data: dict[str, Any]) -> Any: ...
