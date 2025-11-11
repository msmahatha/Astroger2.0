from pydantic import BaseModel


class AnswerOutput(BaseModel):
    category: str
    answer: str