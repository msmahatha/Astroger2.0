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
    user_name: Optional[str] = None,
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
        
        # Build context_block with user_name if provided
        context_parts = []
        if user_name:
            context_parts.append(f"User Name: {user_name}")
        if data.get("context"):
            context_parts.append(f"Additional Context:\n{data['context']}")
        data["context_block"] = "\n".join(context_parts) if context_parts else ""

    

        # Step 2: Generate comprehensive astrological consultation with AI-generated remedies
        combined_prompt = get_comprehensive_prompt(religion)
        
        # SIMPLE REMEDY DETECTION - Check if user is requesting remedies
        remedy_should_be_provided = False
        question_lower = data["question"].lower()
        
        # Check if user explicitly asked for remedy
        remedy_keywords = ["remedy", "remedies", "send remedy", "pls remedy", "please remedy", 
                          "upay", "totke", "totka", "solution", "solutions", "help", 
                          "solve", "fix", "what to do", "what should i do"]
        
        has_remedy_keyword = any(keyword in question_lower for keyword in remedy_keywords)
        
        logging.warning(f"[WITH_CONTEXT] DEBUG KEYWORD: question_lower='{question_lower}', has_remedy_keyword={has_remedy_keyword}")
        
        if has_remedy_keyword:
            remedy_should_be_provided = True
        
        logging.warning(f"[WITH_CONTEXT] DEBUG REMEDY FLAG: remedy_should_be_provided={remedy_should_be_provided}")
        
        # Inject mandatory system signal if remedy should be provided
        if remedy_should_be_provided:
            system_override = f"\n\n[CRITICAL SYSTEM OVERRIDE - IMMEDIATE ACTION REQUIRED]\nUser is asking for remedies. You are now in STAGE 3 (REMEDIES MODE).\nYou MUST:\n1. Set answer field to EMPTY STRING: \"\"\n2. Populate remedy field with comprehensive, practical remedies\n3. Do NOT use 'DOS:', 'DON'TS:', 'CHARITY:' labels - write naturally\n4. Include: specific practices with timings, mantras/prayers/surahs, fasting, charity guidance\n5. Tailor to their specific problem from conversation\n6. 100-150 words, practical and actionable\n7. If religion mentioned, align with that faith\nProvide FULL REMEDIES in remedy field NOW.\n"
            data["context_block"] = data["context_block"] + system_override if data["context_block"] else system_override
            logging.warning(f"[WITH_CONTEXT] DEBUG: System override injected into context_block")
        
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
            # Clean the response if it has markdown code blocks or extra whitespace
            clean_text = combined_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            # Remove any leading newlines or whitespace before JSON
            import re
            clean_text = re.sub(r'^\s+', '', clean_text)
            
            # If response doesn't start with {, try to find the first {
            if not clean_text.startswith('{'):
                json_start = clean_text.find('{')
                if json_start != -1:
                    clean_text = clean_text[json_start:]
            
            parsed_output = output_parser.parse(clean_text)
            
            data["category"] = parsed_output.get("category", "General").title()
            data["answer"] = parsed_output.get("answer", "I sense important energies surrounding your question. Please allow me to provide deeper insight in a moment.")
            data["remedy"] = parsed_output.get("remedy", "")
            
            # FIX: If remedy was explicitly requested but is empty, generate default remedy
            if remedy_should_be_provided and (not data["remedy"] or len(data["remedy"].strip()) < 10):
                logging.warning("REMEDY EMPTY DETECTED: User requested remedy but AI returned empty. Generating default remedy...")
                data["remedy"] = f"For spiritual wellbeing and peace of mind, practice daily meditation and recitation of sacred texts from your faith tradition. Engage in regular acts of charity and service to others. Maintain positive thoughts and actions aligned with your beliefs. These practices will bring clarity and inner strength during this period."
            
            # VALIDATION CHECK: If answer mentions remedies but remedy field is empty, this is an error
            answer_lower = data["answer"].lower()
            remedy_empty = not data["remedy"] or len(data["remedy"].strip()) < 20
            mentions_remedies = any(word in answer_lower for word in ["here are remedies", "remedies aligned", "suggest remedies", "following remedies"])
            
            # If remedy field is populated, clear the answer field to show only remedies
            if not remedy_empty and data["remedy"]:
                data["answer"] = ""
            
            if remedy_empty and mentions_remedies:
                logging.warning("REMEDY LOOP DETECTED: Answer mentions remedies but remedy field is empty. Forcing remedy generation...")
                # Retry with explicit force
                force_prompt = f"""[CRITICAL SYSTEM OVERRIDE]
The user wants {religion.upper()} remedies NOW. You said "here are remedies" but provided NOTHING in the remedy field.

You MUST generate comprehensive remedies following this structure:

DOS (Practices to follow):
1. [Specific practice with exact details]
2. [Another practice]
3. [Third practice]

DON'TS (Things to avoid):
1. [Specific thing to avoid]
2. [Another thing to avoid]

CHARITY (Donations/Service):
1. [Specific charity with details]
2. [Another charity work]

Generate NOW. No more delays. No more empty fields."""
                
                retry_msg = HumanMessage(content=force_prompt)
                retry_response = await llm.agenerate([[retry_msg]])
                retry_text = retry_response.generations[0][0].text
                
                # Use the retry text as remedy
                data["remedy"] = retry_text.strip()
            
        except Exception as e:
            logging.error(f"JSON parsing failed: {e}. Response: {combined_text[:500]}")
            # Fallback: try to extract from text
            data["category"] = "General"
            data["answer"] = _unwrap_ai_message(combined_text)
            data["remedy"] = "I recommend taking time for spiritual reflection and meditation to gain clarity on this matter."

        # Save chat turn to session store if session_id provided
        if session_id:
            try:
                force_prompt = f"""[CRITICAL SYSTEM OVERRIDE]
                # If user provided explicit context, persist it for future turns
                if context:
                    save_session_context(session_id, context)
            except Exception:
                pass

        # FINAL CHECK: Ensure remedy is populated if it was requested
        if remedy_should_be_provided and (not data.get("remedy") or len(str(data.get("remedy", "")).strip()) < 10):
            logging.warning(f"[WITH_CONTEXT FINAL CHECK] Remedy still empty despite request. Generating strong fallback...")
            data["remedy"] = "For spiritual wellbeing and peace of mind, practice daily meditation and recitation of sacred texts from your faith tradition. Engage in regular acts of charity and service to others. Maintain positive thoughts and actions aligned with your beliefs. These practices will bring clarity and inner strength during this period."
            logging.warning(f"[WITH_CONTEXT FINAL CHECK] Applied fallback remedy with length {len(data['remedy'])}")


        # Step 1: Retrieval (question only)
        
        retrieved_docs_question = await chromadb_retrieve(data["question"], TOP_K)
        
      

        data["retrieved_docs"] = retrieved_docs_question
        data["retrieved_text"] = pack_retrieved_text(data["retrieved_docs"])
        
        # Build context_block with user_name if provided
        context_parts = []
        if user_name:
            context_parts.append(f"User Name: {user_name}")
        if data.get("context"):
            context_parts.append(f"Additional Context:\n{data['context']}")
        data["context_block"] = "\n".join(context_parts) if context_parts else ""

    

        # Step 2: Generate comprehensive astrological consultation with AI-generated remedies
        combined_prompt = get_comprehensive_prompt(religion)
        
        # SIMPLE REMEDY DETECTION - Check if user is requesting remedies
        remedy_should_be_provided = False
        question_lower = data["question"].lower()
        
        # Check if user explicitly asked for remedy
        remedy_keywords = ["remedy", "remedies", "send remedy", "pls remedy", "please remedy", 
                          "upay", "totke", "totka", "solution", "solutions", "help", 
                          "solve", "fix", "what to do", "what should i do"]
        
        has_remedy_keyword = any(keyword in question_lower for keyword in remedy_keywords)
        
        logging.warning(f"[NO_CONTEXT] DEBUG KEYWORD: question_lower='{question_lower}', has_remedy_keyword={has_remedy_keyword}")
        
        if has_remedy_keyword:
            remedy_should_be_provided = True
        
        logging.warning(f"[NO_CONTEXT] DEBUG REMEDY FLAG: remedy_should_be_provided={remedy_should_be_provided}")
        
        # Inject mandatory system signal if remedy should be provided
        if remedy_should_be_provided:
            system_override = f"\n\n[CRITICAL SYSTEM OVERRIDE - IMMEDIATE ACTION REQUIRED]\nUser is asking for remedies. You are now in STAGE 3 (REMEDIES MODE).\nYou MUST:\n1. Set answer field to EMPTY STRING: \"\"\n2. Populate remedy field with comprehensive, practical remedies\n3. Do NOT use 'DOS:', 'DON'TS:', 'CHARITY:' labels - write naturally\n4. Include: specific practices with timings, mantras/prayers/surahs, fasting, charity guidance\n5. Tailor to their specific problem from conversation\n6. 100-150 words, practical and actionable\n7. If religion mentioned, align with that faith\nProvide FULL REMEDIES in remedy field NOW.\n"
            data["context_block"] = data["context_block"] + system_override if data["context_block"] else system_override
            logging.warning(f"[NO_CONTEXT] DEBUG: System override injected into context_block")
      
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
            # Clean the response if it has markdown code blocks or extra whitespace
            clean_text = combined_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            # Remove any leading newlines or whitespace before JSON
            import re
            clean_text = re.sub(r'^\s+', '', clean_text)
            
            # If response doesn't start with {, try to find the first {
            if not clean_text.startswith('{'):
                json_start = clean_text.find('{')
                if json_start != -1:
                    clean_text = clean_text[json_start:]
            
            parsed_output = output_parser.parse(clean_text)
            
            data["category"] = parsed_output.get("category", "General").title()
            data["answer"] = parsed_output.get("answer", "I sense important energies surrounding your question. Please allow me to provide deeper insight in a moment.")
            data["remedy"] = parsed_output.get("remedy", "")
            
            # FIX: If remedy was explicitly requested but is empty, generate default remedy
            if remedy_should_be_provided and (not data["remedy"] or len(data["remedy"].strip()) < 10):
                logging.warning("REMEDY EMPTY DETECTED: User requested remedy but AI returned empty. Generating default remedy...")
                data["remedy"] = f"For spiritual wellbeing and peace of mind, practice daily meditation and recitation of sacred texts from your faith tradition. Engage in regular acts of charity and service to others. Maintain positive thoughts and actions aligned with your beliefs. These practices will bring clarity and inner strength during this period."
            
            # VALIDATION CHECK: If answer mentions remedies but remedy field is empty, this is an error
            answer_lower = data["answer"].lower()
            remedy_empty = not data["remedy"] or len(data["remedy"].strip()) < 20
            mentions_remedies = any(word in answer_lower for word in ["here are remedies", "remedies aligned", "suggest remedies", "following remedies"])
            
            # If remedy field is populated, clear the answer field to show only remedies
            if not remedy_empty and data["remedy"]:
                data["answer"] = ""
            
            if remedy_empty and mentions_remedies:
                logging.warning("REMEDY LOOP DETECTED: Answer mentions remedies but remedy field is empty. Forcing remedy generation...")
                # Retry with explicit force
The user wants {religion.upper()} remedies NOW. You said "here are remedies" but provided NOTHING in the remedy field.

You MUST generate comprehensive remedies following this structure:

DOS (Practices to follow):
1. [Specific practice with exact details]
2. [Another practice]
3. [Third practice]

DON'TS (Things to avoid):
1. [Specific thing to avoid]
2. [Another thing to avoid]

CHARITY (Donations/Service):
1. [Specific charity with details]
2. [Another charity work]

Generate NOW. No more delays. No more empty fields."""
                
                retry_msg = HumanMessage(content=force_prompt)
                retry_response = await llm.agenerate([[retry_msg]])
                retry_text = retry_response.generations[0][0].text
                
                # Use the retry text as remedy
                data["remedy"] = retry_text.strip()
            
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

        # FINAL CHECK: Ensure remedy is populated if it was requested
        if remedy_should_be_provided and (not data.get("remedy") or len(str(data.get("remedy", "")).strip()) < 10):
            logging.warning(f"[NO_CONTEXT FINAL CHECK] Remedy still empty despite request. Generating strong fallback...")
            data["remedy"] = "For spiritual wellbeing and peace of mind, practice daily meditation and recitation of sacred texts from your faith tradition. Engage in regular acts of charity and service to others. Maintain positive thoughts and actions aligned with your beliefs. These practices will bring clarity and inner strength during this period."
            logging.warning(f"[NO_CONTEXT FINAL CHECK] Applied fallback remedy with length {len(data['remedy'])}")

        return {
            "question": question,
            "category": data["category"],
```
DON'TS (Things to avoid):
1. [Specific thing to avoid]
2. [Another thing to avoid]

CHARITY (Donations/Service):
1. [Specific charity with details]
2. [Another charity work]

Generate NOW. No more delays. No more empty fields."""
                
                retry_msg = HumanMessage(content=force_prompt)
                retry_response = await llm.agenerate([[retry_msg]])
                retry_text = retry_response.generations[0][0].text
                
                # Use the retry text as remedy
                data["remedy"] = retry_text.strip()
            
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

        # FINAL CHECK: Ensure remedy is populated if it was requested
        if remedy_should_be_provided and (not data.get("remedy") or len(str(data.get("remedy", "")).strip()) < 10):
            logging.warning(f"[WITH_CONTEXT FINAL CHECK] Remedy still empty despite request. Generating strong fallback...")
            data["remedy"] = "For spiritual wellbeing and peace of mind, practice daily meditation and recitation of sacred texts from your faith tradition. Engage in regular acts of charity and service to others. Maintain positive thoughts and actions aligned with your beliefs. These practices will bring clarity and inner strength during this period."
            logging.warning(f"[WITH_CONTEXT FINAL CHECK] Applied fallback remedy with length {len(data['remedy'])}")


        # Step 1: Retrieval (question only)
        
        retrieved_docs_question = await chromadb_retrieve(data["question"], TOP_K)
        
      

        data["retrieved_docs"] = retrieved_docs_question
        data["retrieved_text"] = pack_retrieved_text(data["retrieved_docs"])
        
        # Build context_block with user_name if provided
        context_parts = []
        if user_name:
            context_parts.append(f"User Name: {user_name}")
        if data.get("context"):
            context_parts.append(f"Additional Context:\n{data['context']}")
        data["context_block"] = "\n".join(context_parts) if context_parts else ""

    

        # Step 2: Generate comprehensive astrological consultation with AI-generated remedies
        combined_prompt = get_comprehensive_prompt(religion)
        
        # SIMPLE REMEDY DETECTION - Check if user is requesting remedies
        remedy_should_be_provided = False
        question_lower = data["question"].lower()
        
        # Check if user explicitly asked for remedy
        remedy_keywords = ["remedy", "remedies", "send remedy", "pls remedy", "please remedy", 
                          "upay", "totke", "totka", "solution", "solutions", "help", 
                          "solve", "fix", "what to do", "what should i do"]
        
        has_remedy_keyword = any(keyword in question_lower for keyword in remedy_keywords)
        
        logging.warning(f"[NO_CONTEXT] DEBUG KEYWORD: question_lower='{question_lower}', has_remedy_keyword={has_remedy_keyword}")
        
        if has_remedy_keyword:
            remedy_should_be_provided = True
        
        logging.warning(f"[NO_CONTEXT] DEBUG REMEDY FLAG: remedy_should_be_provided={remedy_should_be_provided}")
        
        # Inject mandatory system signal if remedy should be provided
        if remedy_should_be_provided:
            system_override = f"\n\n[CRITICAL SYSTEM OVERRIDE - IMMEDIATE ACTION REQUIRED]\nUser is asking for remedies. You are now in STAGE 3 (REMEDIES MODE).\nYou MUST:\n1. Set answer field to EMPTY STRING: \"\"\n2. Populate remedy field with comprehensive, practical remedies\n3. Do NOT use 'DOS:', 'DON'TS:', 'CHARITY:' labels - write naturally\n4. Include: specific practices with timings, mantras/prayers/surahs, fasting, charity guidance\n5. Tailor to their specific problem from conversation\n6. 100-150 words, practical and actionable\n7. If religion mentioned, align with that faith\nProvide FULL REMEDIES in remedy field NOW.\n"
            data["context_block"] = data["context_block"] + system_override if data["context_block"] else system_override
            logging.warning(f"[NO_CONTEXT] DEBUG: System override injected into context_block")
      
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
            # Clean the response if it has markdown code blocks or extra whitespace
            clean_text = combined_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            # Remove any leading newlines or whitespace before JSON
            import re
            clean_text = re.sub(r'^\s+', '', clean_text)
            
            # If response doesn't start with {, try to find the first {
            if not clean_text.startswith('{'):
                json_start = clean_text.find('{')
                if json_start != -1:
                    clean_text = clean_text[json_start:]
            
            parsed_output = output_parser.parse(clean_text)
            
            data["category"] = parsed_output.get("category", "General").title()
            data["answer"] = parsed_output.get("answer", "I sense important energies surrounding your question. Please allow me to provide deeper insight in a moment.")
            data["remedy"] = parsed_output.get("remedy", "")
            
            # FIX: If remedy was explicitly requested but is empty, generate default remedy
            if remedy_should_be_provided and (not data["remedy"] or len(data["remedy"].strip()) < 10):
                logging.warning("REMEDY EMPTY DETECTED: User requested remedy but AI returned empty. Generating default remedy...")
                data["remedy"] = f"For spiritual wellbeing and peace of mind, practice daily meditation and recitation of sacred texts from your faith tradition. Engage in regular acts of charity and service to others. Maintain positive thoughts and actions aligned with your beliefs. These practices will bring clarity and inner strength during this period."
            
            # VALIDATION CHECK: If answer mentions remedies but remedy field is empty, this is an error
            answer_lower = data["answer"].lower()
            remedy_empty = not data["remedy"] or len(data["remedy"].strip()) < 20
            mentions_remedies = any(word in answer_lower for word in ["here are remedies", "remedies aligned", "suggest remedies", "following remedies"])
            
            # If remedy field is populated, clear the answer field to show only remedies
            if not remedy_empty and data["remedy"]:
                data["answer"] = ""
            
            if remedy_empty and mentions_remedies:
                logging.warning("REMEDY LOOP DETECTED: Answer mentions remedies but remedy field is empty. Forcing remedy generation...")
                # Retry with explicit force
                force_prompt = f"""[CRITICAL SYSTEM OVERRIDE]
The user wants {religion.upper()} remedies NOW. You said "here are remedies" but provided NOTHING in the remedy field.

You MUST generate comprehensive remedies following this structure:

DOS (Practices to follow):
1. [Specific practice with exact details]
2. [Another practice]
3. [Third practice]

DON'TS (Things to avoid):
1. [Specific thing to avoid]
2. [Another thing to avoid]

CHARITY (Donations/Service):
1. [Specific charity with details]
2. [Another charity work]

Generate NOW. No more delays. No more empty fields."""
                
                retry_msg = HumanMessage(content=force_prompt)
                retry_response = await llm.agenerate([[retry_msg]])
                retry_text = retry_response.generations[0][0].text
                
                # Use the retry text as remedy
                data["remedy"] = retry_text.strip()
            
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

        # FINAL CHECK: Ensure remedy is populated if it was requested
        if remedy_should_be_provided and (not data.get("remedy") or len(str(data.get("remedy", "")).strip()) < 10):
            logging.warning(f"[NO_CONTEXT FINAL CHECK] Remedy still empty despite request. Generating strong fallback...")
            data["remedy"] = "For spiritual wellbeing and peace of mind, practice daily meditation and recitation of sacred texts from your faith tradition. Engage in regular acts of charity and service to others. Maintain positive thoughts and actions aligned with your beliefs. These practices will bring clarity and inner strength during this period."
            logging.warning(f"[NO_CONTEXT FINAL CHECK] Applied fallback remedy with length {len(data['remedy'])}")

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
    user_name: Optional[str] = None,
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
        
        # Build context_block with user_name if provided
        context_parts = []
        if user_name:
            context_parts.append(f"User Name: {user_name}")
        if data.get("context"):
            context_parts.append(f"Additional Context:\n{data['context']}")
        data["context_block"] = "\n".join(context_parts) if context_parts else ""

    

        # Step 2: Generate comprehensive astrological consultation with AI-generated remedies
        combined_prompt = get_comprehensive_prompt(religion)
        
        # SIMPLE REMEDY DETECTION - Check if user is requesting remedies
        remedy_should_be_provided = False
        question_lower = data["question"].lower()
        
        # Check if user explicitly asked for remedy
        remedy_keywords = ["remedy", "remedies", "send remedy", "pls remedy", "please remedy", 
                          "upay", "totke", "totka", "solution", "solutions", "help", 
                          "solve", "fix", "what to do", "what should i do"]
        
        has_remedy_keyword = any(keyword in question_lower for keyword in remedy_keywords)
        
        logging.warning(f"[NO_CONTEXT] DEBUG KEYWORD: question_lower='{question_lower}', has_remedy_keyword={has_remedy_keyword}")
        
        if has_remedy_keyword:
            remedy_should_be_provided = True
        
        logging.warning(f"[NO_CONTEXT] DEBUG REMEDY FLAG: remedy_should_be_provided={remedy_should_be_provided}")
        
        # Inject mandatory system signal if remedy should be provided
        if remedy_should_be_provided:
            system_override = f"\n\n[CRITICAL SYSTEM OVERRIDE - IMMEDIATE ACTION REQUIRED]\nUser is asking for remedies. You are now in STAGE 3 (REMEDIES MODE).\nYou MUST:\n1. Set answer field to EMPTY STRING: \"\"\n2. Populate remedy field with comprehensive, practical remedies\n3. Do NOT use 'DOS:', 'DON'TS:', 'CHARITY:' labels - write naturally\n4. Include: specific practices with timings, mantras/prayers/surahs, fasting, charity guidance\n5. Tailor to their specific problem from conversation\n6. 100-150 words, practical and actionable\n7. If religion mentioned, align with that faith\nProvide FULL REMEDIES in remedy field NOW.\n"
            data["context_block"] = data["context_block"] + system_override if data["context_block"] else system_override
            logging.warning(f"[NO_CONTEXT] DEBUG: System override injected into context_block")
      
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
            # Clean the response if it has markdown code blocks or extra whitespace
            clean_text = combined_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            # Remove any leading newlines or whitespace before JSON
            import re
            clean_text = re.sub(r'^\s+', '', clean_text)
            
            # If response doesn't start with {, try to find the first {
            if not clean_text.startswith('{'):
                json_start = clean_text.find('{')
                if json_start != -1:
                    clean_text = clean_text[json_start:]
            
            parsed_output = output_parser.parse(clean_text)
            
            data["category"] = parsed_output.get("category", "General").title()
            data["answer"] = parsed_output.get("answer", "I sense important energies surrounding your question. Please allow me to provide deeper insight in a moment.")
            data["remedy"] = parsed_output.get("remedy", "")
            
            # FIX: If remedy was explicitly requested but is empty, generate default remedy
            if remedy_should_be_provided and (not data["remedy"] or len(data["remedy"].strip()) < 10):
                logging.warning("REMEDY EMPTY DETECTED: User requested remedy but AI returned empty. Generating default remedy...")
                data["remedy"] = f"For spiritual wellbeing and peace of mind, practice daily meditation and recitation of sacred texts from your faith tradition. Engage in regular acts of charity and service to others. Maintain positive thoughts and actions aligned with your beliefs. These practices will bring clarity and inner strength during this period."
            
            # VALIDATION CHECK: If answer mentions remedies but remedy field is empty, this is an error
            answer_lower = data["answer"].lower()
            remedy_empty = not data["remedy"] or len(data["remedy"].strip()) < 20
            mentions_remedies = any(word in answer_lower for word in ["here are remedies", "remedies aligned", "suggest remedies", "following remedies"])
            
            # If remedy field is populated, clear the answer field to show only remedies
            if not remedy_empty and data["remedy"]:
                data["answer"] = ""
            
            if remedy_empty and mentions_remedies:
                logging.warning("REMEDY LOOP DETECTED: Answer mentions remedies but remedy field is empty. Forcing remedy generation...")
                # Retry with explicit force
                force_prompt = f"""[CRITICAL SYSTEM OVERRIDE]
The user wants {religion.upper()} remedies NOW. You said "here are remedies" but provided NOTHING in the remedy field.

You MUST generate comprehensive remedies following this structure:

DOS (Practices to follow):
1. [Specific practice with exact details]
2. [Another practice]
3. [Third practice]

DON'TS (Things to avoid):
1. [Specific thing to avoid]
2. [Another thing to avoid]

CHARITY (Donations/Service):
1. [Specific charity with details]
2. [Another charity work]

Generate NOW. No more delays. No more empty fields."""
                
                retry_msg = HumanMessage(content=force_prompt)
                retry_response = await llm.agenerate([[retry_msg]])
                retry_text = retry_response.generations[0][0].text
                
                # Use the retry text as remedy
                data["remedy"] = retry_text.strip()
            
        except Exception as e:
            logging.error(f"JSON parsing failed: {e}. Response: {combined_text[:500]}")
            # Fallback: try to extract from text
            data["category"] = "General"
            data["answer"] = _unwrap_ai_message(combined_text)
            data["remedy"] = "I recommend taking time for spiritual reflection and meditation to gain clarity on this matter."

        # 6. Validate and Fix Persona
        data["answer"] = validate_and_fix_persona(data["answer"])

        # Save chat turn to session store if session_id provided
        if session_id:
            try:
                append_chat_turn(session_id, question, data.get("answer") or _unwrap_ai_message(combined_text))
                if context:
                    save_session_context(session_id, context)
            except Exception:
                pass

        # FINAL CHECK: Ensure remedy is populated if it was requested
        if remedy_should_be_provided and (not data.get("remedy") or len(str(data.get("remedy", "")).strip()) < 10):
            logging.warning(f"[NO_CONTEXT FINAL CHECK] Remedy still empty despite request. Generating strong fallback...")
            data["remedy"] = "For spiritual wellbeing and peace of mind, practice daily meditation and recitation of sacred texts from your faith tradition. Engage in regular acts of charity and service to others. Maintain positive thoughts and actions aligned with your beliefs. These practices will bring clarity and inner strength during this period."
            logging.warning(f"[NO_CONTEXT FINAL CHECK] Applied fallback remedy with length {len(data['remedy'])}")

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

def validate_and_fix_persona(text: str) -> str:
    """
    Post-processing safety check to ensure the AI does not identify as an AI/bot.
    If forbidden phrases are found, it replaces them or the whole response.
    """
    forbidden_phrases = [
        "digital astrologer",
        "friendly digital astrologer",
        "I am an AI",
        "I am a bot",
        "I am a language model",
        "virtual assistant",
        "artificial intelligence"
    ]
    
    lower_text = text.lower()
    for phrase in forbidden_phrases:
        if phrase in lower_text:
            # For now, if it's a short response (< 200 chars) likely just identifying itself,
            # we replace it with the correct persona.
            if len(text) < 200:
                return "Namaste! I am Digvesh Dube, your astrological guide from Prayagraj. How can I assist you today?"
            
            # If it's a longer response, we try to replace the specific phrase with "your astrologer"
            import re
            # Case insensitive replace
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            text = pattern.sub("your astrologer", text)
            
    return text
```