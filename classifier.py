# classifier.py
import os

def classify_file(filename: str, content: str = None) -> str:
    """Phân loại file dựa trên phần mở rộng."""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in ['.puml', '.dsl', '.mermaid']:
        return "structured-text"
    elif ext in ['.png', '.jpg', '.jpeg', '.svg']:
        return "diagram-image"
    elif ext in ['.md', '.txt', '.docx', '.pdf']:
        return "narrative-doc"
    else:
        # Fallback: Nếu không rõ, dựa vào nội dung
        if content and "@startuml" in content:
            return "structured-text"
        return "unknown"