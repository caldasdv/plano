from datetime import date, time

import pytest

from src.services.session_service import SessionService
from src.services.subject_service import SubjectService
from src.services.user_service import UserService


class FakeSessionRepository:
    def __init__(self, pending=None):
        self.pending = pending or []
        self.created = []
        self.updated = []
        self.completed = []
        self.reopened = []
        self.deleted = []

    def list_by_user(self, user_id, start_date=None, end_date=None):
        self.list_range = (user_id, start_date, end_date)
        return []

    def list_pending_by_date(self, user_id, study_date):
        return self.pending

    def create(self, data):
        self.created.append(data)
        return "session-id"

    def mark_completed(self, session_id, user_id):
        self.completed.append((session_id, user_id))

    def mark_pending(self, session_id, user_id):
        self.reopened.append((session_id, user_id))

    def update(self, session_id, user_id, data):
        self.updated.append((session_id, user_id, data))

    def delete(self, session_id, user_id):
        self.deleted.append((session_id, user_id))


class FakeUserRepository:
    def __init__(self):
        self.users = {}

    def find_or_create_by_identity(self, identity):
        key = (identity["provider"], identity["subject"])
        return self.users.setdefault(
            key,
            {
                "_id": key,
                "identity": {"provider": identity["provider"], "subject": identity["subject"]},
                "name": identity["name"],
                "email": identity["email"],
                "weekly_goal_minutes": 300,
            },
        )

    def update_weekly_goal(self, user_id, minutes):
        self.goal = (user_id, minutes)

    def update_current_academic_period(self, user_id, period_id):
        self.current_period = (user_id, period_id)


class FakeSubjectRepository:
    def __init__(self, valid_subject_ids=None):
        self.valid_subject_ids = set(valid_subject_ids or ["subject-id"])
        self.normalized_names = set()
        self.created = []
        self.assigned = []
        self.updated = []
        self.period_subjects = []

    def belongs_to_user_period(self, user_id, subject_id, academic_period_id):
        return subject_id in self.valid_subject_ids and academic_period_id == "period-id"

    def list_by_user(self, user_id):
        return [
            {"_id": index, "name": name}
            for index, name in enumerate(getattr(self, "legacy_names", []))
        ] + self.period_subjects

    def list_by_period(self, user_id, academic_period_id):
        return [
            subject
            for subject in self.list_by_user(user_id)
            if subject.get("academic_period_id") == academic_period_id
        ]

    def list_without_period(self, user_id):
        return [
            subject
            for subject in self.list_by_user(user_id)
            if "academic_period_id" not in subject
        ]

    def find_legacy_owned(self, user_id, subject_id):
        return next(
            (
                subject
                for subject in self.list_without_period(user_id)
                if subject["_id"] == subject_id
            ),
            None,
        )

    def exists_by_normalized_name(self, user_id, academic_period_id, normalized_name):
        return (academic_period_id, normalized_name) in self.normalized_names

    def create(self, user_id, academic_period_id, name, normalized_name, color):
        self.created.append((user_id, academic_period_id, name, normalized_name, color))
        self.normalized_names.add((academic_period_id, normalized_name))
        return "subject-id"

    def assign_legacy_to_period(
        self, user_id, subject_id, academic_period_id, normalized_name
    ):
        self.assigned.append(
            (user_id, subject_id, academic_period_id, normalized_name)
        )

    def update(
        self, user_id, subject_id, academic_period_id, name, normalized_name, color
    ):
        self.updated.append(
            (user_id, subject_id, academic_period_id, name, normalized_name, color)
        )


class FakeAcademicPeriodRepository:
    def is_active_owned_by(self, user_id, academic_period_id):
        return user_id == "user-id" and academic_period_id == "period-id"


class FakeTopicRepository:
    def __init__(self, valid_topic_ids=None):
        self.valid_topic_ids = set(valid_topic_ids or [])

    def belongs_to_subject(self, user_id, academic_period_id, subject_id, topic_id):
        return topic_id in self.valid_topic_ids


def build_subject_service(repository=None):
    return SubjectService(
        repository or FakeSubjectRepository(), FakeAcademicPeriodRepository()
    )


