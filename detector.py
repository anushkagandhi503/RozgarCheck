"""
detector.py
Core bias detection engine for RozgarCheck — Phase 1 upgrade.

Architecture:
  Layer 1: Rule/lexicon matching (fast, fully explainable, high precision/lower recall)
  Layer 2: Semantic similarity via sentence-transformers (catches paraphrased bias)
  Explainability: every flag carries a reason, confidence, and suggested rewrite
  Audit logging: every scan is logged to a structured JSONL file for compliance export

Layer 3 (trained classifier) is intentionally left out of this file — add it once
you have a labeled benchmark dataset of 300+ sentences (see benchmark_dataset.csv
and README.md for instructions). Wiring it in is a small addition once the data exists.
"""

import re
import json
import hashlib
from datetime import datetime, timezone
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer, util

from exemplars import EXEMPLARS, CATEGORY_LABELS, REWRITE_SUGGESTIONS

AUDIT_LOG_PATH = "scan_audit_log.jsonl"
SEMANTIC_THRESHOLD = 0.65  # starting point — tune once benchmark data exists

# ---------------------------------------------------------------------------
# Layer 1: Rule-based detection
# ---------------------------------------------------------------------------

# Simple keyword/regex rules. Kept deliberately small and high-precision —
# this layer's job is to catch obvious, unambiguous terms fast and cheaply.
RULE_PATTERNS = {
    "gender_coded": [
        r"\brockstar\b", r"\bninja\b", r"\bguru\b", r"\bdominant\b",
        r"\baggressive\b", r"\bhe\s+will\b", r"\bhis\s+duties\b", r"\bmanpower\b",
        r"\bmale\s+candidate\b", r"\bshe\s+will\b", r"\bbro[\s-]culture\b",
        r"\bhustle\b", r"\bgrind\b", r"\bwarrior\b", r"\bgunslinger\b",
        r"\bsharp[\s-]?shooter\b", r"\bevangelist\b", r"\bsensei\b",
        r"\bman\s+the\b", r"\bkiller\s+drive\b", r"\bkiller\s+instinct\b",
    ],
    "age_coded": [
        r"\bdigital\s+native[s]?\b", r"\byoung\b", r"\byouthful\b",
        r"\brecent\s+grad(uate)?[s]?\b", r"\bfresh\s+blood\b",
        r"\bmillennial[s]?\b", r"\bgen[\s-]?z\b",
        r"\bretirement[\s-]age\b", r"\bcandidates?\s+over\s+\d+\b",
        r"\bno\s+more\s+than\s+\d+\s+years?\s+(of\s+)?experience\b",
    ],
    "ability_coded": [
        r"\bable[\s-]bodied\b", r"\bno\s+health\s+issues\b",
        r"\bphysically\s+fit\b", r"\bmust\s+be\s+able\s+to\s+lift\b",
        r"\blicen[sc]e\s+is\s+non[\s-]negotiable\b",
        r"\bno\s+medical\s+accommodations?\b",
    ],
    "cultural_exclusion": [
        r"\bnative\s+english\s+speaker\b", r"\bculture\s+fit\b",
        r"\btraditional\s+values\b", r"\bwork[\s-]hard[\s-]play[\s-]hard\b",
        r"\bno\s+regional\s+accent\b", r"\bwestern[\s-]style\b",
    ],
    "socioeconomic_exclusion": [
        r"\bunpaid\s+intern", r"\bmust\s+own\s+a\s+car\b", r"\btop[\s-]tier\s+colleges?\s+only\b",
        r"\biit\s+or\s+iim\b", r"\bequity\s+only\b", r"\bunpaid\s+trial\b",
        r"\bdelayed\s+compensation\b", r"\bbig\s+4\s+or\s+fortune\b",
        r"\bpremium\s+mba\b", r"\bfinancially\s+stable\s+enough\b",
        r"\bpersonal\s+internet\s+connection\b",
    ],
}

_COMPILED_RULES = {
    category: [re.compile(pat, re.IGNORECASE) for pat in patterns]
    for category, patterns in RULE_PATTERNS.items()
}


def rule_based_flags(sentence: str) -> list[dict]:
    """Returns rule-matched flags for a sentence. Confidence is fixed at 0.95
    since rule matches are exact/near-exact and don't need a similarity score."""
    flags = []
    for category, patterns in _COMPILED_RULES.items():
        for pattern in patterns:
            match = pattern.search(sentence)
            if match:
                flags.append({
                    "category": category,
                    "method": "rule",
                    "confidence": 0.95,
                    "matched_text": match.group(0),
                    "sentence": sentence,
                })
                break  # one rule match per category is enough; avoid duplicate flags
    return flags


