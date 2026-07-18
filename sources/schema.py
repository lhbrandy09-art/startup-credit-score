import pandas as pd

STANDARD_COLUMNS = [
    "name", "website", "description", "industry", "source", "accelerator",
    "location", "founded_year", "linkedin", "twitter", "crunchbase",
    "ph_votes", "ph_comments", "github_total_stars", "github_followers",
    "github_public_repos", "github_total_forks"
]

def normalize(df, source_name):
    df = df.copy()

    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df["source"] = df["source"].replace("", source_name).fillna(source_name)

    return df[STANDARD_COLUMNS]