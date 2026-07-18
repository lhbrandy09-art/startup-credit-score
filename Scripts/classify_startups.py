import pandas as pd

df = pd.read_csv("outputs/yc_clean_dataset.csv")

# AI classifier
def classify_ai(text):
    text = str(text).lower()

    ai_keywords = [
    "artificial intelligence",
    "machine learning",
    "llm",
    "large language model",
    "neural network",
    "computer vision",
    "generative ai",
    "deep learning",
    "gpt"
]

    for keyword in ai_keywords:
        if keyword in text:
            return "Yes"

    return "No"

# B2B/B2C classifier
def classify_business(industry):
    industry = str(industry).lower()

    b2b_keywords = [
        "b2b",
        "enterprise",
        "fintech",
        "developer tools",
        "security",
        "industrials"
    ]

    b2c_keywords = [
        "consumer",
        "social",
        "gaming",
        "education"
    ]

    for word in b2b_keywords:
        if word in industry:
            return "B2B"

    for word in b2c_keywords:
        if word in industry:
            return "B2C"

    return "Mixed"

# Create new columns
df["AI_Company"] = df["one_liner"].apply(classify_ai)

df["Business_Type"] = df["industry"].apply(classify_business)

# Save smarter dataset
df.to_csv("outputs/yc_classified_dataset.csv", index=False)

print("Saved classified dataset.")
print(df[[
    "name",
    "industry",
    "AI_Company",
    "Business_Type"
]].head(20))
