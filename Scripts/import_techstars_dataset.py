import pandas as pd

df = pd.read_csv("data/techstars_companies.csv")

print("Rows:", len(df))
print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())
