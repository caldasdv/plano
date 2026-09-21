"""Grade semanal visual de aulas com seleção contextual."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import time
import re
from typing import Any

import streamlit as st


_TIMETABLE = st.components.v2.component(
    "class_timetable",
    html='''<p class="timetable-hint">Deslize para ver a semana completa.</p><div class="timetable-scroll"><div class="timetable" id="timetable-root" role="list" aria-label="Grade semanal de aulas"></div></div>''',
    css='''
    .timetable-hint { display: none; margin: 0 0 .5rem; color: var(--st-gray-text-color); font: .8rem var(--st-font); }
    .timetable-scroll { box-sizing: border-box; max-width: 100%; overflow-x: auto; padding: .15rem .15rem .75rem; scrollbar-color: var(--st-primary-color) var(--st-secondary-background-color); scrollbar-width: thin; }
    .timetable { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: .8rem; min-width: 0; width: 100%; }
    .day { min-width: 0; min-height: 14rem; overflow: hidden; padding: .85rem; border: 1px solid #dce5de; border-radius: 14px; background: #edf2ed; }
    .day h3 { margin: 0 0 .7rem; padding-bottom: .6rem; border-bottom: 1px solid var(--st-border-color); color: var(--st-heading-color); font: 600 .85rem var(--st-heading-font); letter-spacing: .04em; text-transform: uppercase; }
    .empty { margin-top: 2.6rem; color: var(--st-gray-text-color); font: .75rem var(--st-font); text-align: center; }
    .meeting { display: block; width: 100%; min-height: 5.2rem; margin: .3rem 0; padding: .65rem; border: 1px solid #dce5de; border-left: 3px solid var(--meeting-color, #176b5d); border-radius: 9px; background: #fcfdf9; color: #172529; cursor: pointer; text-align: left; transition: border-color .15s ease, box-shadow .15s ease, transform .15s ease; }
    .meeting:hover { border-color: var(--st-primary-color); box-shadow: 0 4px 12px rgba(23, 107, 93, .12); transform: translateY(-1px); }
    .meeting.selected { border-color: var(--st-primary-color); background: #e6f2e9; box-shadow: 0 0 0 2px rgba(23, 107, 93, .16), 0 8px 18px rgba(23, 107, 93, .12); transform: translateY(-1px); }
    .meeting:focus-visible { outline: 3px solid var(--st-primary-color); outline-offset: 2px; }
    .meeting-head { display: flex; align-items: center; justify-content: space-between; gap: .4rem; min-width: 0; }
    .meeting-head strong { flex: 0 0 auto; min-width: 0; line-height: 1.15; white-space: nowrap; }
    .meeting strong, .meeting span { display: block; }
    .meeting strong { font: 600 .78rem var(--st-font); }
    .meeting span { margin-top: .35rem; overflow-wrap: anywhere; font: .78rem var(--st-font); line-height: 1.3; }
    .meeting-location { color: var(--st-gray-text-color); font-size: .68rem !important; }
    .timetable.dark .day { border-color: #304840; background: #20332e; }
    .timetable.dark .day h3 { color: #9ce3c5; }
    .timetable.dark .empty { color: #a7b9b1; }
    .timetable.dark .meeting { border-color: #304840; background: #182522; color: #edf7f1; }
    .timetable.dark .meeting-location { color: #a7b9b1 !important; }
    .timetable.dark .meeting.selected { background: #1e493d; }
    @media (max-width: 640px) and (hover: none) { .timetable-hint { display: block; } .timetable-scroll { -webkit-overflow-scrolling: touch; } .timetable { grid-template-columns: repeat(7, minmax(130px, 1fr)); min-width: 950px; } }
    ''',
    js='''
    export default function (component) {
      const { data, parentElement, setStateValue } = component
      const root = parentElement.querySelector("#timetable-root")
      if (!root) return
      root.classList.toggle("dark", Boolean(data?.dark))
      root.replaceChildren()
      let currentSelected = data?.selected ?? ""
      for (const day of (data?.days ?? [])) {
        const section = document.createElement("section")
        section.className = "day"
        section.setAttribute("role", "listitem")
        const heading = document.createElement("h3")
        heading.textContent = day.label
        section.appendChild(heading)
        if (!day.meetings.length) {
          const empty = document.createElement("p")
          empty.className = "empty"
          empty.textContent = "Livre"
          section.appendChild(empty)
        }
        for (const meeting of day.meetings) {
          const card = document.createElement("button")
          card.className = "meeting"
          card.type = "button"
          card.setAttribute("aria-label", `Ver detalhes de ${meeting.subject}`)
          if (meeting.id === data?.selected) card.classList.add("selected")
          card.onclick = () => {
            currentSelected = currentSelected === meeting.id ? "" : meeting.id
            root.querySelectorAll(".meeting.selected").forEach((item) => item.classList.remove("selected"))
            if (currentSelected === meeting.id) card.classList.add("selected")
            setStateValue("selected", currentSelected)
          }
          if (meeting.color) card.style.setProperty("--meeting-color", meeting.color)
          const time = document.createElement("strong")
          time.textContent = `${meeting.start}–${meeting.end}`
          const header = document.createElement("div")
          header.className = "meeting-head"
          header.appendChild(time)
          card.appendChild(header)
          const subject = document.createElement("span")
          subject.textContent = meeting.subject
          card.appendChild(subject)
          if (meeting.location) {
            const location = document.createElement("span")
            location.className = "meeting-location"
            location.textContent = meeting.location
            card.appendChild(location)
          }
          section.appendChild(card)
        }
        root.appendChild(section)
      }
    }
    ''',
)


def _safe_color(value: Any) -> str:
    return (
        value
        if isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value)
        else "#176B5D"
    )


def render_class_timetable(
    meetings: Iterable[dict[str, Any]],
    weekdays: Sequence[str],
    *,
    key: str,
    selected_id: str | None = None,
    dark_mode: bool = False,
) -> tuple[str | None, str | None, str | None]:
    """Renderiza a grade e retorna IDs removida, editada e selecionada."""
    meetings_by_day: dict[int, list[dict[str, str]]] = {
        weekday: [] for weekday in range(len(weekdays))
    }
    for meeting in meetings:
        start = time.fromisoformat(str(meeting["start_time"]))
        end = time.fromisoformat(str(meeting["end_time"]))
        meetings_by_day[meeting["weekday"]].append(
            {
                "id": str(meeting["_id"]),
                "start": start.strftime("%H:%M"),
                "end": end.strftime("%H:%M"),
                "subject": str(meeting["subject_name"]),
                "location": str(meeting.get("location", "")),
                "color": _safe_color(meeting.get("subject_color")),
            }
        )
    days = [
        {"label": weekday_name[:3], "meetings": meetings_by_day[weekday]}
        for weekday, weekday_name in enumerate(weekdays)
    ]
    result = _TIMETABLE(
        key=key,
        data={"days": days, "selected": selected_id, "dark": dark_mode},
        default={"selected": selected_id or ""},
        on_deleted_change=lambda: None,
        on_edited_change=lambda: None,
        on_selected_change=lambda: None,
    )
    return (
        getattr(result, "deleted", None),
        getattr(result, "edited", None),
        getattr(result, "selected", None),
    )


def render_class_timetable_fallback(
    meetings: Iterable[dict[str, Any]], weekdays: Sequence[str]
) -> None:
    """Oferece uma leitura textual nativa quando o componente visual não é suportado."""
    meetings = list(meetings)
    with st.expander("Ver lista textual da grade", expanded=False):
        for weekday, weekday_name in enumerate(weekdays):
            day_meetings = [meeting for meeting in meetings if meeting["weekday"] == weekday]
            st.markdown(f"**{weekday_name}**")
            if not day_meetings:
                st.caption("Livre")
                continue
            for meeting in day_meetings:
                location = f" · {meeting['location']}" if meeting.get("location") else ""
                st.caption(
                    f"{meeting['start_time']}–{meeting['end_time']} · "
                    f"{meeting['subject_name']}{location}"
                )
