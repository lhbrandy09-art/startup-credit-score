from pathlib import Path

html = Path("outputs/500global_page.html").read_text(encoding="utf-8")

keywords = [
    "__NEXT_DATA__",
    "company",
    "companies",
    "portfolio",
    "airtable",
    "graphql",
    "api",
    "json"
]

for word in keywords:
    print(word, word.lower() in html.lower())

print("\nFirst links:")
import re
links = re.findall(r'https?://[^"\']+', html)
for link in links[:30]:
    print(link)
    