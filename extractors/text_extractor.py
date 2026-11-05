# extractors/text_extractor.py
import json
from openai import AsyncOpenAI
from schema import ArchitectureGraph

async def extract_from_text(text: str, client: AsyncOpenAI) -> ArchitectureGraph:
    """Gọi LLM (Groq) để trích xuất kiến trúc từ văn bản mô tả."""
    
    # --- PROMPT "ÉP" LLM HIỂU VỀ C4 VÀ UML ---
    system_prompt = """
Bạn là một Software Architect chuyên về mô hình C4 và UML.
Nhiệm vụ: Đọc văn bản mô tả hệ thống và trích xuất kiến trúc dưới dạng JSON.

QUY TẮC BẮT BUỘC:
1. Trường "type" CHỈ ĐƯỢC PHÉP chọn 1 trong các giá trị: "service", "database", "ui", "queue", "cache", "external_system", "actor".
2. Trường "relationship_type" CHỈ ĐƯỢC PHÉP chọn 1 trong các giá trị: "sync_call", "async_call", "data_flow", "dependency", "contains".
3. Trường "c4_level" CHỈ ĐƯỢC PHÉP chọn 1 trong các giá trị: "context", "container", "component".
4. Trường "confidence" phải là số thực từ 0.0 đến 1.0.
5. Trường "source" luôn là "text".
6. Trường "evidence" PHẢI trích dẫn câu gốc trong văn bản.

ĐỊNH DẠNG ĐẦU RA (JSON thuần, KHÔNG thêm markdown):
{
  "system_name": "Tên hệ thống",
  "nodes": [
    {
      "id": "string_id_khong_dau",
      "name": "Tên hiển thị",
      "type": "service", 
      "c4_level": "container",
      "properties": {"tech_stack": "ngôn ngữ nếu có"},
      "source": "text",
      "confidence": 0.9,
      "evidence": "Câu trích dẫn từ văn bản gốc"
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source_id": "id_nguon",
      "target_id": "id_dich",
      "relationship_type": "sync_call",
      "label": "Mô tả quan hệ",
      "source": "text",
      "confidence": 0.9
    }
  ]
}
"""

    try:
        # Gọi LLM thật
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Model Groq
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Văn bản mô tả:\n{text}"}
            ],
            response_format={"type": "json_object"},  # Ép trả về JSON
            temperature=0.1,  # Gần 0 để tăng độ chính xác
            max_tokens=4000
        )
        
        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)
        
        # Validate bằng Pydantic (nếu LLM trả sai schema sẽ báo lỗi ngay)
        return ArchitectureGraph(**data)
        
    except json.JSONDecodeError as e:
        return ArchitectureGraph(warnings=[f"LLM trả JSON không hợp lệ: {e}"])
    except Exception as e:
        return ArchitectureGraph(warnings=[f"Lỗi gọi LLM: {e}"])