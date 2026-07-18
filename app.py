import pandas as pd
import joblib
import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

# =========================
# LOAD MODEL + DATA
# =========================

model = joblib.load("outputs/startup_credit_score_model.pkl")
yc_data = pd.read_csv("outputs/yc_github_metrics.csv")

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Startup Credit Score",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SIDEBAR NAVIGATION
# =========================

page = st.sidebar.radio(
    "Navigation",
    [
        "Score a Startup",
        "Startup Database",
        "Successful Company Examples",
        "Model Insights",
        "About the Project",
        "Compare Startups",
        "Leaderboards",
        "Startup Profile"
    ]
)

# =========================
# KEYWORDS
# =========================

enterprise_keywords = [
    "enterprise", "business", "companies", "workflow", "automation",
    "saas", "platform", "teams", "developers", "infrastructure", "cloud", "api", "integration", "analytics", "security", "compliance"
]

healthcare_keywords = [
    "healthcare", "health", "hospital", "clinical", "doctor",
    "patient", "medical", "care", "diagnosis", "treatment", "pharma", "biotech", "medtech"
]

ai_keywords = [
    "artificial intelligence", "machine learning", "llm",
    "large language model", "generative ai", "computer vision",
    "deep learning", "neural network", "gpt", "AI-powered", "AI-driven",
    "AI-Voice", "AI-Video", "AI-Image", "AI-Text", "AI-Chatbot", "AI-Assistant",
    "AI-Analytics", "AI-Automation", "AI-Recommendation", "AI-Prediction", "AI-Optimization", "AI-Detection", "AI-Recognition",
    "AI-Translation", "AI-Summarization", "AI-Generation", "AI-Classification", "AI-Search", "AI-Content", "AI-Design", "AI-Creator", "AI-Data", "AI-Model", "AI-Platform", "AI-Service"
]

fintech_keywords = [
    "payments",
    "banking",
    "fintech",
    "financial",
    "credit",
    "loans",
    "mortgage",
    "insurance",
    "investing",
    "trading",
    "wealth",
    "crypto",
    "blockchain",
    "defi",
    "wallet",
    "transaction",
    "invoice",
    "accounting",
    "payroll",
    "tax"
]

developer_keywords = [
    "api",
    "sdk",
    "developer",
    "infrastructure",
    "cloud",
    "database",
    "deployment",
    "backend",
    "frontend",
    "devops",
    "terminal",
    "container",
    "kubernetes",
    "hosting",
    "repository",
    "github",
    "code",
    "software engineering",
    "framework"
]

consumer_keywords = [
    "social",
    "friends",
    "community",
    "chat",
    "messaging",
    "creator",
    "influencer",
    "video",
    "photos",
    "music",
    "dating",
    "consumer",
    "users",
    "followers",
    "streaming",
    "lifestyle",
    "shopping",
    "marketplace"
]

security_keywords = [
    "security",
    "cybersecurity",
    "threat",
    "authentication",
    "encryption",
    "identity",
    "compliance",
    "vpn",
    "firewall",
    "fraud",
    "monitoring",
    "zero trust",
    "soc",
    "detection"
]

climate_keywords = [
    "climate",
    "carbon",
    "renewable",
    "solar",
    "energy",
    "battery",
    "sustainability",
    "emissions",
    "electric vehicle",
    "ev",
    "green",
    "recycling",
    "clean energy"
]

education_keywords = [
    "education",
    "learning",
    "students",
    "teacher",
    "classroom",
    "courses",
    "tutoring",
    "school",
    "university",
    "curriculum",
    "exam",
    "study"
]

robotics_keywords = [
    "robotics",
    "robot",
    "hardware",
    "iot",
    "sensor",
    "manufacturing",
    "drone",
    "autonomous",
    "embedded",
    "machine vision",
    "industrial",
    "supply chain"
]

biotech_keywords = [
    "biotech",
    "genomics",
    "dna",
    "drug discovery",
    "therapeutics",
    "bioinformatics",
    "protein",
    "clinical trial",
    "pharmaceutical",
    "molecular",
    "biology"
]

# =========================
# FUNCTIONS
# =========================

def keyword_count(text, keywords):
    text = str(text).lower()
    return sum(1 for word in keywords if word in text)

