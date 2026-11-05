# agent.py
import asyncio
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from schema import ArchitectureGraph
from classifier import classify_file
from extractors.plantuml_parser import extract_from_plantuml
from extractors.vision_extractor import extract_from_image
from extractors.text_extractor import extract_from_text
from merger import merge_graphs

# 1. Định nghĩa State cho LangGraph
class AgentState(TypedDict):
    inputs: List[Dict[str, Any]] # List các file: {'name': '...', 'content': '...', 'bytes': b'...'}
    extracted_graphs: List[ArchitectureGraph]
    final_graph: ArchitectureGraph
    errors: List[str]

# 2. Định nghĩa các Node (Hàm thuần)

async def node_classify_and_extract(state: AgentState, config: RunnableConfig) -> dict:
    """Node này chạy song song các extractor."""
    client = config.get("configurable", {}).get("llm_client")
    tasks = []
    
    for f in state["inputs"]:
        kind = classify_file(f["name"], f.get("content"))
        
        if kind == "structured-text":
            # PlantUML là hàm sync, chạy bình thường
            tasks.append(asyncio.to_thread(extract_from_plantuml, f["content"]))
        elif kind == "diagram-image":
            tasks.append(extract_from_image(f["bytes"], client))
        elif kind == "narrative-doc":
            tasks.append(extract_from_text(f["content"], client))
            
    # Chạy tất cả các tác vụ song song
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    extracted = []
    errors = []
    for res in results:
        if isinstance(res, ArchitectureGraph):
            extracted.append(res)
        else:
            errors.append(str(res))
            
    return {"extracted_graphs": extracted, "errors": state.get("errors", []) + errors}

def node_merge(state: AgentState) -> dict:
    """Node gộp kết quả."""
    if not state["extracted_graphs"]:
        return {"final_graph": ArchitectureGraph(warnings=["No valid data extracted"])}
    
    merged = merge_graphs(state["extracted_graphs"])
    merged.warnings.extend(state["errors"]) # Gắn lỗi vào cảnh báo của graph
    return {"final_graph": merged}

# 3. Xây dựng Đồ thị (StateGraph)
workflow = StateGraph(AgentState)

workflow.add_node("extract", node_classify_and_extract)
workflow.add_node("merge", node_merge)

workflow.set_entry_point("extract")
workflow.add_edge("extract", "merge")
workflow.add_edge("merge", END)

# Compile graph
app_graph = workflow.compile()

# 4. Class Wrapper để dễ sử dụng
class ArchitectureExtractionAgent:
    def __init__(self, llm_client):
        self.client = llm_client

    async def run(self, inputs: List[Dict[str, Any]]) -> ArchitectureGraph:
        # Chạy LangGraph với config chứa LLM client
        initial_state = {"inputs": inputs, "extracted_graphs": [], "errors": []}
        result = await app_graph.ainvoke(
            initial_state, 
            config={"configurable": {"llm_client": self.client}}
        )
        return result["final_graph"]