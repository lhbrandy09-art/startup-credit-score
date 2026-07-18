
def generate_investment_memo(profile: dict) -> dict:
    name = profile["company"]["name"]
    return {
        "company": name,
        "assessment": "Insufficient public evidence for a reliable investment conclusion.",
        "executive_summary": (
            f"VERO created an initial case file for {name}. "
            "More verified evidence is required before scoring the company."
        ),
        "investment_thesis": (
            "No defensible investment thesis has been established yet. "
            "The next step is collecting evidence from the company, founders, market, competitors, and funding sources."
        ),
        "pros": [],
        "cons": [
            "Major company and traction information is unknown.",
            "No verified market or competitive evidence has been collected."
        ],
        "risks": [{"name": "Information risk", "severity": "high", "reason": "The case file is incomplete."}],
        "opportunities": [],
        "questions_to_ask": [
            "What exact customer problem does the company solve?",
            "Who pays and how much?",
            "What evidence of retention exists?",
            "Why will the company win against competitors?",
            "What are burn rate and runway?"
        ],
        "missing_information": profile["unknowns"],
        "confidence": profile["data_quality"]["confidence"],
        "data_completeness": profile["data_quality"]["completeness"]
    }
