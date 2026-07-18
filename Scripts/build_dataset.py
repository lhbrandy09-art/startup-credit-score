import pandas as pd

df = pd.read_csv("data/yc_companies_raw.csv")

keep_columns = [
    "name",
    "one_liner",
    "long_description",
    "team_size",
    "industry",
    "subindustry",
    "batch",
    "status",
    "stage",
    "tags",
    "industries",
    "regions",
    "isHiring",
    "top_company",
    "website",
]

clean = df[keep_columns].copy()

clean["accelerator"] = "YC"

clean.to_csv("outputs/yc_clean_dataset.csv", index=False)

print("Saved cleaned dataset to outputs/yc_clean_dataset.csv")
print("Rows:", len(clean))
