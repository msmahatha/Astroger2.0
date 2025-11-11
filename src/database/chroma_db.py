import chromadb
import asyncio
from typing import  List, Dict, Any
from config import CHROMADB_API_KEY, CHROMADB_TENANT, CHROMADB_DB_NAME, COLLECTION_NAME , TOP_K , EMBED_MODEL, OPENAI_API_KEY
from src.utils.helper import normalize_metadata
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ---- Validations ----
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment.")

if not CHROMADB_API_KEY or not CHROMADB_TENANT:
    raise RuntimeError("Missing ChromaDB Cloud credentials.")

# -- Global clients initialized once --

chromadb_client = chromadb.CloudClient(
    api_key=CHROMADB_API_KEY,
    tenant=CHROMADB_TENANT,
    database=CHROMADB_DB_NAME,
)

chromadb_collection = chromadb_client.get_or_create_collection(COLLECTION_NAME)


embeddings = OpenAIEmbeddings(model=EMBED_MODEL, api_key=OPENAI_API_KEY)

async def chromadb_retrieve(question: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    try:
        def sync_call():
            q_vec = embeddings.embed_query(question)

            results = chromadb_collection.query(
                query_embeddings=[q_vec],
                n_results=top_k,
                include=["documents", "metadatas"],
            )

            docs_list = results.get("documents") or [[]]
            metas_list = results.get("metadatas") or [[]]
            docs0 = docs_list[0] if docs_list else []
            metas0 = metas_list[0] if metas_list else []

            out: List[Dict[str, Any]] = []
            for doc_text, meta in zip(docs0, metas0):
                out.append({"text": doc_text, "metadata": normalize_metadata(meta)})
            return out

        return await asyncio.to_thread(sync_call)

    except Exception as e:
        raise RuntimeError(f"Chroma (cloud) retrieval failed: {e}")
