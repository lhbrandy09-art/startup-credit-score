import requests
import pandas as pd

url = "https://yc-oss.github.io/api/companies/all.json"

response = requests.get(url)

print("Status code:", response.status_code)

data = response.json()

print("Number of companies:", len(data))
print("First company:")
print(data[0])

df = pd.DataFrame(data)

df.to_csv("data/yc_companies_raw.csv", index=False)

print("Saved to data/yc_companies_raw.csv")