def classify_ai(text):
    return "Yes" if keyword_count(text, ai_keywords) > 0 else "No"

def classify_fintech(text):
    return "Yes" if keyword_count(text, fintech_keywords) > 0 else "No"

def classify_developer(text):
    return "Yes" if keyword_count(text, developer_keywords) > 0 else "No"

def classify_consumer(text):
    return "Yes" if keyword_count(text, consumer_keywords) > 0 else "No"

def classify_security(text):
    return "Yes" if keyword_count(text, security_keywords) > 0 else "No"

def classify_climate(text):
    return "Yes" if keyword_count(text, climate_keywords) > 0 else "No"

def classify_education(text):
    return "Yes" if keyword_count(text, education_keywords) > 0 else "No"

def classify_robotics(text):
    return "Yes" if keyword_count(text, robotics_keywords) > 0 else "No"

def classify_biotech(text):
    return "Yes" if keyword_count(text, biotech_keywords) > 0 else "No"

def classify_business_type(text):
    text = str(text).lower()

    b2b_words = [
        "enterprise", "businesses", "companies", "teams",
        "developers", "saas", "workflow", "infrastructure", "platform"
    ]

    b2c_words = [
        "consumer", "users", "shoppers", "students",
        "creators", "families", "personal", "social", "fitness"
    ]

    b2b_score = keyword_count(text, b2b_words)
    b2c_score = keyword_count(text, b2c_words)

    if b2b_score > b2c_score:
        return "B2B"
    elif b2c_score > b2b_score:
        return "B2C"
    return "Mixed"

def find_yc_match(name):
    if not name:
        return None

    name_clean = name.lower().strip()

    yc_data["name_match"] = yc_data["name"].astype(str).str.lower().str.strip()

    exact = yc_data[yc_data["name_match"] == name_clean]

    if len(exact) > 0:
        return exact.iloc[0]

    partial = yc_data[
        yc_data["name_match"].str.contains(name_clean, case=False, na=False)
    ]

    if len(partial) > 0:
        return partial.iloc[0]

    return None

    matches = yc_data[
        yc_data["name"].astype(str).str.lower() == name.lower().strip()
    ]

    if len(matches) > 0:
        return matches.iloc[0]

    return None

