# ai-soc-analyst
An ML pipeline that hunts compromised accounts in Microsoft Entra (Azure AD) sign-in logs.

The headline: fed ~26,000 real sign-in logs, the Isolation Forest ranked a known compromised account #4 out of the entire dataset — no rules, no labels, no hints. It found the needle on its own.
The problem

A SOC drowns in sign-in logs. Most legacy detection is hand-written rules ("flag logins from IE", "flag 3AM logins"). Rules are brittle, they go stale, and they only catch what someone already thought to write down. This project asks: can an unsupervised model catch the things the rules miss?

---------------------------------------------------------------------------------------------------------------------------
The problem:

A SOC drowns in sign-in logs. Most legacy detection is hand-written rules ("flag logins from IE", "flag 3AM logins"). Rules are brittle, they go stale, and they only catch what someone already thought to write down. This project asks: can an unsupervised model catch the things the rules miss?

The detective story:

I approached this the way I approach any bug: state the theory, collect evidence, and only fix once the evidence proves the theory. That method is also what saved this project from a bad result.

Theory: a supervised model trained on our legacy rules would just automate the SOC's existing detection.

Evidence: I trained a Random Forest on rule-derived labels — and got near-perfect F1 scores. Suspiciously perfect. The evidence didn't fit an honest model; it fit a leak.

The crime: label leakage. Training labels and test labels were both derived from the same rules. The Random Forest wasn't detecting attacks, it was memorizing the rules that generated its own answer key. The metrics were meaningless.

That failure is in this repo on purpose — training_script.py and evaluate_models.py both show the supervised setup. Catching it is the point. It reframed the whole project.

The fix: pivot to an unsupervised Isolation Forest. No labels. It learns what "normal" traffic looks like and flags the outliers. It stayed stable at ~1% anomaly rate across splits, and — the payoff — its flagged set barely overlapped the rules. It was catching genuinely different, more meaningful patterns.

What it found

The Isolation Forest surfaced 252 anomalous logins the legacy rules called safe (model_blind_spots.csv). Those are the blind spots — the compromises hiding in traffic the rules waved through. That's the case for unsupervised detection in one number.

Architecture

Two complementary paths:

Batch path — retrospective detection and validation. Clean the logs, score every login, export the ranked anomalies for review. This is what produced the #4-of-26k result.

API path real-time production scoring. An Express server takes a single login, scores it against the trained model, and if it trips the anomaly flag, routes it to an LLM analyst (Claude via LangChain) that writes an incident-response report for the engineering team.

Pipeline

users.csv + SignIns.csv
        │
        ▼
cleaning_script.py      →  ml_ready_logs.csv   (merge, temporal features, encode, drop noise)
        │
        ├─► training_script.py   →  presentation_blind_spots.csv   (supervised baseline — see "the crime")
        │
        └─► evaluate_models.py    →  model_blind_spots.csv + isolation_forest_model.pkl
                                          │
                                          ▼
                              server.js  →  spawns predict.py  →  ai_analyst.js (LLM report)

Stack


ML: Python, scikit-learn (Isolation Forest, Random Forest), pandas
API: Node.js / Express
AI analyst: Anthropic API via LangChain
Data source: Microsoft Entra sign-in logs (portal CSV export; Microsoft Graph API pull via MSAL on the roadmap)
