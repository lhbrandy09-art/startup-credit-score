import pandas as pd
import joblib

model = joblib.load("outputs/startup_credit_score_model.pkl")

startup = pd.DataFrame([{
    "combined_text": "AI platform that helps hospitals automate clinical workflows",
    "AI_Company": "Yes",
    "Business_Type": "B2B",
    "top_company": False,
    "hiring_binary": "true",
    "startup_age": 2,
    "tag_count": 3,
    "enterprise_keyword_count": 3,
    "healthcare_keyword_count": 4,
    "ai_keyword_count": 2,
    "Product_Hunt_Present": "No",
    "github_followers": 0,
    "github_public_repos": 0,
    "github_total_stars": 0,
    "github_total_forks": 0
}])

probability = model.predict_proba(startup)[0][1]

score = round(probability * 100)

print("Startup Credit Score:", score)
print("Probability of raising next round:", round(probability * 100, 2), "%")
