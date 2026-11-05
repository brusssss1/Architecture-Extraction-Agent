# extractors/plantuml_parser.py
import re
from schema import ArchitectureGraph, GraphNode, GraphEdge

def extract_from_plantuml(text: str) -> ArchitectureGraph:
    """
    Parse file PlantUML (đặc biệt là C4) bằng Regex.
    Hỗ trợ cú pháp: Container, ContainerDb, Person, System, Rel.
    """
    graph = ArchitectureGraph(system_name="PlantUML Extracted System")
    
    # --- BƯỚC 1: Bóc tách các Nodes (Thành phần) ---
    # Regex bắt các dòng: Container(id, "Name", "Tech", "Desc") hoặc ContainerDb(...)
    node_patterns = {
        "actor": r'Person\s*\(\s*(\w+)\s*,\s*"([^"]+)"',
        "service": r'Container\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*,\s*"([^"]*)"',
        "database": r'ContainerDb\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*,\s*"([^"]*)"',
    }
    
    for node_type, pattern in node_patterns.items():
        for match in re.finditer(pattern, text):
            node_id = match.group(1)
            node_name = match.group(2)
            tech_stack = match.group(3) if len(match.groups()) >= 3 else None
            
            graph.nodes.append(GraphNode(
                id=node_id,
                name=node_name,
                type=node_type,
                c4_level="container" if node_type != "actor" else "context",
                properties={"tech_stack": tech_stack} if tech_stack else {},
                source="diagram",
                confidence=1.0 # Parser chính xác 100%
            ))
    
    # --- BƯỚC 2: Bóc tách các Edges (Quan hệ) ---
    # Regex bắt dòng: Rel(source, target, "Label", "Tech")
    edge_pattern = r'Rel\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*"([^"]+)"(?:\s*,\s*"([^"]*)")?\s*\)'
    
    for idx, match in enumerate(re.finditer(edge_pattern, text)):
        source_id = match.group(1)
        target_id = match.group(2)
        label = match.group(3)
        tech = match.group(4)
        
        # Suy luận loại quan hệ dựa vào công nghệ (nếu có)
        rel_type = "sync_call" # Mặc định
        if tech and ("Kafka" in tech or "RabbitMQ" in tech or "async" in tech.lower()):
            rel_type = "async_call"
        elif tech and "SQL" in tech:
            rel_type = "data_flow"
            
        graph.edges.append(GraphEdge(
            id=f"edge_{idx}",
            source_id=source_id,
            target_id=target_id,
            relationship_type=rel_type,
            label=f"{label} ({tech})" if tech else label,
            source="diagram",
            confidence=1.0
        ))
    
    return graph