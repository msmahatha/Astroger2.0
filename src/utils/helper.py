from typing import Optional, List, Dict, Any
from langchain_core.messages import AIMessage



def _unwrap_ai_message(x: Any) -> str:
    """Extracts and cleans content from an AIMessage or converts other types to string."""
    if isinstance(x, AIMessage):
        return (x.content or "").strip()
    return str(x).strip()





def normalize_metadata(meta: Any) -> Dict[str, Any]:
    """Normalizes metadata into a consistent dictionary format."""
    if meta is None:
        return {}
    if isinstance(meta, dict):
        return meta
    if isinstance(meta, list):
        return {f"m_{i}": v for i, v in enumerate(meta)}
    if isinstance(meta, (str, int, float, bool)):
        return {"value": meta}
    try:
        return dict(meta)
    except Exception:
        return {"value": str(meta)}
    
    
    
def pack_retrieved_text(docs: List[Dict[str, Any]]) -> str:
    """Formats retrieved documents into a single text block."""
    if not docs:
        return ""
    lines = []
    for d in docs:
        meta = normalize_metadata(d.get("metadata"))
        title = meta.get("title", "Doc")
        text = d.get("text", "")
        lines.append(f"{title}: {text}")
    return "\n\n".join(lines)

