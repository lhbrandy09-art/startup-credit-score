import pandas as pd
import joblib

model = joblib.load("outputs/startup_credit_score_model.pkl")
db = pd.read_csv("outputs/master_startup_database_standardized.csv")

def clean_text(value):
    return str(value).lower().strip()

def search_startups(query, limit=20):
    query = clean_text(query)

    results = db[
        db["name"].astype(str).str.lower().str.contains(query, na=False)
    ].copy()

    return results.head(limit)

def get_startup_profile(name):
    results = search_startups(name, limit=1)

    if len(results) == 0:
        return None

    row = results.iloc[0]

    profile = {
        "name": row.get("name", ""),
        "source": row.get("source", ""),
        "website": row.get("website_clean", ""),
        "industry": row.get("industry_clean", ""),
        "description": row.get("description_clean", ""),
        "product_hunt_votes": row.get("ph_votes", 0),
        "product_hunt_comments": row.get("ph_comments", 0),
        "github_stars": row.get("github_total_stars", 0),
        "github_followers": row.get("github_followers", 0),
        "github_repos": row.get("github_public_repos", 0),
        "yc": row.get("has_yc", False),
        "product_hunt": row.get("has_product_hunt", False),
    }

    return profile

def keyword_count(text, keywords):
    text = str(text).lower()
    return sum(1 for word in keywords if word in text)

ai_keywords = [
    "artificial intelligence", "machine learning", "llm",
    "large language model", "generative ai", "computer vision",
    "deep learning", "neural network", "gpt"
]

enterprise_keywords = [
    "enterprise", "business", "companies", "workflow", "automation",
    "saas", "platform", "teams", "developers", "infrastructure"
]

healthcare_keywords = [
    "healthcare", "health", "hospital", "clinical", "doctor",
    "patient", "medical", "care", "diagnosis"
]

def score_profile(profile):
    if profile is None:
        return None

    description = profile.get("description", "")

    startup = pd.DataFrame([{
        "combined_text": description,
        "AI_Company": "Yes" if keyword_count(description, ai_keywords) > 0 else "No",
        "Business_Type": "B2B",
        "top_company": bool(profile.get("yc", False)),
        "hiring_binary": "false",
        "startup_age": 2,
        "tag_count": 0,
        "enterprise_keyword_count": keyword_count(description, enterprise_keywords),
        "healthcare_keyword_count": keyword_count(description, healthcare_keywords),
        "ai_keyword_count": keyword_count(description, ai_keywords),
        "Product_Hunt_Present": "Yes" if profile.get("product_hunt", False) else "No",
        "github_followers": profile.get("github_followers", 0),
        "github_public_repos": profile.get("github_repos", 0),
        "github_total_stars": profile.get("github_stars", 0),
        "github_total_forks": 0
    }])

    probability = model.predict_proba(startup)[0][1]
    score = round(probability * 100)

    return {
        "score": score,
        "probability": round(probability * 100, 2)
    }

def compare_startups(names):
    rows = []

    for name in names:
        profile = get_startup_profile(name)
        score = score_profile(profile)

        if profile and score:
            rows.append({
                "name": profile["name"],
                "industry": profile["industry"],
                "source": profile["source"],
                "score": score["score"],
                "probability": score["probability"],
                "ph_votes": profile["product_hunt_votes"],
                "github_stars": profile["github_stars"]
            })

    return pd.DataFrame(rows).sort_values("score", ascending=False)

def rank_database(limit=50):
    sample = db.head(1000).copy()
    rows = []

    for _, row in sample.iterrows():
        profile = {
            "name": row.get("name", ""),
            "source": row.get("source", ""),
            "website": row.get("website_clean", ""),
            "industry": row.get("industry_clean", ""),
            "description": row.get("description_clean", ""),
            "product_hunt_votes": row.get("ph_votes", 0),
            "product_hunt_comments": row.get("ph_comments", 0),
            "github_stars": row.get("github_total_stars", 0),
            "github_followers": row.get("github_followers", 0),
            "github_repos": row.get("github_public_repos", 0),
            "yc": row.get("has_yc", False),
            "product_hunt": row.get("has_product_hunt", False),
        }

        score = score_profile(profile)

        if score:
            rows.append({
                "name": profile["name"],
                "industry": profile["industry"],
                "source": profile["source"],
                "score": score["score"],
                "probability": score["probability"]
            })

    return pd.DataFrame(rows).sort_values("score", ascending=False).head(limit)

if __name__ == "__main__":
    print("Backend engine loaded.")

    print("\nSearch test:")
    print(search_startups("airbnb")[["name", "source"]].head())

    print("\nProfile test:")
    print(get_startup_profile("Airbnb"))

    print("\nScore test:")
    print(score_profile(get_startup_profile("Airbnb")))

    print("\nRanking test:")
    print(rank_database(10))
    