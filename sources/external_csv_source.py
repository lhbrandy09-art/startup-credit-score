import pandas as pd
from pathlib import Path
from sources.schema import normalize

def load():
    folder = Path("data/external_sources")
    frames = []

    for file in folder.glob("*.csv"):
        print("Loading external CSV:", file)

        df = pd.read_csv(file)

        column_map = {
            "company": "name",
            "company_name": "name",
            "startup": "name",
            "url": "website",
            "site": "website",
            "summary": "description",
            "desc": "description",
            "sector": "industry",
            "category": "industry",
            "city": "location"
        }

        df = df.rename(columns={
            col: column_map.get(col.lower().strip(), col)
            for col in df.columns
        })

        df["source"] = file.stem

        frames.append(normalize(df, file.stem))

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
    