"""Small web interface for the DOCX PII redaction tool."""
from __future__ import annotations

import io
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse

from redact import redact_document

app = FastAPI(title="PII Redaction Tool")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html><head><title>PII Redaction Tool</title>
<style>body{font-family:Arial,sans-serif;max-width:680px;margin:72px auto;line-height:1.5}input,button{font-size:16px;margin:12px 0}button{padding:10px 16px}</style>
</head><body><h1>PII Redaction Tool</h1><p>Upload a DOCX file to receive a redacted copy. Uploaded files are processed only for this request and are not stored.</p>
<form action="/redact" method="post" enctype="multipart/form-data"><input type="file" name="document" accept=".docx" required><br><button type="submit">Redact document</button></form>
</body></html>"""


@app.post("/redact")
async def redact_upload(document: UploadFile = File(...)):
    if not document.filename or not document.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Please upload a .docx file.")

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "source.docx"
        output_path = Path(temp_dir) / "redacted.docx"
        input_path.write_bytes(await document.read())
        redact_document(input_path, output_path)
        content = output_path.read_bytes()

    filename = f"redacted_{Path(document.filename).name}"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(io.BytesIO(content), headers=headers, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
