# tests/test.py
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1. XỬ LÝ ĐƯỜNG DẪN: File đang ở trong tests/, phải lùi 2 cấp để về thư mục gốc
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
    
    # ========================================================
    # 🎯 PHẦN ĐỌC FILE TỪ THƯ MỤC DATA
    # ========================================================
    puml_path = project_root / "data" / "system.puml"
    md_path = project_root / "data" / "description.md"
    
    # Kiểm tra xem file có tồn tại không trước khi đọc (tránh lỗi sập chương trình)
    if not puml_path.exists() or not md_path.exists():
        print(f"❌ LỖI: Không tìm thấy file tại {puml_path} hoặc {md_path}")
        print("Vui lòng kiểm tra lại xem bạn đã tạo thư mục 'data' và 2 file bên trong chưa.")
        return

    print(f"📂 Đang đọc dữ liệu từ thư mục data/...")
    
    # Đọc nội dung thực tế của file
    puml_content = puml_path.read_text(encoding='utf-8')
    md_content = md_path.read_text(encoding='utf-8')

    # Đóng gói vào inputs
    inputs = [
        {
            "name": "system.puml", 
            "content": puml_content, 
            "bytes": b""
        },
        {
            "name": "description.md", 
            "content": md_content, 
            "bytes": b""
        }
    ]
    # ========================================================
    
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