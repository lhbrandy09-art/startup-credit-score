import pandas as pd

df = pd.read_csv("outputs/universal_startup_database.csv")

# Clean names
df["name_clean"] = (
    df["name"]
    .astype(str)
    .str.lower()
    .str.strip()
)

# Unified description
if "description" not in df.columns:
    df["description"] = ""

for col in ["description", "one_liner", "long_description"]:
    if col not in df.columns:
        df[col] = ""

df["description_clean"] = (
    df["description"].fillna("").astype(str) + " " +
    df["one_liner"].fillna("").astype(str) + " " +
    df["long_description"].fillna("").astype(str)
).str.strip()

# Source flags
df["has_yc"] = df["source"].astype(str).str.contains("YC", case=False, na=False)
df["has_product_hunt"] = df["source"].astype(str).str.contains("Product Hunt", case=False, na=False)

# Basic signal fields
df["website_clean"] = df.get("website", "").fillna("").astype(str)
df["industry_clean"] = df.get("industry", "").fillna("").astype(str)

# Product Hunt fields
for col in ["ph_votes", "ph_comments"]:
    if col not in df.columns:
        df[col] = 0

df["ph_votes"] = pd.to_numeric(df["ph_votes"], errors="coerce").fillna(0)
df["ph_comments"] = pd.to_numeric(df["ph_comments"], errors="coerce").fillna(0)

# GitHub fields
for col in [
    "github_followers",
    "github_public_repos",
    "github_total_stars",
    "github_total_forks"
]:
    if col not in df.columns:
        df[col] = 0

    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Final dedupe
df = df.sort_values(
    by=["has_yc", "has_product_hunt", "ph_votes"],
    ascending=False
)

df = df.drop_duplicates(subset=["name_clean"], keep="first")

df.to_csv("outputs/universal_startup_database.csv", index=False)

print("Standardized master database saved.")
print("Rows:", len(df))
print(df[[
    "name",
    "source",
    "has_yc",
    "has_product_hunt",
    "website_clean",
    "ph_votes",
    "ph_comments"
]].head(20))