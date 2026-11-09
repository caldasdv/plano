"""Casos de uso de usuário."""

from __future__ import annotations

from typing import Any


class UserService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def get_or_create_authenticated_user(self, identity: dict[str, str]) -> dict[str, Any]:
        """Resolve o usuário pelo identificador estável do provedor OIDC."""
        return self.repository.find_or_create_by_identity(identity)

    def update_weekly_goal(self, user_id: Any, hours: float) -> None:
        if not 1 <= hours <= 80:
            raise ValueError("A meta semanal deve ficar entre 1 e 80 horas.")
        self.repository.update_weekly_goal(user_id, round(hours * 60))

    def update_current_academic_period(self, user_id: Any, period_id: Any) -> None:
        self.repository.update_current_academic_period(user_id, period_id)

    def update_dark_mode(self, user_id: Any, enabled: bool) -> None:
        """Persiste a preferência visual do usuário."""
        if not isinstance(enabled, bool):
            raise ValueError("A preferência de modo escuro deve ser booleana.")
        self.repository.update_dark_mode(user_id, enabled)

    def complete_onboarding(self, user_id: Any) -> None:
        """Registra que o usuário viu ou pulou o tour de boas-vindas."""
        self.repository.mark_onboarding_completed(user_id)
