# schema.py
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any

class GraphNode(BaseModel):
    id: str = Field(description="ID duy nhất, vd: 'order-service-01'")
    name: str = Field(description="Tên hiển thị, vd: 'Order Service'")
    type: Literal["service", "database", "ui", "queue", "cache", "external_system", "actor"]
    c4_level: Literal["context", "container", "component", "code"] = "container"
    properties: Dict[str, Any] = Field(default_factory=dict)
    source: Literal["diagram", "text", "inferred"] = "diagram"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: Optional[str] = None

class GraphEdge(BaseModel):
    id: str
    source_id: str
    target_id: str
    relationship_type: Literal["sync_call", "async_call", "data_flow", "dependency", "contains"]
    label: Optional[str] = None
    source: Literal["diagram", "text", "inferred"] = "diagram"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class ArchitectureGraph(BaseModel):
    schema_version: str = "1.0.0"
    system_name: str = "Extracted System"
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)