"""Agenda visual experimental baseada em Custom Component v2."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta
import re
from typing import Any

import streamlit as st

from src.domain.session_rules import effective_status


_AGENDA = st.components.v2.component(
    "study_agenda",
    html='''<p class="agenda-hint">Deslize para ver a semana completa.</p><div class="agenda-scroll"><div class="agenda" id="agenda-root" role="list" aria-label="Agenda semanal"></div></div>''',
    css='''
    .agenda-hint { display: none; margin: 0 0 .5rem; color: #687679; font: .8rem var(--st-font); }
    .agenda-scroll { max-width: 100%; overflow-x: auto; padding: .15rem .15rem .75rem; scrollbar-color: #176b5d #edf2ed; scrollbar-width: thin; }
    .agenda { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: .8rem; min-width: 0; }
    .day { padding: .8rem; border: 1px solid #dce5de; border-radius: 14px; background: #edf2ed; }
    .day.today { border-color: #176b5d; box-shadow: 0 0 0 3px rgba(23, 107, 93, .1), 0 10px 20px rgba(23, 107, 93, .08); }
    .day h3 { margin: 0 0 .9rem; padding-bottom: .7rem; border-bottom: 1px solid #dce5de; color: #0d4d43; font: 600 .95rem var(--st-heading-font); letter-spacing: .04em; text-transform: uppercase; }
    .day-body { position: relative; min-height: 720px; border-radius: 10px; background: repeating-linear-gradient(to bottom, transparent 0, transparent 29px, #dce5de 30px); }
    .empty { margin: 0; padding-top: 2rem; color: #687679; font: .75rem var(--st-font); text-align: center; }
    .session { position: absolute; top: calc(var(--session-top) * 1px); left: 0; width: 100%; min-height: 2.2rem; height: max(36px, calc(var(--session-height) * 1px)); margin: 0; padding: .4rem .55rem; overflow: hidden; border: 1px solid #dce5de; border-left: 4px solid var(--session-color, #176b5d); border-radius: 9px; background: #fcfdf9; color: #172529; text-align: left; cursor: pointer; }
    .session:hover, .session:focus-visible { border-color: #176b5d; }
    .session:focus-visible { outline: 3px solid #c58b22; outline-offset: 2px; }
    .session strong, .session span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .session strong { color: #0d4d43; font: 700 .82rem var(--st-font); }
    .session span { margin-top: .15rem; font: .72rem var(--st-font); line-height: 1.2; }
    .agenda.dark .day { border-color: #304840; background: #20332e; }
    .agenda.dark .day h3 { color: #9ce3c5; }
    .agenda.dark .day-body { background: repeating-linear-gradient(to bottom, transparent 0, transparent 29px, #304840 30px); }
    .agenda.dark .empty { color: #a7b9b1; }
    .agenda.dark .session { border-color: #304840; background: #182522; color: #edf7f1; }
    .agenda.dark .session strong { color: #9ce3c5; }
    @media (max-width: 768px) { .agenda-hint { display: block; } .agenda-scroll { -webkit-overflow-scrolling: touch; } .agenda { grid-template-columns: repeat(7, minmax(155px, 1fr)); min-width: 1140px; } }
    ''',
    js='''
    export default function (component) {
      const { data, parentElement, setTriggerValue } = component
      const root = parentElement.querySelector("#agenda-root")
      if (!root) return
      root.classList.toggle("dark", Boolean(data?.dark))
      root.replaceChildren()
      for (const day of (data?.days ?? [])) {
        const section = document.createElement("section")
        section.className = `day${day.is_today ? " today" : ""}`
        section.setAttribute("role", "listitem")
        const heading = document.createElement("h3")
        heading.textContent = day.label
        section.appendChild(heading)
        const body = document.createElement("div")
        body.className = "day-body"
        const latestEnd = Math.max(720, ...(day.sessions ?? []).map((session) => {
          const start = Number(session.start_minute) - 360
          return start + Number(session.duration)
        }))
        body.style.minHeight = `${latestEnd + 24}px`
        if (!day.sessions.length) {
          const empty = document.createElement("p")
          empty.className = "empty"
          empty.textContent = "Sem sessões"
          body.appendChild(empty)
        }
        for (const session of day.sessions) {
          const button = document.createElement("button")
          button.className = "session"
          button.type = "button"
          if (session.color) button.style.setProperty("--session-color", session.color)
          button.style.setProperty("--session-top", Math.max(0, session.start_minute - 360))
          button.style.setProperty("--session-height", Math.max(36, Number(session.duration)))
          button.setAttribute("aria-label", `${session.time}, ${session.topic}, ${session.status}`)
          const time = document.createElement("strong")
          time.textContent = session.time
          const topic = document.createElement("span")
          topic.textContent = `${session.topic} · ${session.duration} min`
          button.append(time, topic)
          button.onclick = () => setTriggerValue("selected", session.id)
          body.appendChild(button)
        }
        section.appendChild(body)
        root.appendChild(section)
      }
    }
    ''',
)


def render_study_agenda(
    sessions: Iterable[dict[str, Any]], week_start: date, *, key: str, dark_mode: bool = False
) -> str | None:
    """Renderiza a agenda e retorna o ID selecionado nesta execução."""
    sessions_by_date: dict[str, list[dict[str, Any]]] = {}
    for session in sessions:
        sessions_by_date.setdefault(session["study_date"], []).append(
            {
                "id": str(session["_id"]),
                "time": str(session["study_time"]),
                "topic": str(session["topic"]),
                "duration": str(session["duration"]),
                "start_minute": int(session["study_time"][:2]) * 60 + int(session["study_time"][3:]),
                "status": effective_status(session),
                "color": str(session.get("subject_color", "#176B5D"))
                if isinstance(session.get("subject_color"), str)
                and re.fullmatch(r"#[0-9A-Fa-f]{6}", session["subject_color"])
                else "#176B5D",
            }
        )
    weekdays = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    days = [
        {
            "label": f"{weekday} {(week_start + timedelta(days=offset)):%d/%m/%Y}",
            "date": (week_start + timedelta(days=offset)).isoformat(),
            "is_today": week_start + timedelta(days=offset) == date.today(),
            "sessions": sessions_by_date.get((week_start + timedelta(days=offset)).isoformat(), []),
        }
        for offset, weekday in enumerate(weekdays)
    ]
    result = _AGENDA(key=key, data={"days": days, "dark": dark_mode}, on_selected_change=lambda: None)
    return getattr(result, "selected", None)
