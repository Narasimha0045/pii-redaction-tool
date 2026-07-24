"""Evaluate PII detection against the manually annotated sample set."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import spacy

from redact import find_pii

ROOT = Path(__file__).parent
GOLD_PATH = ROOT / "evaluation" / "evaluation_gold.json"
REPORT_PATH = ROOT / "evaluation" / "evaluation_report.md"


def load_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError as error:
        raise RuntimeError("Install the spaCy model first: python -m spacy download en_core_web_sm") from error


def entity_counts(entities: list[dict]) -> Counter:
    return Counter((entity["type"], entity["text"].casefold()) for entity in entities)


def evaluate() -> dict:
    nlp = load_model()
    gold_rows = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    totals = Counter()

    for row in gold_rows:
        expected = entity_counts(row["entities"])
        predicted = entity_counts(find_pii(row["text"], nlp))
        totals["TP"] += sum((expected & predicted).values())
        totals["FP"] += sum((predicted - expected).values())
        totals["FN"] += sum((expected - predicted).values())

    precision = totals["TP"] / (totals["TP"] + totals["FP"]) if totals["TP"] + totals["FP"] else 0.0
    recall = totals["TP"] / (totals["TP"] + totals["FN"]) if totals["TP"] + totals["FN"] else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"TP": totals["TP"], "FP": totals["FP"], "FN": totals["FN"], "precision": precision, "recall": recall, "f1": f1}


def write_report(results: dict) -> None:
    REPORT_PATH.write_text(
        "# Evaluation Report\n\n"
        "This run compares the detector against a manually annotated sample set. "
        "It reports entity-level precision, recall, and F1. Accuracy is intentionally omitted: "
        "without token-level non-PII annotation, true negatives are not well-defined for NER.\n\n"
        "| Metric | Value |\n| --- | ---: |\n"
        f"| True positives | {results['TP']} |\n| False positives | {results['FP']} |\n| False negatives | {results['FN']} |\n"
        f"| Precision | {results['precision']:.3f} |\n| Recall | {results['recall']:.3f} |\n| F1 | {results['f1']:.3f} |\n",
        encoding="utf-8",
    )


def main() -> None:
    results = evaluate()
    write_report(results)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
