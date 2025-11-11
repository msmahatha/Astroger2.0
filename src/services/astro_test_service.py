# ----  RAG processing ----



# async def process_question(question: str, context: Optional[str] = None) -> dict:
#     if not question or not isinstance(question, str):
#         raise ValueError("Question must be a non-empty string.")
#     try:
#         data = {"question": question, "context": context or ""}

#         # categorization_chain.invoke is sync, run in thread
#         data["category_raw"] = await asyncio.to_thread(categorization_chain.invoke, {"question": data["question"]})

#         data["category"] = _unwrap_ai_message(data["category_raw"]).title()

#         data["retrieved_docs"] = await chromadb_retrieve(data["question"], TOP_K)

#         data["retrieved_text"] = pack_retrieved_text(data["retrieved_docs"])
#         data["context_block"] = f"Additional Context:\n{data['context']}" if data.get("context") else ""

#         data["answer_raw"] = await asyncio.to_thread(answering_chain.invoke, {
#             "question": data["question"],
#             "category": data["category"],
#             "retrieved_block": f"Retrieved texts:\n{data['retrieved_text']}" if data["retrieved_text"] else "",
#             "context_block": data["context_block"],
#         })

#         data["answer"] = _unwrap_ai_message(data["answer_raw"])

#         category = data.get("category") or "General"
#         answer = data.get("answer") or ""
#         remedy = get_remedy(category)

#         return {
#             "question": question,
#             "category": category,
#             "answer": answer,
#             "remedy": remedy,
#             "retrieved_sources": [normalize_metadata(d.get("metadata")) for d in data.get("retrieved_docs", [])],
#         }

#     except Exception as e:
#         logging.error(f"[AstroRAG Cloud] Error: {e}")
#         raise


# async def process_question_with_context(question: str, context: Optional[str] = None) -> dict:
#     if not question or not isinstance(question, str):
#         raise ValueError("Question must be a non-empty string.")
#     try:
#         data = {"question": question, "context": context or ""}

#         # Categorize question (sync call wrapped in thread)
#         data["category_raw"] = await asyncio.to_thread(categorization_chain.invoke, {"question": data["question"]})
#         data["category"] = _unwrap_ai_message(data["category_raw"]).title()

#         # Retrieve docs for question
#         retrieved_docs_question = await chromadb_retrieve(data["question"], TOP_K)

#         # Retrieve docs for context if available
#         retrieved_docs_context = []
#         if data.get("context"):
#             retrieved_docs_context = await chromadb_retrieve(data["context"], TOP_K)

#         # Combine and deduplicate docs by 'text'
#         combined_docs_map = {}
#         for doc in retrieved_docs_question + retrieved_docs_context:
#             combined_docs_map[doc['text']] = doc
#         combined_docs = list(combined_docs_map.values())

#         data["retrieved_docs"] = combined_docs
#         data["retrieved_text"] = pack_retrieved_text(data["retrieved_docs"])

#         data["context_block"] = f"Additional Context:\n{data['context']}" if data.get("context") else ""

#         # Generate answer (sync call wrapped in thread)
#         data["answer_raw"] = await asyncio.to_thread(answering_chain.invoke, {
#             "question": data["question"],
#             "category": data["category"],
#             "retrieved_block": f"Retrieved texts:\n{data['retrieved_text']}" if data["retrieved_text"] else "",
#             "context_block": data["context_block"],
#         })

#         data["answer"] = _unwrap_ai_message(data["answer_raw"])

#         category = data.get("category") or "General"
#         answer = data.get("answer") or ""
#         remedy = get_remedy(category)

#         return {
#             "question": question,
#             "category": category,
#             "answer": answer,
#             "remedy": remedy,
#             "retrieved_sources": [normalize_metadata(d.get("metadata")) for d in data.get("retrieved_docs", [])],
#         }

#     except Exception as e:
#         logging.error(f"[AstroRAG Cloud] Error: {e}")
#         raise






# without sessions 
# async def process_question_with_context(question: str, context: Optional[str] = None) -> dict:
#     if not question or not isinstance(question, str):
#         raise ValueError("Question must be a non-empty string.")

#     try:
#         data = {"question": question, "context": context or ""}

