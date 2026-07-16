"""
Reading service qatlami — o'qish jarayoni va AI suhbat loglari bilan ishlash.
"""

from reading.models import AIChatLog


async def log_ai_chat(reader_id: int, book_id: int | None, question: str, answer: str) -> AIChatLog:
    return await AIChatLog.objects.acreate(
        reader_id=reader_id,
        book_id=book_id,
        question=question,
        answer=answer,
    )