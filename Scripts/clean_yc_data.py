import pandas as pd

df = pd.read_csv("data/yc_companies_raw.csv")

print("Columns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

# Save preview file
df.head(100).to_csv("outputs/yc_preview_100.csv", index=False)

print("\nSaved preview to outputs/yc_preview_100.csv")
