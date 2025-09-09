import os
import uuid
import aiofiles
from ollama import AsyncClient


client = AsyncClient(host='http://localhost:11434')


async def run_vlm_chat(file, prompt: str, model: str = "qwen2.5vl:7b") -> str:
    """
    调用 VLM 模型进行多模态对话
    :param file: 上传文件 (UploadFile)
    :param prompt: 用户输入的提示词
    :param model: 模型名称 (默认 qwen2.5vl:7b)
    :return: 模型返回文本
    """
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(temp_dir, unique_filename)

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        response = await client.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [file_path],
            }],
        )

        return response.message.content
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
