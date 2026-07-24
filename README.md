# PII Redaction Tool

## Overview

This tool reads a DOCX file, detects common personally identifiable information, replaces it with deterministic fake values, and writes a new DOCX. Repeated source values map to the same replacement for the duration of a run.

## Setup

```powershell
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Place the source document at `input/Red_Herring_Prospectus.docx`, then run:

```powershell
python redact.py input/Red_Herring_Prospectus.docx output/redacted_output.docx
```

## Approach

- Regex handles structured PII: email addresses, phone numbers, SSNs, credit-card numbers, dates of birth, and IP addresses.
- spaCy's `en_core_web_sm` model detects people, organizations, and geographical entities.
- A small address regex supplements spaCy for common street-address formats.
- Faker produces realistic replacement names, companies, addresses, emails, and phone numbers. A dictionary keeps replacements consistent within one execution.
- python-docx reads paragraphs, tables, headers, and footers, then writes the redacted document.

## Tradeoffs

Regex is precise for well-formed structured values. spaCy improves recall for names and organizations, but may miss ambiguous or domain-specific entities. Addresses remain the hardest category because their formats vary widely. To keep the implementation simple, redacted paragraphs are rewritten as text, which may reduce fine-grained run formatting.

## Evaluation

`evaluation/evaluation_gold.json` is a manually annotated sample set. Run:

```powershell
python evaluate.py
```

The evaluator reports precision, recall, and F1 from entity-level matches. Accuracy is intentionally omitted because true negatives are undefined without token-level annotation of all non-PII text. The metrics are useful regression checks, not a claim of production-wide performance.

## Web deployment

The repository includes a small FastAPI upload page for Render. Create a Render web service from this GitHub repository and let Render use `render.yaml`. The service accepts a DOCX upload, returns a redacted copy, and uses a temporary directory so uploaded files are not retained after the request.
