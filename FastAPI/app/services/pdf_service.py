from pdf2image import convert_from_bytes
from fastapi import HTTPException
from typing import Optional, List
from PIL import Image
import io
import zipfile


def pdf_to_images(contents: bytes, dpi: int = 400, page_range: Optional[str] = None) -> List[Image.Image]:
    """PDF 转单页图片列表"""
    try:
        if page_range:
            pages = []
            ranges = page_range.split(',')
            for r in ranges:
                if '-' in r:
                    start, end = map(int, r.split('-'))
                    pages.extend(range(start, end + 1))
                else:
                    pages.append(int(r))
            images = convert_from_bytes(contents, dpi=dpi, first_page=min(pages), last_page=max(pages))
            images = [images[i - 1] for i in pages if 0 <= i - 1 < len(images)]
        else:
            images = convert_from_bytes(contents, dpi=dpi)

        if not images:
            raise HTTPException(status_code=500, detail="No pages found in PDF")

        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF conversion error: {str(e)}")


def images_to_zip(images: List[Image.Image], fmt: str = "jpeg") -> io.BytesIO:
    """将多张图片打包成 zip"""
    img_io = io.BytesIO()
    with zipfile.ZipFile(img_io, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for idx, img in enumerate(images, start=1):
            buf = io.BytesIO()
            img.save(buf, format=fmt.upper())
            zf.writestr(f"page_{idx}.{fmt.lower()}", buf.getvalue())
    img_io.seek(0)
    return img_io
