"""Balões de explicação que apontam para os elementos reais da tela.

Cada passo indica um alvo: um item da navegação lateral (``nav``) ou um seletor
CSS (``selector``, por exemplo ``.st-key-open_help`` para um botão com ``key``).
Passos cujo alvo não está visível na tela atual são pulados.
O balão termina com ``done`` = ``"finish"`` ou ``"skip"``.
"""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st


_CSS = """
.plan-coach-spot { position: fixed; z-index: 2147483000; border-radius: 12px; pointer-events: none;
  box-shadow: 0 0 0 4px #f5b301, 0 0 0 9999px rgba(6, 20, 40, .55); transition: all .2s ease; }
.plan-coach-bubble { position: fixed; z-index: 2147483001; width: min(340px, calc(100vw - 32px)); box-sizing: border-box;
  padding: 1rem 1.1rem .9rem; border-radius: 14px; background: #06457f; color: #ffffff;
  box-shadow: 0 18px 40px rgba(6, 20, 40, .35); font-family: "Source Sans", "Source Sans Pro", "Source Sans 3", sans-serif; }
.plan-coach-bubble:focus { outline: none; }
.plan-coach-arrow { position: absolute; width: 14px; height: 14px; background: #06457f; transform: rotate(45deg); }
.plan-coach-count { margin: 0 0 .25rem; color: #d6e4f7; font-size: .78rem; letter-spacing: .04em; }
.plan-coach-title { margin: 0 0 .35rem; color: #ffffff; font-size: 1.05rem; font-weight: 700; line-height: 1.3; }
.plan-coach-body { margin: 0 0 .9rem; color: #ffffff; font-size: .92rem; line-height: 1.45; }
.plan-coach-actions { display: flex; gap: .5rem; justify-content: flex-end; flex-wrap: wrap; }
.plan-coach-actions button { min-height: 2.25rem; padding: .35rem .8rem; border-radius: 9px; font: inherit; font-size: .88rem; cursor: pointer; }
.plan-coach-skip { margin-right: auto; border: 1px solid transparent; background: transparent; color: #ffffff; text-decoration: underline; }
.plan-coach-back { border: 1px solid #a8c4ec; background: transparent; color: #ffffff; }
.plan-coach-next { border: 1px solid #ffffff; background: #ffffff; color: #06457f; font-weight: 700; }
.plan-coach-actions button:focus-visible { outline: 3px solid #f5b301; outline-offset: 2px; }
.plan-coach-back[disabled] { opacity: .45; cursor: default; }
@media (prefers-reduced-motion: reduce) { .plan-coach-spot { transition: none; } }
"""

