from fastapi import FastAPI
from routes import text, pdf, vlm, image

app = FastAPI(
    title="Doc/PDF to Text API",
    description="Convert .doc, .docx, .pdf files to plain text or images",
    version="1.1"
)

# 注册路由
app.include_router(text.router, prefix="/text", tags=["Text"])
app.include_router(pdf.router, prefix="/pdf", tags=["PDF"])
app.include_router(vlm.router, prefix="/vlm", tags=["VLM"])
app.include_router(image.router, prefix="/image", tags=["Image"])