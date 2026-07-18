import pandas as pd
from pathlib import Path

SOURCE_FILES = [
    "outputs/yc_github_metrics.csv",
    "outputs/product_hunt_startups.csv",
    "outputs/techstars_startups.csv",
    "outputs/500global_startups.csv",
    "outputs/techstars_vcbacked.csv",
    "outputs/techstars_complete.csv"
    # Later:
    # "outputs/techstars_startups.csv",
    # "outputs/wellfound_startups.csv",
    # "outputs/github_trending_startups.csv",
    # "outputs/huggingface_startups.csv",
]

STANDARD_COLUMNS = [
    "name",
    "website",
    "description",
    "source",
    "industry",
    "location",
    "accelerator",
    "ph_votes",
    "ph_comments",
    "github_total_stars",
    "github_followers",
]

frames = []

for file in SOURCE_FILES:
    path = Path(file)

    if not path.exists():
        print(f"Missing: {file}")
        continue

    df = pd.read_csv(path)
    print(f"Loaded {file}: {len(df)} rows")

    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[STANDARD_COLUMNS]
    frames.append(df)

master = pd.concat(frames, ignore_index=True)

master["name_clean"] = master["name"].astype(str).str.lower().str.strip()
master["website_clean"] = master["website"].astype(str).str.lower().str.strip()

master = master.drop_duplicates(subset=["name_clean"], keep="first")

master.to_csv("outputs/universal_startup_database.csv", index=False)

print("Universal startup database saved.")
print("Rows:", len(master))
