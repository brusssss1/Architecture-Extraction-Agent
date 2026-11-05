# merger.py
from schema import ArchitectureGraph, GraphNode, GraphEdge
from typing import List
from rapidfuzz import fuzz  # Thư viện fuzzy matching (pip install rapidfuzz)

def merge_graphs(graphs: List[ArchitectureGraph]) -> ArchitectureGraph:
    """Gộp đồ thị với fuzzy matching để tránh trùng lặp."""
    final = ArchitectureGraph(system_name="Merged Architecture")
    
    # Bước 1: Gộp Nodes với Fuzzy Matching
    merged_nodes = {}
    
    for g in graphs:
        for node in g.nodes:
            # Tìm node đã có với tên tương tự (>= 85% giống nhau)
            duplicate_key = None
            for existing_key, existing_node in merged_nodes.items():
                similarity = fuzz.ratio(node.name.lower(), existing_node.name.lower())
                if similarity >= 85:  # Ngưỡng 85%
                    duplicate_key = existing_key
                    break
            
            if duplicate_key:
                # Đã tồn tại -> Hợp nhất (ưu tiên diagram vì chính xác hơn)
                existing = merged_nodes[duplicate_key]
                if node.source == "diagram" and existing.source == "text":
                    # Ghi đè bằng diagram nhưng giữ evidence từ text
                    node.evidence = existing.evidence
                    merged_nodes[duplicate_key] = node
                    final.warnings.append(f"Node '{node.name}' được ưu tiên từ diagram.")
            else:
                merged_nodes[node.id] = node
    
    final.nodes = list(merged_nodes.values())
    
    # Bước 2: Gộp Edges (chỉ giữ những edge có source_id/target_id tồn tại)
    valid_ids = {n.id for n in final.nodes}
    seen_edges = set()  # Tránh trùng edge
    
    for g in graphs:
        for edge in g.edges:
            # Map lại ID nếu tên bị đổi (do fuzzy matching)
            # (Đơn giản hóa: giả sử ID không đổi)
            edge_key = (edge.source_id, edge.target_id, edge.relationship_type)
            if edge_key in seen_edges:
                continue
                
            if edge.source_id in valid_ids and edge.target_id in valid_ids:
                final.edges.append(edge)
                seen_edges.add(edge_key)
            else:
                final.warnings.append(f"Edge {edge.id} bị loại vì thiếu node.")
    
    return final