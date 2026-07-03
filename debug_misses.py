"""
debug_misses.py
Prints every sentence where predicted category didn't match true label.
"""
import pandas as pd
from detector import rule_based_flags, semantic_flags, pick_primary_category

df = pd.read_csv("benchmark_dataset.csv")

misses = 0
for _, row in df.iterrows():
    sentence = row["sentence"]
    true_category = row["category"]

    rule_hits = rule_based_flags(sentence)
    rule_categories = {f["category"] for f in rule_hits}
    sem_hits = [f for f in semantic_flags(sentence) if f["category"] not in rule_categories]

    predicted = pick_primary_category(rule_hits + sem_hits)

    if predicted != true_category:
        misses += 1
        print("=" * 70)
        print(f"SENTENCE:  {sentence}")
        print(f"TRUE:      {true_category}")
        print(f"PREDICTED: {predicted}")
        if rule_hits:
            print(f"  Rule layer: {[f['category'] for f in rule_hits]}")
        for f in sem_hits:
            print(f"  Semantic: category={f['category']} confidence={f['confidence']} "
                  f"exemplar=\"{f['matched_exemplar']}\"")

print(f"\nTotal misses: {misses} / {len(df)}")
print(f"Sentence-level accuracy: {(len(df)-misses)/len(df):.1%}")
