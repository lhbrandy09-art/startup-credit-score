import requests
from bs4 import BeautifulSoup
from datetime import datetime, UTC

VC_SOURCES = [
    {
        "firm": "a16z",
        "url": "https://a16z.com/portfolio/",
    },
    {
        "firm": "Sequoia Capital",
        "url": "https://sequoiacap.com/our-companies/",
    },
    {
        "firm": "Lightspeed Venture Partners",
        "url": "https://lsvp.com/companies/",
    },
]

def scrape_vc_page(firm, url):
    print(f"Scraping {firm}: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text("\n")

    rows = []

    for line in text.split("\n"):
        name = line.strip()

        if len(name) < 2:
            continue

        if len(name) > 80:
            continue

        bad_words = [
            "portfolio",
            "companies",
            "filter",
            "apply",
            "clear",
            "category",
            "partner",
            "stage",
            "status",
            "founded",
            "backed since",
            "privacy",
            "terms",
        ]

        if any(bad in name.lower() for bad in bad_words):
            continue

        rows.append({
            "name": name,
            "source": firm,
            "source_url": url,
            "industry": "",
            "description": "",
            "website": "",
            "founded_year": "",
            "stage": "",
            "status": "",
            "investor": firm,
            "signal_score": 35,
            "ingested_at": datetime.now(UTC).isoformat()
        })

    return rows

def ingest_vc_portfolios():
    all_rows = []

    for source in VC_SOURCES:
        try:
            rows = scrape_vc_page(source["firm"], source["url"])
            all_rows.extend(rows)
            print(f"{source['firm']}: {len(rows)} raw rows")
        except Exception as e:
            print(f"Failed {source['firm']}: {e}")

    df = pd.DataFrame(all_rows)

    if df.empty:
        print("No VC portfolio rows found.")
        return df

    df = df.drop_duplicates(subset=["name", "source"])
    df = df.sort_values(["source", "name"])

    return df

if __name__ == "__main__":
    df = ingest_vc_portfolios()
    df.to_csv("data/vc_portfolio_startups.csv", index=False)
    print(f"Saved {len(df)} VC portfolio rows.")