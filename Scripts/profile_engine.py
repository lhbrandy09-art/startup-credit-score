import pandas as pd

df = pd.read_csv("outputs/final_startup_graph.csv")

def get_profile(query):
    query = str(query).lower().strip()

    matches = df[
        df["name"].astype(str).str.lower().str.contains(query, na=False)
    ]

    if len(matches) == 0:
        return None

    row = matches.iloc[0]

    profile = {
        "startup_id": row.get("startup_id", ""),
        "name": row.get("name", ""),
        "source": row.get("source", ""),
        "website": row.get("website_clean", ""),
        "industry": row.get("industry", ""),
        "description": row.get("description_clean", ""),
        "domain": row.get("domain_clean", ""),
        "product_hunt_votes": row.get("ph_votes", 0),
        "product_hunt_comments": row.get("ph_comments", 0),
        "github_stars": row.get("github_total_stars", 0),
        "github_followers": row.get("github_followers", 0),
        "signal_score": row.get("signal_score", 0),
    }

    return profile

if __name__ == "__main__":
    profile = get_profile("Airbnb")
    print(profile)