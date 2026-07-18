import pandas as pd

df = pd.read_csv("outputs/yc_final_dataset.csv")

# ---------------------------------
# BATCH YEAR
# ---------------------------------

def extract_year(batch):
    batch = str(batch)

    if len(batch) >= 3:

        year = batch[-2:]

        if year.isdigit():
            return "20" + year

    return None

df["batch_year"] = df["batch"].apply(extract_year)

# ---------------------------------
# DESCRIPTION LENGTH
# ---------------------------------

df["description_length"] = (
    df["one_liner"]
    .fillna("")
    .apply(len)
)

# ---------------------------------
# TAG COUNT
# ---------------------------------

def count_tags(tags):
    tags = str(tags)

    if tags == "nan":
        return 0

    return len(tags.split(","))

df["tag_count"] = df["tags"].apply(count_tags)

# ---------------------------------
# HIRING BINARY
# ---------------------------------

df["hiring_binary"] = (
    df["isHiring"]
    .astype(str)
    .str.lower()
)

# ---------------------------------
# SAVE NEW DATASET
# ---------------------------------

df.to_csv(
    "outputs/yc_feature_engineered.csv",
    index=False
)

print("Feature engineered dataset saved.")

print(df[[
    "name",
    "batch",
    "batch_year",
    "description_length",
    "tag_count",
    "hiring_binary"
]].head(20))
