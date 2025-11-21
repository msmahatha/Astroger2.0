import asyncio
import logging
import os
import httpx
import re
from typing import Optional, List, Dict, Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage
from langchain_core.output_parsers import JsonOutputParser

# Custom Imports (Assumed to exist based on context)
ASTROLOGY_API_USER_ID = os.getenv("ASTROLOGY_API_USER_ID")
ASTROLOGY_API_KEY = os.getenv("ASTROLOGY_API_KEY")
ASTROLOGY_API_BASE_URL = "https://json.astrologyapi.com/v1/"  # Example base URL
from src.database.chroma_db import chromadb_retrieve
from config import OPENAI_API_KEY, OPENAI_MODEL, EMBED_MODEL, TOP_K, TEMPERATURE, MAX_TOKENS
from src.utils.helper import normalize_metadata, pack_retrieved_text, _unwrap_ai_message
from src.prompts.astro_prompt import get_comprehensive_prompt
from src.chat_memory.get_chat_history import (
    get_session_context,
    save_session_context,
    append_chat_turn,
)

# ---- Configuration & Constants ----

REMEDY_KEYWORDS = [
    "remedy", "remedies", "send remedy", "pls remedy", "please remedy", 
    "upay", "totke", "totka", "solution", "solutions", "help", 
    "solve", "fix", "what to do", "what should i do"
]

FORBIDDEN_PERSONA_PHRASES = [
    "digital astrologer", "friendly digital astrologer",
    "I am an AI", "I am a bot", "I am a language model",
    "virtual assistant", "artificial intelligence"
]

DEFAULT_FALLBACK_REMEDY = (
    "For spiritual wellbeing and peace of mind, practice daily meditation and "
    "recitation of sacred texts from your faith tradition. Engage in regular acts "
    "of charity and service to others. Maintain positive thoughts and actions "
    "aligned with your beliefs. These practices will bring clarity and inner "
    "strength during this period."
)

# ---- Initialize LLM ----
llm = ChatOpenAI(
    model=OPENAI_MODEL, 
    api_key=OPENAI_API_KEY, 
    temperature=TEMPERATURE, 
    max_tokens=MAX_TOKENS
)

embeddings = OpenAIEmbeddings(model=EMBED_MODEL, api_key=OPENAI_API_KEY)
output_parser = JsonOutputParser()


# ---------------- Helper Functions ----------------

async def get_astrologyapi_remedy(question: str, birth_details: dict = None) -> str:
    """
    Calls AstrologyAPI.com for remedy or answer. You can expand birth_details as needed.
    """
    # Example endpoint: /remedies
    endpoint = f"{ASTROLOGY_API_BASE_URL}remedies"
    payload = {"question": question}
    if birth_details:
        payload.update(birth_details)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                endpoint,
                json=payload,
                auth=(ASTROLOGY_API_USER_ID, ASTROLOGY_API_KEY),
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            # You may need to adjust parsing based on actual API response
            return data.get("remedy") or data.get("answer") or str(data)
        except Exception as e:
            logging.error(f"AstrologyAPI.com call failed: {e}")
            return "Sorry, unable to fetch remedy from AstrologyAPI.com at this time."

def _clean_json_string(text: str) -> str:
    """
    Cleans LLM response to ensure it is valid JSON, removing Markdown wrappers.
    """
    clean_text = text.strip()
    # Remove markdown code blocks
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    
    clean_text = clean_text.strip()
    
    # Find the start of the JSON object
    json_start = clean_text.find('{')
    if json_start != -1:
        clean_text = clean_text[json_start:]
        
    return clean_text

def validate_and_fix_persona(text: str) -> str:
    """
    Post-processing safety check to ensure the AI maintains the Astrologer persona.
    """
    if not text: 
        return ""
        
    lower_text = text.lower()
    for phrase in FORBIDDEN_PERSONA_PHRASES:
        if phrase in lower_text:
            # If response is short/generic identification, replace entirely
            if len(text) < 200:
                return "Namaste! I am Digvesh Dube, your astrological guide from Prayagraj. How can I assist you today?"
            
            # Otherwise, perform surgical replacement
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            text = pattern.sub("your astrologer", text)
            
    return text

