import pandas as pd

df = pd.read_csv("outputs/final_startup_graph.csv")

df["source"] = df["source"].fillna("").astype(str)

df.loc[df["source"].str.strip() == "", "source"] = "Unknown / Imported"

df.to_csv("outputs/final_startup_graph.csv", index=False)

print("Fixed final startup graph.")
print("Rows:", len(df))
print(df[["startup_id", "name", "source"]].head(20))
