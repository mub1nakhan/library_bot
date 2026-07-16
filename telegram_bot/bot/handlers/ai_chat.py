"""
AI Chat handler.

Foydalanuvchi kitob kartochkasidagi "💬 AI bilan suhbat" tugmasini bosganda
ishga tushadi. Savol Claude API'ga uzatiladi, javob AIChatLog'ga yoziladi
(keyinchalik AI Analytics shu ma'lumotdan foydalanadi).
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from ai_assistant.services import ask_about_book
from catalog.services import get_book_by_id
from reading.services import log_ai_chat
from users.services import get_reader_by_telegram_id

router = Router(name="ai_chat")


class AIChatStates(StatesGroup):
    waiting_for_question = State()


@router.callback_query(F.data.startswith("book:ai_chat:"))
async def start_ai_chat(callback: CallbackQuery, state: FSMContext) -> None:
    book_id = int(callback.data.split(":")[-1])
    book = await get_book_by_id(book_id)

    if book is None:
        await callback.answer("Kitob topilmadi", show_alert=True)
        return

    await state.update_data(book_id=book_id)
    await state.set_state(AIChatStates.waiting_for_question)
    await callback.message.answer(
        f"🤖 <b>{book.title}</b> haqida nima bilishni xohlaysiz?\n"
        "Savolingizni yozing."
    )
    await callback.answer()


@router.message(AIChatStates.waiting_for_question)
async def process_ai_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    book = await get_book_by_id(data["book_id"])

    if book is None:
        await message.answer("❌ Kitob topilmadi. Qaytadan urinib ko'ring.")
        await state.clear()
        return

    thinking_message = await message.answer("🤔 O'ylab javob tayyorlayapman...")

    try:
        answer = await ask_about_book(message.text, book)
    except Exception as exc:
        await thinking_message.edit_text(f"❌ AI xizmatiga ulanishda xatolik: {exc}")
        return

    await thinking_message.edit_text(answer)

    reader = await get_reader_by_telegram_id(message.from_user.id)
    if reader:
        await log_ai_chat(
            reader_id=reader.id,
            book_id=book.id,
            question=message.text,
            answer=answer,
        )

    await state.clear()