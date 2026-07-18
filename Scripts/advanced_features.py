import pandas as pd

df = pd.read_csv("outputs/yc_feature_engineered.csv")

# -----------------------------
# STARTUP AGE
# -----------------------------

current_year = 2026

df["batch_year"] = pd.to_numeric(df["batch_year"], errors="coerce")
df["startup_age"] = current_year - df["batch_year"]

# -----------------------------
# TEXT PREP
# -----------------------------

df["combined_text"] = (
    df["one_liner"].fillna("") + " " +
    df["long_description"].fillna("") + " " +
    df["tags"].fillna("")
).str.lower()

df["description_word_count"] = df["combined_text"].apply(
    lambda text: len(str(text).split())
)

# -----------------------------
# KEYWORD COUNTS
# -----------------------------

ai_keywords = [
    "artificial intelligence",
    "machine learning",
    "llm",
    "large language model",
    "generative ai",
    "computer vision",
    "deep learning",
    "neural network",
    "gpt"
]

enterprise_keywords = [
    "enterprise",
    "business",
    "companies",
    "workflow",
    "automation",
    "saas",
    "platform",
    "teams",
    "developers",
    "infrastructure"
]

healthcare_keywords = [
    "healthcare",
    "health",
    "hospital",
    "clinical",
    "doctor",
    "patient",
    "medical",
    "care",
    "diagnosis"
]

def keyword_count(text, keywords):
    text = str(text)
    count = 0

    for keyword in keywords:
        if keyword in text:
            count += 1

    return count

df["ai_keyword_count"] = df["combined_text"].apply(
    lambda text: keyword_count(text, ai_keywords)
)

df["enterprise_keyword_count"] = df["combined_text"].apply(
    lambda text: keyword_count(text, enterprise_keywords)
)

df["healthcare_keyword_count"] = df["combined_text"].apply(
    lambda text: keyword_count(text, healthcare_keywords)
)

# -----------------------------
# SAVE
# -----------------------------

df.to_csv("outputs/yc_advanced_features.csv", index=False)

print("Saved advanced feature dataset.")
print(df[
    [
        "name",
        "startup_age",
        "description_word_count",
        "ai_keyword_count",
        "enterprise_keyword_count",
        "healthcare_keyword_count"
    ]
].head(20))