def test_session_service_creates_normalized_session():
    repository = FakeSessionRepository()
    service = SessionService(repository, FakeSubjectRepository())

    result = service.create(
        user_id="user-id",
        academic_period_id="period-id",
        subject_id="subject-id",
        topic="  Heurísticas  ",
        goal="  Revisar  ",
        study_date=date.today(),
        study_time=time(14, 0),
        duration=60,
        priority="Alta",
    )

    assert result == "session-id"
    assert repository.created[0]["topic"] == "Heurísticas"
    assert repository.created[0]["goal"] == "Revisar"
    assert repository.created[0]["status"] == "Pendente"
    assert repository.created[0]["academic_period_id"] == "period-id"


def test_session_service_links_owned_topic():
    repository = FakeSessionRepository()
    service = SessionService(
        repository, FakeSubjectRepository(), FakeTopicRepository(["topic-id"])
    )

    service.create(
        user_id="user-id",
        academic_period_id="period-id",
        subject_id="subject-id",
        topic="Revisão",
        goal="",
        study_date=date.today(),
        study_time=time(14, 0),
        duration=60,
        priority="Média",
        topic_id="topic-id",
    )

    assert repository.created[0]["topic_id"] == "topic-id"


def test_session_service_rejects_topic_from_other_subject():
    service = SessionService(
        FakeSessionRepository(), FakeSubjectRepository(), FakeTopicRepository()
    )

    with pytest.raises(ValueError, match="conteúdo válido"):
        service.create(
            user_id="user-id",
            academic_period_id="period-id",
            subject_id="subject-id",
            topic="Revisão",
            goal="",
            study_date=date.today(),
            study_time=time(14, 0),
            duration=60,
            priority="Média",
            topic_id="other-topic",
        )


def test_session_service_rejects_conflicting_session():
    repository = FakeSessionRepository([{"study_time": "14:00", "duration": 60}])
    service = SessionService(repository, FakeSubjectRepository())

    with pytest.raises(ValueError, match="conflita"):
        service.create(
            user_id="user-id",
            academic_period_id="period-id",
            subject_id="subject-id",
            topic="Revisão",
            goal="",
            study_date=date.today(),
            study_time=time(14, 30),
            duration=30,
            priority="Média",
        )

    assert repository.created == []


def test_session_service_updates_own_session_without_self_conflict():
    repository = FakeSessionRepository([{"_id": "session-id", "study_time": "14:00", "duration": 60}])
    service = SessionService(repository, FakeSubjectRepository())

    service.update(
        session_id="session-id",
        user_id="user-id",
        academic_period_id="period-id",
        subject_id="subject-id",
        topic="Revisão",
        goal="",
        study_date=date.today(),
        study_time=time(14, 30),
        duration=30,
        priority="Média",
    )

    assert repository.updated[0][0:2] == ("session-id", "user-id")
    assert repository.updated[0][2]["topic"] == "Revisão"


def test_subject_service_rejects_blank_name():
    with pytest.raises(ValueError, match="nome"):
        build_subject_service().create("user-id", "period-id", "  ", "#5E6AD2")


def test_subject_service_rejects_equivalent_duplicate_name():
    repository = FakeSubjectRepository()
    repository.normalized_names.add(("period-id", "interação humano-computador"))

    with pytest.raises(ValueError, match="já possui"):
        build_subject_service(repository).create(
            "user-id", "period-id", "  INTERAÇÃO   HUMANO-COMPUTADOR ", "#5E6AD2"
        )


def test_subject_service_does_not_assign_or_block_legacy_name_implicitly():
    repository = FakeSubjectRepository()
    repository.legacy_names = ["Interação Humano-Computador"]

    build_subject_service(repository).create(
        "user-id", "period-id", " interação  humano-computador ", "#5E6AD2"
    )

    assert repository.created


def test_subject_service_rejects_invalid_color():
    with pytest.raises(ValueError, match="cor válida"):
        build_subject_service().create("user-id", "period-id", "IHC", "red")


def test_subject_service_updates_owned_subject():
    repository = FakeSubjectRepository()
    repository.period_subjects = [
        {"_id": "subject-id", "name": "IHC", "academic_period_id": "period-id"}
    ]

    build_subject_service(repository).update(
        "user-id", "subject-id", "period-id", "Interação Humano-Computador", "#176B5D"
    )

    assert repository.updated == [
        (
            "user-id",
            "subject-id",
            "period-id",
            "Interação Humano-Computador",
            "interação humano-computador",
            "#176B5D",
        )
    ]


