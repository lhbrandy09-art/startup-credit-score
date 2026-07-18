import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://500.co/companies"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=15)

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text(" ", strip=True)

print("Page length:", len(text))
print(text[:1000])

with open("outputs/500global_page.html", "w", encoding="utf-8") as file:
    file.write(response.text)

print("Saved raw page to outputs/500global_page.html")
