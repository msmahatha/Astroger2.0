# from typing import Optional, List
# from langchain_community.chat_message_histories import MongoDBChatMessageHistory
# from langchain.schema import BaseMessage
# import asyncio
# from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION



# def messages_to_context(messages: List[BaseMessage]) -> str:
#     """
#     Converts LangChain messages list into a text block suitable as context.
#     Format:
#         User: <user message>
#         AI: <ai message>
#     """
#     lines = []
#     for msg in messages:
#         role = "User" if msg.type == "human" else "AI"
#         lines.append(f"{role}: {msg.content}")
#     return "\n".join(lines)

# async def load_chat_history(session_id: str) -> str:
#     """Loads chat history from MongoDB and converts to context string."""
#     chat_history = MongoDBChatMessageHistory(
#         collection_name=MONGO_COLLECTION,
#         database_name=MONGO_DB,
#         connection_string=MONGO_URI,
#         session_id=session_id,
#     )
#     # MongoDBChatMessageHistory is synchronous, wrap calls in to_thread
#     messages = await asyncio.to_thread(chat_history.get_messages)
#     return messages_to_context(messages), chat_history

# async def save_chat_turn(chat_history: MongoDBChatMessageHistory, user_msg: str, ai_msg: str):
#     """Save user and AI messages to MongoDB chat history."""
#     await asyncio.to_thread(chat_history.add_user_message, user_msg)
#     await asyncio.to_thread(chat_history.add_ai_message, ai_msg)