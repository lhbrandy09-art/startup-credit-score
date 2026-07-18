import sys
from pathlib import Path
import pandas as pd
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from sources.registry import SOURCE_REGISTRY

def clean_name(name):
    name = str(name).lower().strip()

    endings = [
        " inc", " inc.", " llc", " ltd", " corp",
        " corporation", " company", " co.", " incorporated"
    ]

    for ending in endings:
        if name.endswith(ending):
            name = name.replace(ending, "")

    return name.strip()

def clean_domain(url):
    url = str(url).lower().strip()

    if url in ["", "nan", "none"]:
        return ""

    if not url.startswith("http"):
        url = "https://" + url

    try:
        domain = urlparse(url).netloc
        return domain.replace("www.", "")
    except:
        return ""

def safe_load(source):
    if not source.get("enabled", True):
        print(f"{source['name']}: disabled")
        return pd.DataFrame()

    try:
        df = source["loader"]()
        print(f"{source['name']}: {len(df)} rows")
        return df
    except Exception as e:
        print(f"{source['name']} failed: {e}")
        return pd.DataFrame()

frames = []

for source in SOURCE_REGISTRY:
    frames.append(safe_load(source))

frames = [df for df in frames if len(df) > 0]

if not frames:
    raise ValueError("No source data loaded.")

master = pd.concat(frames, ignore_index=True)

master["name_clean"] = master["name"].apply(clean_name)
master["domain_clean"] = master["website"].apply(clean_domain)
master["description_clean"] = master["description"].fillna("").astype(str).str.strip()

for col in [
    "ph_votes",
    "ph_comments",
    "github_total_stars",
    "github_followers",
    "github_public_repos",
    "github_total_forks"
]:
    master[col] = pd.to_numeric(master[col], errors="coerce").fillna(0)

master["signal_score"] = (
    master["ph_votes"].clip(0, 1000) * 1.0 +
    master["ph_comments"].clip(0, 300) * 2.0 +
    master["github_total_stars"].clip(0, 5000) * 0.2 +
    master["github_followers"].clip(0, 5000) * 0.05
)

master = master.sort_values("signal_score", ascending=False)

has_domain = master[master["domain_clean"] != ""].drop_duplicates(
    subset=["domain_clean"],
    keep="first"
)

no_domain = master[master["domain_clean"] == ""].drop_duplicates(
    subset=["name_clean"],
    keep="first"
)

final = pd.concat([has_domain, no_domain], ignore_index=True)
final = final.drop_duplicates(subset=["name_clean"], keep="first")

final["startup_id"] = range(1, len(final) + 1)

final.to_csv("outputs/final_startup_graph.csv", index=False)

print("Final startup graph saved.")
print("Rows:", len(final))
print(final[["startup_id", "name", "source", "industry", "signal_score"]].head(20))