# ---------------------------------------------------------------------------
# Layer 2: Semantic similarity detection
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Loads the embedding model once and caches it. In Streamlit, wrap the
    call site with @st.cache_resource as well so it survives across reruns."""
    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_exemplar_embeddings():
    model = get_model()
    return {
        category: model.encode(phrases, convert_to_tensor=True)
        for category, phrases in EXEMPLARS.items()
    }


def semantic_flags(sentence: str, threshold: float = SEMANTIC_THRESHOLD) -> list[dict]:
    """Returns semantic-similarity flags for a sentence above the given threshold."""
    model = get_model()
    exemplar_embeddings = get_exemplar_embeddings()
    sent_embedding = model.encode(sentence, convert_to_tensor=True)

    flags = []
    for category, embeddings in exemplar_embeddings.items():
        scores = util.cos_sim(sent_embedding, embeddings)[0]
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        if best_score >= threshold:
            flags.append({
                "category": category,
                "method": "semantic",
                "confidence": round(best_score, 3),
                "matched_exemplar": EXEMPLARS[category][best_idx],
                "sentence": sentence,
            })
    return flags


# ---------------------------------------------------------------------------
# Ensemble + explainability
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> list[str]:
    """Lightweight sentence splitter. Swap for spaCy's sentencizer if you want
    more robust handling of abbreviations, bullet points, etc."""
    raw = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [s.strip() for s in raw if s.strip()]


def explain_flag(flag: dict) -> dict:
    """Attaches a human-readable reason and suggested rewrite to a raw flag."""
    category = flag["category"]
    if flag["method"] == "rule":
        reason = (
            f"Contains the term \"{flag['matched_text']}\", a known "
            f"{CATEGORY_LABELS[category].lower()} term."
        )
    else:
        reason = (
            f"This phrasing is semantically similar to known "
            f"{CATEGORY_LABELS[category].lower()} language "
            f"(e.g. \"{flag['matched_exemplar']}\")."
        )
    return {
        **flag,
        "category_label": CATEGORY_LABELS[category],
        "reason": reason,
        "suggested_rewrite": REWRITE_SUGGESTIONS[category],
    }


def pick_primary_category(flags: list[dict]) -> str:
    """Given a list of explained/raw flags for one sentence, picks a single
    'primary' category for simplified single-label evaluation purposes.
    Rule matches (high, fixed precision) are preferred over semantic matches;
    among semantic-only matches, the highest confidence wins. This does NOT
    affect the live app — the app correctly shows every flag to the user.
    This is only used by evaluate.py / debug_misses.py for scoring."""
    if not flags:
        return "none"
    rule_flags = [f for f in flags if f["method"] == "rule"]
    if rule_flags:
        return rule_flags[0]["category"]
    best = max(flags, key=lambda f: f["confidence"])
    return best["category"]


def analyze_job_description(text: str, user_id: str = "anonymous") -> dict:
    """Main entry point. Runs both layers across every sentence, deduplicates
    flags per sentence/category, attaches explanations, and logs the scan."""
    sentences = split_sentences(text)
    all_flags = []

    for sentence in sentences:
        rule_hits = rule_based_flags(sentence)
        rule_categories = {f["category"] for f in rule_hits}

        # Only run semantic matching for categories the rule layer didn't
        # already catch in this sentence — saves compute, avoids duplicate flags.
        sem_hits = [
            f for f in semantic_flags(sentence)
            if f["category"] not in rule_categories
        ]

        for flag in rule_hits + sem_hits:
            all_flags.append(explain_flag(flag))

    result = {
        "total_sentences": len(sentences),
        "total_flags": len(all_flags),
        "categories_triggered": sorted({f["category"] for f in all_flags}),
        "flags": all_flags,
    }

    log_scan(text, all_flags, user_id)
    return result


# ---------------------------------------------------------------------------
# Audit logging (seed for Phase 4 compliance reports)
# ---------------------------------------------------------------------------

def log_scan(job_description: str, flags: list[dict], user_id: str = "anonymous") -> dict:
    """Logs a scan to a structured JSONL file. Stores a hash of the input by
    default, not the raw text — only store raw text with explicit user consent
    once a privacy policy is in place (see Phase 4 of the roadmap)."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "input_hash": hashlib.sha256(job_description.encode("utf-8")).hexdigest(),
        "flags_found": len(flags),
        "categories_triggered": sorted({f["category"] for f in flags}),
        "flags_detail": flags,
    }
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record
