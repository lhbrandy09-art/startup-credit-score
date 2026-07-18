import pandas as pd

rows = [
    {
        "name": "Example Techstars Startup",
        "website": "",
        "description": "",
        "source": "Techstars",
        "industry": "",
        "location": "",
        "accelerator": "Techstars"
    }
]

df = pd.DataFrame(rows)
df.to_csv("outputs/techstars_startups.csv", index=False)

print("Saved Techstars startups.")
print("Rows:", len(df))