_JS = r"""
export default function (component) {
  const { data, setTriggerValue } = component
  const doc = window.document
  if (!doc.getElementById("plan-coach-style")) {
    const style = doc.createElement("style")
    style.id = "plan-coach-style"
    style.textContent = data.css
    doc.head.appendChild(style)
  }
  const state = window.__planCoach
  if (state && state.run === data.run && doc.getElementById("plan-coach-bubble")) {
    state.setTriggerValue = setTriggerValue
    setTimeout(() => state.show(), 150)
    return
  }
  if (state) state.teardown()

  const coach = { run: data.run, index: 0, setTriggerValue }
  window.__planCoach = coach
  const steps = data.steps || []

  const spot = doc.createElement("div")
  spot.className = "plan-coach-spot"
  spot.setAttribute("aria-hidden", "true")
  const bubble = doc.createElement("div")
  bubble.id = "plan-coach-bubble"
  bubble.className = "plan-coach-bubble"
  bubble.setAttribute("role", "dialog")
  bubble.setAttribute("aria-modal", "false")
  bubble.setAttribute("aria-labelledby", "plan-coach-title")
  bubble.setAttribute("aria-describedby", "plan-coach-body")
  bubble.tabIndex = -1
  bubble.innerHTML = `
    <span class="plan-coach-arrow" aria-hidden="true"></span>
    <p class="plan-coach-count"></p>
    <p class="plan-coach-title" id="plan-coach-title"></p>
    <p class="plan-coach-body" id="plan-coach-body"></p>
    <div class="plan-coach-actions">
      <button type="button" class="plan-coach-skip">Pular</button>
      <button type="button" class="plan-coach-back">Anterior</button>
      <button type="button" class="plan-coach-next">Próximo</button>
    </div>`
  doc.body.append(spot, bubble)
  const arrow = bubble.querySelector(".plan-coach-arrow")

  const visible = (element) => {
    if (!element) return false
    const rect = element.getBoundingClientRect()
    return rect.width > 0 && rect.height > 0
  }
  const findTarget = (step) => {
    if (step.nav) {
      return [...doc.querySelectorAll('[data-testid="stSidebarNav"] a')]
        .find((link) => link.textContent.trim().includes(step.nav))
    }
    return step.selector ? doc.querySelector(step.selector) : null
  }
  const available = () => steps.filter((step) => visible(findTarget(step)))

  const place = (target) => {
    const rect = target.getBoundingClientRect()
    const pad = 6
    Object.assign(spot.style, {
      top: `${rect.top - pad}px`, left: `${rect.left - pad}px`,
      width: `${rect.width + pad * 2}px`, height: `${rect.height + pad * 2}px`,
    })
    const box = bubble.getBoundingClientRect()
    const gap = 16
    const vw = window.innerWidth
    const vh = window.innerHeight
    let top
    let left
    let side
    if (rect.right + gap + box.width <= vw - 16) {
      side = "right"; left = rect.right + gap; top = rect.top + rect.height / 2 - box.height / 2
    } else if (rect.bottom + gap + box.height <= vh - 16) {
      side = "below"; top = rect.bottom + gap; left = rect.left + rect.width / 2 - box.width / 2
    } else {
      side = "above"; top = rect.top - gap - box.height; left = rect.left + rect.width / 2 - box.width / 2
    }
    top = Math.max(16, Math.min(top, vh - box.height - 16))
    left = Math.max(16, Math.min(left, vw - box.width - 16))
    bubble.style.top = `${top}px`
    bubble.style.left = `${left}px`
    const arrowStyle = { top: "", left: "" }
    if (side === "right") {
      arrowStyle.left = "-7px"
      arrowStyle.top = `${Math.max(14, Math.min(rect.top + rect.height / 2 - top - 7, box.height - 28))}px`
    } else {
      arrowStyle.left = `${Math.max(14, Math.min(rect.left + rect.width / 2 - left - 7, box.width - 28))}px`
      arrowStyle.top = side === "below" ? "-7px" : `${box.height - 7}px`
    }
    Object.assign(arrow.style, arrowStyle)
  }

  coach.show = () => {
    const list = available()
    if (!list.length) { finish("finish"); return }
    coach.index = Math.min(coach.index, list.length - 1)
    const step = list[coach.index]
    const target = findTarget(step)
    bubble.querySelector(".plan-coach-count").textContent = `Dica ${coach.index + 1} de ${list.length}`
    bubble.querySelector(".plan-coach-title").textContent = step.title
    bubble.querySelector(".plan-coach-body").textContent = step.body
    bubble.querySelector(".plan-coach-back").disabled = coach.index === 0
    const last = coach.index === list.length - 1
    bubble.querySelector(".plan-coach-next").textContent = last ? "Entendi" : "Próximo"
    target.scrollIntoView({ block: "center", behavior: "instant" })
    requestAnimationFrame(() => { place(target); bubble.querySelector(".plan-coach-next").focus() })
  }
  const reposition = () => {
    const list = available()
    const step = list[coach.index]
    if (step) place(findTarget(step))
  }
  const onKey = (event) => { if (event.key === "Escape") finish("skip") }
  coach.teardown = () => {
    spot.remove(); bubble.remove()
    window.removeEventListener("resize", reposition)
    window.removeEventListener("scroll", reposition, true)
    doc.removeEventListener("keydown", onKey)
    if (window.__planCoach === coach) window.__planCoach = null
  }
  const finish = (reason) => {
    coach.teardown()
    coach.setTriggerValue("done", reason)
  }
  bubble.querySelector(".plan-coach-skip").onclick = () => finish("skip")
  bubble.querySelector(".plan-coach-back").onclick = () => { coach.index -= 1; coach.show() }
  bubble.querySelector(".plan-coach-next").onclick = () => {
    if (coach.index >= available().length - 1) finish("finish")
    else { coach.index += 1; coach.show() }
  }
  window.addEventListener("resize", reposition)
  window.addEventListener("scroll", reposition, true)
  doc.addEventListener("keydown", onKey)
  setTimeout(() => coach.show(), 300)
}
"""


def render_coach_marks(
    *, run: int, steps: list[dict[str, str]], on_done: Callable[[], None], key: str
) -> None:
    """Mostra os balões. Uma nova ``run`` reinicia o passeio do primeiro passo."""
    renderer = st.components.v2.component(
        "plan_coach_marks", html="<span hidden></span>", js=_JS
    )
    renderer(key=key, data={"run": run, "steps": steps, "css": _CSS}, on_done_change=on_done)
