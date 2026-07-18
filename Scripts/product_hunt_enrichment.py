import pandas as pd
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# -----------------------------
# LOAD DATA
# -----------------------------

df = pd.read_csv("outputs/yc_advanced_features.csv")

# -----------------------------
# CLEAN NAME
# -----------------------------

def make_slug(name):
    name = str(name).lower()

    name = re.sub(r"[^a-z0-9\s-]", "", name)

    name = re.sub(r"\s+", "-", name.strip())

    return name

# -----------------------------
# CHECK PRODUCT HUNT
# -----------------------------

def check_product_hunt(name):

    slug = make_slug(name)

    urls = [
        f"https://www.producthunt.com/products/{slug}",
        f"https://www.producthunt.com/posts/{slug}"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for url in urls:

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=5
            )

            if (
                response.status_code == 200
                and "Product Hunt" in response.text
            ):

                return name, "Yes", url

        except:
            pass

    return name, "No", ""

# -----------------------------
# PARALLEL EXECUTION
# -----------------------------

results = []

with ThreadPoolExecutor(max_workers=25) as executor:

    futures = [
        executor.submit(
            check_product_hunt,
            row["name"]
        )
        for _, row in df.iterrows()
    ]

    completed = 0

    for future in as_completed(futures):

        results.append(future.result())

        completed += 1

        if completed % 100 == 0:
            print(f"Completed {completed}")

# -----------------------------
# SAVE RESULTS
# -----------------------------

results_df = pd.DataFrame(
    results,
    columns=[
        "name",
        "Product_Hunt_Present",
        "Product_Hunt_URL"
    ]
)

df = df.merge(results_df, on="name")

df.to_csv(
    "outputs/yc_product_hunt_enriched.csv",
    index=False
)

print("Finished Product Hunt enrichment.")
