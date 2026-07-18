import pandas as pd
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

df = pd.read_csv("outputs/yc_github_enriched.csv")

def extract_github_owner(url):
    match = re.search(r"github\.com/([A-Za-z0-9_.-]+)", str(url))
    return match.group(1) if match else ""

def get_github_metrics(owner):
    if not owner:
        return owner, 0, 0, 0, 0

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        user = requests.get(
            f"https://api.github.com/users/{owner}",
            headers=headers,
            timeout=5
        )

        if user.status_code != 200:
            return owner, 0, 0, 0, 0

        user_data = user.json()

        repos = requests.get(
            f"https://api.github.com/users/{owner}/repos?per_page=100",
            headers=headers,
            timeout=5
        )

        repos_data = repos.json() if repos.status_code == 200 else []

        stars = sum(repo.get("stargazers_count", 0) for repo in repos_data)
        forks = sum(repo.get("forks_count", 0) for repo in repos_data)

        return (
            owner,
            user_data.get("followers", 0),
            user_data.get("public_repos", 0),
            stars,
            forks
        )

    except:
        return owner, 0, 0, 0, 0

df["github_owner"] = df["GitHub_URL"].fillna("").apply(extract_github_owner)

unique_owners = df["github_owner"].dropna().unique()

metrics = {}

with ThreadPoolExecutor(max_workers=30) as executor:
    futures = {
        executor.submit(get_github_metrics, owner): owner
        for owner in unique_owners
    }

    completed = 0

    for future in as_completed(futures):
        owner, followers, repos, stars, forks = future.result()

        metrics[owner] = {
            "github_followers": followers,
            "github_public_repos": repos,
            "github_total_stars": stars,
            "github_total_forks": forks
        }

        completed += 1

        if completed % 50 == 0:
            print(f"Completed {completed} GitHub owners")

df["github_followers"] = df["github_owner"].map(lambda x: metrics.get(x, {}).get("github_followers", 0))
df["github_public_repos"] = df["github_owner"].map(lambda x: metrics.get(x, {}).get("github_public_repos", 0))
df["github_total_stars"] = df["github_owner"].map(lambda x: metrics.get(x, {}).get("github_total_stars", 0))
df["github_total_forks"] = df["github_owner"].map(lambda x: metrics.get(x, {}).get("github_total_forks", 0))

df.to_csv("outputs/yc_github_metrics.csv", index=False)

print("Saved fast GitHub metrics dataset.")
