"""UI theme for the Resume Review Agent — styled after wemakedevs.org.

Dark, terminal-meets-neon developer aesthetic: near-black background, neon
green accent, mono uppercase labels, hairline-bordered cards with corner
brackets, conic-gradient rings and animated gradient bars.

Everything here is presentation-only. Call `inject_theme()` once after
`st.set_page_config` and use the small HTML helpers below.
"""

from __future__ import annotations

import html as _html

import streamlit as st

# Accent colors per score category (echo the reference site's multi-color system).
ACCENT_BLUE = "#3080ff"
ACCENT_PURPLE = "#8a86ff"
ACCENT_ORANGE = "#fe6e00"
ACCENT_GREEN = "#00c758"

CATEGORY_ACCENTS = {
    "formatting": ACCENT_BLUE,
    "clarity": ACCENT_PURPLE,
    "impact": ACCENT_ORANGE,
    "keyword_match": ACCENT_GREEN,
}

WMD_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@100..900&family=Inter:wght@100..900&display=swap');

:root {
  --wmd-bg:#08090d; --wmd-alt:#0c0e13; --wmd-card:#18181b;
  --wmd-fg:#fafafa; --wmd-muted:#9f9fa9;
  --wmd-border:rgba(255,255,255,.10);
  --wmd-green:#00c758; --wmd-green2:#00a544;
  --wmd-blue:#3080ff; --wmd-purple:#8a86ff;
  --wmd-orange:#fe6e00; --wmd-red:#ff6568;
  --wmd-font:'Inter',sans-serif;
  --wmd-mono:'Geist Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
}

html, body, [class*="css"], .stApp { font-family:var(--wmd-font); color:var(--wmd-fg); }

/* page background with hero "light rays" */
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 20% 8%,  rgba(160,210,255,.14), transparent 45%),
    radial-gradient(circle at 85% 6%,  rgba(0,199,88,.10),  transparent 50%),
    var(--wmd-bg) !important;
}
[data-testid="stHeader"] { background:transparent; }
#MainMenu, footer, [data-testid="stDecoration"] { visibility:hidden; }

/* content column framed by dashed vertical hairlines */
[data-testid="stMainBlockContainer"] {
  max-width:1300px; margin:0 auto; padding:1.5rem 2.5rem;
  border-left:1px dashed rgba(255,255,255,.12);
  border-right:1px dashed rgba(255,255,255,.12);
}

code, pre, [data-testid="stMetricLabel"] { font-family:var(--wmd-mono); }

