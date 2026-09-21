"""Fundação visual do Plano: uma mesa de estudos calma e orientada à ação."""

from __future__ import annotations

import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --plan-bg: #e7d6ba;
            --plan-surface: #ffffff;
            --plan-input: #f4ebdd;
            --plan-text: #1a243e;
            --plan-muted: #8a8f9a;
            --plan-border: rgba(26, 36, 62, .22);
            --plan-accent: #b49345;
            --plan-accent-dark: #0e4b3a;
            --plan-attention: #b49345;
            --plan-shadow: 0 10px 26px rgba(26, 36, 62, .12);
        }
        .stApp { background: var(--plan-bg); color: var(--plan-text); }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { background: #0e4b3a; border-right: 1px solid rgba(180, 147, 69, .6); width: 19rem !important; }
        [data-testid="stSidebar"] > div:first-child { width: 19rem !important; }
        [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapseButton"] button { background: var(--plan-accent) !important; border-radius: 12px; color: #eeeeff !important; }
        [data-testid="stSidebarCollapseButton"] svg, [data-testid="stSidebarCollapseButton"] span { color: #eeeeff !important; fill: currentColor; }
        [data-testid="stSidebar"] section { padding-top: 1.25rem; }
        [data-testid="stSidebarNav"] { border-bottom: 1px solid var(--plan-border); padding: 0 .45rem 1rem; }
        [data-testid="stSidebarNav"] ul { gap: .2rem; }
        [data-testid="stSidebarNav"] > ul > li > div:not(:has(a)) { color: #b49345; font-size: .68rem; font-weight: 800; letter-spacing: .12em; margin: 1.1rem .7rem .35rem; text-transform: uppercase; }
        [data-testid="stSidebarNav"] li div a { border-radius: 10px; color: #ffffff; font-weight: 650; padding: .55rem .7rem; }
        [data-testid="stSidebarNav"] li div a:hover { background: rgba(90, 188, 185, .14); color: #ffffff; }
        [data-testid="stSidebarNav"] li div a[aria-current="page"] { background: rgba(165, 153, 181, .36); box-shadow: none; color: #ffffff; }
        [data-testid="stSidebarNav"] svg,
        [data-testid="stSidebarNav"] [data-testid="stIconMaterial"],
        [data-testid="stSidebarNav"] .material-symbols-rounded,
        [data-testid="stSidebarNav"] .material-symbols-outlined { color: #ffffff !important; fill: currentColor; -webkit-text-fill-color: #ffffff; }
        [data-testid="stSidebarNav"] li div a[aria-current="page"] svg,
        [data-testid="stSidebarNav"] li div a[aria-current="page"] [data-testid="stIconMaterial"],
        [data-testid="stSidebarNav"] li div a[aria-current="page"] .material-symbols-rounded,
        [data-testid="stSidebarNav"] li div a[aria-current="page"] .material-symbols-outlined { color: #b49345 !important; fill: currentColor; -webkit-text-fill-color: #b49345; }
        [data-testid="stSidebarNav"] li div a:focus-visible { outline: 3px solid var(--plan-attention); outline-offset: 2px; }
        .plan-sidebar-brand { align-items: center; display: flex; gap: .7rem; justify-content: flex-start; padding: .25rem .4rem 1rem; text-align: left; }
        .plan-sidebar-brand > div { min-width: 0; text-align: left; }
        .plan-sidebar-brand strong, .plan-sidebar-brand small { display: block; }
        .plan-sidebar-brand strong { color: #eeeeff; font-size: 1.15rem; letter-spacing: -.04em; }
        .plan-sidebar-brand small { color: rgba(238, 238, 255, .72); font-size: .72rem; margin-top: .1rem; }
        .plan-sidebar-mark { align-items: center; background: #b49345; border-radius: 10px; color: #0e4b3a; display: inline-flex; flex: 0 0 auto; height: 2rem; justify-content: center; width: 2rem; }
        .plan-sidebar-mark svg { height: 1.45rem; width: 1.45rem; }
        .plan-sidebar-user { background: rgba(165, 153, 181, .2); border: 1px solid rgba(90, 188, 185, .5); border-radius: 12px; margin: .4rem 0 .65rem; padding: .7rem .75rem; text-align: left; }
        .plan-sidebar-user strong, .plan-sidebar-user span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .plan-sidebar-user strong { color: #eeeeff; font-size: .82rem; }
        .plan-sidebar-user span { color: #ffffff; font-size: .7rem; margin-top: .2rem; }
        .plan-sidebar-section-label { color: #b49345; font-size: .72rem; font-weight: 750; letter-spacing: .07em; margin: .25rem 0 .4rem; text-align: left; text-transform: uppercase; }
        .block-container, [data-testid="stMainBlockContainer"] { box-sizing: border-box; margin-left: auto; margin-right: auto; max-width: 1120px; padding-top: 3.75rem; padding-bottom: 5rem; width: 100%; }
        h1, h2, h3 { color: var(--plan-text); font-weight: 700; letter-spacing: -0.025em; overflow: visible; white-space: normal; overflow-wrap: break-word; }
        h1 { font-size: clamp(2rem, 4vw, 3.1rem); line-height: 1.15; margin-bottom: .55rem; }
        .plan-page-title { font-size: clamp(2rem, 4vw, 3.1rem); line-height: 1.15; margin: 0 0 .55rem; }
        h2 { font-size: 1.55rem; line-height: 1.25; margin-top: 1.8rem; }
        h3 { font-size: 1.1rem; line-height: 1.3; }
        .plan-eyebrow { align-items: center; color: var(--plan-accent); display: flex; font-size: clamp(1.25rem, 2.4vw, 1.7rem); font-weight: 800; gap: .65rem; letter-spacing: .05em; line-height: 1.2; margin-bottom: .85rem; overflow: visible; white-space: normal; overflow-wrap: break-word; }
        .plan-eyebrow::before { background: #b49345; border-radius: 50%; box-shadow: 0 0 0 4px rgba(180, 147, 69, .2); content: ''; display: inline-block; height: .48rem; width: .48rem; }
        .plan-page-description { color: #2c444c; font-size: 1.05rem; line-height: 1.55; max-width: 48rem; }
        .plan-header-motif { align-items: center; display: flex; gap: .35rem; height: .5rem; margin: 1.15rem 0 1.5rem; }
        .plan-header-motif span, .plan-header-motif i { border-radius: 999px; display: block; height: .28rem; }
        .plan-header-motif-long { background: var(--plan-accent); width: 3.8rem; }
        .plan-header-motif-short { background: #5379ae; width: 1.5rem; }
        .plan-header-motif i { background: #b49345; height: .4rem; width: .4rem; }
        [data-testid="stCaptionContainer"] p { color: var(--plan-muted); }
        [data-testid="stVerticalBlockBorderWrapper"] { background: var(--plan-surface); border-color: var(--plan-border); border-radius: 10px; box-shadow: none; }
        [data-testid="stForm"] { background: var(--plan-surface); border: 1px solid var(--plan-border); border-radius: 10px; box-shadow: none; padding: 1rem 1.15rem 1.15rem; }
        [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div { background: var(--plan-input); border-color: var(--plan-border); border-radius: 10px; transition: border-color .15s ease, box-shadow .15s ease; }
        [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"] > div:focus-within { border-color: #b49345; box-shadow: 0 0 0 3px rgba(180, 147, 69, .24); }
        [data-baseweb="select"] > div { color: #1a243e; }
        [data-baseweb="select"] input, [data-baseweb="select"] span { color: #1a243e !important; }
        [data-baseweb="menu"] { background: var(--plan-surface); border: 1px solid #b49345; box-shadow: 0 12px 28px rgba(26, 36, 62, .18); }
        [data-baseweb="menu"] li[role="option"] { color: #1a243e; }
        [data-baseweb="menu"] li[role="option"]:hover,
        [data-baseweb="menu"] li[aria-selected="true"] { background: #a8c4ec; color: #262b40; }
        [data-baseweb="calendar"] { background: var(--plan-surface); border: 1px solid #b49345; box-shadow: 0 12px 28px rgba(26, 36, 62, .18); }
        [data-baseweb="calendar"] button { color: #1a243e; }
        [data-baseweb="calendar"] button:hover { background: rgba(165, 153, 181, .26); }
        [data-baseweb="calendar"] [aria-selected="true"] { background: #b49345 !important; color: #1a243e !important; }
        [data-testid="stWidgetLabel"] p { color: var(--plan-text); font-size: .82rem; font-weight: 650; }
        [data-testid="stExpander"] { background: var(--plan-surface); border: 1px solid var(--plan-border); border-radius: 10px; }
        [data-testid="stExpander"] summary:hover { background: rgba(90, 188, 185, .1); }
        [data-testid="stAlert"] { border-radius: 14px; border-width: 1px; }
        [data-testid="stMarkdownContainer"] hr { border-color: var(--plan-border); margin: 2rem 0; }
        [data-testid="stDataFrame"] { background: var(--plan-surface); border: 1px solid #b49345; border-radius: 14px; overflow: hidden; }
        [data-testid="stDataFrame"] [role="columnheader"] { background: #0e4b3a !important; color: #ffffff !important; }
        [data-testid="stDataFrame"] [role="gridcell"] { color: #1a243e !important; }
        [data-testid="stSlider"] [data-baseweb="slider"] { --slider-primary: #b49345; }
        [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] { background: #b49345 !important; border-color: #b49345 !important; box-shadow: 0 0 0 2px #e7d6ba !important; }
        [data-testid="stSlider"] [data-baseweb="slider"] > div > div { background: #e7d6ba !important; }
        [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div { background: #b49345 !important; }
        [data-testid="stProgress"] > div > div > div { background: #b49345 !important; }
        .stPlotlyChart { border-radius: 16px; overflow: hidden; }
        [data-baseweb="input"] input, [data-baseweb="textarea"] textarea { color: var(--plan-text); }
        [data-testid="stMetric"] { background: var(--plan-surface); border: 1px solid var(--plan-border); border-radius: 10px; box-shadow: none; padding: 1rem 1.1rem; }
        [data-testid="stMetricLabel"] p { color: var(--plan-muted); font-size: .78rem; font-weight: 650; letter-spacing: .04em; text-transform: uppercase; }
        [data-testid="stMetricValue"] { color: var(--plan-text); font-weight: 750; letter-spacing: -.04em; }
        .plan-session-meta { color: var(--plan-muted); font-size: .82rem; margin-bottom: .3rem; }
        .plan-session-content { display: grid; gap: .32rem; padding-bottom: .65rem; }
        .plan-session-subject { align-items: center; color: var(--plan-text); display: flex; font-size: .92rem; font-weight: 700; line-height: 1.25; }
        .plan-session-topic { color: var(--plan-text); font-size: 1.2rem; font-weight: 700; line-height: 1.25; }
        .plan-session-goal { color: var(--plan-muted); line-height: 1.35; margin-top: .05rem; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.plan-session-topic) { background: var(--plan-surface); border-left: 4px solid #b49345; padding: 1rem 1.2rem !important; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.plan-session-topic) > div { padding: .45rem .3rem .9rem !important; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.plan-session-topic) [data-testid="stButton"] { margin-top: .45rem; margin-bottom: .25rem; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.plan-session-topic) [data-testid="stButton"] button { padding-left: 1rem; padding-right: 1rem; }
        .plan-status-badge { border: 1px solid transparent; border-radius: 999px; display: inline-flex; font-size: .72rem; font-weight: 700; letter-spacing: .01em; line-height: 1; padding: .45rem .6rem; white-space: nowrap; }
        .plan-status-done { background: #e7d6ba; border-color: #b49345; color: #0e4b3a; }
        .plan-status-pending { background: #f4ebdd; border-color: #8a8f9a; color: #2c444c; }
        .plan-status-overdue { background: rgba(26, 36, 62, .1); border-color: #1a243e; color: #1a243e; }
        .plan-status-neutral { background: var(--plan-input); border-color: var(--plan-border); color: var(--plan-muted); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #ffffff; }
        [data-testid="stSidebar"] h2 { color: #ffffff; letter-spacing: -.04em; line-height: 1.25; overflow: visible; }
        [data-testid="stSidebar"] [data-testid="stButton"] button { background: #0e4b3a !important; border-color: #ffffff !important; color: #ffffff !important; }
        [data-testid="stSidebar"] [data-testid="stButton"] button:hover { background: #b49345 !important; border-color: #b49345 !important; color: #1a243e !important; }
        [data-testid="stSidebar"] [data-testid="stNumberInput"] [data-baseweb="input"] { background: rgba(252, 253, 249, .7); }
        .stButton button, .stFormSubmitButton button { border-radius: 11px; border-width: 1px; box-shadow: none; font-weight: 700; min-height: 2.7rem; transition: transform .15s ease, box-shadow .15s ease, background .15s ease; }
        .stButton button:not([kind="primary"]), .stFormSubmitButton button:not([kind="primary"]) { background: var(--plan-surface); border-color: #8a8f9a; color: #1a243e; }
        .stButton button:not([kind="primary"]):hover, .stFormSubmitButton button:not([kind="primary"]):hover { background: #e7d6ba; color: #0e4b3a; }
        .stButton button:hover { box-shadow: 0 6px 16px rgba(26, 36, 62, .16); transform: translateY(-1px); }
        .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] { background: #0e4b3a; border-color: #0e4b3a; color: #ffffff; }
        .stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primary"]:hover { background: #b49345; border-color: #b49345; color: #1a243e; }
        .stButton button:focus-visible, .stFormSubmitButton button:focus-visible,
        input:focus-visible, textarea:focus-visible, [role="combobox"]:focus-visible { outline: 3px solid #b49345; outline-offset: 2px; }
        button, input, textarea, select { min-height: 2.5rem; }
        .subject-dot { display: inline-block; width: .7rem; height: .7rem; border-radius: 50%; margin-right: .35rem; vertical-align: .05rem; }
        .plan-subject-swatch { width: 1rem; height: 1rem; border-radius: 50%; margin-bottom: .7rem; }
        .plan-timetable-hint { color: var(--plan-muted); display: none; font-size: .8rem; margin: -.25rem 0 .5rem; }
        .plan-timetable-scroll { max-width: 100%; overflow-x: auto; overscroll-behavior-inline: contain; padding: .15rem .15rem .75rem; scrollbar-color: var(--plan-accent) var(--plan-input); scrollbar-width: thin; }
        .plan-timetable { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: .8rem; min-width: 0; }
        .plan-timetable-day { background: var(--plan-input); border: 1px solid var(--plan-border); border-radius: 14px; min-height: 16rem; padding: 1rem; }
        .plan-timetable-day h3 { border-bottom: 1px solid var(--plan-border); color: var(--plan-accent-dark); font-size: .95rem; letter-spacing: .06em; margin: 0 0 .9rem; padding-bottom: .7rem; text-transform: uppercase; }
        .plan-meeting { background: var(--plan-surface); border-left: 5px solid var(--meeting-color); border-radius: 9px; box-shadow: 0 2px 8px rgba(30, 45, 49, .06); display: flex; flex-direction: column; gap: .3rem; margin-bottom: .7rem; padding: .8rem; }
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
        .plan-overview-hero { background: #0e4b3a; border: 1px solid #0e4b3a; border-radius: 10px; box-shadow: none; color: #ffffff; margin-bottom: .7rem; min-height: 12rem; overflow: hidden; padding: 1.5rem 1.65rem; position: relative; }
        .plan-overview-divider { border-top: 1px solid var(--plan-border); margin: 1.25rem 0 .75rem; }
        .plan-overview-day-title { color: var(--plan-text); font-size: 1.55rem; letter-spacing: -.045em; line-height: 1.2; margin: 1rem 0 .75rem; }
        .plan-overview-hero-copy { position: relative; z-index: 2; }
        .plan-overview-hero-kicker { color: #e7d6ba; display: block; font-size: .68rem; font-weight: 800; letter-spacing: .15em; margin-bottom: .85rem; }
        .plan-overview-hero h2 { color: #ffffff; font-size: clamp(2rem, 4vw, 3rem); letter-spacing: -.065em; line-height: .98; margin: 0; }
        .plan-overview-hero h2 em { color: #b49345; font-style: normal; }
        .plan-overview-hero p { color: #ffffff; font-size: .92rem; line-height: 1.45; margin: 1rem 0 0; max-width: 19rem; opacity: .82; }
        .plan-overview-hero-stat { background: rgba(238, 238, 255, .14); border: 1px solid rgba(238, 238, 255, .24); border-radius: 16px; bottom: 1.8rem; padding: .85rem 1rem; position: absolute; right: 2rem; width: 10.5rem; z-index: 2; }
        .plan-overview-hero-stat > span, .plan-overview-hero-stat > small { color: rgba(238, 238, 255, .72); display: block; font-size: .66rem; }
        .plan-overview-hero-stat strong { color: #fff; display: block; font-size: 2rem; letter-spacing: -.06em; line-height: 1.15; margin: .25rem 0 .55rem; }
        .plan-overview-hero-stat strong small { color: rgba(238, 238, 255, .72); display: inline; font-size: .75rem; letter-spacing: 0; }
        .plan-overview-hero-track { background: rgba(255,255,255,.18); border-radius: 99px; height: .35rem; margin-bottom: .45rem; overflow: hidden; }
        .plan-overview-hero-track i { background: #b49345; border-radius: inherit; display: block; height: 100%; }
        .plan-overview-orbit { display: none; }
        .plan-overview-orbit-a { height: 27rem; right: -5rem; top: -9rem; transform: rotate(28deg); width: 13rem; }
        .plan-overview-orbit-b { bottom: -10rem; height: 21rem; right: 7rem; transform: rotate(-32deg); width: 35rem; }
        .plan-overview-spark { display: none; }
        .spark-one { right: 35%; top: 22%; } .spark-two { bottom: 18%; right: 36%; height: .3rem; width: .3rem; } .spark-three { right: 13%; top: 17%; height: .35rem; width: .35rem; }
        .plan-rhythm { background: var(--plan-surface); border: 1px solid var(--plan-border); border-radius: 10px; box-shadow: none; margin: .85rem 0 1.25rem; padding: 1rem 1.1rem .9rem; }
        .plan-rhythm-heading { align-items: baseline; display: flex; justify-content: space-between; margin-bottom: .8rem; }
        .plan-rhythm-heading strong { color: var(--plan-text); font-size: .95rem; letter-spacing: -.02em; }
        .plan-rhythm-heading span { color: var(--plan-muted); font-size: .67rem; }
        .plan-rhythm-grid { display: grid; gap: .55rem; grid-template-columns: repeat(7, minmax(0, 1fr)); }
        .plan-rhythm-day { align-items: center; background: var(--plan-input); border: 1px solid transparent; border-radius: 12px; display: flex; flex-direction: column; min-height: 5.7rem; padding: .55rem .35rem .45rem; }
        .plan-rhythm-day > span { color: var(--plan-muted); font-size: .62rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
        .plan-rhythm-day > strong { color: var(--plan-text); font-size: 1rem; margin: .2rem 0 .25rem; }
        .plan-rhythm-day > i { background: #e7d6ba; border-radius: 99px; display: flex; height: 1.45rem; justify-content: center; overflow: hidden; position: relative; width: .35rem; }
        .plan-rhythm-day > i b { background: var(--plan-accent); border-radius: inherit; bottom: 0; display: block; position: absolute; width: 100%; }
        .plan-rhythm-day > small { color: var(--plan-muted); font-size: .62rem; margin-top: .3rem; }
        .plan-rhythm-done { background: #e7d6ba; border-color: #b49345; } .plan-rhythm-done > strong { color: var(--plan-accent-dark); }
        .plan-rhythm-planned { border-color: #8a8f9a; } .plan-rhythm-planned > i b { background: var(--plan-attention); }
        .plan-rhythm-empty { opacity: .62; }
        .plan-quick-actions { align-items: center; display: flex; margin: 1.2rem 0 .55rem; }
        .plan-quick-actions span { color: var(--plan-muted); font-size: .78rem; font-weight: 700; }
        .plan-topic-path { display: grid; gap: .65rem; padding: .25rem 0 .85rem; }
        .plan-topic-path-item { align-items: center; display: flex !important; gap: .65rem; min-height: 1.8rem; }
        .plan-topic-path-item > i { background: var(--plan-border); border-radius: 50%; display: block; flex: 0 0 auto; height: .55rem; width: .55rem; }
        .plan-topic-path-item.is-done > i { background: #0474c4; box-shadow: 0 0 0 4px rgba(4, 116, 196, .16); }
        .plan-topic-path-item strong { color: var(--plan-text); font-size: .88rem; }
        .plan-topic-path-item small { color: var(--plan-muted); margin-left: auto; white-space: nowrap; }
        .plan-login-shell { align-items: center; display: grid; gap: clamp(2rem, 7vw, 7rem); grid-template-columns: minmax(0, 1.05fr) minmax(20rem, .95fr); margin: clamp(1rem, 7vh, 5rem) auto 2rem; max-width: 1000px; min-height: 32rem; }
        .plan-login-copy { padding: .5rem 0; }
        .plan-login-kicker { align-items: center; color: var(--plan-accent); display: flex; font-size: .72rem; font-weight: 800; gap: .55rem; letter-spacing: .14em; margin-bottom: 1.7rem; }
        .plan-login-dot { background: var(--plan-accent); border-radius: 50%; box-shadow: 0 0 0 5px rgba(23, 107, 93, .12); display: inline-block; height: .55rem; width: .55rem; }
        .plan-login-copy h1 { font-size: clamp(3.1rem, 6vw, 5.35rem); letter-spacing: -.075em; line-height: .98; margin: 0; }
        .plan-login-copy h1 em { color: var(--plan-accent); font-style: normal; }
        .plan-login-lead { color: var(--plan-muted); font-size: 1.08rem; line-height: 1.55; margin: 1.5rem 0 2.2rem; max-width: 30rem; }
        .plan-login-signals { display: grid; gap: .85rem; }
        .plan-login-signals > div { align-items: center; display: flex; gap: .75rem; }
        .plan-login-signal-icon { align-items: center; background: #e7d6ba; border: 1px solid #b49345; border-radius: 10px; color: var(--plan-accent-dark); display: inline-flex; font-size: 1rem; font-weight: 800; height: 2rem; justify-content: center; width: 2rem; }
        .plan-login-signals strong, .plan-login-signals small { display: block; }
        .plan-login-signals strong { color: var(--plan-text); font-size: .83rem; }
        .plan-login-signals small { color: var(--plan-muted); font-size: .75rem; margin-top: .12rem; }
        .plan-login-visual { align-items: center; background: #e7d6ba; border: 1px solid #8a8f9a; border-radius: 14px; display: flex; justify-content: center; min-height: 29rem; overflow: hidden; position: relative; }
        .plan-login-visual::before { background: rgba(255,255,255,.3); border-radius: 50%; content: ''; height: 21rem; position: absolute; right: -5rem; top: -5rem; width: 21rem; }
        .plan-login-orbit { border: 1px solid rgba(6, 69, 127, .18); border-radius: 50%; position: absolute; }
        .plan-login-orbit-one { height: 24rem; transform: rotate(30deg); width: 11rem; }
        .plan-login-orbit-two { height: 11rem; transform: rotate(-38deg); width: 24rem; }
        .plan-login-week-card { background: rgba(252, 253, 249, .94); border: 1px solid rgba(255,255,255,.85); border-radius: 1.2rem; box-shadow: 0 22px 45px rgba(41, 83, 64, .17); padding: 1.35rem; position: relative; transform: rotate(-5deg); width: min(78%, 17rem); z-index: 1; }
        .plan-login-card-top { color: var(--plan-muted); display: flex; font-size: .67rem; justify-content: space-between; letter-spacing: .08em; text-transform: uppercase; }
        .plan-login-card-top b { color: var(--plan-accent); font-size: .8rem; }
        .plan-login-card-title { color: var(--plan-text); font-size: 1.35rem; font-weight: 750; letter-spacing: -.05em; line-height: 1.08; margin: 1.4rem 0 1.7rem; }
        .plan-login-bars { align-items: end; display: flex; gap: .42rem; height: 5.2rem; }
        .plan-login-bars i { background: #e7d6ba; border-radius: 99px 99px .2rem .2rem; display: block; flex: 1; height: 42%; }
        .plan-login-bars i:nth-child(2) { height: 68%; } .plan-login-bars i:nth-child(3) { background: var(--plan-accent); height: 88%; } .plan-login-bars i:nth-child(4) { height: 56%; } .plan-login-bars i:nth-child(5) { height: 75%; } .plan-login-bars i:nth-child(6) { height: 48%; } .plan-login-bars i:nth-child(7) { height: 30%; }
        .plan-login-card-foot { color: #8a8f9a; display: flex; font-size: .57rem; justify-content: space-between; margin-top: .55rem; text-transform: uppercase; }
        .plan-login-float { background: var(--plan-surface); border: 1px solid rgba(255,255,255,.9); border-radius: .7rem; box-shadow: 0 10px 24px rgba(41, 83, 64, .13); color: var(--plan-accent); font-size: .95rem; font-weight: 800; padding: .65rem .75rem; position: absolute; z-index: 2; }
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
        .stApp:has(.plan-dark-mode-marker) {
            --plan-bg: #262b40;
            --plan-surface: #06457f;
            --plan-input: #2c444c;
            --plan-text: #ffffff;
            --plan-muted: #ffffff;
            --plan-border: #b49345;
            --plan-accent: #b49345;
            --plan-accent-dark: #ffffff;
            --plan-attention: #e7d6ba;
            --plan-shadow: 0 16px 36px rgba(0, 0, 0, .2);
            color-scheme: dark;
            background: #262b40;
        }
        body:has(.plan-dark-mode-marker) { background: #262b40; color-scheme: dark; }
        body:has(.plan-dark-mode-marker) .stApp,
        body:has(.plan-dark-mode-marker) [data-testid="stAppViewContainer"] { background-color: #262b40; color: #ffffff; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] { background: #06457f; border-right-color: #0474c4; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarCollapseButton"],
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarCollapseButton"] button { background: #b49345 !important; border-color: #ffffff !important; color: #0e4b3a !important; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarCollapseButton"] svg,
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarCollapseButton"] span { color: #0e4b3a !important; fill: currentColor; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] { border-bottom-color: #b49345; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] li div a { color: #ffffff; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] li div a[aria-current="page"] { color: #ffffff; border: 1px solid #b49345; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] svg,
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] [data-testid="stIconMaterial"],
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] .material-symbols-rounded,
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] .material-symbols-outlined { color: #eeeeff !important; fill: currentColor; -webkit-text-fill-color: #eeeeff; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] li a span,
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] li > div > span { color: #eeeeff !important; -webkit-text-fill-color: #eeeeff; }
        body:has(.plan-dark-mode-marker) h1,
        body:has(.plan-dark-mode-marker) h2,
        body:has(.plan-dark-mode-marker) h3,
        body:has(.plan-dark-mode-marker) [data-testid="stMarkdownContainer"] p,
        body:has(.plan-dark-mode-marker) [data-testid="stWidgetLabel"] p { color: #eeeeff; }
        body:has(.plan-dark-mode-marker) [data-testid="stCaptionContainer"] p,
        body:has(.plan-dark-mode-marker) [data-testid="stHelpInfo"] { color: rgba(238, 238, 255, .72); }
        body:has(.plan-dark-mode-marker) [data-testid="stTextInput"] input,
        body:has(.plan-dark-mode-marker) [data-testid="stNumberInput"] input,
        body:has(.plan-dark-mode-marker) textarea { color: #ffffff !important; caret-color: #b49345; }
        body:has(.plan-dark-mode-marker) [data-baseweb="select"] span,
        body:has(.plan-dark-mode-marker) [data-baseweb="select"] input { color: #eeeeff !important; }
        body:has(.plan-dark-mode-marker) [data-testid="stMetricValue"] { color: #eeeeff; }
        body:has(.plan-dark-mode-marker) [data-testid="stMetricLabel"] p { color: rgba(238, 238, 255, .72); }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] .plan-sidebar-user { background: rgba(180, 147, 69, .18); border-color: #b49345; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] .plan-sidebar-user strong { color: #eeeeff; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] .plan-sidebar-user span { color: #ffffff; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] [data-testid="stExpander"] summary { background: #0e4b3a; color: #ffffff; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] [data-testid="stExpander"] summary svg { color: #b49345; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] input,
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] label,
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #eeeeff !important; -webkit-text-fill-color: #eeeeff; }
        body:has(.plan-dark-mode-marker) [data-testid="stVerticalBlockBorderWrapper"],
        body:has(.plan-dark-mode-marker) [data-testid="stForm"],
        body:has(.plan-dark-mode-marker) [data-testid="stExpander"],
        body:has(.plan-dark-mode-marker) [data-testid="stMetric"],
        body:has(.plan-dark-mode-marker) [data-testid="stDataFrame"] { border-color: #b49345; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] hr,
        body:has(.plan-dark-mode-marker) [data-testid="stMarkdownContainer"] hr { border-color: #b49345; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] svg,
        body:has(.plan-dark-mode-marker) [data-testid="stButton"] [data-testid="stIcon"],
        body:has(.plan-dark-mode-marker) [data-testid="stFormSubmitButton"] [data-testid="stIcon"] { color: #eeeeff !important; fill: currentColor; }
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        body:has(.plan-dark-mode-marker) [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #ffffff; }
        .stApp:has(.plan-dark-mode-marker) [data-testid="stSidebar"] { background: #1b3b6f; }
        .stApp:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] li div a:hover { background: rgba(90, 188, 185, .14); }
        .stApp:has(.plan-dark-mode-marker) [data-testid="stSidebarNav"] li div a[aria-current="page"],
        .stApp:has(.plan-dark-mode-marker) [data-testid="stVerticalBlockBorderWrapper"],
        .stApp:has(.plan-dark-mode-marker) [data-testid="stForm"],
        .stApp:has(.plan-dark-mode-marker) [data-testid="stExpander"],
        .stApp:has(.plan-dark-mode-marker) [data-testid="stMetric"] { background: #1b3b6f; }
        .stApp:has(.plan-dark-mode-marker) [data-testid="stForm"] { background: #1b3b6f; }
        .stApp:has(.plan-dark-mode-marker) [data-testid="stExpander"] summary,
        .stApp:has(.plan-dark-mode-marker) [data-testid="stExpander"] summary:hover { background: #1b3b6f; color: #eeeeff; }
        .stApp:has(.plan-dark-mode-marker) [data-testid="stExpander"] summary svg { color: #5abcb9; }
        .stApp:has(.plan-dark-mode-marker) [data-baseweb="input"],
        .stApp:has(.plan-dark-mode-marker) [data-baseweb="textarea"],
        .stApp:has(.plan-dark-mode-marker) [data-baseweb="select"] > div { background: rgba(165, 153, 181, .2); border-color: #5abcb9; }
        .stApp:has(.plan-dark-mode-marker) [data-baseweb="input"] input,
        .stApp:has(.plan-dark-mode-marker) [data-baseweb="textarea"] textarea { color: #eeeeff; }
        .stApp:has(.plan-dark-mode-marker) .plan-overview-hero { background: #1b3b6f; box-shadow: 0 24px 48px rgba(0, 0, 0, .25); }
        .stApp:has(.plan-dark-mode-marker) .plan-overview-hero-stat { background: rgba(165, 153, 181, .2); border-color: rgba(90, 188, 185, .45); }
        .stApp:has(.plan-dark-mode-marker) .plan-rhythm { background: rgba(27, 59, 111, .82); border-color: #5abcb9; }
        .stApp:has(.plan-dark-mode-marker) .plan-rhythm-day { background: rgba(165, 153, 181, .2); }
        .stApp:has(.plan-dark-mode-marker) .plan-rhythm-done { background: rgba(90, 188, 185, .22); border-color: #5abcb9; }
        .stApp:has(.plan-dark-mode-marker) .plan-rhythm-planned { border-color: #5abcb9; }
        .stApp:has(.plan-dark-mode-marker) .plan-progress-card { background: #1b3b6f; border-color: #5abcb9; }
        .stApp:has(.plan-dark-mode-marker) .plan-progress-track { background: rgba(90, 188, 185, .28); }
        .stApp:has(.plan-dark-mode-marker) .plan-login-visual { background: #1b3b6f; border-color: #5abcb9; }
        .stApp:has(.plan-dark-mode-marker) .plan-login-week-card,
        .stApp:has(.plan-dark-mode-marker) .plan-login-float { background: #1b3b6f; border-color: #5abcb9; }
        .stApp:has(.plan-dark-mode-marker) .stButton button[kind="primary"],
        .stApp:has(.plan-dark-mode-marker) .stFormSubmitButton button[kind="primary"] { background: #eeeeff; border-color: #eeeeff; color: #1b3b6f; }
        .stApp:has(.plan-dark-mode-marker) .stButton button[kind="primary"]:hover,
        .stApp:has(.plan-dark-mode-marker) .stFormSubmitButton button[kind="primary"]:hover { background: #a599b5; border-color: #a599b5; color: #1b3b6f; }
        .stApp:has(.plan-dark-mode-marker) .stButton button:not([kind="primary"]),
        .stApp:has(.plan-dark-mode-marker) .stFormSubmitButton button:not([kind="primary"]) { background: transparent; border-color: #eeeeff; color: #eeeeff; }
        [data-testid="stSidebar"] [data-testid="stButton"] button { background: #06457f !important; border: 1px solid #ffffff !important; color: #ffffff !important; }
        [data-testid="stSidebar"] [data-testid="stButton"] button:hover { background: #0474c4 !important; border-color: #0474c4 !important; color: #ffffff !important; }
        [data-testid="stSidebarNav"] li a svg,
        [data-testid="stSidebarNav"] li a svg path,
        [data-testid="stSidebarNav"] li a [data-testid="stIconMaterial"],
        [data-testid="stSidebarNav"] li a .material-symbols-rounded,
        [data-testid="stSidebarNav"] li a .material-symbols-outlined { color: #ffffff !important; fill: #ffffff !important; -webkit-text-fill-color: #ffffff !important; stroke: #ffffff !important; }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.get("plan_dark_mode", False):
        st.markdown('<span class="plan-dark-mode-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