def analyze_website(url):
    if not url:
        return "", ""

    if not url.startswith("http"):
        url = "https://" + url

    try:
        response = requests.get(
            url,
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else ""

        meta = soup.find("meta", attrs={"name": "description"})
        meta_description = meta["content"] if meta and meta.get("content") else ""

        text = soup.get_text(" ", strip=True)
        text = text[:5000]

        blocked_phrases = [
            "enable javascript and cookies",
            "just a moment",
            "verify you are human",
            "cloudflare",
            "access denied"
        ]

        if any(phrase in text.lower() for phrase in blocked_phrases):
            text = ""

        github_match = re.search(
            r"https?://github\.com/[A-Za-z0-9_.-]+",
            response.text
        )

        github_url = github_match.group(0) if github_match else ""

        combined = f"{title} {meta_description} {text[:1000]}"

        return combined, github_url

    except:
        return "", ""

# =========================
# SESSION STATE DEFAULTS
# =========================

defaults = {
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
    "github_total_forks": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================
# PAGE 1 — SCORE A STARTUP
# =========================

if page == "Score a Startup":

    st.title("📊 Startup Credit Score")
    st.write("Estimate a startup’s probability of raising a follow-on funding round.")

    st.subheader("Auto Website Analysis")

    website_url = st.text_input("Startup website URL", "")
    name = st.text_input("Startup name", "Example Startup")

    if st.button("Analyze Website"):

        auto_description, auto_github = analyze_website(website_url)

        if auto_description:
            st.session_state["description_text"] = auto_description
            st.session_state["ai_company"] = classify_ai(auto_description)
            st.session_state["business_type"] = classify_business_type(auto_description)
            st.success("Website analyzed successfully.")

        if auto_github:
            st.write("Detected GitHub:", auto_github)

        yc_match = find_yc_match(name)


        if yc_match is not None:

            st.session_state["top_company"] = bool(
                yc_match.get("top_company", False)
            )

            ph_value = yc_match.get(
                "Product_Hunt_Present",
                "No"
            )

            st.session_state["product_hunt"] = (
                "Yes"
                if str(ph_value).lower() == "yes"
                else "No"
            )

            hiring_value = yc_match.get(
                "isHiring",
                False
            )

            st.session_state["hiring"] = (
                "true"
                if str(hiring_value).lower() == "true"
                else "false"
            )

            if (
                "startup_age" in yc_match.index
                and pd.notna(yc_match["startup_age"])
            ):
                st.session_state["startup_age"] = int(
                    yc_match["startup_age"]
                )

            if (
                "tag_count" in yc_match.index
                and pd.notna(yc_match["tag_count"])
            ):
                st.session_state["tag_count"] = int(
                    yc_match["tag_count"]
                )

            st.session_state["github_followers"] = int(
                yc_match.get("github_followers", 0)
            )

            st.session_state["github_public_repos"] = int(
                yc_match.get("github_public_repos", 0)
            )

            st.session_state["github_total_stars"] = int(
                yc_match.get("github_total_stars", 0)
            )

            st.session_state["github_total_forks"] = int(
                yc_match.get("github_total_forks", 0)
            )

            st.success(
                f"Matched {yc_match.get('name')} in YC dataset and updated fields."
            )

            st.rerun()

        else:

            st.info(
                "No YC dataset match found."
            )

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Startup Profile")

        description = st.text_area(
            "Startup description",
            key="description_text",
            height=180
        )

        ai_company = st.selectbox(
            "AI company?",
            ["Yes", "No"],
            key="ai_company"
        )

        business_type = st.selectbox(
            "Business type",
            ["B2B", "B2C", "Mixed"],
            key="business_type"
        )

        hiring = st.selectbox(
            "Currently hiring?",
            ["true", "false"],
            key="hiring"
        )

        top_company = st.selectbox(
            "YC top company?",
            [False, True],
            key="top_company"
        )

        product_hunt = st.selectbox(
            "Product Hunt present?",
            ["No", "Yes"],
            key="product_hunt"
        )

    with right:
        st.subheader("External Signals")

        startup_age = st.number_input(
            "Startup age",
            min_value=0,
            max_value=25,
            key="startup_age"
        )

        tag_count = st.number_input(
            "Tag count",
            min_value=0,
            max_value=20,
            key="tag_count"
        )

        github_followers = st.number_input(
            "GitHub followers",
            min_value=0,
            key="github_followers"
        )

        github_public_repos = st.number_input(
            "GitHub public repos",
            min_value=0,
            key="github_public_repos"
        )

        github_total_stars = st.number_input(
            "GitHub total stars",
            min_value=0,
            key="github_total_stars"
        )

        github_total_forks = st.number_input(
            "GitHub total forks",
            min_value=0,
            key="github_total_forks"
        )

        if st.button("Calculate Startup Credit Score"):

            enterprise_count = keyword_count(description, enterprise_keywords)
            healthcare_count = keyword_count(description, healthcare_keywords)
            ai_count = keyword_count(description, ai_keywords)

            keyword_scores = {
                "AI": keyword_count(description, ai_keywords),
                "Healthcare": keyword_count(description, healthcare_keywords),
                "Fintech": keyword_count(description, fintech_keywords),
                "Developer": keyword_count(description, developer_keywords),
                "Consumer": keyword_count(description, consumer_keywords),
                "Cybersecurity": keyword_count(description, security_keywords),
                "Climate": keyword_count(description, climate_keywords),
                "Education": keyword_count(description, education_keywords),
                "Robotics": keyword_count(description, robotics_keywords),
                "Biotech": keyword_count(description, biotech_keywords)
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
                "github_total_forks": github_total_forks
            }])

            probability = model.predict_proba(startup)[0][1]
            score = round(probability * 100)

            st.divider()
            st.subheader(f"{name} — Startup Credit Score")

            col1, col2, col3 = st.columns(3)

            col1.metric("Credit Score", f"{score}/100")
            col2.metric("Follow-on Probability", f"{probability * 100:.2f}%")

            if score >= 70:
                rating = "High Potential"
            elif score >= 45:
                rating = "Moderate Potential"
            else:
                rating = "High Risk"

            col3.metric("Rating", rating)

            st.subheader("Detected Signals")

            st.write({
                "Primary Startup Sector": top_category,
                "AI keyword count": ai_count,
                "Enterprise keyword count": enterprise_count,
                "Healthcare keyword count": healthcare_count,
                "Business type": business_type,
                "AI company": ai_company,
                "Top company": top_company,
                "Product Hunt": product_hunt,
                "Hiring": hiring,
                "Startup age": startup_age,
                "Tag count": tag_count,
                "GitHub stars": github_total_stars
            })

            st.subheader("Sector Keyword Scores")
            st.write(keyword_scores)

