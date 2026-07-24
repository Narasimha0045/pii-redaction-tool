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
<style>
  body{font-family:Arial,sans-serif;max-width:600px;margin:60px auto;line-height:1.6;padding:0 16px}
  h1{font-size:24px;margin-bottom:4px}
  p{color:#555;margin-bottom:20px}
  input[type=file]{font-size:15px;margin:8px 0;display:block}
  button{padding:10px 20px;font-size:15px;background:#2563eb;color:#fff;border:none;border-radius:6px;cursor:pointer;margin-top:10px}
  button:hover{background:#1d4ed8}
  #status{display:none;margin-top:24px;padding:16px;border:1px solid #ddd;border-radius:8px;background:#f9f9f9}
  #bar-wrap{background:#e5e7eb;border-radius:6px;height:14px;margin:10px 0}
  #bar{height:14px;width:0%;background:#2563eb;border-radius:6px;transition:width 0.4s ease}
  #pct{font-size:14px;color:#333}
  #step{font-size:13px;color:#666;margin-top:6px}
</style>
</head>
<body>
  <h1>PII Redaction Tool</h1>
  <p>Upload a DOCX file to receive a redacted copy. Files are not stored.</p>
  <form id="redact-form" action="/redact" method="post" enctype="multipart/form-data">
    <input type="file" name="document" accept=".docx" required>
    <button type="submit">Redact Document</button>
  </form>

  <div id="status">
    <strong>Redacting your document...</strong>
    <div id="bar-wrap"><div id="bar"></div></div>
    <div id="pct">0%</div>
    <div id="step">Scanning document...</div>
  </div>

  <script>
    const steps = [
      [10, "Scanning document..."],
      [25, "Detecting names and emails..."],
      [42, "Identifying phone numbers..."],
      [58, "Redacting personal addresses..."],
      [72, "Removing ID numbers..."],
      [85, "Finalizing redactions..."],
      [95, "Preparing download..."],
    ];

    document.getElementById("redact-form").addEventListener("submit", function(e) {
      const file = this.querySelector('input[type=file]').files[0];
      if (!file) return;

      document.getElementById("status").style.display = "block";
      this.querySelector("button").disabled = true;

      let i = 0;
      function next() {
        if (i >= steps.length) return;
        const [pct, msg] = steps[i++];
        document.getElementById("bar").style.width = pct + "%";
        document.getElementById("pct").textContent = pct + "%";
        document.getElementById("step").textContent = msg;
        setTimeout(next, 1800);
      }
      next();
    });
  </script>
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
