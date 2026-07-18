from pathlib import Path
import pandas as pd

SEARCH_DIRS = [
    Path("Data"),
    Path("Outputs")
]

frames = []

seen = set()

for folder in SEARCH_DIRS:

    print(f"\nScanning {folder}")

    if not folder.exists():
        continue

    for csv in folder.glob("*.csv"):

        if csv.name in seen:
            continue

        seen.add(csv.name)

        try:

            df = pd.read_csv(csv)

            if "name" not in df.columns:
                print(f"Skipping {csv.name}")
                continue

            print(f"Loaded {csv.name:<40} {len(df):>8,}")

            frames.append(df)

        except Exception as e:
            print(csv.name, e)

combined = pd.concat(frames, ignore_index=True, sort=False)

combined["name"] = combined["name"].astype(str)

combined["name_clean"] = (
    combined["name"]
    .str.lower()
    .str.strip()
)

before = len(combined)

combined = combined.drop_duplicates(subset="name_clean")

after = len(combined)

combined.to_csv(
    "Outputs/final_startup_graph.csv",
    index=False
)

print("\n==============================")
print(f"Before: {before:,}")
print(f"After : {after:,}")
print("==============================")