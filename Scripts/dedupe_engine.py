import pandas as pd
from urllib.parse import urlparse

df = pd.read_csv("outputs/universal_startup_database.csv")

def clean_name(name):
    name = str(name).lower().strip()

    endings = [
        " inc",
        " inc.",
        " llc",
        " ltd",
        " corp",
        " corporation",
        " company",
        " co."
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
        domain = domain.replace("www.", "")
        return domain
    except:
        return ""

df["name_clean"] = df["name"].apply(clean_name)
df["domain_clean"] = df["website_clean"].apply(clean_domain)

# Prefer rows with more signal
df["signal_score"] = (
    df.get("has_yc", False).astype(int) * 5 +
    df.get("has_product_hunt", False).astype(int) * 3 +
    df.get("ph_votes", 0).fillna(0) +
    df.get("github_total_stars", 0).fillna(0)
)

df = df.sort_values("signal_score", ascending=False)

# First dedupe by domain when available
has_domain = df[df["domain_clean"] != ""]
no_domain = df[df["domain_clean"] == ""]

has_domain = has_domain.drop_duplicates(
    subset=["domain_clean"],
    keep="first"
)

# Then dedupe no-domain rows by clean name
no_domain = no_domain.drop_duplicates(
    subset=["name_clean"],
    keep="first"
)

final = pd.concat([has_domain, no_domain], ignore_index=True)

final = final.drop_duplicates(
    subset=["name_clean"],
    keep="first"
)

final.to_csv("outputs/master_startup_database_deduped.csv", index=False)

print("Before:", len(df))
print("After:", len(final))
print("Saved deduped master database.")
