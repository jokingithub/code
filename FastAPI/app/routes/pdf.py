from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from typing import Optional

from services.pdf_service import pdf_to_images, images_to_zip
from services.image_service import merge_images

router = APIRouter()

@router.post("/convert")
async def convert_pdf_to_images(
    file: UploadFile = File(..., description="PDF file to convert"),
    dpi: int = 400,
    fmt: str = "jpeg",
    page_range: Optional[str] = None
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
    contents = await file.read()

    images = pdf_to_images(contents, dpi=dpi, page_range=page_range)
    img_io = images_to_zip(images, fmt)

    safe_filename = file.filename.replace('.pdf', '') + f"_pages.zip"
    safe_filename_ascii = quote(safe_filename)
    return StreamingResponse(
        img_io,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename_ascii}"}
    )


@router.post("/convert-merged")
async def convert_pdf_to_merged_image(
    file: UploadFile = File(..., description="PDF file to convert and merge"),
    dpi: int = 400,
    fmt: str = "jpeg",
    page_range: Optional[str] = None
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
    contents = await file.read()

    images = pdf_to_images(contents, dpi=dpi, page_range=page_range)
    img_io = merge_images(images, fmt)

    safe_filename = file.filename.replace('.pdf', '') + f"_merged.{fmt}"
    safe_filename_ascii = quote(safe_filename)
    return StreamingResponse(
        img_io,
        media_type=f"image/{fmt.lower()}",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename_ascii}"}
    )
