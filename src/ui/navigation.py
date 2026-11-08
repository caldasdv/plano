"""Mapa único de navegação: os quatro lugares fixos do Plano e os ajustes.

Páginas, títulos e ícones vivem só aqui para que sidebar, atalhos e testes
usem sempre os mesmos nomes (consistência e padronização).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanPage:
    path: str
    title: str
    icon: str


TODAY = PlanPage("app_pages/overview.py", "Hoje", ":material/home:")
WEEK = PlanPage("app_pages/weekly.py", "Semana", ":material/calendar_view_week:")
PROGRESS = PlanPage("app_pages/progress.py", "Progresso", ":material/insights:")
SUBJECTS = PlanPage("app_pages/subjects.py", "Disciplinas", ":material/menu_book:")
PERIODS = PlanPage(
    "app_pages/academic_periods.py", "Períodos acadêmicos", ":material/date_range:"
)

MAIN_PLACES = (TODAY, WEEK, PROGRESS, SUBJECTS)
SETTINGS = (PERIODS,)
