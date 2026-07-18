
VERO AI Analyst
===============

Files
-----
Copy `vero/ai/ai_analyst.py` into your existing project.

What it does
------------
1. Loads a profile created by Research Agent v2.
2. Sends only the collected profile evidence to the OpenAI Responses API.
3. Requires the AI to return structured JSON.
4. Rejects source URLs that were not in the original profile.
5. Writes the thesis, bull case, bear case, pros, cons, risks,
   opportunities, missing information, and diligence questions back into the
   company profile.

PowerShell setup
----------------
Set the API key for the current PowerShell window:

    $env:OPENAI_API_KEY="YOUR_API_KEY"

Optional model override:

    $env:VERO_AI_MODEL="gpt-5-mini"

Run
---
From the startup-credit-score folder:

    python -m vero.ai.ai_analyst "vero\data\companies\stripe_profile.json"

To preserve the original profile:

    python -m vero.ai.ai_analyst `
      "vero\data\companies\stripe_profile.json" `
      --output "vero\data\companies\stripe_analyzed.json" `
      --analysis-output "vero\data\companies\stripe_ai_analysis.json"

Security
--------
Never paste an API key into a Python file or commit it to GitHub.