# =========================
# PAGE 2 — STARTUP DATABASE
# =========================

elif page == "Startup Database":

    st.title("🗂 Startup Database")

    master = pd.read_csv("outputs/final_startup_graph.csv")

    st.write(f"Total startups in database: {len(master):,}")

    search = st.text_input("Search startups", "")

    source_filter = st.selectbox(
        "Source",
        ["All"] + sorted(master["source"].fillna("Unknown").astype(str).unique().tolist())
    )

    industry_filter = st.selectbox(
        "Industry",
        ["All"] + sorted(master["industry"].fillna("Unknown").astype(str).unique().tolist())
    )

    filtered = master.copy()

    if source_filter != "All":
        filtered = filtered[
            filtered["source"].astype(str) == source_filter
        ]

    if industry_filter != "All":
        filtered = filtered[
            filtered["industry"].astype(str) == industry_filter
        ]

    if search:
        search_text = (
            filtered["name"].fillna("").astype(str) + " " +
            filtered["description_clean"].fillna("").astype(str) + " " +
            filtered["industry"].fillna("").astype(str) + " " +
            filtered["source"].fillna("").astype(str)
        ).str.lower()

        words = search.lower().split()

        mask = True

        for word in words:
            mask = mask & search_text.str.contains(word, na=False)

        filtered = filtered[mask]

    if "signal_score" in filtered.columns:
        filtered = filtered.sort_values("signal_score", ascending=False)

    st.write(f"Results: {len(filtered):,}")

    columns_to_show = [
        "startup_id",
        "name",
        "source",
        "industry",
        "website_clean",
        "ph_votes",
        "ph_comments",
        "github_total_stars",
        "github_followers",
        "signal_score"
    ]

    available_columns = [
        col for col in columns_to_show
        if col in filtered.columns
    ]

    st.dataframe(
        filtered[available_columns].head(250),
        use_container_width=True
    )
# =========================
# PAGE 3 — SUCCESSFUL COMPANIES
# =========================

elif page == "Startup Profile":

    st.title("🏢 Startup Profile")

    graph = pd.read_csv("outputs/final_startup_graph.csv")

    query = st.text_input("Search startup profile", "Airbnb")

    matches = graph[
        graph["name"].astype(str).str.lower().str.contains(
            query.lower(),
            na=False
        )
    ]

    st.write(f"Matches found: {len(matches)}")

    if len(matches) > 0:

        selected_name = st.selectbox(
            "Select startup",
            matches["name"].astype(str).head(50).tolist()
        )

        row = matches[
            matches["name"].astype(str) == selected_name
        ].iloc[0]

        st.subheader(row.get("name", ""))

        col1, col2, col3 = st.columns(3)

        col1.metric("Source", row.get("source", ""))
        col2.metric("Industry", row.get("industry", ""))
        col3.metric("Signal Score", row.get("signal_score", 0))

        st.write("Website:", row.get("website_clean", ""))
        st.write("Domain:", row.get("domain_clean", ""))

        st.subheader("Description")
        description = row.get("description_clean", "")

        if pd.isna(description) or str(description).strip() == "":
            st.write("No description available.")
        else:
            st.write(description)

        st.subheader("Traction Signals")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Product Hunt Votes", row.get("ph_votes", 0))
        c2.metric("Product Hunt Comments", row.get("ph_comments", 0))
        c3.metric("GitHub Stars", row.get("github_total_stars", 0))
        c4.metric("GitHub Followers", row.get("github_followers", 0))
        c5, c6 = st.columns(2)
        c5.metric("GitHub Public Repos", row.get("github_public_repos", 0))
        c6.metric("GitHub Followers", row.get("github_followers", 0))
        st.metric("Overall Signal Score", row.get("signal_score", 0))

    else:

        st.warning("No startup found. Try a shorter search term.")


