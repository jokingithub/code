from PIL import Image
from fastapi import HTTPException
from typing import List
import io


def merge_images(images: List[Image.Image], fmt: str = "jpeg") -> io.BytesIO:
    """垂直拼接多张图片"""
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")

    widths, heights = zip(*(img.size for img in images))
    total_height = sum(heights)
    max_width = max(widths)

    merged_image = Image.new("RGB", (max_width, total_height), (255, 255, 255))
    y_offset = 0
    for img in images:
        merged_image.paste(img, (0, y_offset))
        y_offset += img.height

    img_io = io.BytesIO()
    merged_image.save(img_io, format=fmt.upper())
    img_io.seek(0)
    return img_io
