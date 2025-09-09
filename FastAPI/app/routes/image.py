from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from typing import List
from PIL import Image
import io

from services.image_service import merge_images

router = APIRouter()


@router.post("/merge", summary="垂直拼接多张图片")
async def merge_images_endpoint(
    files: List[UploadFile] = File(..., description="要拼接的图片列表"),
    fmt: str = "jpeg"
):
    """
    垂直拼接多张图片并返回一张合并后的图片。
    
    参数:
        files (List[UploadFile]): 用户上传的图片列表
        fmt (str): 输出图片格式，默认 "jpeg" (可选值: "jpeg", "png", "webp")
    
    返回:
        StreamingResponse: 返回合并后的图片，可直接下载
    """
    try:
        images = []
        for f in files:
            content = await f.read()
            img = Image.open(io.BytesIO(content)).convert("RGB")
            images.append(img)

        if not images:
            raise HTTPException(status_code=400, detail="No images uploaded")

        merged_io = merge_images(images, fmt=fmt)
        safe_filename = f"merged.{fmt}"
        safe_filename_ascii = quote(safe_filename)

        return StreamingResponse(
            merged_io,
            media_type=f"image/{fmt.lower()}",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename_ascii}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merging error: {str(e)}")
