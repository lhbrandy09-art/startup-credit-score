import pandas as pd
from sources.schema import normalize

def load():
    df = pd.read_csv("outputs/yc_github_metrics.csv")

    df["description"] = (
        df.get("one_liner", "").fillna("").astype(str) + " " +
        df.get("long_description", "").fillna("").astype(str)
    )

    df["source"] = "YC"
    df["accelerator"] = "Y Combinator"

    return normalize(df, "YC")