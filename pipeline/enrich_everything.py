import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import pandas as pd

from pipeline.enrichers.website import enrich

df = pd.read_csv("outputs/final_startup_graph.csv")

new_columns = [

    "website_title",
    "website_description",
    "linkedin",
    "github",
    "twitter"

]

for col in new_columns:

    if col not in df.columns:

        df[col] = ""

total = len(df)

for i, row in df.iterrows():

    if i % 100 == 0:

        print(i, "/", total)

    info = enrich(row["website"])

    for key, value in info.items():

        df.at[i, key] = value

df.to_csv("outputs/final_startup_graph.csv", index=False)

print("Done.")