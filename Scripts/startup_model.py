import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# -----------------------------
# LOAD DATA
# -----------------------------

df = pd.read_csv("outputs/yc_feature_engineered.csv")

# -----------------------------
# SELECT FEATURES
# -----------------------------

features = [
    "AI_Company",
    "Business_Type",
    "top_company",
    "hiring_binary",
    "batch_year"
]

target = "Raised_Next_Round"

# -----------------------------
# CLEAN DATA
# -----------------------------

model_df = df[features + [target]].copy()

model_df = model_df.dropna()

# -----------------------------
# CONVERT CATEGORIES TO NUMBERS
# -----------------------------

model_df = pd.get_dummies(model_df)
# Remove leaked target columns
model_df = model_df.drop(columns=[
    "Raised_Next_Round_No"
], errors="ignore")


# -----------------------------
# SPLIT X AND Y
# -----------------------------

X = model_df.drop(columns=[
    "Raised_Next_Round_Yes"
], errors="ignore")

y = model_df["Raised_Next_Round_Yes"]

# -----------------------------
# TRAIN / TEST SPLIT
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------
# TRAIN MODEL
# -----------------------------

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

# -----------------------------
# PREDICT
# -----------------------------

predictions = model.predict(X_test)

# -----------------------------
# ACCURACY
# -----------------------------

accuracy = accuracy_score(y_test, predictions)

print("\nMODEL ACCURACY")
print(f"{accuracy * 100:.2f}%")

# -----------------------------
# FEATURE IMPORTANCE
# -----------------------------

print("\nFEATURE WEIGHTS")

weights = pd.DataFrame({
    "Feature": X.columns,
    "Weight": model.coef_[0]
})

weights = weights.sort_values(
    by="Weight",
    ascending=False
)

print(weights)
