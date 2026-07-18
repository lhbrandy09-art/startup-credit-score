import pandas as pd

df = pd.read_csv("outputs/final_startup_graph.csv")

def search_startups(query, source="All", limit=25):
    query = str(query).lower().strip()

    data = df.copy()

    if source != "All":
        data = data[
            data["source"].astype(str).str.contains(source, case=False, na=False)
        ]

    search_text = (
        data["name"].fillna("").astype(str) + " " +
        data["description_clean"].fillna("").astype(str) + " " +
        data["industry"].fillna("").astype(str)
    ).str.lower()

    words = query.split()

    mask = True

    for word in words:
        mask = mask & search_text.str.contains(word, na=False)

    results = data[mask].copy()

    if "signal_score" in results.columns:
        results = results.sort_values("signal_score", ascending=False)

    return results.head(limit)

if __name__ == "__main__":
    results = search_startups("healthcare", limit=10)

    print(results[[
        "startup_id",
        "name",
        "source",
        "industry",
        "website_clean",
        "signal_score"
    ]])