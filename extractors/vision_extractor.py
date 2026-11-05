# extractors/vision_extractor.py
import asyncio
from schema import ArchitectureGraph, GraphNode

async def extract_from_image(image_bytes: bytes, client) -> ArchitectureGraph:
    """Giả lập gọi Vision LLM. Thực tế dùng OpenAI/Anthropic API."""
    # Mô phỏng độ trễ mạng
    await asyncio.sleep(1) 
    
    graph = ArchitectureGraph(system_name="Vision System")
    graph.nodes.append(GraphNode(id="v_node_1", name="Mobile App", type="ui", source="diagram", confidence=0.8))
    return graph