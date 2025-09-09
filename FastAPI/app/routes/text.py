from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from urllib.parse import quote
import os, tempfile

from services.text_service import extract_doc_with_antiword, extract_docx, extract_pdf

router = APIRouter()

@router.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    filename = file.filename
    if not filename.lower().endswith((".doc", ".docx", ".pdf")):
        raise HTTPException(status_code=400, detail="Only .doc, .docx, .pdf files are supported")

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        if filename.lower().endswith(".docx"):
            text = extract_docx(tmp_path)
        elif filename.lower().endswith(".doc"):
            text = extract_doc_with_antiword(tmp_path)
        else:
            text = extract_pdf(tmp_path)

        return JSONResponse({
            "filename": quote(filename),
            "text": text.strip()
        })
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
