# Evaluation Report

## Evaluation Strategy

The PII detector was evaluated using a small manually annotated dataset (`evaluation_gold.json`) containing examples for all required PII categories. The predicted entities were compared against the ground-truth annotations using exact entity-level matching.

The evaluation reports **precision**, **recall**, and **F1-score**. Accuracy is not reported because true negatives are not well-defined for named entity recognition without token-level annotation of all non-PII text.

## Results

| Metric | Value |
| --- | ---: |
| True Positives | 8 |
| False Positives | 1 |
| False Negatives | 2 |
| Precision | 0.889 |
| Recall | 0.800 |
| F1-score | 0.842 |