import requests

url = "https://www.ycombinator.com/companies"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print("Status code:", response.status_code)

text = response.text

print("Page length:", len(text))

# Check for common hidden data markers
markers = [
    "__NEXT_DATA__",
    "companies",
    "batch",
    "slug",
    "industries"
]

for marker in markers:
    print(marker, "found?", marker in text)

# Save the raw page so we can inspect it
with open("outputs/yc_page.html", "w", encoding="utf-8") as file:
    file.write(text)

print("Saved page to outputs/yc_page.html")
