from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "Outputs"

st.set_page_config(
    page_title="VERO | Startup Intelligence",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
}

if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Executive"


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

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-baseweb="select"] > div {{
            border-radius: 11px !important;
            border-color: var(--vero-border) !important;
            background: var(--vero-surface) !important;
            color: var(--vero-text) !important;
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
        return pd.read_csv(path)
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


@st.cache_data(show_spinner=False)
def load_graph_data() -> pd.DataFrame:
    return load_csv("final_startup_graph.csv")


@st.cache_data(show_spinner=False)
def load_master_data() -> pd.DataFrame:
    data = load_csv("master_startup_database_standardized.csv")
    if data.empty:
        data = load_graph_data()
    return data


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
                st.session_state["overview_company"] = company
                st.info("Open **Analyze Startup** from the sidebar to score it.")
        with col_b:
            if st.button("Open profile search", use_container_width=True):
                st.session_state["profile_query"] = company or "Airbnb"
                st.info("Open **Startup Profile** from the sidebar to view matches.")
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

    if not graph.empty and "signal_score" in graph.columns and "name" in graph.columns:
        section_header("Strongest current signals", "A quick view of highly ranked companies in the graph database.")
        top = graph.sort_values("signal_score", ascending=False).head(8).copy()
        cols = st.columns(4)
        for index, (_, row) in enumerate(top.iterrows()):
            with cols[index % 4]:
                industry = row.get("industry", row.get("industry_clean", "Unknown"))
                kpi_card(str(row.get("name", "Unknown")), f"{safe_number(row.get('signal_score')):.0f}", str(industry))


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
    score = int(result["score"])
    probability = float(result["probability"])
    rating = result["rating"]
    keyword_scores = result["keyword_scores"]

    section_header("VERO assessment", "A visual summary of the current model output and detected signals.")
    left, middle, right = st.columns([0.85, 1.2, 1])
    with left:
        st.markdown(
            f"""
            <div class="vero-card" style="text-align:center;">
                <div class="vero-score-ring" style="--score:{score};">
                    <div class="vero-score-inner">
                        <div class="vero-score-number">{score}</div>
                        <div class="vero-score-label">VERO score</div>
                    </div>
                </div>
                <div style="font-size:1.05rem;font-weight:800;margin-top:1rem;">{safe_html(rating)}</div>
                <div class="vero-kpi-sub">{probability * 100:.2f}% follow-on probability</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with middle:
        st.markdown('<div class="vero-card">', unsafe_allow_html=True)
        st.markdown('<div class="vero-kpi-label">Sector signal strength</div>', unsafe_allow_html=True)
        maximum = max(max(keyword_scores.values()), 1)
        for label, value in sorted(keyword_scores.items(), key=lambda item: item[1], reverse=True)[:6]:
            progress_bar(label, value / maximum * 100)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="vero-card">', unsafe_allow_html=True)
        st.markdown('<div class="vero-kpi-label">Detected profile</div>', unsafe_allow_html=True)
        for label, value in result["signals"].items():
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--vero-border);padding:.58rem 0;"><span style="color:var(--vero-muted)">{safe_html(label)}</span><strong>{safe_html(value)}</strong></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    strengths: list[str] = []
    risks: list[str] = []
    if result["signals"]["Hiring"] == "true":
        strengths.append("The company is currently hiring, a positive expansion signal in the training data.")
    else:
        risks.append("No current hiring signal was detected.")
    if result["signals"]["YC top company"] is True:
        strengths.append("YC top-company status is one of the model's strongest positive indicators.")
    if result["signals"]["Product Hunt"] == "Yes":
        strengths.append("Product Hunt presence adds an external product-discovery signal.")
    if int(result["signals"]["GitHub stars"]) > 100:
        strengths.append("GitHub traction suggests meaningful developer interest.")
    else:
        risks.append("GitHub traction is limited or unavailable.")
    if int(result["signals"]["Startup age"]) > 8:
        risks.append("The company is older than many early-stage startups in the dataset.")
    if not strengths:
        strengths.append("The description contains enough sector and business-model information for the model to evaluate.")

    section_header("Decision notes", "Model-informed strengths and risks—not investment advice.")
    s_col, r_col = st.columns(2)
    with s_col:
        st.markdown('<div class="vero-card"><div class="vero-kpi-label">Strengths</div>', unsafe_allow_html=True)
        for item in strengths:
            st.markdown(f"**✓** {item}")
        st.markdown('</div>', unsafe_allow_html=True)
    with r_col:
        st.markdown('<div class="vero-card"><div class="vero-kpi-label">Watch items</div>', unsafe_allow_html=True)
        for item in risks or ["No major watch item was triggered by the available fields."]:
            st.markdown(f"**•** {item}")
        st.markdown('</div>', unsafe_allow_html=True)


def render_analyze() -> None:
    page_header(
        "Company assessment",
        "Analyze a startup.",
        "Import basic website signals, review the company profile, and calculate its estimated follow-on funding potential.",
    )

    name_default = st.session_state.get("overview_company", "Example Startup")
    top_left, top_right = st.columns([1.2, 1])
    with top_left:
        name = st.text_input("Startup name", value=name_default)
    with top_right:
        website_url = st.text_input("Website URL", placeholder="https://example.com")

    if st.button("Import website and YC signals", use_container_width=True):
        with st.spinner("Collecting public website signals..."):
            auto_description, auto_github = analyze_website(website_url)
            if auto_description:
                st.session_state.description_text = auto_description
                st.session_state.ai_company = classify_ai(auto_description)
                st.session_state.business_type = classify_business_type(auto_description)
            yc_match = find_yc_match(name)
            if yc_match is not None:
                apply_yc_match(yc_match)
                st.success(f"Matched {yc_match.get('name', name)} in the YC dataset and updated its signals.")
            elif auto_description:
                st.success("Website analyzed successfully. No YC match was found.")
            else:
                st.warning("VERO could not extract website text or find a YC match.")
            if auto_github:
                st.info(f"Detected GitHub organization: {auto_github}")

    section_header("Startup profile", "Review and adjust the inputs before calculating the score.")
    with st.form("startup_score_form"):
        description = st.text_area("Description", key="description_text", height=170)
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
            st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Calculate VERO score", use_container_width=True)

    if submitted:
        if model is None:
            st.error("The trained model could not be loaded from Outputs/startup_credit_score_model.pkl.")
            return
        enterprise_count = keyword_count(description, enterprise_keywords)
        healthcare_count = keyword_count(description, healthcare_keywords)
        ai_count = keyword_count(description, ai_keywords)
        keyword_scores = {
            "AI": ai_count,
            "Healthcare": healthcare_count,
            "Fintech": keyword_count(description, fintech_keywords),
            "Developer": keyword_count(description, developer_keywords),
            "Consumer": keyword_count(description, consumer_keywords),
            "Cybersecurity": keyword_count(description, security_keywords),
            "Climate": keyword_count(description, climate_keywords),
            "Education": keyword_count(description, education_keywords),
            "Robotics": keyword_count(description, robotics_keywords),
            "Biotech": keyword_count(description, biotech_keywords),
        }
        top_category = max(keyword_scores, key=keyword_scores.get)
        startup = pd.DataFrame([{
            "combined_text": description,
            "AI_Company": ai_company,
            "Business_Type": business_type,
            "top_company": top_company,
            "hiring_binary": hiring,
            "startup_age": startup_age,
            "tag_count": tag_count,
            "enterprise_keyword_count": enterprise_count,
            "healthcare_keyword_count": healthcare_count,
            "ai_keyword_count": ai_count,
            "Product_Hunt_Present": product_hunt,
            "github_followers": github_followers,
            "github_public_repos": github_public_repos,
            "github_total_stars": github_total_stars,
            "github_total_forks": github_total_forks,
        }])
        try:
            probability = float(model.predict_proba(startup)[0][1])
        except Exception as exc:
            st.error(f"The model could not score these inputs: {exc}")
            return
        score = round(probability * 100)
        rating = "High Potential" if score >= 70 else "Moderate Potential" if score >= 45 else "High Risk"
        st.session_state.score_result = {
            "name": name,
            "score": score,
            "probability": probability,
            "rating": rating,
            "keyword_scores": keyword_scores,
            "signals": {
                "Primary sector": top_category,
                "Business type": business_type,
                "AI company": ai_company,
                "YC top company": top_company,
                "Product Hunt": product_hunt,
                "Hiring": hiring,
                "Startup age": int(startup_age),
                "GitHub stars": int(github_total_stars),
            },
        }

    if st.session_state.score_result:
        render_analysis_result(st.session_state.score_result)


def fuzzy_match(data: pd.DataFrame, name: str) -> pd.Series | None:
    if data.empty or "name" not in data.columns or not name.strip():
        return None
    names = data["name"].astype(str)
    exact = data[names.str.lower().str.strip() == name.lower().strip()]
    if not exact.empty:
        return exact.iloc[0]
    partial = data[names.str.lower().str.contains(re.escape(name.lower().strip()), na=False)]
    return partial.iloc[0] if not partial.empty else None


def company_signal(row: pd.Series, column: str) -> float:
    return max(0.0, safe_number(row.get(column, 0)))


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
        row1, row2 = fuzzy_match(master, startup_1), fuzzy_match(master, startup_2)
        if row1 is None or row2 is None:
            missing = startup_1 if row1 is None else startup_2
            st.warning(f"No match was found for {missing}. Try a shorter company name.")
            return

        def render_company(row: pd.Series) -> None:
            name = row.get("name", "Unknown")
            industry = row.get("industry_clean", row.get("industry", "Unknown"))
            score = row.get("signal_score", 0)
            st.markdown(
                f"""
                <div class="vero-card">
                    <span class="vero-badge">{safe_html(row.get('source', 'Database'))}</span>
                    <div style="font-size:1.7rem;font-weight:850;margin-top:.8rem;">{safe_html(name)}</div>
                    <div class="vero-kpi-sub">{safe_html(industry)}</div>
                    <div class="vero-kpi-value" style="margin-top:1rem;">{safe_number(score):.0f}</div>
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
            ("Product Hunt votes", "ph_votes"),
            ("Product Hunt comments", "ph_comments"),
            ("GitHub stars", "github_total_stars"),
            ("GitHub followers", "github_followers"),
            ("GitHub repositories", "github_public_repos"),
        ]
        for label, column in metrics:
            v1, v2 = company_signal(row1, column), company_signal(row2, column)
            maximum = max(v1, v2, 1)
            st.markdown(f"**{label}**")
            a, b = st.columns(2)
            with a:
                progress_bar(str(row1.get("name", startup_1)), v1 / maximum * 100)
                st.caption(f"Raw value: {v1:,.0f}")
            with b:
                progress_bar(str(row2.get("name", startup_2)), v2 / maximum * 100)
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
        "startup_id", "name", "source", "industry", "website_clean", "ph_votes",
        "ph_comments", "github_total_stars", "github_followers", "signal_score",
    ]
    available = [column for column in columns if column in filtered.columns]
    st.dataframe(filtered[available].head(500), use_container_width=True, hide_index=True)


def render_profile() -> None:
    page_header(
        "Company detail",
        "Open a startup profile.",
        "Search the graph database and turn one row of raw data into a readable company overview.",
    )
    graph = load_graph_data()
    if graph.empty or "name" not in graph.columns:
        st.warning("The startup profile database is unavailable.")
        return
    default_query = st.session_state.get("profile_query", "Airbnb")
    query = st.text_input("Search company", default_query)
    matches = graph[graph["name"].astype(str).str.lower().str.contains(re.escape(query.lower()), na=False)] if query else graph.head(50)
    if matches.empty:
        st.warning("No startup found. Try a shorter search term.")
        return
    selected_name = st.selectbox("Select startup", matches["name"].astype(str).head(100).tolist())
    row = matches[matches["name"].astype(str) == selected_name].iloc[0]

    st.markdown(
        f"""
        <div class="vero-card">
            <span class="vero-badge">{safe_html(row.get('source', 'Database'))}</span>
            <div style="font-size:2rem;font-weight:880;margin-top:.7rem;">{safe_html(row.get('name', ''))}</div>
            <div class="vero-kpi-sub">{safe_html(row.get('industry', row.get('industry_clean', 'Industry unavailable')))}</div>
            <div style="margin-top:.9rem;line-height:1.65;">{safe_html(row.get('description_clean', 'No description available.'))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_header("Traction signals")
    metrics = [
        ("Signal score", row.get("signal_score", 0), "Overall graph score"),
        ("Product Hunt votes", row.get("ph_votes", 0), "Community traction"),
        ("GitHub stars", row.get("github_total_stars", 0), "Developer interest"),
        ("GitHub followers", row.get("github_followers", 0), "Organization reach"),
    ]
    cols = st.columns(4)
    for col, (label, value, subtitle) in zip(cols, metrics):
        with col:
            display = f"{safe_number(value):,.0f}"
            kpi_card(label, display, subtitle)

    with st.expander("View company metadata"):
        detail = {
            "Website": row.get("website_clean", ""),
            "Domain": row.get("domain_clean", ""),
            "Public repositories": int(safe_number(row.get("github_public_repos", 0))),
            "Product Hunt comments": int(safe_number(row.get("ph_comments", 0))),
        }
        st.json(detail)


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