elif page == "Compare Startups":

    st.title("⚔️ Compare Startups")

    master = pd.read_csv(
        "outputs/master_startup_database_standardized.csv"
    )

    startup_1 = st.text_input(
        "Startup 1",
        "Airbnb"
    )

    startup_2 = st.text_input(
        "Startup 2",
        "Stripe"
    )

    if st.button("Compare"):

        def get_match(name):

            results = master[
                master["name"]
                .astype(str)
                .str.lower()
                .str.contains(
                    name.lower(),
                    na=False
                )
            ]

            if len(results) > 0:
                return results.iloc[0]

            return None

        row1 = get_match(startup_1)
        row2 = get_match(startup_2)

        rows = []

        for row in [row1, row2]:

            if row is not None:

                rows.append({
                    "Name": row.get("name", ""),
                    "Source": row.get("source", ""),
                    "Industry": row.get("industry_clean", ""),
                    "YC": row.get("has_yc", False),
                    "Product Hunt": row.get("has_product_hunt", False),
                    "PH Votes": row.get("ph_votes", 0),
                    "GitHub Stars": row.get("github_total_stars", 0),
                    "GitHub Followers": row.get("github_followers", 0),
                    "Description": str(
                        row.get(
                            "description_clean",
                            ""
                        )
                    )[:200]
                })

        compare_df = pd.DataFrame(rows)

        st.dataframe(compare_df)

elif page == "Leaderboards":

    st.title("🏆 Startup Leaderboards")

    master = pd.read_csv(
        "outputs/master_startup_database_standardized.csv"
    )

    leaderboard_type = st.selectbox(
        "Leaderboard Type",
        [
            "Top Product Hunt",
            "Top GitHub",
            "Top YC",
            "Top AI Startups"
        ]
    )

    if leaderboard_type == "Top Product Hunt":

        top = (
            master
            .sort_values(
                "ph_votes",
                ascending=False
            )
            .head(25)
        )

        st.subheader("🚀 Top Product Hunt Startups")

        st.dataframe(
            top[
                [
                    "name",
                    "source",
                    "ph_votes",
                    "ph_comments",
                    "website_clean"
                ]
            ]
        )

    elif leaderboard_type == "Top GitHub":

        top = (
            master
            .sort_values(
                "github_total_stars",
                ascending=False
            )
            .head(25)
        )

        st.subheader("⭐ Top GitHub Startups")

        st.dataframe(
            top[
                [
                    "name",
                    "github_total_stars",
                    "github_followers",
                    "github_public_repos"
                ]
            ]
        )

    elif leaderboard_type == "Top YC":

        top = master[
            master["has_yc"] == True
        ].head(25)

        st.subheader("🏢 YC Startups")

        st.dataframe(
            top[
                [
                    "name",
                    "industry_clean",
                    "website_clean"
                ]
            ]
        )

    elif leaderboard_type == "Top AI Startups":

        ai_terms = [
            "artificial intelligence",
            "machine learning",
            "llm",
            "gpt",
            "generative ai"
        ]

        def is_ai(text):

            text = str(text).lower()

            return any(
                term in text
                for term in ai_terms
            )

        ai_df = master[
            master["description_clean"]
            .apply(is_ai)
        ]

        ai_df = ai_df.head(25)

        st.subheader("🤖 Top AI Startups")

        st.dataframe(
            ai_df[
                [
                    "name",
                    "source",
                    "ph_votes",
                    "github_total_stars"
                ]
            ]
        )

elif page == "Successful Company Examples":

    st.title("🚀 Successful Company Examples")

    examples = yc_data[
        yc_data["Raised_Next_Round"] == "Yes"
    ][[
        "name",
        "industry",
        "Business_Type",
        "AI_Company",
        "top_company",
        "github_total_stars"
    ]].head(25)

    st.dataframe(examples)

# =========================
# PAGE 4 — MODEL INSIGHTS
# =========================

