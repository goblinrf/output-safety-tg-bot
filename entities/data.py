from dataclasses import dataclass

@dataclass
class BotMessage:
    question: str
    answer: str
