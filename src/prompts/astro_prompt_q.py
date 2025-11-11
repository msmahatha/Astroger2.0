from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Religion-specific system messages
RELIGION_SYSTEM_MESSAGES = {
    "hindu": "You are a highly skilled Vedic astrology expert. Answer kindly and with deep spiritual wisdom.",
    "christian": "You are a highly skilled astrology expert with knowledge of Christian mysticism. Answer kindly with spiritual wisdom.",
    "muslim": "You are a highly skilled astrology expert knowledgeable in Islamic teachings. Answer kindly with spiritual wisdom.",
    "buddhist": "You are a highly skilled astrology expert with deep understanding of Buddhist philosophy. Answer kindly with mindfulness and compassion.",
    "jain": "You are a highly skilled astrology expert knowledgeable in Jain philosophy. Answer kindly with spiritual wisdom.",
    "sikh": "You are a highly skilled astrology expert familiar with Sikh teachings. Answer kindly with spiritual wisdom.",
    "secular": "You are a highly skilled astrology expert. Answer kindly with universal spiritual wisdom."
}

# Define system message (shared by both chains) - default to Hindu for backward compatibility
system_message = SystemMessagePromptTemplate.from_template(
    RELIGION_SYSTEM_MESSAGES["hindu"]
)

def get_system_message(religion: str = "hindu"):
    """Get religion-specific system message"""
    message_text = RELIGION_SYSTEM_MESSAGES.get(religion.lower(), RELIGION_SYSTEM_MESSAGES["secular"])
    return SystemMessagePromptTemplate.from_template(message_text)

# Category prompt
category_human_message = HumanMessagePromptTemplate.from_template(
    """
Classify the user's question into one of the following categories:

Career, Health, Marriage, Finance, Education, Relationships, Travel, Spirituality, Property, Legal

Question: {question}

Respond with only the category name. Do not explain.
"""
)

def get_category_prompt(religion: str = "hindu"):
    """Get religion-specific category prompt"""
    sys_msg = get_system_message(religion)
    return ChatPromptTemplate.from_messages([sys_msg, category_human_message])

CATEGORY_PROMPT_Q = ChatPromptTemplate.from_messages(
    [system_message, category_human_message]
)

# Religion-specific astrological guidance
RELIGION_ASTRO_GUIDANCE = {
    "hindu": "Based on classical Vedic astrology principles — including planetary positions, house interpretations, and yogas — provide a detailed yet compassionate response.",
    "christian": "Based on astrological principles and Christian spiritual wisdom, provide a detailed yet compassionate response.",
    "muslim": "Based on astrological principles that align with Islamic values, provide a detailed yet compassionate response.",
    "buddhist": "Based on astrological principles and Buddhist concepts of karma and mindfulness, provide a detailed yet compassionate response.",
    "jain": "Based on astrological principles and Jain philosophy of right conduct and non-violence, provide a detailed yet compassionate response.",
    "sikh": "Based on astrological principles and Sikh teachings of truth and equality, provide a detailed yet compassionate response.",
    "secular": "Based on astrological principles and universal spiritual wisdom, provide a detailed yet compassionate response."
}

# Answer prompt
def get_answer_human_message(religion: str = "hindu"):
    """Get religion-specific answer prompt"""
    guidance = RELIGION_ASTRO_GUIDANCE.get(religion.lower(), RELIGION_ASTRO_GUIDANCE["secular"])
    
    return HumanMessagePromptTemplate.from_template(
        f"""
The user has asked a question in the category: "{{category}}".

Question:
"{{question}}"

Here is the retrieved information you have about the user:
{{retrieved_block}}

Here is the user's additional context (if any):
{{context_block}}

{guidance} Write as if you are gently guiding the user with spiritual wisdom.

Please follow these guidelines:
- Do not repeat the question or context word-for-word, but use them naturally.
- Do not mention that you are an AI.
- Do not use bullet points, tables, or lists.
- Write in 3–4 natural paragraphs with smooth flow.
- Use soft, empathetic, and uplifting language.
- Mention relevant astrological factors (planets, houses, aspects) if applicable.
- Provide safe, culturally appropriate guidance and remedies that align with the user's {religion} background.

End with a spiritually grounded and hopeful note.
"""
    )

answer_human_message = get_answer_human_message("hindu")

def get_answer_prompt(religion: str = "hindu"):
    """Get religion-specific answer prompt"""
    sys_msg = get_system_message(religion)
    ans_msg = get_answer_human_message(religion)
    return ChatPromptTemplate.from_messages([sys_msg, ans_msg])

ANSWER_PROMPT_Q = ChatPromptTemplate.from_messages(
    [system_message, answer_human_message]
)
