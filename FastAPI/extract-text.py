from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import subprocess
import docx2txt
from PyPDF2 import PdfReader

app = FastAPI(
    title="Doc/PDF to Text API",
    description="Convert .doc, .docx, .pdf files to plain text",
    version="1.0"
)

def extract_doc_with_antiword(path: str) -> str:
    """使用 antiword 提取 .doc 文本"""
    try:
        result = subprocess.run(
            ["antiword", path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"antiword failed: {e.stderr}")


@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    filename = file.filename.lower()

    # 只允许 doc, docx, pdf
    if not (filename.endswith(".doc") or filename.endswith(".docx") or filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Only .doc, .docx, .pdf files are supported")

    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        text = ""
        if filename.endswith(".docx"):
            # 处理 Word docx
            text = docx2txt.process(tmp_path)

        elif filename.endswith(".doc"):
            # 处理 Word doc (老格式, 用 antiword)
            text = extract_doc_with_antiword(tmp_path)

        elif filename.endswith(".pdf"):
            # 处理 PDF
            reader = PdfReader(tmp_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages)

        return JSONResponse({
            "filename": filename,
            "text": text.strip()
        })

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