#         # Run categorization and retrieval calls concurrently
#         tasks = [
#             asyncio.to_thread(categorization_chain.invoke, {"question": data["question"]}),
#             chromadb_retrieve(data["question"], TOP_K)
#         ]
#         if data.get("context"):
#             tasks.append(chromadb_retrieve(data["context"], TOP_K))
#         else:
#             tasks.append(asyncio.sleep(0, result=[]))  # dummy for alignment

#         category_raw, retrieved_docs_question, retrieved_docs_context = await asyncio.gather(*tasks)

#         data["category_raw"] = category_raw
#         data["category"] = _unwrap_ai_message(category_raw).title()

#         # Deduplicate
#         combined_docs_map = {doc['text']: doc for doc in (retrieved_docs_question + retrieved_docs_context)}
#         combined_docs = list(combined_docs_map.values())

#         data["retrieved_docs"] = combined_docs
#         data["retrieved_text"] = pack_retrieved_text(data["retrieved_docs"])
#         data["context_block"] = f"Additional Context:\n{data['context']}" if data.get("context") else ""

#         # Generate answer (sync call wrapped in thread)
#         data["answer_raw"] = await asyncio.to_thread(answering_chain.invoke, {
#             "question": data["question"],
#             "category": data["category"],
#             "retrieved_block": f"Retrieved texts:\n{data['retrieved_text']}" if data["retrieved_text"] else "",
#             "context_block": data["context_block"],
#         })

#         data["answer"] = _unwrap_ai_message(data["answer_raw"])

#         category = data.get("category") or "General"
#         answer = data.get("answer") or ""
#         remedy = get_remedy(category)

#         return {
#             "question": question,
#             "category": category,
#             "answer": answer,
#             "remedy": remedy,
#             "retrieved_sources": [normalize_metadata(d.get("metadata")) for d in data.get("retrieved_docs", [])],
#         }
#     except Exception as e:
#         logging.error(f" Error: {e}")
#         raise



# async def process_question(question: str, context: Optional[str] = None) -> dict:
#     if not question or not isinstance(question, str):
#         raise ValueError("Question must be a non-empty string.")

#     try:
#         data = {"question": question, "context": context or ""}

#         # Run categorization and retrieval calls concurrently (ONLY question-based retrieval now)
#         tasks = [
#             asyncio.to_thread(categorization_chain.invoke, {"question": data["question"]}),
#             chromadb_retrieve(data["question"], TOP_K),
#             asyncio.sleep(0, result=[])  # dummy to keep 3 tasks for unpacking consistency
#         ]

#         category_raw, retrieved_docs_question, _ = await asyncio.gather(*tasks)

#         data["category_raw"] = category_raw
#         data["category"] = _unwrap_ai_message(category_raw).title()

#         # Since no context-based docs, combined docs is just question retrieval
#         combined_docs = retrieved_docs_question

#         data["retrieved_docs"] = combined_docs
#         data["retrieved_text"] = pack_retrieved_text(data["retrieved_docs"])
#         data["context_block"] = f"Additional Context:\n{data['context']}" if data.get("context") else ""

#         # Generate answer (sync call wrapped in thread)
#         data["answer_raw"] = await asyncio.to_thread(answering_chain.invoke, {
#             "question": data["question"],
#             "category": data["category"],
#             "retrieved_block": f"Retrieved texts:\n{data['retrieved_text']}" if data["retrieved_text"] else "",
#             "context_block": data["context_block"],
#         })

#         data["answer"] = _unwrap_ai_message(data["answer_raw"])

#         category = data.get("category") or "General"
#         answer = data.get("answer") or ""
#         remedy = get_remedy(category)

#         return {
#             "question": question,
#             "category": category,
#             "answer": answer,
#             "remedy": remedy,
#             "retrieved_sources": [normalize_metadata(d.get("metadata")) for d in data.get("retrieved_docs", [])],
#         }
#     except Exception as e:
#         logging.error(f"Error: {e}")
#         raise



# with sessions

# async def process_question_with_context(
#     question: str,
#     context: Optional[str] = None,
#     use_history: bool = False,
#     session_id: Optional[str] = None,
# ) -> dict:
#     """
#     Processes question with optional context and chat history.

#     Returns dictionary with answer, category, remedy, and metadata.
#     """
#     if not question or not isinstance(question, str):
#         raise ValueError("Question must be a non-empty string.")

#     combined_context = context or ""
#     chat_history = None

#     if use_history:
#         if not session_id:
#             raise ValueError("session_id must be provided if use_history is True.")
#         history_context, chat_history = await load_chat_history(session_id)
#         combined_context = (history_context + "\n" + combined_context).strip()

