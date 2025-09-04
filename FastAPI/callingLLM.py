from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from ollama import AsyncClient
from typing import Optional
import uuid
import aiofiles
import os

app = FastAPI(
    title="CALLING LLM API",
    description="Call LLM API for vision-language tasks",
    version="1.0"
)

# 初始化异步客户端
client = AsyncClient(host='http://localhost:11434')  # Ollama 默认地址

@app.post("/vlchat")
async def vlchat(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    model: Optional[str] = Form("qwen2.5vl:7b")
):
    """
    处理上传的图片文件并进行视觉语言模型问答
    """
    # 创建临时目录（如果不存在）
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(temp_dir, unique_filename)
    
    try:
        # 异步保存上传的文件
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # 调用模型进行视觉问答
        response = await client.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    'images': [file_path],  # 使用保存的文件路径
                }
            ],
        )
        
        # 记录响应（可选）
        print(f"模型响应: {response.message.content}")
        
        # 返回响应
        return JSONResponse({
            "text": response.message.content,
            "model": model,
            "prompt": prompt
        })
        
    except Exception as e:
        # 错误处理
        raise HTTPException(
            status_code=500,
            detail=f"处理图像时发生错误: {str(e)}"
        )
    
    finally:
        # 清理：删除临时文件
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"警告: 无法删除临时文件 {file_path}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