/* buttons: green fill, rounded-sm, glow hover */
div.stButton > button {
  height:40px; padding:0 14px; border-radius:4px; font-weight:500;
  background:var(--wmd-green); color:var(--wmd-bg); border:1px solid transparent;
  transition:background .3s ease, transform .15s ease, box-shadow .3s ease;
}
div.stButton > button:hover { background:var(--wmd-green2); box-shadow:0 0 18px rgba(0,199,88,.35); transform:translateY(-1px); }
div.stButton > button[kind="secondary"] { background:var(--wmd-alt); border:1px solid rgba(255,255,255,.16); color:var(--wmd-fg); }
div.stButton > button[kind="secondary"]:hover { background:#27272a; box-shadow:none; }

/* native progress bar -> premium gradient */
[data-testid="stProgress"] { background:rgba(255,255,255,.08); border-radius:999px; overflow:hidden; }
[data-testid="stProgress"] > div {
  background:linear-gradient(90deg,var(--wmd-green),var(--wmd-green2)) !important;
  border-radius:999px; box-shadow:0 0 12px rgba(0,199,88,.40);
}

/* native metric -> card */
[data-testid="stMetric"] { background:var(--wmd-card); border:1px solid var(--wmd-border); border-radius:4px; padding:1rem 1.25rem; }
[data-testid="stMetricLabel"] { font-size:.75rem; text-transform:uppercase; letter-spacing:.05em; color:var(--wmd-muted); }
[data-testid="stMetricValue"] { font-size:2rem; font-weight:600; color:var(--wmd-fg); }

/* inputs */
[data-testid="stFileUploaderDropzone"] { background:var(--wmd-alt) !important; border:1px dashed rgba(255,255,255,.2) !important; border-radius:8px; }
[data-testid="stFileUploaderDropzone"]:hover { border-color:var(--wmd-green) !important; }
[data-testid="stTextArea"] textarea {
  background:var(--wmd-alt); color:var(--wmd-fg);
  border:1px solid rgba(255,255,255,.15); border-radius:8px;
}
[data-testid="stTextArea"] textarea:focus { border-color:var(--wmd-green); box-shadow:0 0 0 1px var(--wmd-green); }
[data-testid="stAlert"] { border-radius:6px; border:1px solid var(--wmd-border); background:var(--wmd-card); }

/* custom components */
.wmd-eyebrow { font-family:var(--wmd-mono); font-size:.8rem; text-transform:uppercase; letter-spacing:.05em; color:var(--wmd-green); margin:2.5rem 0 .5rem; }

.wmd-hero h1 { font-size:clamp(2rem,5vw,3.4rem); font-weight:700; letter-spacing:-.03em; line-height:1.1; margin:.75rem 0 1rem; }
.wmd-shimmer {
  background:linear-gradient(110deg,#00c758 40%,#eafff2 50%,#00c758 60%);
  background-size:200% 100%; -webkit-background-clip:text; background-clip:text;
  -webkit-text-fill-color:transparent; color:transparent;
  animation:wmd-shimmer 3s linear infinite;
}
@keyframes wmd-shimmer { to { background-position:-200% 0; } }

.wmd-card { position:relative; background:var(--wmd-card); border:1px solid var(--wmd-border); border-radius:4px; padding:1.25rem; margin-bottom:1rem; }
.wmd-card-label { font-family:var(--wmd-mono); font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:var(--wmd-muted); }
.wmd-card-score { font-size:2.4rem; font-weight:600; line-height:1.1; margin:.35rem 0; }

.wmd-corner { position:absolute; width:14px; height:14px; border-color:rgba(255,255,255,.25); transition:border-color .2s ease; pointer-events:none; }
.wmd-card:hover .wmd-corner { border-color:var(--wmd-green); }
.wmd-c-tl { top:-1px; left:-1px;  border-top:1.5px solid; border-left:1.5px solid; }
.wmd-c-tr { top:-1px; right:-1px; border-top:1.5px solid; border-right:1.5px solid; }
.wmd-c-bl { bottom:-1px; left:-1px;  border-bottom:1.5px solid; border-left:1.5px solid; }
.wmd-c-br { bottom:-1px; right:-1px; border-bottom:1.5px solid; border-right:1.5px solid; }

.wmd-bar { height:8px; border-radius:999px; background:rgba(255,255,255,.08); overflow:hidden; margin-top:.75rem; }
.wmd-bar-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,var(--wmd-green),var(--wmd-green2)); box-shadow:0 0 10px rgba(0,199,88,.5); animation:wmd-grow 1s cubic-bezier(.4,0,.2,1); }
@keyframes wmd-grow { from { width:0; } }

.wmd-ring { --pct:0; width:190px; aspect-ratio:1; border-radius:50%;
  background:conic-gradient(var(--wmd-green) calc(var(--pct)*1%), rgba(255,255,255,.08) 0);
  display:grid; place-items:center; position:relative; box-shadow:0 0 34px rgba(0,199,88,.25); }
.wmd-ring::before { content:""; position:absolute; inset:11px; border-radius:50%; background:var(--wmd-alt); }
.wmd-ring-inner { position:relative; z-index:1; text-align:center; }
.wmd-ring-num { font-size:2.6rem; font-weight:700; line-height:1; }
.wmd-ring-num small { font-size:1rem; color:var(--wmd-muted); font-weight:500; }
.wmd-ring-label { font-family:var(--wmd-mono); text-transform:uppercase; letter-spacing:.1em; font-size:.72rem; color:var(--wmd-muted); margin-top:.35rem; }

