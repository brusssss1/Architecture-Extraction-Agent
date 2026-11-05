# tests/test.py
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1. SỬA ĐƯỜNG DẪN: File đang ở trong tests/, phải lùi 2 cấp để về thư mục gốc
project_root = Path(__file__).resolve().parent.parent

# 2. THÊM THƯ MỤC GỐC VÀO HỆ THỐNG: Để Python tìm thấy schema.py, agent.py...
sys.path.insert(0, str(project_root))

# 3. Nạp biến môi trường từ file .env ở thư mục gốc
load_dotenv(dotenv_path=project_root / ".env")

# Bây giờ mới import được các file bên ngoài
from schema import ArchitectureGraph
from agent import ArchitectureExtractionAgent
from llm_client import create_groq_client


async def main():
    """Hàm này để chạy trực tiếp bằng lệnh python tests/test.py"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ LỖI: Chưa tìm thấy GROQ_API_KEY trong file .env")
        return
    
    print(f"✅ Đã lấy được API Key: {api_key[:10]}...")
    client = create_groq_client(api_key)
    agent = ArchitectureExtractionAgent(client)
    
    inputs = [
        {
            "name": "diagram.puml", 
            "content": '''@startuml
!include <C4/C4_Container>
Person(user, "Khách hàng")
Container(webapp, "WebApp", "React", "Giao diện")
Rel(user, webapp, "Sử dụng", "HTTPS")
@enduml''', 
            "bytes": b""
        },
        {
            "name": "doc.md", 
            "content": "Hệ thống có Payment Service viết bằng Java, kết nối database PostgreSQL qua SQL.",
            "bytes": b""
        }
    ]
    
    print("⏳ Đang trích xuất kiến trúc (vui lòng đợi gọi API Groq)...")
    result = await agent.run(inputs)
    
    print("\n=== KẾT QUẢ ===")
    print(f"Nodes: {len(result.nodes)}")
    for n in result.nodes:
        print(f"  - {n.name} ({n.type}, source={n.source})")
    print(f"Edges: {len(result.edges)}")
    for e in result.edges:
        print(f"  - {e.source_id} --> {e.target_id} ({e.relationship_type})")
    print(f"Warnings: {result.warnings}")

if __name__ == "__main__":
    asyncio.run(main())