# RozgarCheck v0.2 — Phase 1 Setup Guide

## What's in this folder
- `app.py` — Streamlit UI
- `detector.py` — hybrid detection engine (rule-based + semantic similarity, explainability, audit logging)
- `exemplars.py` — exemplar phrase bank per bias category (edit/expand this over time)
- `benchmark_dataset.csv` — 30-row starter labeled dataset (expand to 500+ before quoting accuracy numbers externally)
- `evaluate.py` — computes precision/recall/F1 against the benchmark
- `requirements.txt` — dependencies

## Setup (run on your own machine, not this sandbox)

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

First run will download the `all-MiniLM-L6-v2` model (~80MB) from Hugging Face — this needs an internet connection once. After that it's cached locally.

## Running the accuracy evaluation

```bash
python evaluate.py
```

This prints a classification report (precision/recall/F1 per category) and a confusion matrix, so you can see exactly where the engine is strong and where it's still missing things — this is the number you quote in interviews and pilot conversations, not a guess.

## How to merge this into your existing GitHub repo

1. Copy `detector.py`, `exemplars.py`, `evaluate.py`, and `benchmark_dataset.csv` into your existing `RozgarCheck` repo.
2. Compare `app.py` here against your current app file — port over the analysis call (`analyze_job_description`) and the results-rendering UI section, keeping any existing branding/layout you already have.
3. Merge `requirements.txt` — keep your existing spaCy/TextBlob lines (still used if you reference them elsewhere) and add the new `sentence-transformers` and `scikit-learn` lines.
4. Commit, push, and redeploy on Streamlit Cloud. Streamlit Cloud's free tier (1GB RAM) comfortably fits this model — if you hit memory issues, it's almost always from loading the model more than once; confirm `@st.cache_resource` is wrapping the load.

## Next steps (in order)

1. **Expand the benchmark dataset** to 300–500+ labeled sentences. Pull from public job-description datasets (search Kaggle/HuggingFace) plus sentences you write yourself as contrastive pairs (biased vs. neutral version of the same requirement).
2. **Run `evaluate.py`** after every dataset expansion and tune `SEMANTIC_THRESHOLD` in `detector.py` to maximize F1 — don't guess the value, sweep it (try 0.45, 0.50, 0.55, 0.60, 0.65 and compare).
3. **Get a second annotator** to label a 100-sentence subset independently — even a rough inter-annotator agreement check makes your accuracy claims far more credible.
4. **Once the benchmark is solid (300+ rows, F1 reported)**, add Layer 3 — a trained `LogisticRegression` classifier on top of the embeddings (code for this was provided in the Phase 1 technical spec document). This is a small addition once labeled data exists, not a rewrite.
5. **Write up the numbers** — this becomes your new resume bullet, your GSoC application talking point, and the opening line of your Phase 3 pilot pitch.

## A note on what's proven vs. what isn't yet

The rule-based layer (Layer 1) was tested against the starter benchmark in this build session and scored 70% accuracy on its own — every miss was a paraphrase outside its exact keyword patterns (e.g. "killer instinct" not matching the literal rule list, "long hours" phrased differently than the pattern). That's not a flaw, it's the expected ceiling of rule-based matching, and it's exactly the gap the semantic layer (Layer 2) is built to close. The semantic layer itself wasn't testable in this build sandbox (no internet access to Hugging Face here), so the first thing to do on your own machine is run `evaluate.py` and see the actual lift — don't take the architecture's value on faith, verify it with the numbers.
