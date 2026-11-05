# interface.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import os

from schema import ArchitectureGraph
from agent import ArchitectureExtractionAgent
from llm_client import create_groq_client # Import hàm khởi tạo

app = FastAPI(title="Architecture Extraction Agent API")

# Lấy API Key từ biến môi trường (KHÔNG hard-code)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Thiếu biến môi trường GROQ_API_KEY")

# Khởi tạo client thật
groq_client = create_groq_client(GROQ_API_KEY)

# Khởi tạo Agent với client thật
agent = ArchitectureExtractionAgent(llm_client=groq_client)

@app.post("/extract-architecture", response_model=ArchitectureGraph)
async def extract_architecture(files: List[UploadFile] = File(...)):
    try:
        inputs = []
        for f in files:
            content_bytes = await f.read()
            try:
                content_text = content_bytes.decode('utf-8')
            except UnicodeDecodeError:
                content_text = None
                
            inputs.append({
                "name": f.filename,
                "content": content_text,
                "bytes": content_bytes
            })
            
        result = await agent.run(inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))