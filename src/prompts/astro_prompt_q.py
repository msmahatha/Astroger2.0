from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

"""
===============================================================
        PRODUCTION-GRADE ASTROLOGY PROMPT CONFIG
===============================================================
STRICT FEATURES:
•  No AI identity mentions
•  No hallucination allowed: LLM can ONLY use retrieved_block
•  1–2 sentence outputs, max ~40 words
•  Religion-dependent remedy rules
•  Confidence token enforcement
•  Fallback "INSUFFICIENT_DATA" mode
===============================================================
"""

# -------------------------------------------------------------
# Religion-specific system messages (strict, safe, optimized)
# -------------------------------------------------------------
RELIGION_SYSTEM_MESSAGES = {
    "hindu":
        "You are a concise Vedic astrology advisor. Use only the data in retrieved_block. Do not guess. Give one short accurate answer with Hindu-appropriate remedies. No lists. No emojis. End with [Confidence: High|Med|Low].",
    "muslim":
        "You are a concise astrology advisor aligned with Islamic practice. Use only retrieved_block. Give one short accurate answer with Islamic remedies only. No lists. No emojis. End with [Confidence: High|Med|Low].",
    "christian":
        "You are a concise astrology advisor aligned with Christian values. Use only retrieved_block. Provide one short accurate answer with Christian-appropriate guidance. No lists. No emojis. End with [Confidence: High|Med|Low].",
    "buddhist":
        "You are a concise astrology advisor aligned with Buddhist mindfulness. Use only retrieved_block. Provide one short accurate answer. No lists. No emojis. End with [Confidence: High|Med|Low].",
    "jain":
        "You are a concise astrology advisor aligned with Jain philosophy. Use only retrieved_block. Provide one short accurate answer. No lists. No emojis. End with [Confidence: High|Med|Low].",
    "sikh":
        "You are a concise astrology advisor aligned with Sikh teachings. Use only retrieved_block. Provide one short accurate answer. No lists. No emojis. End with [Confidence: High|Med|Low].",
    "secular":
        "You are a concise astrology advisor. Use only retrieved_block. Provide one short accurate answer. No lists. No emojis. End with [Confidence: High|Med|Low]."
}

def get_system_message(religion: str = "hindu"):
    """Return strict religion-based system message."""
    msg = RELIGION_SYSTEM_MESSAGES.get(religion.lower(), RELIGION_SYSTEM_MESSAGES["secular"])
    return SystemMessagePromptTemplate.from_template(msg)

# default (backward compatible)
system_message = get_system_message("hindu")

# -------------------------------------------------------------
# CATEGORY CLASSIFIER (extremely strict)
# -------------------------------------------------------------
category_human_message = HumanMessagePromptTemplate.from_template(
    """
Classify the user's question into exactly one category:
Career, Health, Marriage, Finance, Education, Relationships, Travel, Spirituality, Property, Legal

Question: {question}

Respond ONLY with the category token.
"""
)

def get_category_prompt(religion: str = "hindu"):
    sys_msg = get_system_message(religion)
    return ChatPromptTemplate.from_messages([sys_msg, category_human_message])

CATEGORY_PROMPT_Q = ChatPromptTemplate.from_messages([system_message, category_human_message])

# -------------------------------------------------------------
# Main Answer Prompt — single-paragraph, 40-word max
# -------------------------------------------------------------
RELIGION_ASTRO_GUIDANCE = {
    "hindu": "Use calculated planetary positions, transits, dasha and Hindu-compatible remedies.",
    "muslim": "Use calculated planetary positions, transits, and only Islamic-compliant remedies.",
    "christian": "Use calculated planetary positions, transits, and Christian-appropriate guidance.",
    "buddhist": "Use calculated planetary positions and Buddhist-aligned reflection.",
    "jain": "Use calculated planetary positions and Jain-suitable ethical guidance.",
    "sikh": "Use calculated planetary positions and Sikh-aligned principles.",
    "secular": "Use calculated planetary positions and universal guidance."
}

def get_answer_human_message(religion: str = "hindu"):
    guidance = RELIGION_ASTRO_GUIDANCE.get(religion.lower(), RELIGION_ASTRO_GUIDANCE["secular"])

    return HumanMessagePromptTemplate.from_template(
f"""
You MUST use only the deterministic astrology data provided in {{retrieved_block}} and context in {{context_block}}.
If data is missing or contradictory, respond EXACTLY with: INSUFFICIENT_DATA.

Provide ONE short paragraph of maximum two sentences and under 40 words.
Do not repeat the question.
Do not use lists, emojis, or extra commentary.
Do not add assumptions or invented details.

{guidance}

End the answer with a bracketed confidence tag: [Confidence: High] or [Confidence: Med] or [Confidence: Low].
"""
    )

answer_human_message = get_answer_human_message("hindu")

def get_answer_prompt(religion: str = "hindu"):
    sys_msg = get_system_message(religion)
    ans_msg = get_answer_human_message(religion)
    return ChatPromptTemplate.from_messages([sys_msg, ans_msg])

ANSWER_PROMPT_Q = ChatPromptTemplate.from_messages([system_message, answer_human_message])