#     try:
#         data = {"question": question, "context": combined_context}

#         # Concurrently invoke categorization and retrieval
#         tasks = [
#             asyncio.to_thread(categorization_chain.invoke, {"question": question}),
#             chromadb_retrieve(question, TOP_K),
#         ]

#         if combined_context:
#             tasks.append(chromadb_retrieve(combined_context, TOP_K))
#         else:
#             tasks.append(asyncio.sleep(0, result=[]))  # Dummy

#         category_raw, docs_question, docs_context = await asyncio.gather(*tasks)

#         data["category_raw"] = category_raw
#         data["category"] = _unwrap_ai_message(category_raw).title()

#         # Deduplicate docs by text content
#         combined_docs_map = {doc["text"]: doc for doc in (docs_question + docs_context)}
#         combined_docs = list(combined_docs_map.values())

#         data["retrieved_docs"] = combined_docs
#         data["retrieved_text"] = pack_retrieved_text(combined_docs)
#         data["context_block"] = f"Additional Context:\n{combined_context}" if combined_context else ""

#         # Generate answer
#         data["answer_raw"] = await asyncio.to_thread(answering_chain.invoke, {
#             "question": question,
#             "category": data["category"],
#             "retrieved_block": f"Retrieved texts:\n{data['retrieved_text']}" if data["retrieved_text"] else "",
#             "context_block": data["context_block"],
#         })

#         data["answer"] = _unwrap_ai_message(data["answer_raw"])

#         remedy = get_remedy(data["category"])

#         # Save chat if history enabled
#         if use_history and chat_history is not None:
#             await save_chat_turn(chat_history, question, data["answer"])

#         return {
#             "question": question,
#             "category": data["category"],
#             "answer": data["answer"],
#             "remedy": remedy,
#             "retrieved_sources": [normalize_metadata(doc.get("metadata")) for doc in combined_docs],
#         }

#     except Exception as e:
#         logging.error(f"Error in process_question_with_context: {e}")
#         raise


# async def process_question(
#     question: str,
#     context: Optional[str] = None,
#     use_history: bool = False,
#     session_id: Optional[str] = None,
# ) -> dict:
#     """
#     Processes question without context-based retrieval, optional chat history.

#     Returns dictionary with answer, category, remedy, and metadata.
#     """
#     if not question or not isinstance(question, str):
#         raise ValueError("Question must be a non-empty string.")

#     combined_context = context or ""
#     chat_history = None

#     if use_history:
#         if not session_id:
#             raise ValueError("session_id must be provided if use_history is True.")
#         history_context, chat_history = await load_chat_history(session_id)
#         combined_context = (history_context + "\n" + combined_context).strip()

#     try:
#         data = {"question": question, "context": combined_context}

#         tasks = [
#             asyncio.to_thread(categorization_chain.invoke, {"question": question}),
#             chromadb_retrieve(question, TOP_K),
#             asyncio.sleep(0, result=[])  # dummy for unpacking consistency
#         ]

#         category_raw, docs_question, _ = await asyncio.gather(*tasks)

#         data["category_raw"] = category_raw
#         data["category"] = _unwrap_ai_message(category_raw).title()

#         combined_docs = docs_question

#         data["retrieved_docs"] = combined_docs
#         data["retrieved_text"] = pack_retrieved_text(combined_docs)
#         data["context_block"] = f"Additional Context:\n{combined_context}" if combined_context else ""

#         data["answer_raw"] = await asyncio.to_thread(answering_chain.invoke, {
#             "question": question,
#             "category": data["category"],
#             "retrieved_block": f"Retrieved texts:\n{data['retrieved_text']}" if data["retrieved_text"] else "",
#             "context_block": data["context_block"],
#         })

#         data["answer"] = _unwrap_ai_message(data["answer_raw"])

#         remedy = get_remedy(data["category"])

#         if use_history and chat_history is not None:
#             await save_chat_turn(chat_history, question, data["answer"])

#         return {
#             "question": question,
#             "category": data["category"],
#             "answer": data["answer"],
#             "remedy": remedy,
#             "retrieved_sources": [normalize_metadata(doc.get("metadata")) for doc in combined_docs],
#         }

#     except Exception as e:
#         logging.error(f"Error in process_question: {e}")
#         raise