elif page == "Model Insights":

    st.title("📈 Model Insights")

    st.metric("Cross-validated ROC AUC", "0.79")
    st.metric("Standard Deviation", "0.019")

    st.write("Key model insights:")
    st.write("- YC top-company status was the strongest signal.")
    st.write("- Hiring activity strongly correlated with success.")
    st.write("- Enterprise-focused startups slightly outperformed.")
    st.write("- Simple Product Hunt and GitHub presence were weaker than expected.")

    success_rate = ((yc_data["Raised_Next_Round"] == "Yes").mean() * 100)

    st.subheader("Current Success Rate")
    st.write(f"{success_rate:.2f}% of startups in the training data raised a follow-on round.")

# =========================
# PAGE 5 — ABOUT
# =========================

elif page == "About the Project":

    st.title("🧠 About Startup Credit Score")

    st.write(
        "Startup Credit Score is a machine-learning project designed to estimate "
        "the probability that a startup will raise a follow-on funding round."
    )

    st.write("The project combines:")

    st.write("- YC startup metadata")
    st.write("- Product Hunt startup data")
    st.write("- NLP and keyword analysis")
    st.write("- GitHub enrichment")
    st.write("- Cross-validated machine learning")

    st.write("The current model achieves approximately 0.79 ROC AUC.")

from vero.collectors.website_collector import WebsiteCollector
from vero.builders.profile_builder import CompanyProfileBuilder

# We'll add these later
# from vero.collectors.github_collector import GitHubCollector
# from vero.collectors.news_collector import NewsCollector
# from vero.analyzers.ai_analyzer import AIAnalyzer


class VERO:

    def __init__(self):

        self.collectors = [

            WebsiteCollector(),

            # GitHubCollector(),
            # NewsCollector(),

        ]

        self.builder = CompanyProfileBuilder()

        # self.analyzer = AIAnalyzer()

    def run(self, company):

        print("=" * 60)
        print("VERO Startup Intelligence Platform")
        print("=" * 60)

        print()

        print(f"Researching {company}")

        print()

        # --------------------
        # Collect Evidence
        # --------------------

        for collector in self.collectors:

            collector.run(company)

        print()

        print("--------------------------")
        print("Building Company Profile")
        print("--------------------------")

        profile = self.builder.build(company)

        print("Done.")

        print()

        print("--------------------------")
        print("AI Analysis")
        print("--------------------------")

        # analysis = self.analyzer.analyze(profile)

        print("(coming soon)")

        print()

        print("==========================")
        print("VERO Complete")
        print("==========================")

        return profile


if __name__ == "__main__":

    company = input("Company: ")

    vero = VERO()

    vero.run(company)

from vero.collectors.website_collector import WebsiteCollector
from vero.collectors.github_collector import GitHubCollector
from vero.collectors.news_collector import NewsCollector

from vero.builders.profile_builder import CompanyProfileBuilder
from vero.analyzers.ai_analyzer import AIAnalyzer

from time import perf_counter


class VERO:

    def __init__(self):

        self.collectors = [

            WebsiteCollector(),

            GitHubCollector(),

            NewsCollector(),

            # FundingCollector()
            # HiringCollector()
            # CrunchbaseCollector()
            # LinkedInCollector()

        ]

        self.builder = CompanyProfileBuilder()

        self.analyzer = AIAnalyzer()

    def run(self, company):

        start = perf_counter()

        print()
        print("=" * 70)
        print("                 V E R O")
        print("        Startup Intelligence Platform")
        print("=" * 70)

        print()

        print(f"Research Target : {company}")

        print()

        print("Collecting evidence...")

        print()

        for collector in self.collectors:

            collector.run(company)

        print()

        print("Building company profile...")

        profile = self.builder.build(company)

        print("Done.")

        print()

        print("Running AI analysis...")

        analysis = self.analyzer.analyze(profile)

        print()

        elapsed = perf_counter() - start

        print("=" * 70)

        print("Research Complete")

        print()

        print(
            f"Overall Confidence : "
            f"{analysis['analysis_confidence']:.0%}"
        )

        print()

        print(
            f"Time Elapsed : "
            f"{elapsed:.1f} seconds"
        )

        print("=" * 70)

        return analysis


if __name__ == "__main__":

    company = input("Company Name: ")

    vero = VERO()

    vero.run(company)