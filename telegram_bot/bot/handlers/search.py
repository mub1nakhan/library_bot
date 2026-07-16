"""
Kitob qidiruv handleri.

Bosqich hozirgi: oddiy keyword-based qidiruv (icontains).
Bosqich 3 da: agar oddiy qidiruv natija bermasa yoki foydalanuvchi
uzun/"gapiruvchi" jumla yozsa (masalan "Pythonni endi boshlayotganlar
uchun kitob kerak"), so'rov Claude API'ga AI Intelligent Search sifatida
uzatiladi. Handler tuzilishi o'zgarmaydi — faqat catalog.services.search_books
ichidagi logika kengayadi.

FSM holati xotirada emas, MemoryStorage orqali saqlanadi (Bosqich hozirgi
uchun yetarli; ko'p foydalanuvchili productionda buni RedisStorage bilan
almashtirish tavsiya etiladi — quyida eslatma bor).
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from catalog.services import search_books

router = Router(name="search")


class SearchStates(StatesGroup):
    waiting_for_query = State()


@router.callback_query(F.data == "menu:search")
async def start_search(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_for_query)
    await callback.message.answer(
        "🔍 Nima qidiryapsiz?\n\n"
        "Kitob nomi, muallif yoki hatto oddiy tilda maqsadingizni yozing:\n"
        "<i>masalan: \"Pythonni endi boshlayotganlar uchun kitob kerak\"</i>"
    )
    await callback.answer()


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext) -> None:
    results = await search_books(query=message.text, limit=10)

    if not results:
        await message.answer(
            "😔 Afsuski, hech narsa topilmadi.\n"
            "Boshqa kalit so'z bilan urinib ko'ring, yoki AI Kutubxonachidan yordam so'rang."
        )
        await state.clear()
        return

    lines = ["📚 <b>Topilgan kitoblar:</b>\n"]
    for i, book in enumerate(results, start=1):
        lines.append(f"{i}. <b>{book.title}</b> — {book.author.full_name}")

    await message.answer("\n".join(lines))
    await state.clear()