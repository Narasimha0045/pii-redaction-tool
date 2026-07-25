# PII Redaction Tool

## Overview

This project redacts common types of Personally Identifiable Information (PII) from Microsoft Word (`.docx`) documents. It detects sensitive information, replaces it with realistic fake values, and saves a new redacted document. To keep the document consistent, the same original value is always replaced with the same fake value during a single run.

## Setup

Install the required packages:

```powershell
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Place the input document in the `input` folder and run:

```powershell
python redact.py input/Red_Herring_Prospectus.docx output/redacted_output.docx
```

The redacted document will be saved in the `output` folder.

## Approach

The tool combines regular expressions, spaCy, and Faker to identify and replace PII.

- **Regex** is used for structured information such as email addresses, phone numbers, SSNs, credit card numbers, dates of birth, IP addresses, and common address formats.
- **spaCy (`en_core_web_sm`)** is used to detect people and organisation names.
- **Faker** generates realistic replacement values.
- A mapping dictionary ensures the same original value is always replaced with the same fake value throughout the document.
- **python-docx** is used to read and update paragraphs, tables, headers, and footers while preserving the overall document structure.

## Limitations

This implementation is designed as a simple and practical solution rather than a production-ready system.

- Regex works well for structured data but may miss unusual formats.
- spaCy can occasionally miss names or incorrectly classify some entities.
- Address detection is challenging because address formats vary significantly.
- Rewriting paragraph text may slightly affect detailed run-level formatting in some documents.

## Evaluation

A small manually annotated dataset is included in `evaluation/evaluation_gold.json`.

Run the evaluation with:

```powershell
python evaluate.py
```

The evaluation reports **precision**, **recall**, and **F1-score** based on entity-level matches. Since the dataset does not contain annotations for every non-PII token, accuracy is not reported.
