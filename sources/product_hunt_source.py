import os
import time
import requests
import pandas as pd
from sources.schema import normalize

def load(max_pages=50):
    token = os.getenv("PRODUCT_HUNT_TOKEN")

    if not token:
        print("Missing PRODUCT_HUNT_TOKEN. Skipping Product Hunt.")
        return pd.DataFrame()

    url = "https://api.producthunt.com/v2/api/graphql"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    rows = []
    cursor = None

    for page in range(1, max_pages + 1):
        after = f', after: "{cursor}"' if cursor else ""

        query = f"""
        query {{
          posts(first: 100{after}) {{
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

        response = requests.post(url, headers=headers, json={"query": query})
        print("Product Hunt page:", page, "status:", response.status_code)

        data = response.json()

        if response.status_code != 200:
            print(data)
            break

        posts = data["data"]["posts"]["edges"]
        page_info = data["data"]["posts"]["pageInfo"]

        for item in posts:
            node = item["node"]

            rows.append({
                "name": node.get("name", ""),
                "website": node.get("website", ""),
                "description": node.get("description") or node.get("tagline", ""),
                "source": "Product Hunt",
                "industry": "",
                "location": "",
                "accelerator": "",
                "ph_votes": node.get("votesCount", 0),
                "ph_comments": node.get("commentsCount", 0)
            })

        if not page_info["hasNextPage"]:
            break

        cursor = page_info["endCursor"]
        time.sleep(0.5)

    df = pd.DataFrame(rows)
    return normalize(df, "Product Hunt")