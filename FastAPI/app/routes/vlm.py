from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional

from services.vlm_service import run_vlm_chat

router = APIRouter()


@router.post("/chat")
async def vlchat(
    file: UploadFile = File(..., description="Image or document for VLM"),
    prompt: str = Form(..., description="User prompt"),
    model: Optional[str] = Form("qwen2.5vl:7b", description="Model name")
):
    text = await run_vlm_chat(file, prompt, model)
    return JSONResponse({
        "text": text,
        "model": model,
        "prompt": prompt
    })
