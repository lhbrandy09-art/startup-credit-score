import pandas as pd

df = pd.read_csv("outputs/final_startup_graph.csv")

def enrich_startup(query):

    query = str(query).lower().strip()

    matches = df[
        df["name"]
        .astype(str)
        .str.lower()
        .str.contains(query, na=False)
    ]

    if len(matches) == 0:
        return None

    row = matches.iloc[0]

    enrichment = {
        "name": row.get("name", ""),
        "website": row.get("website_clean", ""),
        "industry": row.get("industry", ""),
        "source": row.get("source", ""),
        "description": row.get("description_clean", ""),
        "github_stars": row.get("github_total_stars", 0),
        "github_followers": row.get("github_followers", 0),
        "product_hunt_votes": row.get("ph_votes", 0),
        "signal_score": row.get("signal_score", 0),
    }

    # AI classification
    text = (
        str(enrichment["description"]) + " " +
        str(enrichment["industry"])
    ).lower()

    ai_terms = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "llm",
        "gpt",
        "neural",
        "deep learning"
    ]

    enrichment["is_ai"] = any(
        term in text
        for term in ai_terms
    )

    # Hiring signal
    hiring_terms = [
        "hiring",
        "careers",
        "join our team",
        "open roles"
    ]

    enrichment["likely_hiring"] = any(
        term in text
        for term in hiring_terms
    )

    return enrichment

if __name__ == "__main__":

    result = enrich_startup("OpenAI")

    print(result)
    