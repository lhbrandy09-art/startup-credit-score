import pandas as pd
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

df = pd.read_csv("outputs/yc_product_hunt_enriched.csv")

def extract_github_from_text(text):
    match = re.search(r"https?://github\.com/[A-Za-z0-9_.-]+", str(text))
    return match.group(0) if match else ""

def check_website_for_github(row):
    name = row["name"]
    website = row.get("website", "")

    if pd.isna(website) or website == "":
        return name, "", "No"

    try:
        response = requests.get(
            website,
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        github_url = extract_github_from_text(response.text)

        if github_url:
            return name, github_url, "Yes"

    except:
        pass

    return name, "", "No"

results = []

with ThreadPoolExecutor(max_workers=30) as executor:
    futures = [
        executor.submit(check_website_for_github, row)
        for _, row in df.iterrows()
    ]

    completed = 0

    for future in as_completed(futures):
        results.append(future.result())
        completed += 1

        if completed % 100 == 0:
            print(f"Completed {completed}")

results_df = pd.DataFrame(
    results,
    columns=["name", "GitHub_URL", "GitHub_Present"]
)

df = df.merge(results_df, on="name", how="left")

df.to_csv("outputs/yc_github_enriched.csv", index=False)

print("Saved GitHub enriched dataset.")
print(df[["name", "website", "GitHub_Present", "GitHub_URL"]].head(20))

