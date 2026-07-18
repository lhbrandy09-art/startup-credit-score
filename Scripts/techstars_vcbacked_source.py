import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.vcbacked.co/directory/investors/techstars?page={}"

headers = {
    "User-Agent": "Mozilla/5.0"
}

rows = []

for page in range(1, 101):

    url = BASE_URL.format(page)

    print(f"Fetching page {page}...")

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    print("Status:", response.status_code)

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    text = soup.get_text("\n", strip=True)

    lines = text.split("\n")

    for i, line in enumerate(lines):

        line = line.strip()

        if len(line) < 2:
            continue

        if (
            "Founder Contacts" in line
            or "Get Instant Access" in line
            or "verified contacts" in line
        ):
            continue

        if (
            line.istitle()
            and len(line.split()) <= 4
            and len(line) < 40
        ):

           rows.append({
                "name": line,
                "website": "",
                "description": "",
                "source": "Techstars / VCBacked",
                "industry": "",
                "location": "",
                "accelerator": "Techstars"
})

df = pd.DataFrame(rows)

df = df.drop_duplicates(
    subset=["name"]
)

df.to_csv(
    "outputs/techstars_vcbacked.csv",
    index=False
)

print("Saved Techstars VCBacked companies.")
print("Rows:", len(df))

print(df.head(20))
