"""Passos de "Primeiros passos", calculados a partir dos dados do usuário."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OnboardingStep:
    key: str
    label: str
    done: bool


def build_onboarding_steps(
    *,
    has_period: bool,
    subject_count: int,
    class_meeting_count: int,
    topic_count: int,
    session_count: int,
    completed_session_count: int,
) -> list[OnboardingStep]:
    return [
        OnboardingStep("period", "Adicionar o período acadêmico", has_period),
        OnboardingStep("subject", "Adicionar uma disciplina", subject_count > 0),
        OnboardingStep("class", "Cadastrar um horário de aula", class_meeting_count > 0),
        OnboardingStep("topic", "Cadastrar um conteúdo para estudar", topic_count > 0),
        OnboardingStep("session", "Planejar a primeira sessão de estudo", session_count > 0),
        OnboardingStep("complete", "Concluir uma sessão", completed_session_count > 0),
    ]


def next_step(steps: list[OnboardingStep]) -> OnboardingStep | None:
    return next((step for step in steps if not step.done), None)
