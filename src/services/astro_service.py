import asyncio
import logging
import os
import httpx
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
def test_kundali_api():
    # Example birth details for testing
    birth_details = {
        "birthDate": "16 January 2002",
        "birthTime": "19:44",
        "birthLatitude": 22.5743545,
        "birthLongitude": 88.3628734
    }
    question = "Show my kundali"
    import asyncio
    result = asyncio.run(get_astrologyapi_remedy(question, birth_details))
    print("API Response:", result)

if __name__ == "__main__":
    test_kundali_api()
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

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
from src.services.kundli import calculate_vimshottari_dasha, parse_birth_datetime

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
    Calls AstrologyAPI.com for comprehensive kundali or remedy.
    For kundali requests, fetches multiple endpoints and formats beautifully.
    """
    # Determine if this is a kundali request
    kundali_keywords = ["kundali", "birth chart", "janam kundali", "natal chart", "kundli", "horoscope chart"]
    is_kundali_request = any(k in question.lower() for k in kundali_keywords)
    
    # Parse birth details
    try:
        if not birth_details:
            return "Please provide your complete birth details (date, time, and place) to generate your kundali."
        
        date_parts = birth_details.get("birthDate", "").strip().split()
        if not date_parts or len(date_parts) < 3:
            return "Please provide your complete birth date in format: DD Month YYYY (e.g., 02 February 1996)"
        
        day = int(date_parts[0]) if date_parts[0] else 1
        month = 1
        year = 2000
        
        if len(date_parts) == 3:
            month_str = date_parts[1].lower()
            month_map = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}
            month = month_map.get(month_str, 1)
            year = int(date_parts[2]) if date_parts[2] else 2000
        
        time_str = birth_details.get("birthTime", "").strip()
        if not time_str or ":" not in time_str:
            return "Please provide your birth time in format: HH:MM (e.g., 01:19)"
        
        time_parts = time_str.split(":")
        hour = int(time_parts[0]) if time_parts[0] else 0
        minute = int(time_parts[1]) if len(time_parts) > 1 and time_parts[1] else 0
        
        lat = float(birth_details.get("birthLatitude", 0))
        lon = float(birth_details.get("birthLongitude", 0))
        
        if lat == 0 and lon == 0:
            return "Please provide your birth place with valid coordinates."
        
        place = birth_details.get("birthPlace", "Unknown")
        tzone = 5.5  # Default to IST
        
        payload = {
            "day": day,
            "month": month,
            "year": year,
            "hour": hour,
            "min": minute,
            "lat": lat,
            "lon": lon,
            "tzone": tzone
        }
        logging.info(f"AstrologyAPI Payload: {payload}")
    except (ValueError, AttributeError, KeyError) as e:
        logging.error(f"Failed to parse birth details: {e}")
        return "Unable to parse birth details. Please ensure you've provided complete information: birth date (DD Month YYYY), time (HH:MM), and place."
    
    async with httpx.AsyncClient() as client:
        try:
            if is_kundali_request:
                # Fetch comprehensive kundali data from multiple endpoints
                kundali_parts = []
                
                # 1. Birth Details
                try:
                    resp = await client.post(f"{ASTROLOGY_API_BASE_URL}birth_details", json=payload, auth=(ASTROLOGY_API_USER_ID, ASTROLOGY_API_KEY), timeout=10.0)
                    birth_data = resp.json()
                    kundali_parts.append(f"📋 BIRTH DETAILS\n")
                    kundali_parts.append(f"Date: {day:02d}/{month:02d}/{year}\n")
                    kundali_parts.append(f"Time: {hour:02d}:{minute:02d}\n")
                    kundali_parts.append(f"Place: {place}\n")
                    kundali_parts.append(f"Ayanamsha: {birth_data.get('ayanamsha', 'N/A')}\n")
                    kundali_parts.append(f"Sunrise: {birth_data.get('sunrise', 'N/A')}\n")
                    kundali_parts.append(f"Sunset: {birth_data.get('sunset', 'N/A')}\n\n")
                except Exception as e:
                    logging.error(f"Birth Details API failed: {e}")
                    pass

                # 2. Planets
                try:
                    resp = await client.post(f"{ASTROLOGY_API_BASE_URL}planets", json=payload, auth=(ASTROLOGY_API_USER_ID, ASTROLOGY_API_KEY), timeout=10.0)
                    planets_data = resp.json()
                    kundali_parts.append(f"🌟 PLANETARY POSITIONS\n\n")
                    
                    # Ascendant
                    for p in planets_data:
                        if p.get("name") == "Ascendant":
                            kundali_parts.append(f"🔺 ASCENDANT (LAGNA): {p.get('sign')} at {p.get('normDegree'):.2f}°\n")
                            kundali_parts.append(f"   Nakshatra: {p.get('nakshatra')} (Pada {p.get('nakshatra_pad')})\n\n")
                            break
                    
                    # Other Planets
                    for p in planets_data:
                        if p.get("name") != "Ascendant":
                            retro = " (R)" if p.get("isRetro") == "true" else ""
                            kundali_parts.append(f"{p.get('name')}: {p.get('sign')} {p.get('normDegree'):.2f}° - {p.get('nakshatra')}{retro}\n")
                    kundali_parts.append("\n")
                except Exception as e:
                    logging.error(f"Planets API failed: {e}")
                    pass

                # 3. Current Dasha
                try:
                    resp = await client.post(f"{ASTROLOGY_API_BASE_URL}current_vdasha", json=payload, auth=(ASTROLOGY_API_USER_ID, ASTROLOGY_API_KEY), timeout=10.0)
                    dasha_data = resp.json()
                    
                    kundali_parts.append(f"⏰ CURRENT VIMSHOTTARI DASHA\n\n")
                    
                    # Check if response has 'major', 'minor' keys directly
                    if dasha_data and 'major' in dasha_data:
                        major = dasha_data.get('major', {})
                        minor = dasha_data.get('minor', {})
                        sub_minor = dasha_data.get('sub_minor', {})
                        
                        kundali_parts.append(f"Maha Dasha: {major.get('planet')} ({major.get('start')} to {major.get('end')})\n")
                        kundali_parts.append(f"Antar Dasha: {minor.get('planet')} ({minor.get('start')} to {minor.get('end')})\n")
                        kundali_parts.append(f"Pratyantar: {sub_minor.get('planet')} ({sub_minor.get('start')} to {sub_minor.get('end')})\n\n")
                    
                    # Fallback to old structure if needed
                    elif dasha_data.get("current_dasha"):
                        current_dasha = dasha_data.get("current_dasha", {})
                        kundali_parts.append(f"Maha Dasha: {current_dasha.get('major_dasha')} ({current_dasha.get('start_date')} to {current_dasha.get('end_date')})\n")
                        kundali_parts.append(f"Antar Dasha: {current_dasha.get('minor_dasha')}\n")
                        kundali_parts.append(f"Pratyantar: {current_dasha.get('sub_minor_dasha')}\n\n")

                except Exception as e:
                    logging.error(f"Dasha API failed: {e}")
                    pass

                # 3.5 Major Maha Dasha (Local Calculation)
                try:
                    # Find Moon's longitude from planets data
                    moon_long = None
                    if 'planets_data' in locals() and planets_data:
                        for p in planets_data:
                            if p.get("name") == "Moon":
                                moon_long = p.get("normDegree")
                                break
                    
                    if moon_long is not None:
                        # Parse birth datetime
                        birth_dt = parse_birth_datetime(f"{day:02d}-{month:02d}-{year}", f"{hour:02d}:{minute:02d}")
                        
                        # Calculate Dasha
                        major_dashas = calculate_vimshottari_dasha(moon_long, birth_dt)
                        
                        kundali_parts.append(f"🗓️ MAJOR MAHA DASHA PERIODS\n\n")
                        for dasha in major_dashas:
                            # Handle both dict and object (DashaPeriod)
                            planet = getattr(dasha, 'planet', None) or dasha.get('planet')
                            start = getattr(dasha, 'start_date', None) or dasha.get('start_date')
                            end = getattr(dasha, 'end_date', None) or dasha.get('end_date')
                            
                            kundali_parts.append(f"{planet}: {start} to {end}\n")
                        kundali_parts.append("\n")
                    else:
                        logging.warning("Moon longitude not found for Dasha calculation")

                except Exception as e:
                    logging.error(f"Major Dasha calculation failed: {e}")
                    pass

                # 4. Rashi Chart (D1)
                try:
                    resp = await client.post(f"{ASTROLOGY_API_BASE_URL}horo_chart/D1", json=payload, auth=(ASTROLOGY_API_USER_ID, ASTROLOGY_API_KEY), timeout=10.0)
                    chart_data = resp.json()
                    kundali_parts.append(f"📊 RASHI CHART (D1)\n\n")
                    for house in chart_data:
                        planets_in_house = house.get("planet", [])
                        if planets_in_house:
                            planets_str = ", ".join(planets_in_house).upper()
                            kundali_parts.append(f"{house['sign_name']}: {planets_str}\n")
                    kundali_parts.append("\n")
                except Exception as e:
                    logging.error(f"Chart API failed: {e}")
                    pass
                
                final_kundali = "".join(kundali_parts)
                return final_kundali if kundali_parts else "Unable to generate complete kundali at this time."
            
            else:
                # For non-kundali requests (remedies, etc.)
                endpoint = f"{ASTROLOGY_API_BASE_URL}remedies"
                payload["question"] = question
                
                response = await client.post(endpoint, json=payload, auth=(ASTROLOGY_API_USER_ID, ASTROLOGY_API_KEY), timeout=10.0)
                response.raise_for_status()
                data = response.json()
                return data.get("remedy") or data.get("answer") or str(data)
                
        except Exception as e:
            logging.error(f"AstrologyAPI.com call failed: {e}")
            return "Sorry, unable to fetch astrological details at this time."

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
    perform_context_retrieval: bool,
    user_info: Optional[dict] = None
) -> dict:
    """
    Unified logic handler for both public processing functions.
    """
    # 1. Setup Context & Session
    final_context = context or ""
    context_block = ""  # Initialize early to avoid NameError
    
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
    
    context_block = "\n".join(context_parts) if context_parts else ""



    # 4. Detect Question Type & Extract Birth Details
    question_lower = question.lower()
    needs_remedy = any(k in question_lower for k in REMEDY_KEYWORDS)
    
    astrology_keywords = [
        "kundali", "birth chart", "janam kundali", "natal chart", "remedy", "astrology", 
        "planet", "dasha", "lagna", "horoscope", "zodiac", "graha", "nakshatra", "rashi", 
        "upay", "totka", "totke"
    ]
    is_astrology_question = any(k in question.lower() for k in astrology_keywords)

    logging.info(f"Processing Question: '{question[:50]}...' | Astrology: {is_astrology_question} | Needs Remedy: {needs_remedy}")

    # Extract birth details from context if available
    # Extract birth details from user_info (preferred) or context
    birth_details = {}
    
    # Priority 1: Use structured user_info if available
    if user_info and isinstance(user_info, dict):
        birth_fields = ["birthDate", "birthTime", "birthPlace", "birthLatitude", "birthLongitude"]
        for field in birth_fields:
            if field in user_info:
                birth_details[field] = user_info[field]
        logging.info(f"Extracted birth details from user_info: {birth_details}")
        
    # Priority 2: Fallback to context if birth details missing
    if not birth_details and context and isinstance(context, dict):
        birth_fields = ["birthDate", "birthTime", "birthPlace", "birthLatitude", "birthLongitude"]
        for field in birth_fields:
            if field in context:
                birth_details[field] = context[field]
        logging.info(f"Extracted birth details from context: {birth_details}")

    # 5. Get AstrologyAPI.com Response (if astrology question) as enrichment
    api_enrichment = ""
    kundali_keywords = ["kundali", "kundli", "birth chart", "janam kundali", "natal chart", "horoscope chart"]
    is_kundali_request = any(k in question.lower() for k in kundali_keywords)
    
    if is_astrology_question:
        try:
            api_response = await get_astrologyapi_remedy(question, birth_details)
            
            # For kundali requests, return the formatted data directly
            if is_kundali_request and api_response and len(api_response) > 200:
                logging.info("Returning kundali data directly")
                return {
                    "question": question,
                    "category": "Kundali",
                    "answer": api_response,
                    "remedy": "",
                    "retrieved_sources": [normalize_metadata(d.get("metadata")) for d in retrieved_docs],
                }
            
            api_enrichment = f"\n\nAstrologyAPI.com Data:\n{api_response}"
            logging.info("Successfully retrieved AstrologyAPI.com data")
        except Exception as e:
            logging.warning(f"AstrologyAPI.com call failed, continuing with ChromaDB only: {e}")
            api_enrichment = ""

    # 6. Build Enhanced Retrieved Block (ChromaDB + AstrologyAPI.com)
    enhanced_retrieved_block = retrieved_text
    if api_enrichment:
        enhanced_retrieved_block = f"{retrieved_text}\n{api_enrichment}" if retrieved_text else api_enrichment
    
    if not enhanced_retrieved_block:
        enhanced_retrieved_block = "No specific knowledge retrieved. Use your expertise."

    # 7. Generate Response using Comprehensive Prompt
    user_language = user_info.get("language") if user_info else None
    prompt_template = get_comprehensive_prompt(religion, user_language)
    human_msg = HumanMessage(content=prompt_template.format(
        question=question,
        retrieved_block=f"Retrieved Astrological Knowledge:\n{enhanced_retrieved_block}",
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
    data["remedy"] = validate_and_fix_persona(data["remedy"])

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
    user_info: Optional[dict] = None,
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
        perform_context_retrieval=True, # Explicitly retrieve based on context
        user_info=user_info
    )


async def process_question(
    question: str,
    context: Optional[str] = None,
    religion: str = "hindu",
    session_id: Optional[str] = None,
    use_history: bool = False,
    user_name: Optional[str] = None,
    user_info: Optional[dict] = None,
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
        perform_context_retrieval=False, # Do NOT retrieve based on context
        user_info=user_info
    )