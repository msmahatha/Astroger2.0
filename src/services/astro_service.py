import asyncio
import logging
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage
from src.database.chroma_db import chromadb_retrieve
from config import OPENAI_API_KEY, OPENAI_MODEL, EMBED_MODEL, TOP_K, TEMPERATURE, MAX_TOKENS
from src.utils.helper import normalize_metadata, pack_retrieved_text, _unwrap_ai_message
from src.prompts.astro_prompt import get_comprehensive_prompt
from src.chat_memory.get_chat_history import (
    get_session_context,
    save_session_context,
    append_chat_turn,
)
from langchain_core.output_parsers import JsonOutputParser

# ---- Initialize LLM and Embeddings ----
llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=TEMPERATURE, max_tokens=MAX_TOKENS)

embeddings = OpenAIEmbeddings(model=EMBED_MODEL, api_key=OPENAI_API_KEY)

# ---------------- Output Parser ----------------
output_parser = JsonOutputParser()


# ---------------- Main Processing Methods ----------------
async def process_question_with_context(
    question: str,
    context: Optional[str] = None,
    religion: str = "hindu",
    session_id: Optional[str] = None,
    use_history: bool = False,
) -> dict:
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string.")

    try:
        
        data = {"question": question, "context": context or "", "religion": religion}

        # If session id provided and no explicit context, try to load session context
        if session_id and (not data.get("context") or use_history):
            session_ctx = get_session_context(session_id)
            if session_ctx:
                # Check if this is a returning conversation (has chat history)
                has_chat_history = "User:" in session_ctx and "AI:" in session_ctx
                # If explicit context existed, append session context for retrieval/use
                if data.get("context"):
                    if has_chat_history:
                        data["context"] = f"[RETURNING CONVERSATION - DO NOT GREET AGAIN]\n{data['context']}\n\n{session_ctx}"
                    else:
                        data["context"] = data["context"] + "\n\n" + session_ctx
                else:
                    if has_chat_history:
                        data["context"] = f"[RETURNING CONVERSATION - DO NOT GREET AGAIN]\n{session_ctx}"
                    else:
                        data["context"] = session_ctx

        # Step 1: Retrieval (question + context) concurrently
       
        tasks = [chromadb_retrieve(data["question"], TOP_K)]
        if data.get("context"):
            tasks.append(chromadb_retrieve(data["context"], TOP_K))
        else:
            tasks.append(asyncio.sleep(0, result=[]))  # dummy for alignment

        retrieved_docs_question, retrieved_docs_context = await asyncio.gather(*tasks)
        
        

        # Deduplicate retrieved docs
        combined_docs_map = {doc['text']: doc for doc in (retrieved_docs_question + retrieved_docs_context)}
        combined_docs = list(combined_docs_map.values())
        data["retrieved_docs"] = combined_docs
        data["retrieved_text"] = pack_retrieved_text(data["retrieved_docs"])
        data["context_block"] = f"Additional Context:\n{data['context']}" if data.get("context") else ""

    

        # Step 2: Generate comprehensive astrological consultation with AI-generated remedies
        combined_prompt = get_comprehensive_prompt(religion)
        
        human_msg = HumanMessage(content=combined_prompt.format(
            question=data["question"],
            retrieved_block=f"Retrieved Astrological Knowledge:\n{data['retrieved_text']}" if data["retrieved_text"] else "No specific knowledge retrieved. Use your expertise.",
            context_block=data["context_block"] if data["context_block"] else "No additional context provided."
        ))

        combined_response = await llm.agenerate([[human_msg]])
        combined_text = combined_response.generations[0][0].text
       
        logging.info(f"AI Response: {combined_text[:200]}...")

        # Step 3: Parse & validate JSON output
        try:
            # Clean the response if it has markdown code blocks
            clean_text = combined_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            parsed_output = output_parser.parse(clean_text)
            
            data["category"] = parsed_output.get("category", "General").title()
            data["answer"] = parsed_output.get("answer", "I sense important energies surrounding your question. Please allow me to provide deeper insight in a moment.")
            data["remedy"] = parsed_output.get("remedy", "Take time for reflection and meditation. Trust in the cosmic timing of your journey.")
            
        except Exception as e:
            logging.error(f"JSON parsing failed: {e}. Response: {combined_text[:500]}")
            # Fallback: try to extract from text
            data["category"] = "General"
            data["answer"] = _unwrap_ai_message(combined_text)
            data["remedy"] = "I recommend taking time for spiritual reflection and meditation to gain clarity on this matter."

        # Save chat turn to session store if session_id provided
        if session_id:
            try:
                append_chat_turn(session_id, question, data.get("answer") or _unwrap_ai_message(combined_text))
                # If user provided explicit context, persist it for future turns
                if context:
                    save_session_context(session_id, context)
            except Exception:
                pass

        return {
            "question": question,
            "category": data["category"],
            "answer": data["answer"],
            "remedy": data["remedy"],
            "retrieved_sources": [normalize_metadata(d.get("metadata")) for d in data.get("retrieved_docs", [])],
        }

    except Exception as e:
        logging.error(f"Error: {e}")
        raise


