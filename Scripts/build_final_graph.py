import pandas as pd

df = pd.read_csv(
    "outputs/master_startup_database_deduped.csv"
)

# Basic cleanup
df = df.fillna("")

# Add universal startup ID
df["startup_id"] = range(1, len(df) + 1)

# Reorder columns
priority_columns = [
    "startup_id",
    "name",
    "source",
    "accelerator",
    "industry",
    "website_clean",
    "description_clean",
    "github_total_stars",
    "github_followers",
    "ph_votes",
    "ph_comments",
]

remaining = [
    c for c in df.columns
    if c not in priority_columns
]

df = df[
    priority_columns + remaining
]

df.to_csv(
    "outputs/final_startup_graph.csv",
    index=False
)

print("Final startup graph saved.")
print("Rows:", len(df))
print(df.head())