def test_subject_service_requires_active_owned_period():
    with pytest.raises(ValueError, match="período acadêmico ativo"):
        build_subject_service().create(
            "user-id", "another-period", "IHC", "#5E6AD2"
        )


def test_subject_service_assigns_legacy_subject_to_active_period():
    repository = FakeSubjectRepository()
    repository.legacy_names = ["  Interação   Humano-Computador "]

    build_subject_service(repository).assign_legacy_to_period(
        "user-id", 0, "period-id"
    )

    assert repository.assigned == [
        ("user-id", 0, "period-id", "interação humano-computador")
    ]


def test_subject_service_rejects_missing_or_already_assigned_legacy_subject():
    with pytest.raises(ValueError, match="não foi encontrada"):
        build_subject_service().assign_legacy_to_period(
            "user-id", "foreign-subject", "period-id"
        )


def test_subject_service_rejects_inactive_destination_period():
    repository = FakeSubjectRepository()
    repository.legacy_names = ["IHC"]

    with pytest.raises(ValueError, match="período acadêmico ativo"):
        build_subject_service(repository).assign_legacy_to_period(
            "user-id", 0, "archived-period"
        )


def test_subject_service_rejects_duplicate_name_in_destination_period():
    repository = FakeSubjectRepository()
    repository.legacy_names = ["IHC"]
    repository.normalized_names.add(("period-id", "ihc"))

    with pytest.raises(ValueError, match="já possui"):
        build_subject_service(repository).assign_legacy_to_period(
            "user-id", 0, "period-id"
        )

    assert repository.assigned == []


def test_session_service_rejects_subject_from_another_user():
    repository = FakeSessionRepository()
    service = SessionService(repository, FakeSubjectRepository(valid_subject_ids=[]))

    with pytest.raises(ValueError, match="disciplina válida"):
        service.create(
            user_id="user-id",
            academic_period_id="period-id",
            subject_id="another-user-subject",
            topic="Revisão",
            goal="",
            study_date=date.today(),
            study_time=time(14, 0),
            duration=30,
            priority="Média",
        )

    assert repository.created == []


def test_session_service_rejects_subject_from_another_period():
    repository = FakeSessionRepository()
    service = SessionService(repository, FakeSubjectRepository())

    with pytest.raises(ValueError, match="período acadêmico atual"):
        service.create(
            user_id="user-id",
            academic_period_id="another-period",
            subject_id="subject-id",
            topic="Revisão",
            goal="",
            study_date=date.today(),
            study_time=time(14, 0),
            duration=30,
            priority="Média",
        )

    assert repository.created == []


def test_session_service_forwards_requested_date_range():
    repository = FakeSessionRepository()
    service = SessionService(repository, FakeSubjectRepository())

    service.list_for_user(
        "user-id", [], start_date=date(2026, 8, 24), end_date=date(2026, 8, 30)
    )

    assert repository.list_range == (
        "user-id",
        date(2026, 8, 24),
        date(2026, 8, 30),
    )


def test_user_service_resolves_user_by_provider_subject():
    repository = FakeUserRepository()
    service = UserService(repository)
    identity = {
        "provider": "google",
        "subject": "google-subject",
        "name": "Ana",
        "email": "ana@example.com",
    }

    first = service.get_or_create_authenticated_user(identity)
    second = service.get_or_create_authenticated_user(identity)

    assert first == second
    assert first["identity"] == {"provider": "google", "subject": "google-subject"}


@pytest.mark.parametrize("hours", [0, 80.5])
def test_user_service_rejects_weekly_goal_outside_allowed_range(hours):
    service = UserService(FakeUserRepository())

    with pytest.raises(ValueError, match="entre 1 e 80"):
        service.update_weekly_goal("user-id", hours)


def test_user_service_updates_current_academic_period():
    repository = FakeUserRepository()

    UserService(repository).update_current_academic_period("user-id", "period-id")

    assert repository.current_period == ("user-id", "period-id")


def test_reopen_returns_completed_session_to_pending():
    repository = FakeSessionRepository()
    service = SessionService(repository, subject_repository=None)

    service.reopen("session-id", "user-id")

    assert repository.reopened == [("session-id", "user-id")]
