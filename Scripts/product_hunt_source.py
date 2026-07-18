import os
import requests
import pandas as pd
import time

TOKEN = os.getenv("PRODUCT_HUNT_TOKEN")

if not TOKEN:
    raise ValueError("Missing PRODUCT_HUNT_TOKEN environment variable.")

url = "https://api.producthunt.com/v2/api/graphql"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

all_rows = []
cursor = None
page = 1
max_pages = 100

while page <= max_pages:

    after_clause = f', after: "{cursor}"' if cursor else ""

    query = f"""
    query {{
      posts(first: 100{after_clause}) {{
        pageInfo {{
          hasNextPage
          endCursor
        }}
        edges {{
          node {{
            name
            tagline
            description
            website
            votesCount
            commentsCount
            createdAt
          }}
        }}
      }}
    }}
    """

    response = requests.post(
        url,
        headers=headers,
        json={"query": query}
    )

    print("Page:", page, "Status:", response.status_code)

    data = response.json()

    if response.status_code != 200:
        print("API error:")
        print(data)
        break

    posts = data["data"]["posts"]["edges"]
    page_info = data["data"]["posts"]["pageInfo"]

    for item in posts:
        node = item["node"]

        all_rows.append({
            "name": node.get("name"),
            "website": node.get("website"),
            "description": node.get("description") or node.get("tagline"),
            "source": "Product Hunt",
            "industry": "",
            "location": "",
            "accelerator": "",
            "ph_votes": node.get("votesCount", 0),
            "ph_comments": node.get("commentsCount", 0),
            "ph_created_at": node.get("createdAt")
        })

    print("Total rows so far:", len(all_rows))

    if not page_info["hasNextPage"]:
        break

    cursor = page_info["endCursor"]
    page += 1

    time.sleep(0.5)

df = pd.DataFrame(all_rows)

df.to_csv("outputs/product_hunt_startups.csv", index=False)

print("Saved Product Hunt startups.")
print("Rows:", len(df))
print(df.head())