async def process_question(
    question: str,
    context: Optional[str] = None,
    religion: str = "hindu",
    session_id: Optional[str] = None,
    use_history: bool = False,
) -> dict:
    """
    Same as above but only question-based retrieval (no extra context)
    """
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string.")

    try:
        
        data = {"question": question, "context": context or "", "religion": religion}

        # populate session context if available
        if session_id and (not data.get("context") or use_history):
            session_ctx = get_session_context(session_id)
            if session_ctx:
                # Check if this is a returning conversation (has chat history)
                has_chat_history = "User:" in session_ctx and "AI:" in session_ctx
                if data.get("context"):
                    if has_chat_history:
                        data["context"] = f"[RETURNING CONVERSATION - DO NOT GREET AGAIN]\n{data['context']}\n\n{session_ctx}"
                    else:
                        data["context"] = data["context"] + "\n\n" + session_ctx
                else:
                    if has_chat_history:
                        data["context"] = f"[RETURNING CONVERSATION - DO NOT GREET AGAIN]\n{session_ctx}"
                    else:
                        data["context"] = session_ctx

        # Step 1: Retrieval (question only)
        
        retrieved_docs_question = await chromadb_retrieve(data["question"], TOP_K)
        
      

        data["retrieved_docs"] = retrieved_docs_question
        data["retrieved_text"] = pack_retrieved_text(data["retrieved_docs"])
        data["context_block"] = f"Additional Context:\n{data['context']}" if data.get("context") else ""

    

        # Step 2: Generate comprehensive astrological consultation with AI-generated remedies
        combined_prompt = get_comprehensive_prompt(religion)
      
        human_msg = HumanMessage(content=combined_prompt.format(
            question=data["question"],
            retrieved_block=f"Retrieved Astrological Knowledge:\n{data['retrieved_text']}" if data["retrieved_text"] else "No specific knowledge retrieved. Use your expertise.",
            context_block=data["context_block"] if data["context_block"] else "No additional context provided."
        ))

        combined_response = await llm.agenerate([[human_msg]])
        combined_text = combined_response.generations[0][0].text

        logging.info(f"AI Response: {combined_text[:200]}...")

        # Step 3: Parse & validate
        try:
            # Clean the response if it has markdown code blocks
            clean_text = combined_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            parsed_output = output_parser.parse(clean_text)
            
            data["category"] = parsed_output.get("category", "General").title()
            data["answer"] = parsed_output.get("answer", "I sense important energies surrounding your question. Please allow me to provide deeper insight in a moment.")
            data["remedy"] = parsed_output.get("remedy", "Take time for reflection and meditation. Trust in the cosmic timing of your journey.")
            
        except Exception as e:
            logging.error(f"JSON parsing failed: {e}. Response: {combined_text[:500]}")
            # Fallback: try to extract from text
            data["category"] = "General"
            data["answer"] = _unwrap_ai_message(combined_text)
            data["remedy"] = "I recommend taking time for spiritual reflection and meditation to gain clarity on this matter."

        # Save chat turn to session store if session_id provided
        if session_id:
            try:
                append_chat_turn(session_id, question, data.get("answer") or _unwrap_ai_message(combined_text))
                if context:
                    save_session_context(session_id, context)
            except Exception:
                pass

        return {
            "question": question,
            "category": data["category"],
            "answer": data["answer"],
            "remedy": data["remedy"],
            "retrieved_sources": [normalize_metadata(d.get("metadata")) for d in data.get("retrieved_docs", [])],
        }

    except Exception as e:
        logging.error(f"Error: {e}")
        raise