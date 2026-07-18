import pandas as pd

df = pd.read_csv("outputs/final_startup_graph.csv")

for col in [
    "ph_votes",
    "ph_comments",
    "github_total_stars",
    "github_followers"
]:
    if col not in df.columns:
        df[col] = 0

    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["signal_score"] = (
    df["ph_votes"].clip(0, 1000) * 1.0 +
    df["ph_comments"].clip(0, 300) * 2.0 +
    df["github_total_stars"].clip(0, 5000) * 0.2 +
    df["github_followers"].clip(0, 5000) * 0.05
)

df.to_csv("outputs/final_startup_graph.csv", index=False)

print("Signal scores recalculated.")
print(df[["name", "source", "ph_votes", "github_total_stars", "signal_score"]].sort_values(
    "signal_score",
    ascending=False
).head(20))