.wmd-item { display:flex; gap:.75rem; align-items:flex-start; background:var(--wmd-card);
  border:1px solid var(--wmd-border); border-left:3px solid var(--wmd-green);
  border-radius:4px; padding:.85rem 1rem; margin-bottom:.6rem; font-size:.95rem; line-height:1.55; }
.wmd-item--orange { border-left-color:var(--wmd-orange); }
.wmd-item--purple { border-left-color:var(--wmd-purple); }
.wmd-item-mark { color:var(--wmd-green); font-weight:700; flex-shrink:0; }
.wmd-item--orange .wmd-item-mark { color:var(--wmd-orange); }
.wmd-item--purple .wmd-item-mark { color:var(--wmd-purple); }

.wmd-divider { height:36px; margin:1.5rem 0; border-bottom:1px solid var(--wmd-border);
  background:repeating-linear-gradient(315deg, rgba(255,255,255,.05) 0 1px, transparent 1px 50%); background-size:10px 10px; }

.wmd-footer { margin-top:3.5rem; padding-top:1.25rem; border-top:1px dashed rgba(255,255,255,.15);
  font-family:var(--wmd-mono); font-size:.78rem; color:var(--wmd-muted); text-transform:uppercase; letter-spacing:.05em; }
</style>"""


def inject_theme() -> None:
    """Inject the full stylesheet. Call once after st.set_page_config."""
    st.markdown(WMD_CSS, unsafe_allow_html=True)


# --- small HTML helpers ---

def html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def eyebrow(number: str, label: str) -> None:
    html(f'<div class="wmd-eyebrow">{_html.escape(number)} / {_html.escape(label)}</div>')


def brackets() -> str:
    return (
        '<span class="wmd-corner wmd-c-tl"></span>'
        '<span class="wmd-corner wmd-c-tr"></span>'
        '<span class="wmd-corner wmd-c-bl"></span>'
        '<span class="wmd-corner wmd-c-br"></span>'
    )


def score_card(label: str, value: int | None, accent: str = ACCENT_GREEN, note: str | None = None) -> None:
    shown = "N/A" if value is None else f"{value}"
    pct = value if value is not None else 0
    note_html = ""
    if note:
        note_html = (
            f'<div style="color:#9f9fa9;font-size:.8rem;margin-top:.4rem">'
            f"{_html.escape(note)}</div>"
        )
    html(
        f'<div class="wmd-card">{brackets()}'
        f'<div class="wmd-card-label">{_html.escape(label)}</div>'
        f'<div class="wmd-card-score" style="color:{accent}">{shown}'
        f'<span style="font-size:1rem;color:#9f9fa9">/100</span></div>'
        f'<div class="wmd-bar"><div class="wmd-bar-fill" style="width:{pct}%;'
        f'background:linear-gradient(90deg,{accent},{accent})"></div></div>'
        f'{note_html}</div>'
    )


def ring(score: int, label: str = "Overall Score") -> None:
    html(
        f'<div class="wmd-ring" style="--pct:{score}">'
        f'<div class="wmd-ring-inner"><div class="wmd-ring-num">{score}'
        f'<small>/100</small></div>'
        f'<div class="wmd-ring-label">{_html.escape(label)}</div></div></div>'
    )


def item_list(items: list[str], variant: str = "", mark: str = "+") -> None:
    cls = f" wmd-item--{variant}" if variant else ""
    for item in items:
        html(
            f'<div class="wmd-item{cls}"><span class="wmd-item-mark">{_html.escape(mark)}</span>'
            f'<span>{_html.escape(item)}</span></div>'
        )


def divider() -> None:
    html('<div class="wmd-divider"></div>')


def footer(text: str) -> None:
    html(f'<div class="wmd-footer">{_html.escape(text)}</div>')
