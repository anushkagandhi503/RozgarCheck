"""
evaluate.py
Computes precision/recall/F1 of the current detection engine against
benchmark_dataset.csv. Run this after every change to thresholds or
exemplar lists to see the actual impact, instead of guessing.

Usage:  python evaluate.py
"""

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from detector import rule_based_flags, semantic_flags, pick_primary_category

df = pd.read_csv("benchmark_dataset.csv")

y_true = []
y_pred = []

for _, row in df.iterrows():
    sentence = row["sentence"]
    true_category = row["category"]

    rule_hits = rule_based_flags(sentence)
    rule_categories = {f["category"] for f in rule_hits}
    sem_hits = [f for f in semantic_flags(sentence) if f["category"] not in rule_categories]

    predicted = pick_primary_category(rule_hits + sem_hits)

    y_true.append(true_category)
    y_pred.append(predicted)

print("=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)
print(classification_report(y_true, y_pred, zero_division=0))

print("=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)
labels = sorted(set(y_true) | set(y_pred))
cm = confusion_matrix(y_true, y_pred, labels=labels)
cm_df = pd.DataFrame(cm, index=labels, columns=labels)
print(cm_df)

print("\nNote: This is a starter benchmark of ~30 sentences — treat these")
print("numbers as directional, not final. Expand benchmark_dataset.csv to")
print("500+ labeled sentences before quoting accuracy numbers externally.")
