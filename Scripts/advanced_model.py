import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

df = pd.read_csv("outputs/yc_advanced_features.csv")

features = [
    "AI_Company",
    "Business_Type",
    "top_company",
    "hiring_binary",
    "startup_age",
    "description_word_count",
    "tag_count",
    "ai_keyword_count",
    "enterprise_keyword_count",
    "healthcare_keyword_count"
]

target = "Raised_Next_Round"

model_df = df[features + [target]].copy()
model_df = model_df.dropna()

model_df = pd.get_dummies(model_df)

model_df = model_df.drop(columns=[
    "Raised_Next_Round_No"
], errors="ignore")

X = model_df.drop(columns=[
    "Raised_Next_Round_Yes"
], errors="ignore")

y = model_df["Raised_Next_Round_Yes"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = LogisticRegression(max_iter=2000)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nADVANCED MODEL ACCURACY")
print(f"{accuracy * 100:.2f}%")

print("\nADVANCED FEATURE WEIGHTS")

weights = pd.DataFrame({
    "Feature": X.columns,
    "Weight": model.coef_[0]
})

print(weights.sort_values(by="Weight", ascending=False))
