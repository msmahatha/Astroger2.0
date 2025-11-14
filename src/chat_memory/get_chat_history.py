"""Simple in-memory chat/session context store.

This module provides a tiny session-based context store used by the local
service to remember user-supplied context (for example: religion, partial
birth details, name) across requests when the client includes a `session_id`.

Note: this is an in-memory store and will not persist across process restarts.
For production, replace with a persistent store (Redis, MongoDB, etc.).
"""
from typing import Optional, Dict, Any
from threading import Lock

# Simple thread-safe in-memory store
_STORE: Dict[str, Dict[str, Any]] = {}
_LOCK = Lock()


def save_session_context(session_id: str, context_text: str) -> None:
	"""Save or replace the free-text context for a session."""
	if not session_id:
		return
	with _LOCK:
		s = _STORE.setdefault(session_id, {})
		# store the last supplied free-text context
		s["context_text"] = context_text


def append_chat_turn(session_id: str, user_msg: str, ai_msg: Optional[str] = None) -> None:
	"""Append a conversational turn to the session history.

	The history is stored as a simple list of strings under 'history'.
	"""
	if not session_id:
		return
	with _LOCK:
		s = _STORE.setdefault(session_id, {})
		hist = s.setdefault("history", [])
		hist.append({"user": user_msg, "ai": ai_msg})


def get_session_context(session_id: str) -> str:
	"""Return a composed context string for the session.

	This includes explicitly stored `context_text` (if any) followed by a
	short summary of recent chat turns to provide helpful background to the LLM.
	"""
	if not session_id:
		return ""
	with _LOCK:
		s = _STORE.get(session_id, {})
		parts = []
		if "context_text" in s and s["context_text"]:
			parts.append(f"User-provided context:\n{s['context_text']}")

		hist = s.get("history", [])
		if hist:
			# include up to last 6 turns
			last = hist[-6:]
			lines = []
			for turn in last:
				u = turn.get("user", "")
				a = turn.get("ai", "")
				lines.append(f"User: {u}")
				if a:
					lines.append(f"AI: {a}")
			parts.append("\n".join(lines))

		return "\n\n".join(parts)


def clear_session(session_id: str) -> None:
	"""Clear stored session data (useful for tests)."""
	if not session_id:
		return
	with _LOCK:
		_STORE.pop(session_id, None)

# from typing import Optional, List
# from langchain_community.chat_message_histories import MongoDBChatMessageHistory
# from langchain.schema import BaseMessage
