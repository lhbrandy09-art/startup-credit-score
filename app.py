from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

from vero.intelligence.profile_engine import build_company_profile
from vero.intelligence.vero_score_engine import analyze_vero_score

try:
    from vero.research.agent import ResearchError, research_company, research_to_description
    AI_RESEARCH_AVAILABLE = True
except Exception:
    AI_RESEARCH_AVAILABLE = False
    ResearchError = RuntimeError


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "Outputs"

st.set_page_config(
    page_title="VERO | Startup Intelligence",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Make Streamlit Cloud secrets available to the research agent.
try:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = str(st.secrets["OPENAI_API_KEY"])
    if "VERO_AI_MODEL" in st.secrets:
        os.environ["VERO_AI_MODEL"] = str(st.secrets["VERO_AI_MODEL"])
except Exception:
    pass

THEMES = {
    "Executive": {
        "primary": "#3155D9",
        "secondary": "#D8A928",
        "background": "#F5F7FC",
        "surface": "#FFFFFF",
        "surface_alt": "#EEF2FF",
        "text": "#121A2F",
        "muted": "#667085",
        "border": "#DFE4EF",
        "positive": "#16A36A",
        "warning": "#D98E04",
        "danger": "#D64545",
        "sidebar": "#11182B",
        "sidebar_text": "#F8FAFC",
    },
    "Evergreen": {
        "primary": "#167A5B",
        "secondary": "#C6A15B",
        "background": "#F4F7F2",
        "surface": "#FFFFFF",
        "surface_alt": "#E9F4EE",
        "text": "#16312A",
        "muted": "#66746F",
        "border": "#D8E2DA",
        "positive": "#12805C",
        "warning": "#C08A24",
        "danger": "#C95151",
        "sidebar": "#102E26",
        "sidebar_text": "#F4FBF8",
    },
    "Capital": {
        "primary": "#0F9B6C",
        "secondary": "#0A4D3B",
        "background": "#F2F8F5",
        "surface": "#FFFFFF",
        "surface_alt": "#E4F4EC",
        "text": "#102A22",
        "muted": "#63716B",
        "border": "#D6E5DD",
        "positive": "#0F9B6C",
        "warning": "#C88719",
        "danger": "#CF4D4D",
        "sidebar": "#092A21",
        "sidebar_text": "#F0FFF9",
    },
    "Midnight": {
        "primary": "#65B8FF",
        "secondary": "#A6E0FF",
        "background": "#09111F",
        "surface": "#111C2E",
        "surface_alt": "#15243A",
        "text": "#F5F8FC",
        "muted": "#9AAAC0",
        "border": "#26364E",
        "positive": "#42D39B",
        "warning": "#F2B84B",
        "danger": "#FF7272",
        "sidebar": "#060C16",
        "sidebar_text": "#F5F8FC",
    },
    "Minimal": {
        "primary": "#161616",
        "secondary": "#707070",
        "background": "#F6F6F6",
        "surface": "#FFFFFF",
        "surface_alt": "#EEEEEE",
        "text": "#111111",
        "muted": "#6E6E6E",
        "border": "#DDDDDD",
        "positive": "#1D7A4C",
        "warning": "#A96F0A",
        "danger": "#B94242",
        "sidebar": "#111111",
        "sidebar_text": "#FFFFFF",
    },
    "Quantum": {
        "primary": "#2E9BFF",
        "secondary": "#8B5CF6",
        "background": "#080A10",
        "surface": "#11141D",
        "surface_alt": "#181C28",
        "text": "#F7F8FC",
        "muted": "#A0A7B8",
        "border": "#292E3D",
        "positive": "#36D399",
        "warning": "#F7B955",
        "danger": "#FF6B77",
        "sidebar": "#05060A",
        "sidebar_text": "#F7F8FC",
    },
    "Ivy": {
        "primary": "#7A2233",
        "secondary": "#C5A35A",
        "background": "#F7F3EC",
        "surface": "#FFFDFC",
        "surface_alt": "#F0E6E2",
        "text": "#2D1720",
        "muted": "#75666B",
        "border": "#E4D8D5",
        "positive": "#2E7B57",
        "warning": "#B17A17",
        "danger": "#B8454E",
        "sidebar": "#35121B",
        "sidebar_text": "#FFF9F7",
    },
    "Ocean": {
        "primary": "#0077B6",
        "secondary": "#48CAE4",
        "background": "#F1FAFF",
        "surface": "#FFFFFF",
        "surface_alt": "#DFF4FC",
        "text": "#08263A",
        "muted": "#607D8B",
        "border": "#CBE7F2",
        "positive": "#129970",
        "warning": "#D9911B",
        "danger": "#D84D4D",
        "sidebar": "#06283D",
        "sidebar_text": "#F4FBFF",
    },
    "Sunset": {
        "primary": "#F26B38",
        "secondary": "#F6B73C",
        "background": "#FFF7F1",
        "surface": "#FFFFFF",
        "surface_alt": "#FFE8D8",
        "text": "#352018",
        "muted": "#806A61",
        "border": "#F1D8C8",
        "positive": "#2A9D6F",
        "warning": "#E39A18",
        "danger": "#D94A4A",
        "sidebar": "#3A1F18",
        "sidebar_text": "#FFF8F4",
    },
    "Lavender": {
        "primary": "#7C5CE7",
        "secondary": "#C084FC",
        "background": "#F7F4FF",
        "surface": "#FFFFFF",
        "surface_alt": "#EFE9FF",
        "text": "#251C3D",
        "muted": "#756B8C",
        "border": "#DFD6F5",
        "positive": "#2F9E72",
        "warning": "#C78A17",
        "danger": "#D45267",
        "sidebar": "#261A46",
        "sidebar_text": "#FBF8FF",
    },
    "Rose": {
        "primary": "#D9467B",
        "secondary": "#F59AB7",
        "background": "#FFF5F8",
        "surface": "#FFFFFF",
        "surface_alt": "#FFE5EE",
        "text": "#351A25",
        "muted": "#846B74",
        "border": "#F0D1DC",
        "positive": "#21926A",
        "warning": "#C68A1A",
        "danger": "#C93D52",
        "sidebar": "#3A1422",
        "sidebar_text": "#FFF8FB",
    },
    "Copper": {
        "primary": "#B7652A",
        "secondary": "#D99A5D",
        "background": "#FAF5EF",
        "surface": "#FFFDFC",
        "surface_alt": "#F1E4D5",
        "text": "#2E2118",
        "muted": "#77695E",
        "border": "#E5D7C7",
        "positive": "#2D8661",
        "warning": "#B98221",
        "danger": "#C84D48",
        "sidebar": "#2E1B12",
        "sidebar_text": "#FFF9F3",
    },
    "Arctic": {
        "primary": "#2C7BE5",
        "secondary": "#8ED7F7",
        "background": "#F6FBFF",
        "surface": "#FFFFFF",
        "surface_alt": "#EAF5FC",
        "text": "#12263A",
        "muted": "#6E8091",
        "border": "#D7E8F3",
        "positive": "#1F9A72",
        "warning": "#C98C1C",
        "danger": "#D64B57",
        "sidebar": "#0B2035",
        "sidebar_text": "#F4FAFF",
    },
    "Solar": {
        "primary": "#E6A700",
        "secondary": "#FFCC33",
        "background": "#FFFBEF",
        "surface": "#FFFFFF",
        "surface_alt": "#FFF3C7",
        "text": "#2B2411",
        "muted": "#786F55",
        "border": "#E9DCA7",
        "positive": "#24845F",
        "warning": "#D38A00",
        "danger": "#D24C42",
        "sidebar": "#2D250E",
        "sidebar_text": "#FFFDF5",
    },
    "Crimson": {
        "primary": "#C62828",
        "secondary": "#EF5350",
        "background": "#FFF5F5",
        "surface": "#FFFFFF",
        "surface_alt": "#FDE6E6",
        "text": "#321A1A",
        "muted": "#816A6A",
        "border": "#EED0D0",
        "positive": "#24845F",
        "warning": "#C58B1A",
        "danger": "#B71C1C",
        "sidebar": "#330F12",
        "sidebar_text": "#FFF8F8",
    },
    "Teal": {
        "primary": "#0F8B8D",
        "secondary": "#49C5B6",
        "background": "#F1FAF9",
        "surface": "#FFFFFF",
        "surface_alt": "#DFF3F1",
        "text": "#123332",
        "muted": "#647B79",
        "border": "#CDE6E3",
        "positive": "#1D956B",
        "warning": "#C58A1C",
        "danger": "#D34B55",
        "sidebar": "#0A3435",
        "sidebar_text": "#F3FFFD",
    },
    "Sakura": {
        "primary": "#E76F9A",
        "secondary": "#F6B8CE",
        "background": "#FFF8FB",
        "surface": "#FFFFFF",
        "surface_alt": "#FDEAF1",
        "text": "#35202A",
        "muted": "#836E77",
        "border": "#EFD7E0",
        "positive": "#2A8D68",
        "warning": "#C58A1C",
        "danger": "#C84763",
        "sidebar": "#43202E",
        "sidebar_text": "#FFF9FC",
    },
    "Obsidian Gold": {
        "primary": "#E0B84F",
        "secondary": "#F2D781",
        "background": "#0D0D0E",
        "surface": "#171719",
        "surface_alt": "#222225",
        "text": "#FAF8F1",
        "muted": "#B8B3A5",
        "border": "#343438",
        "positive": "#45C58A",
        "warning": "#E0B84F",
        "danger": "#FF7373",
        "sidebar": "#080809",
        "sidebar_text": "#FFF9E8",
    },
    "Cyber Lime": {
        "primary": "#B7F34A",
        "secondary": "#43E6C2",
        "background": "#090D0A",
        "surface": "#131915",
        "surface_alt": "#1A231D",
        "text": "#F4FFE8",
        "muted": "#AAB8A3",
        "border": "#2D3A31",
        "positive": "#62E6A7",
        "warning": "#F0C95A",
        "danger": "#FF6B7A",
        "sidebar": "#050805",
        "sidebar_text": "#F6FFE9",
    },

}

if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Executive"
if "page" not in st.session_state:
    st.session_state.page = "Overview"

# Apply navigation requests before the sidebar radio widget is created.
# Streamlit does not allow changing st.session_state.page after the widget
# with key="page" has already been instantiated during the same run.
pending_page = st.session_state.pop("pending_page", None)
if pending_page:
    st.session_state.page = pending_page


def navigate_to(page_name: str) -> None:
    st.session_state["pending_page"] = page_name
    st.rerun()


def inject_css(theme: dict[str, str]) -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --vero-primary: {theme['primary']};
            --vero-secondary: {theme['secondary']};
            --vero-bg: {theme['background']};
            --vero-surface: {theme['surface']};
            --vero-surface-alt: {theme['surface_alt']};
            --vero-text: {theme['text']};
            --vero-muted: {theme['muted']};
            --vero-border: {theme['border']};
            --vero-positive: {theme['positive']};
            --vero-warning: {theme['warning']};
            --vero-danger: {theme['danger']};
        }}

        .stApp {{
            background: var(--vero-bg);
            color: var(--vero-text);
        }}

        [data-testid="stSidebar"] {{
            background: {theme['sidebar']};
            border-right: 1px solid {theme['border']};
        }}

        [data-testid="stSidebar"] * {{
            color: {theme['sidebar_text']};
        }}

        [data-testid="stSidebar"] .stRadio label {{
            border-radius: 10px;
            padding: 0.35rem 0.5rem;
        }}

        .block-container {{
            max-width: 1440px;
            padding-top: 1.7rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3, h4, h5, h6, p, label {{
            color: var(--vero-text);
        }}

        .vero-brand {{
            font-size: 1.8rem;
            font-weight: 850;
            letter-spacing: 0.18em;
            color: {theme['sidebar_text']};
            margin: 0.35rem 0 0;
        }}

        .vero-brand-sub {{
            color: {theme['sidebar_text']};
            opacity: 0.68;
            font-size: 0.82rem;
            margin-bottom: 1.25rem;
        }}

        .vero-eyebrow {{
            color: var(--vero-primary);
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.76rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }}

        .vero-page-title {{
            font-size: clamp(2rem, 4vw, 3.35rem);
            line-height: 1.04;
            font-weight: 850;
            letter-spacing: -0.045em;
            margin: 0;
            color: var(--vero-text);
        }}

        .vero-page-copy {{
            color: var(--vero-muted);
            font-size: 1.04rem;
            max-width: 760px;
            margin-top: 0.65rem;
            margin-bottom: 1.8rem;
        }}

        .vero-card {{
            background: var(--vero-surface);
            border: 1px solid var(--vero-border);
            border-radius: 18px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 10px 28px rgba(16, 24, 40, 0.06);
            height: 100%;
        }}

        .vero-card:hover {{
            transform: translateY(-2px);
            transition: transform 150ms ease, box-shadow 150ms ease;
            box-shadow: 0 14px 34px rgba(16, 24, 40, 0.10);
        }}

        .vero-kpi-label {{
            font-size: 0.80rem;
            color: var(--vero-muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 760;
        }}

        .vero-kpi-value {{
            font-size: 2rem;
            font-weight: 850;
            letter-spacing: -0.04em;
            color: var(--vero-text);
            margin: 0.24rem 0 0.18rem;
        }}

        .vero-kpi-sub {{
            color: var(--vero-muted);
            font-size: 0.86rem;
        }}

        .vero-badge {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.32rem 0.65rem;
            background: var(--vero-surface-alt);
            color: var(--vero-primary);
            border: 1px solid var(--vero-border);
            font-size: 0.78rem;
            font-weight: 750;
        }}

        .vero-section-title {{
            font-size: 1.28rem;
            font-weight: 820;
            letter-spacing: -0.02em;
            margin: 1.8rem 0 0.2rem;
        }}

        .vero-section-copy {{
            color: var(--vero-muted);
            margin: 0 0 0.9rem;
        }}

        .vero-score-ring {{
            width: 164px;
            height: 164px;
            border-radius: 50%;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            background: conic-gradient(var(--vero-primary) calc(var(--score) * 1%), var(--vero-border) 0);
            position: relative;
        }}

        .vero-score-ring::before {{
            content: "";
            position: absolute;
            width: 126px;
            height: 126px;
            border-radius: 50%;
            background: var(--vero-surface);
        }}

        .vero-score-inner {{
            z-index: 1;
            text-align: center;
        }}

        .vero-score-number {{
            font-size: 2.35rem;
            font-weight: 900;
            line-height: 1;
        }}

        .vero-score-label {{
            color: var(--vero-muted);
            font-size: 0.78rem;
            margin-top: 0.25rem;
        }}

        .vero-progress-wrap {{
            margin-bottom: 0.95rem;
        }}

        .vero-progress-head {{
            display: flex;
            justify-content: space-between;
            font-size: 0.87rem;
            margin-bottom: 0.35rem;
        }}

        .vero-progress-track {{
            height: 9px;
            border-radius: 999px;
            overflow: hidden;
            background: var(--vero-border);
        }}

        .vero-progress-fill {{
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--vero-primary), var(--vero-secondary));
        }}

        div.stButton > button, div.stDownloadButton > button {{
            border-radius: 11px;
            border: 1px solid var(--vero-primary);
            background: var(--vero-primary);
            color: white;
            font-weight: 760;
            min-height: 2.8rem;
            box-shadow: none;
        }}

        div.stButton > button:hover, div.stDownloadButton > button:hover {{
            border-color: var(--vero-secondary);
            background: var(--vero-secondary);
            color: white;
        }}

        div.stButton > button *,
        div.stDownloadButton > button * {{
            color: #FFFFFF !important;
        }}

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-baseweb="select"] > div {{
            border-radius: 11px !important;
            border-color: var(--vero-border) !important;
            background: var(--vero-surface) !important;
            color: var(--vero-text) !important;
        }}


        /* Keep select boxes readable in every theme */
        [data-baseweb="select"] > div {{
            background: var(--vero-surface) !important;
            color: var(--vero-text) !important;
        }}

        [data-baseweb="select"] input,
        [data-baseweb="select"] span,
        [data-baseweb="select"] svg {{
            color: var(--vero-text) !important;
            fill: var(--vero-text) !important;
        }}

        [role="listbox"] {{
            background: var(--vero-surface) !important;
            border: 1px solid var(--vero-border) !important;
        }}

        [role="option"] {{
            background: var(--vero-surface) !important;
            color: var(--vero-text) !important;
        }}

        [role="option"]:hover,
        [aria-selected="true"][role="option"] {{
            background: var(--vero-surface-alt) !important;
            color: var(--vero-text) !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background: #FFFFFF !important;
            color: #111827 !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] span,
        [data-testid="stSidebar"] [data-baseweb="select"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] svg {{
            color: #111827 !important;
            fill: #111827 !important;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid var(--vero-border);
            border-radius: 14px;
            overflow: hidden;
        }}

        hr {{
            border-color: var(--vero-border);
        }}

        @media (max-width: 700px) {{
            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
            .vero-page-title {{ font-size: 2.25rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_html(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def safe_number(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clean_text(value: Any, fallback: str = "") -> str:
    """Return readable text without exposing pandas NaN values."""
    if value is None:
        return fallback
    try:
        if pd.isna(value):
            return fallback
    except (TypeError, ValueError):
        pass
    cleaned = str(value).strip()
    if not cleaned or cleaned.lower() in {"nan", "none", "null", "n/a", "unknown"}:
        return fallback
    return cleaned


def first_present(row: pd.Series, columns: list[str], fallback: Any = "") -> Any:
    """Return the first non-empty value found across possible column aliases."""
    for column in columns:
        if column in row.index:
            value = row.get(column)
            if clean_text(value):
                return value
            if isinstance(value, (int, float)) and not pd.isna(value):
                return value
    return fallback


def first_number(row: pd.Series, columns: list[str], default: float = 0.0) -> float:
    """Return the first valid numeric value across possible column aliases."""
    for column in columns:
        if column not in row.index:
            continue
        value = safe_number(row.get(column), default=float("nan"))
        if not pd.isna(value):
            return value
    return default


def valid_company_name(value: Any) -> bool:
    """Reject IDs, descriptions, and missing values that sometimes leak into name fields."""
    name = clean_text(value)
    if not name or len(name) > 64:
        return False
    if name.replace(".", "").replace("-", "").isdigit():
        return False
    words = name.split()
    if len(words) > 8:
        return False
    sentence_markers = (" is a ", " helps ", " provides ", " platform for ", " company that ")
    if any(marker in name.lower() for marker in sentence_markers):
        return False
    return any(character.isalpha() for character in name)


def page_header(eyebrow: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="vero-eyebrow">{safe_html(eyebrow)}</div>
        <div class="vero-page-title">{safe_html(title)}</div>
        <div class="vero-page-copy">{safe_html(copy)}</div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, copy: str = "") -> None:
    st.markdown(
        f"""
        <div class="vero-section-title">{safe_html(title)}</div>
        <div class="vero-section-copy">{safe_html(copy)}</div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: Any, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="vero-card">
            <div class="vero-kpi-label">{safe_html(label)}</div>
            <div class="vero-kpi-value">{safe_html(value)}</div>
            <div class="vero-kpi-sub">{safe_html(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar(label: str, value: float) -> None:
    value = max(0.0, min(100.0, value))
    st.markdown(
        f"""
        <div class="vero-progress-wrap">
            <div class="vero-progress-head"><span>{safe_html(label)}</span><strong>{value:.0f}</strong></div>
            <div class="vero-progress-track"><div class="vero-progress-fill" style="width:{value:.1f}%"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_csv(filename: str, required: bool = False) -> pd.DataFrame:
    path = OUTPUTS_DIR / filename
    if not path.exists():
        if required:
            st.error(f"Required data file not found: {path}")
            st.stop()
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception as exc:
        if required:
            st.error(f"Could not load {filename}: {exc}")
            st.stop()
        return pd.DataFrame()


@st.cache_resource(show_spinner=False)
def load_model() -> Any:
    path = OUTPUTS_DIR / "startup_credit_score_model.pkl"
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_yc_data() -> pd.DataFrame:
    return load_csv("yc_github_metrics.csv")


def _first_existing_column(data: pd.DataFrame, aliases: list[str]) -> str | None:
    return next((column for column in aliases if column in data.columns), None)


def _numeric_signal(data: pd.DataFrame, aliases: list[str]) -> pd.Series:
    column = _first_existing_column(data, aliases)
    if column is None:
        return pd.Series(0.0, index=data.index, dtype=float)
    return pd.to_numeric(data[column], errors="coerce").fillna(0).clip(lower=0)


def _binary_signal(data: pd.DataFrame, aliases: list[str]) -> pd.Series:
    column = _first_existing_column(data, aliases)
    if column is None:
        return pd.Series(0.0, index=data.index, dtype=float)

    values = data[column].fillna("").astype(str).str.strip().str.lower()
    truthy = {"1", "true", "yes", "y", "present", "active"}
    return values.isin(truthy).astype(float)


def _percentile_signal(values: pd.Series) -> pd.Series:
    values = pd.to_numeric(values, errors="coerce").fillna(0).clip(lower=0)
    positive = values > 0
    result = pd.Series(0.0, index=values.index, dtype=float)

    if positive.any():
        # Rank only companies with real observations. Zero or missing data stays zero.
        result.loc[positive] = values.loc[positive].rank(
            method="average",
            pct=True,
        )

    return result


def recalculate_signal_scores(data: pd.DataFrame) -> pd.DataFrame:
    """Create an evidence-aware 0-100 signal score.

    Missing Product Hunt or GitHub observations are treated as unknown rather
    than as proof that a company has no traction. Low-evidence companies are
    pulled toward a neutral score and receive a low confidence rating.
    """
    if data.empty:
        return data

    scored = data.copy()

    ph_votes_raw = _numeric_signal(scored, [
        "ph_votes", "product_hunt_votes", "votes_count", "votes",
    ])
    ph_comments_raw = _numeric_signal(scored, [
        "ph_comments", "product_hunt_comments", "comments_count", "comments",
    ])
    github_stars_raw = _numeric_signal(scored, [
        "github_total_stars", "github_stars", "stars",
    ])
    github_followers_raw = _numeric_signal(scored, [
        "github_followers", "followers",
    ])
    github_repos_raw = _numeric_signal(scored, [
        "github_public_repos", "public_repos", "repositories", "repo_count",
    ])
    github_forks_raw = _numeric_signal(scored, [
        "github_total_forks", "github_forks", "forks",
    ])

    ph_votes = _percentile_signal(ph_votes_raw)
    ph_comments = _percentile_signal(ph_comments_raw)
    github_stars = _percentile_signal(github_stars_raw)
    github_followers = _percentile_signal(github_followers_raw)
    github_repos = _percentile_signal(github_repos_raw)
    github_forks = _percentile_signal(github_forks_raw)

    hiring = _binary_signal(scored, ["isHiring", "is_hiring", "hiring", "hiring_binary"])
    yc_top = _binary_signal(scored, ["top_company", "is_top_company", "yc_top_company"])
    product_hunt = _binary_signal(scored, [
        "Product_Hunt_Present", "product_hunt_present", "has_product_hunt",
    ])
    ai_company = _binary_signal(scored, ["AI_Company", "ai_company", "is_ai"])

    description_column = _first_existing_column(scored, [
        "description_clean", "description", "short_description", "tagline",
    ])
    if description_column is None:
        description_quality = pd.Series(0.0, index=scored.index, dtype=float)
    else:
        descriptions = scored[description_column].fillna("").astype(str)
        invalid = descriptions.str.strip().str.lower().isin({"", "nan", "none", "null", "unknown"})
        lengths = descriptions.mask(invalid, "").str.len()
        description_quality = (lengths / 350).clip(lower=0, upper=1).astype(float)

    completeness_aliases = [
        ["website_clean", "website", "url"],
        ["industry_clean", "industry", "category"],
        ["business_type", "Business_Type", "business_type_inferred"],
        ["business_model", "revenue_model", "business_model_inferred"],
        ["batch", "yc_batch"],
        ["founded_year", "year_founded"],
        ["location", "city", "country"],
        ["team_size", "employee_count", "employees"],
        ["source"],
    ]
    completeness = pd.Series(0.0, index=scored.index, dtype=float)
    for aliases in completeness_aliases:
        column = _first_existing_column(scored, aliases)
        if column is None:
            continue
        values = scored[column]
        present = values.notna() & values.astype(str).str.strip().ne("")
        present &= ~values.astype(str).str.lower().isin({"nan", "none", "null", "unknown", "unclassified"})
        completeness += present.astype(float)
    completeness = (completeness / len(completeness_aliases)).clip(0, 1)

    source_column = _first_existing_column(scored, ["source"])
    if source_column is None:
        verified_source = pd.Series(0.0, index=scored.index, dtype=float)
    else:
        source_values = scored[source_column].fillna("").astype(str).str.lower()
        verified_source = source_values.str.contains(
            "yc|y combinator|techstars|500 global|product hunt|sequoia|a16z|andreessen|vc",
            regex=True,
        ).astype(float)

    external_observations = (
        (ph_votes_raw > 0).astype(int)
        + (ph_comments_raw > 0).astype(int)
        + (github_stars_raw > 0).astype(int)
        + (github_followers_raw > 0).astype(int)
        + (github_repos_raw > 0).astype(int)
        + (github_forks_raw > 0).astype(int)
    )

    # External evidence is scored only when it exists. A missing metric is not
    # silently converted into a negative signal.
    external_numerator = (
        ph_votes * 28 * (ph_votes_raw > 0)
        + ph_comments * 10 * (ph_comments_raw > 0)
        + github_stars * 28 * (github_stars_raw > 0)
        + github_followers * 12 * (github_followers_raw > 0)
        + github_repos * 12 * (github_repos_raw > 0)
        + github_forks * 10 * (github_forks_raw > 0)
    )
    external_denominator = (
        28 * (ph_votes_raw > 0).astype(float)
        + 10 * (ph_comments_raw > 0).astype(float)
        + 28 * (github_stars_raw > 0).astype(float)
        + 12 * (github_followers_raw > 0).astype(float)
        + 12 * (github_repos_raw > 0).astype(float)
        + 10 * (github_forks_raw > 0).astype(float)
    )
    external_score = (external_numerator / external_denominator.replace(0, pd.NA)).fillna(0) * 100

    # Profile evidence is a quality/completeness signal, not proof of traction.
    profile_score = (
        25
        + description_quality * 20
        + completeness * 25
        + verified_source * 12
        + hiring * 8
        + yc_top * 8
        + product_hunt * 2
    ).clip(0, 100)

    has_external = external_observations.gt(0)
    raw_score = profile_score.astype(float).copy()
    raw_score.loc[has_external] = (
        external_score.loc[has_external].astype(float) * 0.70
        + profile_score.loc[has_external].astype(float) * 0.30
    )

    confidence = (
        12
        + external_observations * 11
        + completeness * 18
        + description_quality * 10
        + verified_source * 8
    ).clip(12, 100)

    # Low-confidence records are pulled toward 50 instead of being falsely
    # presented as terrible companies. Confidence determines how far the score
    # is allowed to move away from neutral.
    confidence_factor = (confidence / 100).clip(0.15, 1.0)
    final_score = 50 + (raw_score - 50) * confidence_factor

    scored["signal_score"] = final_score.round(1).clip(0, 100)
    scored["signal_confidence"] = confidence.round(0)
    scored["signal_external_score"] = external_score.round(1)
    scored["signal_profile_score"] = profile_score.round(1)
    scored["signal_observations"] = external_observations.astype(int)
    scored["signal_basis"] = "Profile evidence only"
    scored.loc[external_observations.between(1, 2), "signal_basis"] = "Limited external evidence"
    scored.loc[external_observations.between(3, 4), "signal_basis"] = "Mixed evidence"
    scored.loc[external_observations.ge(5), "signal_basis"] = "Strong external evidence"

    return scored


@st.cache_data(show_spinner=False)
def load_graph_data() -> pd.DataFrame:
    return recalculate_signal_scores(enrich_company_classifications(load_csv("final_startup_graph.csv")))


@st.cache_data(show_spinner=False)
def load_master_data() -> pd.DataFrame:
    data = load_csv("master_startup_database_standardized.csv")
    if data.empty:
        return load_graph_data()
    return recalculate_signal_scores(enrich_company_classifications(data))


model = load_model()
yc_data = load_yc_data()

enterprise_keywords = [
    "enterprise", "business", "companies", "workflow", "automation", "saas",
    "platform", "teams", "developers", "infrastructure", "cloud", "api",
    "integration", "analytics", "security", "compliance",
]
healthcare_keywords = [
    "healthcare", "health", "hospital", "clinical", "doctor", "patient",
    "medical", "care", "diagnosis", "treatment", "pharma", "biotech", "medtech",
]
ai_keywords = [
    "artificial intelligence", "machine learning", "llm", "large language model",
    "generative ai", "computer vision", "deep learning", "neural network", "gpt",
    "ai-powered", "ai-driven", "ai assistant", "ai platform", "ai automation",
]
fintech_keywords = [
    "payments", "banking", "fintech", "financial", "credit", "loans", "mortgage",
    "insurance", "investing", "trading", "wealth", "crypto", "blockchain",
    "wallet", "transaction", "invoice", "accounting", "payroll", "tax",
]
developer_keywords = [
    "api", "sdk", "developer", "infrastructure", "cloud", "database", "deployment",
    "backend", "frontend", "devops", "container", "kubernetes", "hosting",
    "repository", "github", "code", "software engineering", "framework",
]
consumer_keywords = [
    "social", "friends", "community", "chat", "messaging", "creator", "influencer",
    "video", "photos", "music", "dating", "consumer", "users", "followers",
    "streaming", "lifestyle", "shopping", "marketplace",
]
security_keywords = [
    "security", "cybersecurity", "threat", "authentication", "encryption", "identity",
    "compliance", "vpn", "firewall", "fraud", "monitoring", "zero trust", "detection",
]
climate_keywords = [
    "climate", "carbon", "renewable", "solar", "energy", "battery", "sustainability",
    "emissions", "electric vehicle", "ev", "recycling", "clean energy",
]
education_keywords = [
    "education", "learning", "students", "teacher", "classroom", "courses",
    "tutoring", "school", "university", "curriculum", "exam", "study",
]
robotics_keywords = [
    "robotics", "robot", "hardware", "iot", "sensor", "manufacturing", "drone",
    "autonomous", "embedded", "machine vision", "industrial", "supply chain",
]
biotech_keywords = [
    "biotech", "genomics", "dna", "drug discovery", "therapeutics", "bioinformatics",
    "protein", "clinical trial", "pharmaceutical", "molecular", "biology",
]


def keyword_count(text: Any, keywords: list[str]) -> int:
    lowered = str(text).lower()
    return sum(1 for word in keywords if word.lower() in lowered)


def classify_ai(text: Any) -> str:
    return "Yes" if keyword_count(text, ai_keywords) else "No"


def classify_business_type(text: Any) -> str:
    lowered = str(text).lower()
    b2b = keyword_count(lowered, ["enterprise", "businesses", "companies", "teams", "developers", "saas", "workflow", "infrastructure", "platform"])
    b2c = keyword_count(lowered, ["consumer", "users", "shoppers", "students", "creators", "families", "personal", "social", "fitness"])
    if b2b > b2c:
        return "B2B"
    if b2c > b2b:
        return "B2C"
    return "Mixed"



INDUSTRY_TAXONOMY: dict[str, list[str]] = {
    "Artificial Intelligence": [
        "artificial intelligence", "generative ai", "machine learning", "deep learning",
        "large language model", "llm", "computer vision", "ai-powered", "ai driven",
        "ai assistant", "foundation model", "natural language processing", "nlp",
    ],
    "Healthcare": [
        "healthcare", "health care", "medical", "hospital", "patient", "clinical",
        "doctor", "physician", "telehealth", "diagnostic", "care delivery", "medtech",
    ],
    "Biotechnology": [
        "biotech", "biotechnology", "genomics", "therapeutics", "drug discovery",
        "clinical trial", "protein", "molecular", "pharmaceutical", "bioinformatics",
    ],
    "Financial Technology": [
        "fintech", "payments", "banking", "financial services", "credit", "lending",
        "loan", "mortgage", "insurance", "wealth", "investing", "payroll", "accounting",
        "invoice", "tax", "fraud", "transaction", "wallet",
    ],
    "Enterprise Software": [
        "enterprise software", "saas", "workflow", "business software", "operations",
        "crm", "erp", "productivity", "collaboration", "automation platform",
        "back office", "sales enablement", "customer support",
    ],
    "Developer Tools": [
        "developer tools", "developer platform", "api", "sdk", "devops", "database",
        "cloud infrastructure", "deployment", "observability", "kubernetes", "hosting",
        "software development", "code", "repository",
    ],
    "Cybersecurity": [
        "cybersecurity", "security", "zero trust", "authentication", "encryption",
        "identity", "threat detection", "firewall", "vpn", "compliance", "data protection",
    ],
    "Consumer": [
        "consumer app", "social network", "social media", "dating", "friends", "creator",
        "community", "messaging", "chat", "lifestyle", "personal", "mobile app",
    ],
    "E-commerce and Retail": [
        "ecommerce", "e-commerce", "online store", "retail", "shopping", "merchant",
        "commerce", "marketplace", "brands", "checkout", "direct to consumer", "d2c",
    ],
    "Education": [
        "education", "edtech", "learning", "student", "teacher", "school", "university",
        "classroom", "course", "tutoring", "curriculum", "study", "training platform",
    ],
    "Climate and Energy": [
        "climate", "clean energy", "renewable", "solar", "battery", "carbon", "emissions",
        "sustainability", "electric vehicle", "energy storage", "recycling", "grid",
    ],
    "Real Estate and Construction": [
        "real estate", "property", "construction", "housing", "homebuilder", "mortgage tech",
        "proptech", "building", "contractor", "rental", "landlord", "tenant",
    ],
    "Logistics and Supply Chain": [
        "logistics", "supply chain", "shipping", "freight", "warehouse", "delivery",
        "fleet", "transportation", "procurement", "inventory", "last mile",
    ],
    "Robotics and Hardware": [
        "robotics", "robot", "hardware", "sensor", "drone", "iot", "industrial automation",
        "autonomous vehicle", "embedded", "semiconductor", "manufacturing equipment",
    ],
    "Media and Entertainment": [
        "media", "entertainment", "music", "video", "streaming", "gaming", "game studio",
        "podcast", "content platform", "film", "sports media",
    ],
    "Food and Agriculture": [
        "food", "restaurant", "agriculture", "agtech", "farm", "crop", "grocery",
        "beverage", "kitchen", "meal", "farming",
    ],
    "Travel and Hospitality": [
        "travel", "hotel", "hospitality", "tourism", "booking", "vacation", "flight",
        "accommodation", "trip", "restaurant reservation",
    ],
    "Human Resources": [
        "human resources", "hr tech", "recruiting", "hiring", "talent", "employee",
        "workforce", "benefits", "people operations", "applicant tracking",
    ],
    "Legal Technology": [
        "legal tech", "legal", "law firm", "lawyer", "contract management", "compliance software",
        "litigation", "court", "attorney",
    ],
    "Government and Civic Technology": [
        "government", "civic", "public sector", "municipality", "federal", "defense",
        "public safety", "city government", "govtech",
    ],
}

BUSINESS_MODEL_TAXONOMY: dict[str, list[str]] = {
    "SaaS": ["saas", "software as a service", "cloud software", "subscription software", "web platform", "dashboard"],
    "Enterprise Contract": ["enterprise contract", "annual contract", "multi-year contract", "enterprise customers", "sold to enterprises", "procurement"],
    "Marketplace": ["marketplace", "connects buyers and sellers", "two-sided", "booking platform", "matching platform"],
    "Transaction Fee": ["transaction fee", "take rate", "commission", "per transaction", "payment processing fee"],
    "Usage-Based": ["usage based", "usage-based", "pay as you go", "consumption based", "per request", "metered"],
    "Subscription": ["subscription", "monthly plan", "annual plan", "membership", "recurring fee"],
    "API / Infrastructure": ["api", "sdk", "developer platform", "infrastructure platform", "api-first", "platform as a service"],
    "E-commerce": ["ecommerce", "e-commerce", "online store", "direct to consumer", "d2c", "sells products"],
    "Advertising": ["advertising", "ad-supported", "sponsored", "media buying", "ad network"],
    "Hardware Sales": ["hardware", "device", "equipment", "sensor", "robot", "manufacturing hardware"],
    "Services": ["consulting", "professional services", "agency", "managed service", "implementation services"],
    "Licensing": ["licensing", "license fee", "technology license", "royalty"],
}


def _usable_series(data: pd.DataFrame, aliases: list[str]) -> pd.Series:
    column = _first_existing_column(data, aliases)
    if column is None:
        return pd.Series("", index=data.index, dtype=str)
    values = data[column].fillna("").astype(str).str.strip()
    invalid = values.str.lower().isin({"", "nan", "none", "null", "unknown", "unclassified", "n/a"})
    return values.mask(invalid, "")


def _classification_text(data: pd.DataFrame) -> pd.Series:
    combined = pd.Series("", index=data.index, dtype=str)
    alias_groups = [
        ["name", "company_name", "startup_name"],
        ["description_clean", "description", "short_description", "tagline"],
        ["tags", "tag_list", "keywords"],
        ["industry_clean", "industry", "category", "vertical"],
        ["business_type", "Business_Type"],
    ]
    for aliases in alias_groups:
        combined = combined + " " + _usable_series(data, aliases)
    return combined.str.lower().str.replace(r"\s+", " ", regex=True).str.strip()


def _best_taxonomy_match(text: str, taxonomy: dict[str, list[str]]) -> tuple[str, float]:
    if not text:
        return "", 0.0
    scored: list[tuple[str, float]] = []
    for label, terms in taxonomy.items():
        score = 0.0
        for term in terms:
            normalized = term.lower()
            if normalized in text:
                score += 1.0 + min(1.5, 0.22 * max(0, len(normalized.split()) - 1))
        if score:
            scored.append((label, score))
    if not scored:
        return "", 0.0
    scored.sort(key=lambda item: item[1], reverse=True)
    label, top = scored[0]
    second = scored[1][1] if len(scored) > 1 else 0.0
    confidence = min(0.95, 0.42 + 0.09 * top + 0.16 * ((top - second) / top if top else 0))
    return label, round(confidence, 2)


def enrich_company_classifications(data: pd.DataFrame) -> pd.DataFrame:
    """Fill genuinely missing classifications from existing company text.

    Existing source classifications are preserved. Inferred values are clearly
    marked with method and confidence columns so VERO does not pretend that a
    keyword inference is verified source data.
    """
    if data.empty:
        return data

    enriched = data.copy()
    text = _classification_text(enriched)
    industry_results = text.apply(lambda value: _best_taxonomy_match(value, INDUSTRY_TAXONOMY))
    model_results = text.apply(lambda value: _best_taxonomy_match(value, BUSINESS_MODEL_TAXONOMY))

    inferred_industry = industry_results.map(lambda item: item[0])
    industry_confidence = industry_results.map(lambda item: item[1])
    inferred_model = model_results.map(lambda item: item[0])
    model_confidence = model_results.map(lambda item: item[1])

    existing_industry = _usable_series(enriched, ["industry_clean", "industry", "category", "vertical"])
    existing_type = _usable_series(enriched, ["business_type", "Business_Type"])

    enriched["industry_inferred"] = existing_industry.where(existing_industry.ne(""), inferred_industry)
    enriched["industry_classification_method"] = "Source data"
    missing_industry = existing_industry.eq("")
    enriched.loc[missing_industry, "industry_classification_method"] = "VERO text inference"
    enriched["industry_classification_confidence"] = 1.0
    enriched.loc[missing_industry, "industry_classification_confidence"] = industry_confidence[missing_industry]
    enriched.loc[enriched["industry_inferred"].eq(""), "industry_classification_method"] = "Insufficient evidence"

    inferred_audience = text.apply(classify_business_type)
    enriched["business_type_inferred"] = existing_type.where(existing_type.ne(""), inferred_audience)
    enriched["business_type_classification_method"] = existing_type.ne("").map({True: "Source data", False: "VERO text inference"})

    enriched["business_model_inferred"] = inferred_model
    enriched["business_model_confidence"] = model_confidence
    enriched["ai_classification_inferred"] = text.apply(classify_ai)

    # Put enriched industry into the common display/filter column without destroying originals.
    if "industry" not in enriched.columns:
        enriched["industry"] = enriched["industry_inferred"]
    else:
        current = enriched["industry"].fillna("").astype(str).str.strip()
        invalid = current.str.lower().isin({"", "nan", "none", "null", "unknown", "unclassified", "n/a"})
        enriched.loc[invalid, "industry"] = enriched.loc[invalid, "industry_inferred"]

    return enriched


def find_yc_match(name: str) -> pd.Series | None:
    if not name or yc_data.empty or "name" not in yc_data.columns:
        return None
    normalized = yc_data["name"].astype(str).str.lower().str.strip()
    target = name.lower().strip()
    exact = yc_data[normalized == target]
    if not exact.empty:
        return exact.iloc[0]
    partial = yc_data[normalized.str.contains(re.escape(target), na=False)]
    return partial.iloc[0] if not partial.empty else None


def analyze_website(url: str) -> tuple[str, str]:
    if not url:
        return "", ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        response = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        meta = soup.find("meta", attrs={"name": "description"})
        description = meta.get("content", "") if meta else ""
        text = soup.get_text(" ", strip=True)[:5000]
        blocked = ["enable javascript and cookies", "verify you are human", "cloudflare", "access denied"]
        if any(phrase in text.lower() for phrase in blocked):
            text = ""
        github_match = re.search(r"https?://github\.com/[A-Za-z0-9_.-]+", response.text)
        github_url = github_match.group(0) if github_match else ""
        return f"{title} {description} {text[:1000]}".strip(), github_url
    except requests.RequestException:
        return "", ""


FORM_DEFAULTS = {
    "description_text": "AI platform that helps hospitals automate clinical workflows",
    "ai_company": "Yes",
    "business_type": "B2B",
    "top_company": False,
    "product_hunt": "No",
    "hiring": "false",
    "startup_age": 2,
    "tag_count": 0,
    "github_followers": 0,
    "github_public_repos": 0,
    "github_total_stars": 0,
    "github_total_forks": 0,
    "score_result": None,
    "ai_research_report": None,
}
for key, value in FORM_DEFAULTS.items():
    st.session_state.setdefault(key, value)


with st.sidebar:
    st.markdown('<div class="vero-brand">VERO</div>', unsafe_allow_html=True)
    st.markdown('<div class="vero-brand-sub">Startup Intelligence Platform</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Analyze Startup",
            "Compare Startups",
            "Startup Database",
            "Startup Profile",
            "Leaderboards",
            "Model Insights",
            "About",
            "Settings",
        ],
        key="page",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("Appearance")
    selected_theme = st.selectbox(
        "Theme",
        list(THEMES),
        index=list(THEMES).index(st.session_state.theme_name),
        label_visibility="collapsed",
    )
    st.session_state.theme_name = selected_theme
    st.caption("VERO v1.0")

inject_css(THEMES[st.session_state.theme_name])


def render_overview() -> None:
    page_header(
        "Startup intelligence",
        "Make startup signals understandable.",
        "Explore companies, estimate follow-on funding potential, and compare the traction signals that shape the VERO score.",
    )

    graph = load_graph_data()
    total_startups = len(graph) if not graph.empty else len(yc_data)
    source_count = graph["source"].nunique() if not graph.empty and "source" in graph.columns else 1
    success_rate = ((yc_data.get("Raised_Next_Round", pd.Series(dtype=str)) == "Yes").mean() * 100) if not yc_data.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Startups indexed", f"{total_startups:,}", "Across the current VERO database")
    with c2:
        kpi_card("Data sources", f"{source_count:,}", "Unified into one searchable graph")
    with c3:
        kpi_card("Model ROC AUC", "0.79", "Cross-validated performance")
    with c4:
        kpi_card("Training success rate", f"{success_rate:.1f}%", "Raised a follow-on round")

    section_header("Start with a company", "Jump directly into one of VERO's core workflows.")
    left, right = st.columns([1.5, 1])
    with left:
        st.markdown('<div class="vero-card">', unsafe_allow_html=True)
        company = st.text_input("Search or analyze a startup", placeholder="Try Stripe, Airbnb, or a startup website")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Analyze startup", use_container_width=True):
                st.session_state["overview_company"] = company or "Example Startup"
                navigate_to("Analyze Startup")
        with col_b:
            if st.button("Open profile search", use_container_width=True):
                st.session_state["profile_query"] = company or "Airbnb"
                navigate_to("Startup Profile")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class="vero-card">
                <div class="vero-kpi-label">How VERO works</div>
                <div style="font-size:1.05rem;font-weight:760;margin-top:.55rem;">Evidence → Signals → Score</div>
                <div class="vero-kpi-sub" style="margin-top:.55rem;line-height:1.65;">
                    VERO combines company descriptions, YC metadata, Product Hunt activity, GitHub traction, hiring, and startup age into a single decision-support view.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not graph.empty:
        section_header("Strongest current signals", "A quick view of highly ranked companies in the graph database.")

        name_columns = ["name", "company_name", "startup_name", "organization_name"]
        score_columns = ["signal_score", "vero_score", "score", "startup_score"]
        description_columns = ["description_clean", "description", "short_description", "tagline"]
        industry_columns = ["industry", "industry_clean", "category", "sector"]

        cards: list[dict[str, Any]] = []
        seen_names: set[str] = set()

        sortable = graph.copy()
        score_column = next((column for column in score_columns if column in sortable.columns), None)
        if score_column:
            sortable["_display_score"] = pd.to_numeric(sortable[score_column], errors="coerce").fillna(0)
            sortable = sortable.sort_values("_display_score", ascending=False)

        for _, row in sortable.iterrows():
            name = clean_text(first_present(row, name_columns))
            if not valid_company_name(name):
                continue
            normalized_name = name.lower()
            if normalized_name in seen_names:
                continue

            score = first_number(row, score_columns, 0)
            industry = clean_text(first_present(row, industry_columns), "Industry unavailable")
            description = clean_text(
                first_present(row, description_columns),
                f"{name} is included in VERO's startup intelligence database."
            )
            if len(description) > 135:
                description = description[:132].rstrip() + "..."

            cards.append({
                "name": name,
                "score": score,
                "industry": industry,
                "description": description,
            })
            seen_names.add(normalized_name)
            if len(cards) == 8:
                break

        if cards:
            cols = st.columns(4)
            for index, card in enumerate(cards):
                with cols[index % 4]:
                    initials = "".join(word[0] for word in card["name"].split()[:2]).upper()
                    st.markdown(
                        f"""
                        <div class="vero-card">
                            <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.8rem;">
                                <div style="width:42px;height:42px;border-radius:12px;background:var(--vero-surface-alt);display:flex;align-items:center;justify-content:center;font-weight:850;color:var(--vero-primary);">
                                    {safe_html(initials)}
                                </div>
                                <div>
                                    <div style="font-weight:850;font-size:1rem;">{safe_html(card["name"])}</div>
                                    <span class="vero-badge">{safe_html(card["industry"])}</span>
                                </div>
                            </div>
                            <div class="vero-kpi-sub" style="min-height:58px;line-height:1.5;">{safe_html(card["description"])}</div>
                            <div style="display:flex;justify-content:space-between;align-items:end;margin-top:1rem;">
                                <span class="vero-kpi-sub">Signal score</span>
                                <strong style="font-size:1.7rem;">{card["score"]:.0f}</strong>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No clean company records were available for this section.")


def apply_yc_match(match: pd.Series) -> None:
    st.session_state.top_company = bool(match.get("top_company", False))
    st.session_state.product_hunt = "Yes" if str(match.get("Product_Hunt_Present", "No")).lower() == "yes" else "No"
    st.session_state.hiring = "true" if str(match.get("isHiring", False)).lower() == "true" else "false"
    for state_key, column in [
        ("startup_age", "startup_age"),
        ("tag_count", "tag_count"),
        ("github_followers", "github_followers"),
        ("github_public_repos", "github_public_repos"),
        ("github_total_stars", "github_total_stars"),
        ("github_total_forks", "github_total_forks"),
    ]:
        st.session_state[state_key] = int(safe_number(match.get(column, 0)))


def render_analysis_result(result: dict[str, Any]) -> None:
    profile = result.get("profile")
    vero = result.get("vero")
    company_name = clean_text(result.get("name"), "Startup")

    if profile is None or vero is None:
        st.error("The saved VERO result is incomplete. Run the analysis again.")
        return

    def readable(value: Any) -> str:
        if value in (None, ""):
            return "Not detected"
        return str(value).replace("_", " ").title()

    def evidence_items(evidence: dict[str, list[str]] | None, limit: int = 12) -> list[str]:
        items: list[str] = []
        for category, values in (evidence or {}).items():
            for value in values:
                cleaned = str(value).lstrip("+ -").strip()
                if cleaned:
                    items.append(f"{readable(category)}: {cleaned}")
                if len(items) >= limit:
                    return items
        return items

    score = safe_number(getattr(vero, "overall_score", 0))
    grade = clean_text(getattr(vero, "investment_grade", ""), "Unrated")
    components = dict(getattr(vero, "score_components", {}) or {})
    strengths = list(getattr(vero, "strengths", []) or [])
    concerns = list(getattr(vero, "concerns", []) or [])

    section_header(
        f"{company_name} — VERO assessment",
        "Deterministic scoring based on the submitted profile and any verified AI research evidence.",
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VERO score", f"{score:.1f}/100")
    c2.metric("Investment grade", grade)
    c3.metric("Business quality", f"{profile.overall_business_quality_score:.2f}/10")
    c4.metric("Risk", f"{profile.overall_risk_score:.2f}/10")

    st.info(
        f"**Why this rating:** VERO assigned **{grade}** because the weighted "
        f"components total **{score:.1f}/100**. Business quality contributed "
        f"{safe_number(components.get('business_quality')):.2f}/30, moat "
        f"{safe_number(components.get('moat')):.2f}/25, strategic signals "
        f"{safe_number(components.get('signals')):.2f}/15, risk adjustment "
        f"{safe_number(components.get('risk_adjustment')):.2f}/20, and evidence "
        f"confidence {safe_number(components.get('confidence')):.2f}/10."
    )

    section_header("Detected profile", "VERO's primary classifications from the available evidence.")
    p1, p2, p3 = st.columns(3)
    with p1:
        kpi_card("Industry", profile.primary_industry or "Not detected", profile.primary_subindustry or "No subindustry")
    with p2:
        kpi_card("Business model", profile.primary_business_model or "Not detected", f"{profile.business_model_confidence:.0%} confidence")
    with p3:
        kpi_card("Signal engine", f"{profile.overall_signal_score:.1f}/100", "Strategic evidence score")

    section_header("Score breakdown", "Each component's contribution to the final 100-point score.")
    maximums = {
        "business_quality": 30.0,
        "moat": 25.0,
        "signals": 15.0,
        "risk_adjustment": 20.0,
        "confidence": 10.0,
    }
    explanations = {
        "business_quality": f"Raw business-quality score: {profile.overall_business_quality_score:.2f}/10.",
        "moat": f"Raw moat score: {profile.overall_moat_score:.2f}/10; strongest moat: {readable(profile.strongest_moat)}.",
        "signals": f"Raw strategic-signal score: {profile.overall_signal_score:.2f}/100.",
        "risk_adjustment": f"Raw risk score: {profile.overall_risk_score:.2f}/10. Lower risk earns more points.",
        "confidence": "Rewards specific, well-supported evidence across VERO's engines.",
    }
    for key in maximums:
        value = safe_number(components.get(key))
        progress_bar(readable(key), value / maximums[key] * 100)
        st.caption(f"{value:.2f} / {maximums[key]:.0f} — {explanations[key]}")

    section_header("Decision notes", "Threshold-based strengths and concerns.")
    left, right = st.columns(2)
    with left:
        st.markdown("### Strengths")
        if strengths:
            for item in strengths:
                st.markdown(f"- {item}")
        else:
            st.info("No current strength threshold was triggered by the supplied evidence.")
    with right:
        st.markdown("### Concerns")
        if concerns:
            for item in concerns:
                st.markdown(f"- {item}")
        else:
            st.info("No current concern threshold was triggered.")

    section_header("Evidence", "Phrases used by the business-quality, moat, risk, and signal engines.")
    tabs = st.tabs(["Business quality", "Moats", "Risks", "Signals"])
    with tabs[0]:
        items = evidence_items(profile.business_quality_evidence)
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.info("No direct business-quality evidence was detected.")
    with tabs[1]:
        items = evidence_items(profile.moat_evidence)
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.info("No direct moat evidence was detected.")
    with tabs[2]:
        items = evidence_items(profile.risk_evidence)
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.info("No direct risk phrases were detected; industry baselines may still apply.")
    with tabs[3]:
        if profile.strategic_scores:
            for category, value in profile.strategic_scores.items():
                progress_bar(readable(category), safe_number(value) * 10)
                st.caption(f"{safe_number(value):.2f}/10")
        else:
            st.info("No strategic signal category received a score.")

    section_header("Competitive and risk context")
    left, right = st.columns(2)
    with left:
        st.markdown("### Likely competitors")
        if profile.competitors:
            for competitor in profile.competitors[:10]:
                st.markdown(f"- {competitor}")
        else:
            st.info("No likely competitor was identified from this evidence.")
    with right:
        st.markdown("### Largest risks")
        if profile.largest_risks:
            for risk in profile.largest_risks:
                st.markdown(f"- **{readable(risk)}:** {safe_number(profile.risk_scores.get(risk)):.2f}/10")
        else:
            st.info("No risk category crossed the major-risk threshold.")

    st.warning(
        "Missing information is treated as unknown, not automatically negative. "
        "This output is decision support, not an investment recommendation."
    )

    with st.expander("View full VERO intelligence profile"):
        st.json(profile.to_dict())
    with st.expander("View full VERO score output"):
        st.json(vero.to_dict())



def render_analyze() -> None:
    page_header(
        "Company assessment",
        "Analyze a startup.",
        "Use manual evidence, website imports, and optional live AI research. The final score remains deterministic and explainable.",
    )

    name_default = clean_text(st.session_state.get("overview_company"), "Example Startup")
    top_left, top_right = st.columns([1.2, 1])
    with top_left:
        name = st.text_input("Startup name", value=name_default, key="analysis_company_name")
    with top_right:
        website_url = st.text_input("Website URL", placeholder="https://example.com", key="analysis_website_url")

    research_col, import_col, clear_col = st.columns([2, 2, 1])
    with research_col:
        ai_research_clicked = st.button("Research with AI + live web", use_container_width=True, type="primary")
    with import_col:
        import_signals_clicked = st.button("Import website and YC signals", use_container_width=True)
    with clear_col:
        if st.button("Clear", use_container_width=True):
            st.session_state.score_result = None
            st.session_state.ai_research_report = None
            st.rerun()

    if ai_research_clicked:
        if not AI_RESEARCH_AVAILABLE:
            st.error("The VERO AI research module is missing. Copy vero/research into the project.")
        else:
            with st.spinner("Researching current public sources..."):
                try:
                    report = research_company(
                        company_name=name,
                        website_url=website_url,
                        existing_description=st.session_state.get("description_text", ""),
                    )
                    st.session_state.ai_research_report = report
                    enriched = research_to_description(report)
                    if enriched:
                        st.session_state.description_text = enriched
                    st.success(f"Research complete — {report.get('research_confidence', 0)}% evidence confidence.")
                except ResearchError as exc:
                    message = str(exc)
                    if "quota" in message.lower() or "429" in message:
                        st.warning(
                            "AI research is temporarily unavailable because the API account has no remaining quota. "
                            "Manual scoring and website/YC imports still work. Add API billing, then retry."
                        )
                    else:
                        st.error(message)

    if import_signals_clicked:
        with st.spinner("Collecting public website signals..."):
            auto_description, auto_github = analyze_website(website_url)
            if auto_description:
                st.session_state.description_text = auto_description
                st.session_state.ai_company = classify_ai(auto_description)
                st.session_state.business_type = classify_business_type(auto_description)
            yc_match = find_yc_match(name)
            if yc_match is not None:
                apply_yc_match(yc_match)
                st.success(f"Matched {yc_match.get('name', name)} in the YC dataset.")
            elif auto_description:
                st.success("Website text imported. No YC match was found.")
            else:
                st.warning("No website text or YC match was found. Manual analysis remains available.")
            if auto_github:
                st.info(f"Detected GitHub organization: {auto_github}")

    report = st.session_state.get("ai_research_report")
    if isinstance(report, dict):
        section_header("AI research evidence", "Review current external evidence before scoring.")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Research confidence", f"{report.get('research_confidence', 0)}%")
        r2.metric("Sources", len(report.get("sources", [])))
        r3.metric("Positive signals", len(report.get("positive_signals", [])))
        r4.metric("Risk signals", len(report.get("risk_signals", [])))
        if report.get("one_sentence_summary"):
            st.info(report["one_sentence_summary"])
        tabs = st.tabs(["Signals", "News", "Sources", "Missing evidence"])
        with tabs[0]:
            a, b = st.columns(2)
            with a:
                st.markdown("#### Positive")
                for item in report.get("positive_signals", []) or ["No verified positive signals found."]:
                    st.markdown(f"- {item}")
            with b:
                st.markdown("#### Risks")
                for item in report.get("risk_signals", []) or ["No verified risk signals found."]:
                    st.markdown(f"- {item}")
        with tabs[1]:
            for item in report.get("recent_news", []):
                if isinstance(item, dict):
                    st.markdown(f"**{item.get('headline', 'News item')}**")
                    st.caption(f"{item.get('date') or 'Date unavailable'} · {str(item.get('impact', 'neutral')).title()}")
                    st.write(item.get("why_it_matters", ""))
                    if item.get("source_url"):
                        st.link_button("Open source", item["source_url"])
                    st.divider()
        with tabs[2]:
            for source in report.get("sources", []):
                if isinstance(source, dict) and source.get("url"):
                    st.markdown(f"- [{source.get('title') or source['url']}]({source['url']}) — {source.get('source_type', 'other')}")
        with tabs[3]:
            for item in report.get("missing_information", []) or ["No major missing field identified."]:
                st.markdown(f"- {item}")

    section_header("Startup evidence", "Provide specific product, customer, revenue, traction, moat, and risk evidence.")
    with st.form("startup_score_form"):
        description = st.text_area("Description and evidence", key="description_text", height=230)
        left, middle, right = st.columns(3)
        with left:
            ai_company = st.selectbox("AI company", ["Yes", "No"], key="ai_company")
            business_type = st.selectbox("Business type", ["B2B", "B2C", "Mixed"], key="business_type")
            hiring = st.selectbox("Currently hiring", ["true", "false"], key="hiring")
            top_company = st.selectbox("YC top company", [False, True], key="top_company")
        with middle:
            product_hunt = st.selectbox("Product Hunt presence", ["No", "Yes"], key="product_hunt")
            startup_age = st.number_input("Startup age", min_value=0, max_value=50, key="startup_age")
            tag_count = st.number_input("Tag count", min_value=0, max_value=100, key="tag_count")
            github_followers = st.number_input("GitHub followers", min_value=0, key="github_followers")
        with right:
            github_public_repos = st.number_input("GitHub public repositories", min_value=0, key="github_public_repos")
            github_total_stars = st.number_input("GitHub total stars", min_value=0, key="github_total_stars")
            github_total_forks = st.number_input("GitHub total forks", min_value=0, key="github_total_forks")
        submitted = st.form_submit_button("Calculate VERO score", use_container_width=True)

    if submitted:
        cleaned = description.strip()
        if len(cleaned) < 25:
            st.error("Add a more detailed description before scoring.")
        else:
            metadata = (
                f"\n\nCompany metadata: business type {business_type}; AI company {ai_company}; "
                f"currently hiring {hiring}; YC top company {top_company}; Product Hunt {product_hunt}; "
                f"startup age {startup_age}; tag count {tag_count}; GitHub followers {github_followers}; "
                f"public repositories {github_public_repos}; stars {github_total_stars}; forks {github_total_forks}."
            )
            with st.spinner("Building VERO intelligence profile..."):
                try:
                    profile = build_company_profile(cleaned + metadata)
                    vero_score = analyze_vero_score(profile)
                    st.session_state.score_result = {
                        "name": name.strip() or "Unnamed startup",
                        "profile": profile,
                        "vero": vero_score,
                    }
                except Exception as exc:
                    st.error(f"VERO could not analyze this startup: {exc}")

    if st.session_state.score_result:
        render_analysis_result(st.session_state.score_result)



def fuzzy_match(data: pd.DataFrame, name: str) -> pd.Series | None:
    if data.empty or not name.strip():
        return None

    name_column = next(
        (column for column in ["name", "company_name", "startup_name", "organization_name"] if column in data.columns),
        None,
    )
    if name_column is None:
        return None

    names = data[name_column].fillna("").astype(str).str.strip()
    target = name.lower().strip()

    exact = data[names.str.lower() == target]
    candidates = exact if not exact.empty else data[names.str.lower().str.contains(re.escape(target), na=False)]
    if candidates.empty:
        return None

    # Prefer the matching record containing the most usable traction information.
    metric_aliases = [
        "signal_score", "vero_score", "score",
        "ph_votes", "product_hunt_votes", "votes_count",
        "github_total_stars", "github_stars", "stars",
        "github_followers", "followers",
    ]
    ranked = candidates.copy()
    ranked["_record_quality"] = 0.0
    for column in metric_aliases:
        if column in ranked.columns:
            ranked["_record_quality"] += pd.to_numeric(ranked[column], errors="coerce").fillna(0).gt(0).astype(float)
    return ranked.sort_values("_record_quality", ascending=False).iloc[0]


def company_signal(row: pd.Series, columns: str | list[str]) -> float:
    aliases = [columns] if isinstance(columns, str) else columns
    return max(0.0, first_number(row, aliases, 0))


def render_compare() -> None:
    page_header(
        "Side-by-side analysis",
        "Compare startups.",
        "Place two companies next to each other and see where each one leads across product, developer, and platform signals.",
    )
    master = load_master_data()
    if master.empty:
        st.warning("No comparison database is currently available.")
        return

    c1, c2 = st.columns(2)
    with c1:
        startup_1 = st.text_input("First startup", "Airbnb")
    with c2:
        startup_2 = st.text_input("Second startup", "Stripe")

    if st.button("Run comparison", use_container_width=True):
        graph = load_graph_data()

        def best_match(company_name: str) -> pd.Series | None:
            candidates = [
                match for match in (fuzzy_match(master, company_name), fuzzy_match(graph, company_name))
                if match is not None
            ]
            if not candidates:
                return None

            def quality(row: pd.Series) -> float:
                aliases = [
                    ["signal_score", "vero_score", "score"],
                    ["ph_votes", "product_hunt_votes", "votes_count"],
                    ["github_total_stars", "github_stars", "stars"],
                    ["github_followers", "followers"],
                    ["github_public_repos", "public_repos", "repositories"],
                ]
                return sum(company_signal(row, group) > 0 for group in aliases)

            return max(candidates, key=quality)

        row1, row2 = best_match(startup_1), best_match(startup_2)
        if row1 is None or row2 is None:
            missing = startup_1 if row1 is None else startup_2
            st.warning(f"No match was found for {missing}. Try a shorter company name.")
            return

        def render_company(row: pd.Series) -> None:
            name = clean_text(first_present(row, ["name", "company_name", "startup_name"]), "Unknown company")
            industry = clean_text(first_present(row, ["industry_clean", "industry", "category", "sector"]), "Industry unavailable")
            source = clean_text(first_present(row, ["source", "data_source", "platform"]), "VERO database")
            score = first_number(row, ["signal_score", "vero_score", "score", "startup_score"], 0)
            st.markdown(
                f"""
                <div class="vero-card">
                    <span class="vero-badge">{safe_html(source)}</span>
                    <div style="font-size:1.7rem;font-weight:850;margin-top:.8rem;">{safe_html(name)}</div>
                    <div class="vero-kpi-sub">{safe_html(industry)}</div>
                    <div class="vero-kpi-value" style="margin-top:1rem;">{score:.0f}</div>
                    <div class="vero-kpi-sub">Overall signal score</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        l_col, r_col = st.columns(2)
        with l_col:
            render_company(row1)
        with r_col:
            render_company(row2)

        section_header("Signal comparison", "Longer bars indicate stronger observable traction in the selected database.")
        metrics = [
            ("Product Hunt votes", ["ph_votes", "product_hunt_votes", "votes_count", "votes"]),
            ("Product Hunt comments", ["ph_comments", "product_hunt_comments", "comments_count", "comments"]),
            ("GitHub stars", ["github_total_stars", "github_stars", "stars"]),
            ("GitHub followers", ["github_followers", "followers"]),
            ("GitHub repositories", ["github_public_repos", "public_repos", "repositories", "repo_count"]),
        ]
        for label, columns in metrics:
            v1, v2 = company_signal(row1, columns), company_signal(row2, columns)
            maximum = max(v1, v2, 1)
            st.markdown(f"**{label}**")
            a, b = st.columns(2)
            with a:
                progress_bar(clean_text(first_present(row1, ["name", "company_name", "startup_name"]), startup_1), v1 / maximum * 100)
                st.caption(f"Raw value: {v1:,.0f}")
            with b:
                progress_bar(clean_text(first_present(row2, ["name", "company_name", "startup_name"]), startup_2), v2 / maximum * 100)
                st.caption(f"Raw value: {v2:,.0f}")


def render_database() -> None:
    page_header(
        "Company graph",
        "Explore the startup database.",
        "Search, filter, and inspect the unified company dataset without digging through raw CSV files.",
    )
    master = load_graph_data()
    if master.empty:
        st.warning("Outputs/final_startup_graph.csv is not available.")
        return

    f1, f2, f3 = st.columns([1.5, 1, 1])
    with f1:
        search = st.text_input("Search startups", placeholder="Name, description, industry, or source")
    with f2:
        source_values = sorted(master.get("source", pd.Series(dtype=str)).fillna("Unknown").astype(str).unique().tolist())
        source_filter = st.selectbox("Source", ["All"] + source_values)
    with f3:
        industry_values = sorted(master.get("industry", pd.Series(dtype=str)).fillna("Unknown").astype(str).unique().tolist())
        industry_filter = st.selectbox("Industry", ["All"] + industry_values)

    filtered = master.copy()
    if source_filter != "All" and "source" in filtered.columns:
        filtered = filtered[filtered["source"].astype(str) == source_filter]
    if industry_filter != "All" and "industry" in filtered.columns:
        filtered = filtered[filtered["industry"].astype(str) == industry_filter]
    if search:
        searchable = pd.Series("", index=filtered.index)
        for column in ["name", "description_clean", "industry", "source"]:
            if column in filtered.columns:
                searchable = searchable + " " + filtered[column].fillna("").astype(str)
        mask = pd.Series(True, index=filtered.index)
        for word in search.lower().split():
            mask &= searchable.str.lower().str.contains(re.escape(word), na=False)
        filtered = filtered[mask]
    if "signal_score" in filtered.columns:
        filtered = filtered.sort_values("signal_score", ascending=False)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Matching startups", f"{len(filtered):,}", "After the current filters")
    with c2:
        kpi_card("Total database", f"{len(master):,}", "All indexed records")
    with c3:
        avg = filtered["signal_score"].mean() if "signal_score" in filtered.columns and not filtered.empty else 0
        kpi_card("Average signal score", f"{avg:.1f}", "For the filtered results")

    columns = [
        "startup_id", "name", "source", "industry", "business_type_inferred",
        "business_model_inferred", "industry_classification_method", "website_clean", "ph_votes",
        "ph_comments", "github_total_stars", "github_followers", "signal_score",
    ]
    available = [column for column in columns if column in filtered.columns]
    st.dataframe(filtered[available].head(500), use_container_width=True, hide_index=True)


def render_profile() -> None:
    page_header(
        "Company intelligence",
        "Open a startup profile.",
        "Search VERO's company graph for a clean overview of traction, identity, and available evidence.",
    )

    graph = load_graph_data()
    if graph.empty or "name" not in graph.columns:
        st.warning("The startup profile database is unavailable.")
        return

    graph = graph[graph["name"].apply(valid_company_name)].copy()
    graph["name"] = graph["name"].astype(str).str.strip()

    search_col, count_col = st.columns([4, 1])
    with search_col:
        default_query = clean_text(st.session_state.get("profile_query"), "Airbnb")
        query = st.text_input(
            "Search company",
            value=default_query,
            placeholder="Search Airbnb, Stripe, FlatX...",
        )
    with count_col:
        st.metric("Companies", f"{len(graph):,}")

    if query.strip():
        exact = graph["name"].str.lower().eq(query.strip().lower())
        contains = graph["name"].str.lower().str.contains(
            re.escape(query.strip().lower()), na=False
        )
        matches = pd.concat([graph[exact], graph[contains & ~exact]]).drop_duplicates()
    else:
        matches = graph.sort_values("signal_score", ascending=False).head(100)

    if matches.empty:
        st.warning("No startup found. Try a shorter company name.")
        return

    selected_name = st.selectbox(
        "Select startup",
        matches["name"].head(100).tolist(),
        key="profile_company_selector",
    )
    row = matches[matches["name"].eq(selected_name)].iloc[0]

    company_name = clean_text(row.get("name"), "Unnamed company")
    source = clean_text(first_present(row, ["source", "dataset"]), "VERO database")
    industry = clean_text(
        first_present(row, ["industry_clean", "industry", "industry_inferred", "category", "vertical"]),
        "Industry not classified",
    )
    description = clean_text(
        first_present(row, ["description_clean", "description", "short_description", "tagline"]),
        "VERO does not yet have a company description for this record.",
    )
    website = clean_text(first_present(row, ["website_clean", "website", "url"]))
    location = clean_text(first_present(row, ["location", "city", "country"]), "Location unavailable")
    business_type = clean_text(first_present(row, ["business_type", "Business_Type", "business_type_inferred"]), "Audience not classified")
    revenue_model = clean_text(first_present(row, ["business_model", "revenue_model", "business_model_inferred"]), "Revenue model not classified")
    ai_classification = clean_text(first_present(row, ["AI_Company", "ai_company", "ai_classification_inferred"]), "Unknown")
    classification_method = clean_text(row.get("industry_classification_method"), "Source data")
    classification_confidence = safe_number(row.get("industry_classification_confidence"), 0)

    score = safe_number(row.get("signal_score"))
    confidence = safe_number(row.get("signal_confidence"), 20)
    basis = clean_text(row.get("signal_basis"), "Available evidence")

    header_left, header_right = st.columns([3, 1])
    with header_left:
        st.markdown(
            f"""
            <div class="vero-card" style="min-height:230px;">
                <span class="vero-badge">{safe_html(source)}</span>
                <div style="font-size:2.35rem;font-weight:900;margin-top:.85rem;line-height:1.05;">{safe_html(company_name)}</div>
                <div class="vero-kpi-sub" style="font-size:1rem;margin-top:.55rem;">{safe_html(industry)} · {safe_html(location)}</div>
                <div style="margin-top:1rem;line-height:1.7;max-width:900px;">{safe_html(description)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if website:
            st.link_button("Visit company website", website, use_container_width=False)

    with header_right:
        st.markdown(
            f"""
            <div class="vero-card" style="text-align:center;min-height:230px;display:flex;flex-direction:column;justify-content:center;">
                <div class="vero-kpi-label">VERO SIGNAL SCORE</div>
                <div style="font-size:3.6rem;font-weight:950;line-height:1;margin:.55rem 0;">{score:.0f}</div>
                <div class="vero-kpi-sub">out of 100</div>
                <div style="margin-top:.9rem;font-weight:750;">{safe_html(basis)}</div>
                <div class="vero-kpi-sub">{confidence:.0f}% data confidence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_header(
        "Signal snapshot",
        "Observed traction and profile evidence currently available in VERO.",
    )
    metrics = [
        ("Product Hunt votes", first_number(row, ["ph_votes", "product_hunt_votes", "votes_count"]), "Community demand"),
        ("GitHub stars", first_number(row, ["github_total_stars", "github_stars", "stars"]), "Developer interest"),
        ("GitHub followers", first_number(row, ["github_followers", "followers"]), "Organization reach"),
        ("Public repositories", first_number(row, ["github_public_repos", "public_repos", "repo_count"]), "Open-source activity"),
    ]
    cols = st.columns(4)
    for col, (label, value, subtitle) in zip(cols, metrics):
        with col:
            kpi_card(label, f"{value:,.0f}", subtitle)

    profile_tab, classification_tab, evidence_tab, raw_tab = st.tabs(["Company profile", "VERO classifications", "Score explanation", "Raw metadata"])

    with profile_tab:
        left, right = st.columns(2)
        with left:
            kpi_card("Industry", industry, classification_method)
            kpi_card("Customer type", business_type, "B2B, B2C, or mixed")
            kpi_card("Revenue model", revenue_model, "Detected monetization model")
        with right:
            founded = clean_text(first_present(row, ["founded_year", "year_founded", "batch", "yc_batch"]), "Unavailable")
            hiring = clean_text(first_present(row, ["isHiring", "is_hiring", "hiring"]), "Unknown")
            kpi_card("Founded / batch", founded, "Available timeline signal")
            kpi_card("Hiring", hiring, "Current operating signal")

    with classification_tab:
        class_cols = st.columns(3)
        with class_cols[0]:
            kpi_card("Industry", industry, f"{classification_method} · {classification_confidence:.0%} confidence" if classification_confidence else classification_method)
        with class_cols[1]:
            kpi_card("Customer type", business_type, "Inferred from customers and positioning")
        with class_cols[2]:
            kpi_card("Revenue model", revenue_model, f"AI company: {ai_classification}")

        if classification_method == "VERO text inference":
            st.info("This classification was inferred from the company's name, description, tags, and existing metadata. It is useful for discovery but is not treated as verified source data.")
        elif classification_method == "Insufficient evidence":
            st.warning("VERO still lacks enough descriptive evidence to classify this company reliably.")
        else:
            st.success("The primary industry came from an existing source record. VERO only filled the missing secondary classifications.")

    with evidence_tab:
        external_score = safe_number(row.get("signal_external_score"), 0)
        profile_score = safe_number(row.get("signal_profile_score"), 0)
        observations = int(safe_number(row.get("signal_observations"), 0))

        st.markdown("### Why this score was assigned")
        st.write(
            f"VERO currently gives **{company_name}** a signal score of "
            f"**{score:.1f}/100** with **{confidence:.0f}% confidence**. "
            "Missing metrics are treated as unknown, not as zero traction."
        )

        explain_cols = st.columns(3)
        with explain_cols[0]:
            kpi_card("External evidence", f"{external_score:.1f}/100" if observations else "Not observed", f"{observations} measured traction signals")
        with explain_cols[1]:
            kpi_card("Profile evidence", f"{profile_score:.1f}/100", "Description, source, hiring, and completeness")
        with explain_cols[2]:
            kpi_card("Confidence", f"{confidence:.0f}%", basis)

        progress_bar("Final signal score", score)
        progress_bar("Data confidence", confidence)

        reasons = []
        ph_votes_value = first_number(row, ["ph_votes", "product_hunt_votes", "votes_count"])
        github_stars_value = first_number(row, ["github_total_stars", "github_stars", "stars"])
        github_followers_value = first_number(row, ["github_followers", "followers"])
        github_repos_value = first_number(row, ["github_public_repos", "public_repos", "repo_count"])

        if observations == 0:
            reasons.append("No verified Product Hunt or GitHub traction metrics are currently stored for this company.")
        else:
            if ph_votes_value > 0:
                reasons.append(f"Product Hunt activity contributes evidence through {ph_votes_value:,.0f} recorded votes.")
            if github_stars_value > 0:
                reasons.append(f"Developer interest contributes evidence through {github_stars_value:,.0f} GitHub stars.")
            if github_followers_value > 0:
                reasons.append(f"GitHub organization reach includes {github_followers_value:,.0f} followers.")
            if github_repos_value > 0:
                reasons.append(f"Open-source activity includes {github_repos_value:,.0f} public repositories.")

        if description and "does not yet have" not in description.lower():
            reasons.append("A usable company description improved profile completeness and classification confidence.")
        if classification_method == "VERO text inference":
            reasons.append("Industry and business-model classifications were inferred from text and are not treated as verified facts.")
        if confidence < 40:
            reasons.append("Because the evidence is sparse, the score is pulled toward neutral rather than being allowed to become extremely high or low.")

        for reason in reasons:
            st.markdown(f"- {reason}")

        if confidence < 35:
            st.warning(
                "This is a low-confidence estimate. It should not be used as an investment verdict until VERO has verified traction, customer, funding, team, and financial data."
            )
        elif confidence < 60:
            st.info(
                "This is a preliminary score. More verified company evidence can materially change it."
            )
        else:
            st.success(
                "This score is supported by several stored evidence fields, though it is still not a substitute for diligence."
            )

    with raw_tab:
        metadata = {
            str(key): (None if pd.isna(value) else value)
            for key, value in row.to_dict().items()
        }
        st.json(metadata)


def render_leaderboards() -> None:
    page_header(
        "Ranked discovery",
        "Startup leaderboards.",
        "Discover companies with the strongest Product Hunt, GitHub, YC, and AI-related signals.",
    )
    master = load_master_data()
    if master.empty:
        st.warning("No leaderboard database is available.")
        return
    leaderboard_type = st.selectbox("Leaderboard", ["Top Product Hunt", "Top GitHub", "Top YC", "Top AI Startups"])
    if leaderboard_type == "Top Product Hunt":
        top = master.sort_values("ph_votes", ascending=False).head(50) if "ph_votes" in master.columns else master.head(50)
        columns = ["name", "source", "ph_votes", "ph_comments", "website_clean"]
    elif leaderboard_type == "Top GitHub":
        top = master.sort_values("github_total_stars", ascending=False).head(50) if "github_total_stars" in master.columns else master.head(50)
        columns = ["name", "github_total_stars", "github_followers", "github_public_repos"]
    elif leaderboard_type == "Top YC":
        top = master[master.get("has_yc", False) == True].head(50) if "has_yc" in master.columns else master.head(50)
        columns = ["name", "industry_clean", "website_clean"]
    else:
        descriptions = master.get("description_clean", pd.Series("", index=master.index)).astype(str).str.lower()
        ai_mask = descriptions.str.contains("artificial intelligence|machine learning|generative ai|\\bllm\\b|\\bgpt\\b", regex=True, na=False)
        top = master[ai_mask].sort_values("signal_score", ascending=False).head(50) if "signal_score" in master.columns else master[ai_mask].head(50)
        columns = ["name", "source", "ph_votes", "github_total_stars", "signal_score"]
    available = [column for column in columns if column in top.columns]
    st.dataframe(top[available], use_container_width=True, hide_index=True)


def render_model_insights() -> None:
    page_header(
        "Model transparency",
        "Understand the scoring model.",
        "See the model's current performance, dataset balance, and the signals that matter most in its predictions.",
    )
    success_rate = ((yc_data.get("Raised_Next_Round", pd.Series(dtype=str)) == "Yes").mean() * 100) if not yc_data.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Cross-validated ROC AUC", "0.79", "Average validation performance")
    with c2:
        kpi_card("Standard deviation", "0.019", "Consistency across folds")
    with c3:
        kpi_card("Observed success rate", f"{success_rate:.2f}%", "Follow-on rounds in training data")

    section_header("Key findings")
    findings = [
        ("YC top-company status", 100, "The strongest observed positive signal."),
        ("Hiring activity", 82, "A meaningful indicator of company expansion."),
        ("Enterprise orientation", 62, "Slightly stronger results in the training data."),
        ("Product Hunt presence", 35, "Useful context, but weaker alone than expected."),
        ("Basic GitHub presence", 30, "Raw presence matters less than deeper traction."),
    ]
    st.markdown('<div class="vero-card">', unsafe_allow_html=True)
    for label, value, note in findings:
        progress_bar(label, value)
        st.caption(note)
    st.markdown('</div>', unsafe_allow_html=True)

    st.info("VERO is a decision-support model, not a guarantee of funding success or investment performance.")


def render_about() -> None:
    page_header(
        "Project story",
        "About VERO.",
        "VERO is a machine-learning startup intelligence platform built to make fragmented startup data easier to understand.",
    )
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown(
            """
            <div class="vero-card">
                <div class="vero-kpi-label">The mission</div>
                <div style="font-size:1.35rem;font-weight:820;margin:.65rem 0;">Turn scattered startup evidence into a clear, explainable view.</div>
                <div class="vero-kpi-sub" style="line-height:1.75;">
                    VERO combines YC metadata, Product Hunt activity, GitHub enrichment, natural-language signals, hiring indicators, and company age. Its current model estimates whether a startup is likely to raise a follow-on funding round.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="vero-card">
                <div class="vero-kpi-label">Current stack</div>
                <div style="line-height:1.9;margin-top:.55rem;">
                    Python and pandas<br>
                    Scikit-learn model pipeline<br>
                    Streamlit product interface<br>
                    YC, Product Hunt, and GitHub signals<br>
                    Cross-validated evaluation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_settings() -> None:
    page_header(
        "Personalization",
        "Customize VERO.",
        "Choose a visual identity for the platform. The layout stays consistent while the full color system changes instantly.",
    )
    st.selectbox("Interface theme", list(THEMES), key="theme_name")
    selected = THEMES[st.session_state.theme_name]
    st.markdown("#### Theme preview")
    swatches = st.columns(5)
    for column, (label, color) in zip(swatches, [
        ("Primary", selected["primary"]),
        ("Secondary", selected["secondary"]),
        ("Background", selected["background"]),
        ("Surface", selected["surface"]),
        ("Text", selected["text"]),
    ]):
        with column:
            st.markdown(
                f'<div class="vero-card"><div style="height:58px;border-radius:11px;background:{color};border:1px solid var(--vero-border);"></div><div class="vero-kpi-sub" style="margin-top:.55rem;">{label}<br>{color}</div></div>',
                unsafe_allow_html=True,
            )
    st.caption("Theme selection is stored for the current browser session.")


PAGES = {
    "Overview": render_overview,
    "Analyze Startup": render_analyze,
    "Compare Startups": render_compare,
    "Startup Database": render_database,
    "Startup Profile": render_profile,
    "Leaderboards": render_leaderboards,
    "Model Insights": render_model_insights,
    "About": render_about,
    "Settings": render_settings,
}

PAGES[page]()