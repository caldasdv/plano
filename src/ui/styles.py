"""Fundação visual do Plano: uma mesa de estudos calma e orientada à ação."""

from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --plan-bg: #f4f7fb;
            --plan-surface: #ffffff;
            --plan-input: #e8eef8;
            --plan-text: #262b40;
            --plan-muted: #5379ae;
            --plan-border: rgba(83, 121, 174, .35);
            --plan-accent: #0474c4;
            --plan-accent-dark: #06457f;
            --plan-attention: #0474c4;
            --plan-sidebar: #06457f;
            --plan-selection: #a8c4ec;
            --plan-shadow: 0 12px 32px rgba(6, 69, 127, .08);
        }
        .stApp { background: radial-gradient(circle at 88% -5%, rgba(168, 196, 236, .34), transparent 32rem), radial-gradient(circle at -10% 70%, rgba(83, 121, 174, .12), transparent 28rem), var(--plan-bg); color: var(--plan-text); }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { background: var(--plan-sidebar); border-right: 1px solid rgba(168, 196, 236, .55); width: 19rem !important; }
        [data-testid="stSidebar"] > div:first-child { width: 19rem !important; }
        [data-testid="stSidebarHeader"] { position: sticky; top: 0; z-index: 10; background: var(--plan-sidebar); }
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stExpandSidebarButton"] { background: #0474c4 !important; border: 1px solid #a8c4ec !important; border-radius: 10px; color: #ffffff !important; opacity: 1 !important; }
        [data-testid="stSidebarCollapseButton"] span,
        [data-testid="stExpandSidebarButton"] span { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="stExpandSidebarButton"] svg { fill: #ffffff !important; }
        [data-testid="stSidebarCollapseButton"] button:focus-visible,
        [data-testid="stExpandSidebarButton"]:focus-visible { outline: 3px solid #a8c4ec; outline-offset: 3px; }
        [data-testid="stHeaderLogo"] { background: #06457f; border-radius: 8px; padding: 3px; }
        [data-testid="stSidebar"] section { padding-top: 1.25rem; }
        [data-testid="stSidebarNav"] { border-bottom: 1px solid var(--plan-border); padding: 0 .45rem 1rem; }
        [data-testid="stSidebarNav"] ul { gap: .2rem; }
        [data-testid="stSidebarNav"] > ul > li > div:not(:has(a)) { color: #a8c4ec; font-size: .68rem; font-weight: 800; letter-spacing: .12em; margin: 1.1rem .7rem .35rem; text-transform: uppercase; }
        [data-testid="stSidebarNav"] li div a { border-radius: 10px; color: #ffffff; font-weight: 650; padding: .55rem .7rem; }
        [data-testid="stSidebarNav"] li div a:hover { background: rgba(168, 196, 236, .16); color: #ffffff; }
        [data-testid="stSidebarNav"] li div a[aria-current="page"] { background: #0474c4; box-shadow: none; color: #ffffff; }
        [data-testid="stSidebarNav"] li div a:focus-visible { outline: 3px solid var(--plan-attention); outline-offset: 2px; }
        .plan-sidebar-brand { align-items: center; display: flex; gap: .7rem; justify-content: flex-start; padding: .25rem .4rem 1rem; text-align: left; }
        .plan-sidebar-brand > div { min-width: 0; text-align: left; }
        .plan-sidebar-brand strong, .plan-sidebar-brand small { display: block; }
        .plan-sidebar-brand strong { color: #ffffff; font-size: 1.15rem; letter-spacing: -.04em; }
        .plan-sidebar-brand small { color: #a8c4ec; font-size: .72rem; margin-top: .1rem; }
        .plan-sidebar-mark { align-items: center; background: #0474c4; border-radius: 10px; color: #ffffff; display: inline-flex; flex: 0 0 auto; height: 2rem; justify-content: center; width: 2rem; }
        .plan-sidebar-mark svg { height: 1.45rem; width: 1.45rem; }
        .plan-sidebar-user { background: rgba(168, 196, 236, .16); border: 1px solid rgba(168, 196, 236, .55); border-radius: 12px; margin: .4rem 0 .65rem; padding: .7rem .75rem; text-align: left; }
        .plan-sidebar-user strong, .plan-sidebar-user span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .plan-sidebar-user strong { color: #ffffff; font-size: .82rem; }
        .plan-sidebar-user span { color: #ffffff; font-size: .7rem; margin-top: .2rem; }
        .plan-sidebar-section-label { color: #a8c4ec; font-size: .72rem; font-weight: 750; letter-spacing: .07em; margin: .25rem 0 .4rem; text-align: left; text-transform: uppercase; }
        .block-container, [data-testid="stMainBlockContainer"] { box-sizing: border-box; margin-left: auto; margin-right: auto; max-width: 1120px; padding-top: 3.75rem; padding-bottom: 5rem; width: 100%; }
        h1, h2, h3 { color: var(--plan-text); font-weight: 700; letter-spacing: -0.025em; overflow: visible; white-space: normal; overflow-wrap: break-word; }
        h1 { font-size: clamp(2rem, 4vw, 3.1rem); line-height: 1.15; margin-bottom: .55rem; }
        .plan-page-title { font-size: clamp(2rem, 4vw, 3.1rem); line-height: 1.15; margin: 0 0 .55rem; }
        h2 { font-size: 1.55rem; line-height: 1.25; margin-top: 1.8rem; }
        h3 { font-size: 1.1rem; line-height: 1.3; }
        .plan-eyebrow { align-items: center; color: var(--plan-accent); display: flex; font-size: .76rem; font-weight: 800; gap: .55rem; letter-spacing: .12em; line-height: 1.35; margin-bottom: .7rem; overflow: visible; white-space: normal; overflow-wrap: break-word; }
        .plan-eyebrow::before { background: var(--plan-accent); border-radius: 50%; box-shadow: 0 0 0 4px rgba(4, 116, 196, .14); content: ''; display: inline-block; height: .48rem; width: .48rem; }
        .plan-page-description { color: var(--plan-muted); font-size: 1.05rem; line-height: 1.55; max-width: 48rem; }
        .plan-header-motif { align-items: center; display: flex; gap: .35rem; height: .5rem; margin: 1.15rem 0 1.5rem; }
        .plan-header-motif span, .plan-header-motif i { border-radius: 999px; display: block; height: .28rem; }
        .plan-header-motif-long { background: var(--plan-accent); width: 3.8rem; }
        .plan-header-motif-short { background: #a8c4ec; width: 1.5rem; }
        .plan-header-motif i { background: #5379ae; height: .4rem; width: .4rem; }
        [data-testid="stCaptionContainer"] p { color: var(--plan-muted); }
        [data-testid="stVerticalBlockBorderWrapper"] { background: var(--plan-surface); border-color: var(--plan-border); border-radius: 18px; box-shadow: var(--plan-shadow); }
        [data-testid="stForm"] { background: var(--plan-surface); border: 1px solid var(--plan-border); border-radius: 20px; box-shadow: var(--plan-shadow); padding: 1rem 1.15rem 1.15rem; }
        [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div { background: var(--plan-input); border-color: var(--plan-border); border-radius: 10px; transition: border-color .15s ease, box-shadow .15s ease; }
        [data-testid="stTextInputRootElement"]:focus-within, [data-testid="stTextAreaRootElement"]:focus-within, [data-testid="stNumberInputContainer"]:focus-within, [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"] > div:focus-within { border-color: var(--plan-accent); box-shadow: 0 0 0 3px rgba(4, 116, 196, .18); }
        [data-testid="stWidgetLabel"] p { color: var(--plan-text); font-size: .82rem; font-weight: 650; }
        [data-testid="stExpander"] { background: var(--plan-surface); border: 1px solid var(--plan-border); border-radius: 16px; }
        [data-testid="stExpander"] summary:hover { background: var(--plan-input); }
        [data-testid="stAlert"] { border-radius: 14px; border-width: 1px; }
        [data-testid="stMarkdownContainer"] hr { border-color: var(--plan-border); margin: 2rem 0; }
        [data-testid="stDataFrame"] { border: 1px solid var(--plan-border); border-radius: 14px; overflow: hidden; }
        .stPlotlyChart { border-radius: 16px; overflow: hidden; }
        [data-baseweb="input"] input, [data-baseweb="textarea"] textarea { color: var(--plan-text); }
        [data-testid="stMetric"] { background: var(--plan-surface); border: 1px solid var(--plan-border); border-radius: 16px; box-shadow: var(--plan-shadow); padding: 1rem 1.1rem; }
        [data-testid="stMetricLabel"] p { color: var(--plan-muted); font-size: .78rem; font-weight: 650; letter-spacing: .04em; text-transform: uppercase; }
        [data-testid="stMetricValue"] { color: var(--plan-text); font-weight: 750; letter-spacing: -.04em; }
        .st-key-overview_weekly_goal [data-testid="stMetricValue"] { font-size: clamp(1.2rem, 2vw, 1.65rem); }
        .plan-session-meta { color: var(--plan-muted); font-size: .82rem; margin-bottom: .3rem; }
        .plan-session-content { display: grid; gap: .32rem; padding-bottom: .65rem; }
        .plan-session-subject { align-items: center; color: var(--plan-text); display: flex; font-size: .92rem; font-weight: 700; line-height: 1.25; }
        .plan-session-topic { color: var(--plan-text); font-size: 1.2rem; font-weight: 700; line-height: 1.25; }
        .plan-session-goal { color: var(--plan-muted); line-height: 1.35; margin-top: .05rem; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.plan-session-topic) { background: var(--plan-surface); padding: 1rem 1.2rem !important; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.plan-session-topic) > div { padding: .45rem .3rem .9rem !important; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.plan-session-topic) [data-testid="stButton"] { margin-top: .45rem; margin-bottom: .25rem; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.plan-session-topic) [data-testid="stButton"] button { padding-left: 1rem; padding-right: 1rem; }
        .plan-status-badge { border: 1px solid transparent; border-radius: 999px; display: inline-flex; font-size: .72rem; font-weight: 700; letter-spacing: .01em; line-height: 1; padding: .45rem .6rem; white-space: nowrap; }
        .plan-status-done { background: var(--plan-input); border-color: var(--plan-accent); color: var(--plan-accent-dark); }
        .plan-status-pending { background: var(--plan-surface); border-color: var(--plan-border); color: var(--plan-muted); }
        .plan-status-overdue { background: var(--plan-input); border-color: var(--plan-muted); color: var(--plan-text); }
        .plan-status-neutral { background: var(--plan-input); border-color: var(--plan-border); color: var(--plan-muted); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--plan-muted); }
        [data-testid="stSidebar"] h2 { color: var(--plan-accent-dark); letter-spacing: -.04em; line-height: 1.25; overflow: visible; }
        [data-testid="stSidebar"] [data-testid="stNumberInput"] [data-baseweb="input"] { background: rgba(255, 255, 255, .12); }
        .stButton button, .stFormSubmitButton button { border-radius: 11px; border-width: 1px; box-shadow: none; font-weight: 700; min-height: 2.7rem; transition: transform .15s ease, box-shadow .15s ease, background .15s ease; }
        .stButton button:hover { box-shadow: 0 6px 16px rgba(6, 69, 127, .16); transform: translateY(-1px); }
        .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] { background: var(--plan-accent); border-color: var(--plan-accent); color: #ffffff; }
        .stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primary"]:hover { background: var(--plan-accent-dark); border-color: var(--plan-accent-dark); }
        .stButton button:focus-visible, .stFormSubmitButton button:focus-visible,
        input:focus-visible, textarea:focus-visible, [role="combobox"]:focus-visible { outline: 3px solid var(--plan-attention); outline-offset: 2px; }
        button, input, textarea, select { min-height: 2.5rem; }
        .subject-dot { display: inline-block; width: .7rem; height: .7rem; border-radius: 50%; margin-right: .35rem; vertical-align: .05rem; }
        .plan-subject-swatch { width: 1rem; height: 1rem; border-radius: 50%; margin-bottom: .7rem; }
        .plan-timetable-hint { color: var(--plan-muted); display: none; font-size: .8rem; margin: -.25rem 0 .5rem; }
        .plan-timetable-scroll { max-width: 100%; overflow-x: auto; overscroll-behavior-inline: contain; padding: .15rem .15rem .75rem; scrollbar-color: var(--plan-accent) var(--plan-input); scrollbar-width: thin; }
        .plan-timetable { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: .8rem; min-width: 0; }
        .plan-timetable-day { background: var(--plan-input); border: 1px solid var(--plan-border); border-radius: 14px; min-height: 16rem; padding: 1rem; }
        .plan-timetable-day h3 { border-bottom: 1px solid var(--plan-border); color: var(--plan-accent-dark); font-size: .95rem; letter-spacing: .06em; margin: 0 0 .9rem; padding-bottom: .7rem; text-transform: uppercase; }
        .plan-meeting { background: var(--plan-surface); border-left: 5px solid var(--meeting-color); border-radius: 9px; box-shadow: 0 2px 8px rgba(6, 69, 127, .06); display: flex; flex-direction: column; gap: .3rem; margin-bottom: .7rem; padding: .8rem; }
        .plan-meeting strong { color: var(--plan-text); font-size: .95rem; }
        .plan-meeting span { color: var(--plan-text); font-size: .9rem; line-height: 1.3; }
        .plan-meeting-location { color: var(--plan-muted) !important; font-size: .8rem !important; }
        .plan-timetable-empty { color: var(--plan-muted); font-size: .85rem; margin: 3.8rem 0 0; text-align: center; }
        .plan-progress-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .8rem; }
        .plan-progress-card { background: var(--plan-surface); border: 1px solid var(--plan-border); border-radius: 16px; box-shadow: var(--plan-shadow); padding: 1rem; }
        .plan-progress-card-heading { align-items: baseline; display: flex; justify-content: space-between; gap: 1rem; }
        .plan-progress-card-heading strong { color: var(--plan-text); font-size: 1rem; }
        .plan-progress-card-heading span { color: var(--plan-accent-dark); font-size: .95rem; font-weight: 750; }
        .plan-progress-track { background: var(--plan-input); border-radius: 999px; height: .6rem; margin: .8rem 0 .55rem; overflow: hidden; }
        .plan-progress-track span { background: var(--plan-accent); border-radius: inherit; display: block; height: 100%; }
        .plan-progress-card-meta, .plan-progress-card-status { color: var(--plan-muted); font-size: .82rem; line-height: 1.4; }
        .plan-progress-card-status { margin-top: .2rem; }
        .plan-overview-hero { background: #06457f; border: 1px solid #06457f; border-radius: 14px; box-shadow: 0 18px 34px rgba(6, 69, 127, .18); color: #ffffff; margin-bottom: .7rem; min-height: 14rem; overflow: hidden; padding: 1.6rem 1.8rem; position: relative; }
        .plan-overview-divider { border-top: 1px solid var(--plan-border); margin: 1.25rem 0 .75rem; }
        .plan-overview-day-title { color: var(--plan-text); font-size: 1.55rem; letter-spacing: -.045em; line-height: 1.2; margin: 1rem 0 .75rem; }
        .plan-overview-hero-copy { position: relative; z-index: 2; }
        .plan-overview-hero-kicker { color: #a8c4ec; display: block; font-size: .68rem; font-weight: 800; letter-spacing: .15em; margin-bottom: .85rem; }
        .plan-overview-hero h2 { color: #ffffff; font-size: clamp(2rem, 4vw, 3rem); letter-spacing: -.065em; line-height: .98; margin: 0; }
        .plan-overview-hero h2 em { color: #a8c4ec; font-style: normal; }
        .plan-overview-hero p { color: #a8c4ec; font-size: .92rem; line-height: 1.45; margin: 1rem 0 0; max-width: 19rem; }
        .plan-overview-hero-stat { background: rgba(245, 251, 246, .12); border: 1px solid rgba(245, 251, 246, .2); border-radius: 16px; bottom: 1.8rem; padding: .85rem 1rem; position: absolute; right: 2rem; width: 10.5rem; z-index: 2; }
        .plan-overview-hero-stat > span, .plan-overview-hero-stat > small { color: #a8c4ec; display: block; font-size: .66rem; }
        .plan-overview-hero-stat strong { color: #fff; display: block; font-size: 2rem; letter-spacing: -.06em; line-height: 1.15; margin: .25rem 0 .55rem; }
        .plan-overview-hero-stat strong small { color: #a8c4ec; display: inline; font-size: .75rem; letter-spacing: 0; }
        .plan-overview-hero-track { background: rgba(255,255,255,.18); border-radius: 99px; height: .35rem; margin-bottom: .45rem; overflow: hidden; }
        .plan-overview-hero-track i { background: #0474c4; border-radius: inherit; display: block; height: 100%; }
        .plan-overview-orbit { border: 1px solid rgba(168, 196, 236, .3); border-radius: 50%; position: absolute; }
        .plan-overview-orbit-a { height: 27rem; right: -5rem; top: -9rem; transform: rotate(28deg); width: 13rem; }
        .plan-overview-orbit-b { bottom: -10rem; height: 21rem; right: 7rem; transform: rotate(-32deg); width: 35rem; }
        .plan-overview-spark { background: #0474c4; border-radius: 50%; box-shadow: 0 0 0 .35rem rgba(4,116,196,.16); height: .55rem; position: absolute; width: .55rem; }
        .spark-one { right: 35%; top: 22%; } .spark-two { bottom: 18%; right: 36%; height: .3rem; width: .3rem; } .spark-three { right: 13%; top: 17%; height: .35rem; width: .35rem; }
        .plan-rhythm { background: var(--plan-surface); border: 1px solid var(--plan-border); border-radius: 18px; box-shadow: var(--plan-shadow); margin: .85rem 0 1.25rem; padding: 1rem 1.1rem .9rem; }
        .plan-rhythm-heading { align-items: baseline; display: flex; justify-content: space-between; margin-bottom: .8rem; }
        .plan-rhythm-heading strong { color: var(--plan-text); font-size: .95rem; letter-spacing: -.02em; }
        .plan-rhythm-heading span { color: var(--plan-muted); font-size: .67rem; }
        .plan-rhythm-grid { display: grid; gap: .55rem; grid-template-columns: repeat(7, minmax(0, 1fr)); }
        .plan-rhythm-day { align-items: center; background: var(--plan-input); border: 1px solid transparent; border-radius: 12px; display: flex; flex-direction: column; min-height: 5.7rem; padding: .55rem .35rem .45rem; }
        .plan-rhythm-day > span { color: var(--plan-muted); font-size: .62rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
        .plan-rhythm-day > strong { color: var(--plan-text); font-size: 1rem; margin: .2rem 0 .25rem; }
        .plan-rhythm-day > i { background: #a8c4ec; border-radius: 99px; display: flex; height: 1.45rem; justify-content: center; overflow: hidden; position: relative; width: .35rem; }
        .plan-rhythm-day > i b { background: var(--plan-accent); border-radius: inherit; bottom: 0; display: block; position: absolute; width: 100%; }
        .plan-rhythm-day > small { color: var(--plan-muted); font-size: .62rem; margin-top: .3rem; }
        .plan-rhythm-done { background: var(--plan-selection); border-color: var(--plan-accent); } .plan-rhythm-done > strong { color: var(--plan-accent-dark); }
        .plan-rhythm-planned { border-color: #a8c4ec; } .plan-rhythm-planned > i b { background: var(--plan-attention); }
        .plan-rhythm-empty { opacity: .62; }
        .plan-quick-actions { align-items: center; display: flex; margin: 1.2rem 0 .55rem; }
        .plan-quick-actions span { color: var(--plan-muted); font-size: .78rem; font-weight: 700; }
        .plan-topic-path { display: grid; gap: .65rem; padding: .25rem 0 .85rem; }
        .plan-topic-path-item { align-items: center; display: flex !important; gap: .65rem; min-height: 1.8rem; }
        .plan-topic-path-item > i { background: var(--plan-border); border-radius: 50%; display: block; flex: 0 0 auto; height: .55rem; width: .55rem; }
        .plan-topic-path-item.is-done > i { background: var(--plan-accent); box-shadow: 0 0 0 4px rgba(4, 116, 196, .14); }
        .plan-topic-path-item strong { color: var(--plan-text); font-size: .88rem; }
        .plan-topic-path-item small { color: var(--plan-muted); margin-left: auto; white-space: nowrap; }
        .plan-login-shell { align-items: center; display: grid; gap: clamp(2rem, 7vw, 7rem); grid-template-columns: minmax(0, 1.05fr) minmax(20rem, .95fr); margin: clamp(1rem, 7vh, 5rem) auto 2rem; max-width: 1000px; min-height: 32rem; }
        .plan-login-copy { padding: .5rem 0; }
        .plan-login-kicker { align-items: center; color: var(--plan-accent); display: flex; font-size: .72rem; font-weight: 800; gap: .55rem; letter-spacing: .14em; margin-bottom: 1.7rem; }
        .plan-login-dot { background: var(--plan-accent); border-radius: 50%; box-shadow: 0 0 0 5px rgba(4, 116, 196, .14); display: inline-block; height: .55rem; width: .55rem; }
        .plan-login-copy h1 { font-size: clamp(3.1rem, 6vw, 5.35rem); letter-spacing: -.075em; line-height: .98; margin: 0; }
        .plan-login-copy h1 em { color: var(--plan-accent); font-style: normal; }
        .plan-login-lead { color: var(--plan-muted); font-size: 1.08rem; line-height: 1.55; margin: 1.5rem 0 2.2rem; max-width: 30rem; }
        .plan-login-signals { display: grid; gap: .85rem; }
        .plan-login-signals > div { align-items: center; display: flex; gap: .75rem; }
        .plan-login-signal-icon { align-items: center; background: #e8eef8; border: 1px solid #a8c4ec; border-radius: 10px; color: var(--plan-accent-dark); display: inline-flex; font-size: 1rem; font-weight: 800; height: 2rem; justify-content: center; width: 2rem; }
        .plan-login-signals strong, .plan-login-signals small { display: block; }
        .plan-login-signals strong { color: var(--plan-text); font-size: .83rem; }
        .plan-login-signals small { color: var(--plan-muted); font-size: .75rem; margin-top: .12rem; }
        .plan-login-visual { align-items: center; background: linear-gradient(145deg, #e8eef8 0%, #a8c4ec 100%); border: 1px solid #a8c4ec; border-radius: 2.2rem; display: flex; justify-content: center; min-height: 29rem; overflow: hidden; position: relative; }
        .plan-login-visual::before { background: rgba(255,255,255,.3); border-radius: 50%; content: ''; height: 21rem; position: absolute; right: -5rem; top: -5rem; width: 21rem; }
        .plan-login-orbit { border: 1px solid rgba(4, 116, 196, .22); border-radius: 50%; position: absolute; }
        .plan-login-orbit-one { height: 24rem; transform: rotate(30deg); width: 11rem; }
        .plan-login-orbit-two { height: 11rem; transform: rotate(-38deg); width: 24rem; }
        .plan-login-week-card { background: rgba(252, 253, 249, .94); border: 1px solid rgba(255,255,255,.85); border-radius: 1.2rem; box-shadow: 0 22px 45px rgba(6, 69, 127, .17); padding: 1.35rem; position: relative; transform: rotate(-5deg); width: min(78%, 17rem); z-index: 1; }
        .plan-login-card-top { color: var(--plan-muted); display: flex; font-size: .67rem; justify-content: space-between; letter-spacing: .08em; text-transform: uppercase; }
        .plan-login-card-top b { color: var(--plan-accent); font-size: .8rem; }
        .plan-login-card-title { color: var(--plan-text); font-size: 1.35rem; font-weight: 750; letter-spacing: -.05em; line-height: 1.08; margin: 1.4rem 0 1.7rem; }
        .plan-login-bars { align-items: end; display: flex; gap: .42rem; height: 5.2rem; }
        .plan-login-bars i { background: #5379ae; border-radius: 99px 99px .2rem .2rem; display: block; flex: 1; height: 42%; }
        .plan-login-bars i:nth-child(2) { height: 68%; } .plan-login-bars i:nth-child(3) { background: var(--plan-accent); height: 88%; } .plan-login-bars i:nth-child(4) { height: 56%; } .plan-login-bars i:nth-child(5) { height: 75%; } .plan-login-bars i:nth-child(6) { height: 48%; } .plan-login-bars i:nth-child(7) { height: 30%; }
        .plan-login-card-foot { color: #5379ae; display: flex; font-size: .57rem; justify-content: space-between; margin-top: .55rem; text-transform: uppercase; }
        .plan-login-float { background: var(--plan-surface); border: 1px solid rgba(255,255,255,.9); border-radius: .7rem; box-shadow: 0 10px 24px rgba(6, 69, 127, .13); color: var(--plan-accent); font-size: .95rem; font-weight: 800; padding: .65rem .75rem; position: absolute; z-index: 2; }
        .plan-login-float span { color: var(--plan-muted); font-size: .63rem; font-weight: 650; margin-left: .25rem; }
        .plan-login-float-check { left: 7%; top: 24%; transform: rotate(-7deg); } .plan-login-float-focus { bottom: 17%; right: 7%; color: var(--plan-muted); font-size: .6rem; line-height: 1.1; transform: rotate(7deg); } .plan-login-float-focus strong { color: var(--plan-accent-dark); font-size: .95rem; }
        .plan-login-action-label { color: var(--plan-muted); font-size: .78rem; margin: .8rem auto .45rem; max-width: 1000px; text-align: center; }
        @media (max-width: 640px) {
            [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { width: 18rem !important; }
            .block-container { padding-top: 2.25rem; padding-left: 1rem; padding-right: 1rem; }
            h1 { font-size: 2rem; }
            [data-testid="stHorizontalBlock"] { gap: .5rem; }
            [data-testid="stMetric"] { padding: .8rem; }
            [data-testid="stMetricValue"] { font-size: 1.5rem; }
            [data-testid="stForm"] { border-radius: 16px; padding: .8rem; }
            .plan-overview-hero { min-height: 23rem; padding: 1.35rem; }
            .plan-overview-hero-stat { bottom: 1.35rem; left: 1.35rem; right: auto; }
            .plan-rhythm { padding: .85rem .75rem; }
            .plan-rhythm-grid { gap: .3rem; }
            .plan-rhythm-day { min-height: 5.3rem; }
            .plan-login-shell { gap: 1.5rem; grid-template-columns: 1fr; margin-top: 1rem; min-height: 0; }
            .plan-login-copy { padding: 0; }
            .plan-login-kicker { margin-bottom: 1.2rem; }
            .plan-login-copy h1 { font-size: clamp(3rem, 15vw, 4.4rem); }
            .plan-login-lead { font-size: .98rem; margin: 1.2rem 0 1.6rem; }
            .plan-login-visual { border-radius: 1.5rem; min-height: 20rem; }
            .plan-login-week-card { width: 68%; }
            .plan-login-float-check { left: 3%; top: 17%; } .plan-login-float-focus { bottom: 10%; right: 3%; }
        }
        @media (max-width: 768px) {
            .plan-timetable-hint { display: block; }
            .plan-timetable-scroll { -webkit-overflow-scrolling: touch; }
            .plan-timetable { grid-template-columns: repeat(7, minmax(155px, 1fr)); min-width: 1140px; }
        }
        @media (max-width: 640px) {
            .plan-progress-grid { grid-template-columns: 1fr; }
        }
        .plan-dark-mode-marker { display: none; }
        body:has(.plan-dark-mode-marker), .stApp:has(.plan-dark-mode-marker) {
            --plan-bg: #262b40;
            --plan-surface: #06457f;
            --plan-input: #1a243e;
            --plan-text: #ffffff;
            --plan-muted: #a8c4ec;
            --plan-border: #5379ae;
            --plan-accent: #0474c4;
            --plan-accent-dark: #a8c4ec;
            --plan-attention: #a8c4ec;
            --plan-sidebar: #06457f;
            --plan-selection: #0474c4;
            --plan-shadow: 0 12px 28px rgba(0, 0, 0, .16);
            color-scheme: dark;
            background: var(--plan-bg);
            color: var(--plan-text);
        }
        .stApp:has(.plan-dark-mode-marker),
        body:has(.plan-dark-mode-marker) [data-testid="stAppViewContainer"] { background: var(--plan-bg); color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stHeader"] { color: var(--plan-text); }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] a span,
        [data-testid="stSidebar"] [data-testid="stNavSectionHeader"],
        [data-testid="stSidebar"] [data-testid="stNavSectionHeader"] p,
        [data-testid="stSidebar"] [data-testid="stIconMaterial"] { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #a8c4ec; }
        [data-testid="stSidebar"] [data-testid="stButton"] button p,
        [data-testid="stSidebar"] .plan-sidebar-user strong,
        [data-testid="stSidebar"] .plan-sidebar-user span { color: #ffffff !important; }
        .stButton button:not([kind="primary"]), .stFormSubmitButton button:not([kind="primary"]) { background: var(--plan-surface); border-color: var(--plan-border); color: var(--plan-text); }
        .stButton button:not([kind="primary"]):hover, .stFormSubmitButton button:not([kind="primary"]):hover { background: var(--plan-selection); border-color: var(--plan-accent); color: var(--plan-text); }
        .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] { background: #0474c4; border-color: #0474c4; color: #ffffff; }
        .stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primary"]:hover { background: #06457f; border-color: #06457f; color: #ffffff; }
        [data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]) { background: #06457f; border-color: #a8c4ec; color: #ffffff; -webkit-text-fill-color: #ffffff; }
        [data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]):is(:hover, :focus-visible, :active) { background: #0474c4; border-color: #a8c4ec; color: #ffffff; }
        [data-testid="stDateInputField"], [data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stNumberInputContainer"], [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div { background: var(--plan-input); border-color: var(--plan-border); color: var(--plan-text); }
        [data-testid="stSelectbox"] [role="group"] { background: var(--plan-input); border-color: var(--plan-border); color: var(--plan-text); }
        [data-testid="stSelectbox"] [role="group"]:focus-within { border-color: var(--plan-accent); }
        [data-testid="stSelectbox"] [role="group"] button { color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) h1,
        body:has(.plan-dark-mode-marker) h2,
        body:has(.plan-dark-mode-marker) h3,
        body:has(.plan-dark-mode-marker) [data-testid="stMarkdownContainer"] p,
        body:has(.plan-dark-mode-marker) [data-testid="stWidgetLabel"] p,
        body:has(.plan-dark-mode-marker) [data-testid="stExpander"] summary { color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stCaptionContainer"] p,
        body:has(.plan-dark-mode-marker) [data-testid="stMetricLabel"] p { color: var(--plan-muted); }
        body:has(.plan-dark-mode-marker) input,
        body:has(.plan-dark-mode-marker) textarea,
        body:has(.plan-dark-mode-marker) [role="spinbutton"],
        body:has(.plan-dark-mode-marker) [data-baseweb="select"] span,
        body:has(.plan-dark-mode-marker) [data-baseweb="select"] input { color: var(--plan-text) !important; -webkit-text-fill-color: var(--plan-text); caret-color: var(--plan-accent); }
        body:has(.plan-dark-mode-marker) input::placeholder,
        body:has(.plan-dark-mode-marker) textarea::placeholder { color: var(--plan-muted); -webkit-text-fill-color: var(--plan-muted); opacity: 1; }
        body:has(.plan-dark-mode-marker) [data-testid="stNumberInput"] button,
        body:has(.plan-dark-mode-marker) [data-testid="stTimeInput"] button { background: var(--plan-input); color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stIconMaterial"] { color: inherit; }
        body:has(.plan-dark-mode-marker) [data-testid="stAlert"] > div { background: var(--plan-input); border: 1px solid var(--plan-border); color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stMetricValue"] { color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stMarkdownContainer"] hr { border-color: var(--plan-border); }
        [role="listbox"], [data-baseweb="popover"] > div { background: var(--plan-surface); border-color: var(--plan-border); color: var(--plan-text); }
        [role="option"] { color: var(--plan-text); }
        [role="option"][aria-selected="true"], [role="option"]:hover { background: var(--plan-selection) !important; color: var(--plan-text) !important; }
        body:has(.plan-dark-mode-marker) [role="dialog"] { background: var(--plan-surface); border-color: var(--plan-border); color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [role="dialog"] button { color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stSlider"] [role="slider"] { background: var(--plan-accent); }
        body:has(.plan-dark-mode-marker) .plan-overview-hero { background: #06457f; border-color: var(--plan-border); box-shadow: var(--plan-shadow); }
        body:has(.plan-dark-mode-marker) .plan-overview-hero p { color: #a8c4ec; }
        body:has(.plan-dark-mode-marker) .plan-overview-hero-stat { background: #06457f; border-color: var(--plan-border); }
        body:has(.plan-dark-mode-marker) .plan-rhythm-done > i b { background: #a8c4ec; }
        body:has(.plan-dark-mode-marker) [data-testid="stTable"] table { background: var(--plan-surface); border-color: var(--plan-border); color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stTable"] :is(th, td) { background: var(--plan-surface); border-color: var(--plan-border); color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stTable"] th { background: var(--plan-input); color: var(--plan-muted); }
        body:has(.plan-dark-mode-marker) [data-testid="stProgressBarTrack"] { background: var(--plan-input); }
        body:has(.plan-dark-mode-marker) [data-testid="stDateInputCalendar"] { background: var(--plan-surface); border: 1px solid var(--plan-border); color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stDateInputCalendar"] :is(th, button, button *) { color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stTimeInputTimeDisplay"] { background: var(--plan-input); color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) [data-testid="stExpander"] summary { background: transparent; }
        body:has(.plan-dark-mode-marker) [data-testid="stExpander"] summary:hover { background: var(--plan-input); }
        body:has(.plan-dark-mode-marker) [data-testid="stElementToolbarButtonContainer"] { background: var(--plan-surface); color: var(--plan-text); }
        body:has(.plan-dark-mode-marker) .plan-login-visual { background: #1a243e; border-color: var(--plan-border); }
        body:has(.plan-dark-mode-marker) .plan-login-week-card,
        body:has(.plan-dark-mode-marker) .plan-login-float { background: var(--plan-surface); border-color: var(--plan-border); }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