async def _retrieve_knowledge(question: str, context: str, include_context_search: bool) -> str:
    """
    Handles the asynchronous retrieval from ChromaDB.
    """
    tasks = [chromadb_retrieve(question, TOP_K)]
    
    if include_context_search and context:
        tasks.append(chromadb_retrieve(context, TOP_K))
    else:
        # dummy task to keep unpacking consistent if no context search needed
        tasks.append(asyncio.sleep(0, result=[]))

    retrieved_docs_question, retrieved_docs_context = await asyncio.gather(*tasks)
    
    # Deduplicate docs based on content
    combined_docs_map = {doc['text']: doc for doc in (retrieved_docs_question + retrieved_docs_context)}
    combined_docs = list(combined_docs_map.values())
    
    return pack_retrieved_text(combined_docs), combined_docs

# ---------------- Core Logic ----------------

async def _core_process(
    question: str,
    context: Optional[str],
    religion: str,
    session_id: Optional[str],
    user_name: Optional[str],
    perform_context_retrieval: bool
) -> dict:
    """
    Unified logic handler for both public processing functions.
    """
    # 1. Setup Context & Session
    final_context = context or ""
    
    if session_id:
        session_ctx = get_session_context(session_id)
        if session_ctx:
            has_history = "User:" in session_ctx and "AI:" in session_ctx
            prefix = "[RETURNING CONVERSATION - DO NOT GREET AGAIN]\n" if has_history else ""
            
            if final_context:
                final_context = f"{prefix}{final_context}\n\n{session_ctx}"
            else:
                final_context = f"{prefix}{session_ctx}"

    # 2. Retrieval
    retrieved_text, retrieved_docs = await _retrieve_knowledge(
        question, final_context, perform_context_retrieval
    )

    # 3. Build Prompt Context Block
    context_parts = []
    if user_name:
        context_parts.append(f"User Name: {user_name}")
    if final_context:
        context_parts.append(f"Additional Context:\n{final_context}")
    
    context_block = "\n".join(context_parts)


    # 4. Remedy Detection Logic & API/AI Switch
    question_lower = question.lower()
    needs_remedy = any(k in question_lower for k in REMEDY_KEYWORDS)
    wants_api = any(k in question_lower for k in ["astroapi", "astrologyapi", "official api", "use api", "external api"])

    logging.info(f"Processing Question: '{question[:50]}...' | Needs Remedy: {needs_remedy} | Wants API: {wants_api}")

    # Always use AstrologyAPI.com for the main response
    birth_details = {}  # You can expand this from context/user input
    api_response = await get_astrologyapi_remedy(question, birth_details)

    # Now, use GPT to rephrase the API response in a human, conversational style
    gpt_prompt = (
        f"You are an expert astrologer. Rephrase the following astrology API response in a friendly, human, and conversational manner for the user.\n"
        f"API Response: {api_response}\n"
        f"User Name: {user_name if user_name else 'User'}\n"
        f"Question: {question}\n"
        f"If the API response is too technical or short, expand it with practical advice and empathy."
    )
    human_msg = HumanMessage(content=gpt_prompt)
    gpt_response = await llm.agenerate([[human_msg]])
    final_text = gpt_response.generations[0][0].text.strip()

    return {
        "question": question,
        "category": "AstrologyAPI.com + GPT",
        "answer": final_text,
        "remedy": final_text,
        "retrieved_sources": [],
    }

    # 5. Generate Initial Response
    prompt_template = get_comprehensive_prompt(religion)
    human_msg = HumanMessage(content=prompt_template.format(
        question=question,
        retrieved_block=f"Retrieved Astrological Knowledge:\n{retrieved_text}" if retrieved_text else "No specific knowledge retrieved. Use your expertise.",
        context_block=context_block if context_block else "No additional context provided."
    ))

    combined_response = await llm.agenerate([[human_msg]])
    raw_text = combined_response.generations[0][0].text
    logging.debug(f"Raw AI Response: {raw_text[:200]}...")

    # 6. Parse Output
    data = {"category": "General", "answer": "", "remedy": ""}
    
    try:
        clean_text = _clean_json_string(raw_text)
        parsed = output_parser.parse(clean_text)
        
        data["category"] = parsed.get("category", "General").title()
        data["answer"] = parsed.get("answer", "I sense important energies surrounding your question.")
        data["remedy"] = parsed.get("remedy", "")
        
        # 7. Remedy Retry Logic (The "Furious" Prompt)
        # Check if user wanted remedy, but AI failed to provide it in the specific field
        remedy_is_empty = not data["remedy"] or len(data["remedy"].strip()) < 10
        answer_mentions_remedy = any(x in data["answer"].lower() for x in ["here are remedies", "suggest remedies"])
        
        if needs_remedy and (remedy_is_empty or (answer_mentions_remedy and remedy_is_empty)):
            logging.warning("Remedy requested but missing. Triggering Force Prompt.")
            
            force_prompt = f"""[CRITICAL SYSTEM OVERRIDE]
The user wants {religion.upper()} remedies NOW. You said "here are remedies" but provided NOTHING in the remedy field.

You MUST generate comprehensive remedies following this structure:
DOS (Practices to follow):
1. [Specific practice with exact details]
2. [Another practice]

DON'TS (Things to avoid):
1. [Specific thing to avoid]

CHARITY (Donations/Service):
1. [Specific charity with details]

Generate NOW. No more delays. No more empty fields."""
            
            retry_res = await llm.agenerate([[HumanMessage(content=force_prompt)]])
            data["remedy"] = retry_res.generations[0][0].text.strip()

    except Exception as e:
        logging.error(f"JSON Parsing or Retry Failed: {e}")
        # Soft Fallback if JSON fails
        data["answer"] = _unwrap_ai_message(raw_text)

    # 8. Final Fallbacks & Cleanup
    if needs_remedy and (not data["remedy"] or len(data["remedy"]) < 10):
        logging.warning("Applying Hard Fallback Remedy.")
        data["remedy"] = DEFAULT_FALLBACK_REMEDY

    # Logic: If we have a good remedy, clear the 'answer' to avoid redundancy (UI specific preference)
    if data["remedy"] and len(data["remedy"]) > 20:
        data["answer"] = ""

    data["answer"] = validate_and_fix_persona(data["answer"])

    # 9. Save Session
    if session_id:
        try:
            # We save the text visible to the user (either answer or remedy)
            final_visible_text = data.get("answer") or data.get("remedy")
            append_chat_turn(session_id, question, final_visible_text)
            
            # Update context if specifically required by the calling logic
            if context and perform_context_retrieval: 
                save_session_context(session_id, context)
        except Exception as e:
            logging.error(f"Session Save Failed: {e}")

    return {
        "question": question,
        "category": data["category"],
        "answer": data["answer"],
        "remedy": data["remedy"],
        "retrieved_sources": [normalize_metadata(d.get("metadata")) for d in retrieved_docs],
    }


# ---------------- Public Interface ----------------

async def process_question_with_context(
    question: str,
    context: Optional[str] = None,
    religion: str = "hindu",
    session_id: Optional[str] = None,
    use_history: bool = False,
    user_name: Optional[str] = None,
) -> dict:
    """
    Processes a question where the provided 'context' string is treated as 
    searchable knowledge (retrieved against) alongside the question.
    """
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string.")

    return await _core_process(
        question=question,
        context=context,
        religion=religion,
        session_id=session_id,
        user_name=user_name,
        perform_context_retrieval=True # Explicitly retrieve based on context
    )


async def process_question(
    question: str,
    context: Optional[str] = None,
    religion: str = "hindu",
    session_id: Optional[str] = None,
    use_history: bool = False,
    user_name: Optional[str] = None,
) -> dict:
    """
    Processes a question where 'context' is treated purely as prompt background info,
    NOT as a query for the vector database.
    """
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string.")

    return await _core_process(
        question=question,
        context=context,
        religion=religion,
        session_id=session_id,
        user_name=user_name,
        perform_context_retrieval=False # Do NOT retrieve based on context
    )