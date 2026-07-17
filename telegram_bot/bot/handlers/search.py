"""
Kitob qidiruv handleri.

Bosqich hozirgi: oddiy keyword-based qidiruv (icontains), natijalar
1-rasmdagi kabi raqamli va sahifalanadigan (pagination) ko'rinishda chiqadi:
har bir natija tartib raqami bilan tugma bo'ladi, pastda esa
⬅️ (oldingi) / ❌ (yopish) / ➡️ (keyingi) navigatsiya qatori turadi.

Foydalanuvchi biror raqamni bossa — o'sha kitobning PDF fayli darhol
yuboriladi. Agar shu kitobning audio versiyasi ham mavjud bo'lsa, PDF'dan
keyin alohida xabar bilan "audio versiyasini ham xohlaysizmi?" deb
so'raladi — faqat o'quvchi "Ha" desagina audio yuboriladi, aks holda
(yoki audio umuman mavjud bo'lmasa) hech narsa qo'shimcha chiqmaydi.

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

from catalog.services import (
    count_search_results,
    get_book_by_id,
    increment_read_counter,
    search_books,
)
from telegram_bot.bot.keyboards.main_menu import audio_offer_keyboard, search_results_keyboard

router = Router(name="search")

PAGE_SIZE = 10


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


async def _render_results_page(query: str, offset: int) -> tuple[str, list[int], bool, bool] | None:
    """
    Berilgan so'rov va offset uchun natijalar matnini va klaviatura
    parametrlarini tayyorlaydi. Natija topilmasa None qaytaradi.
    """
    total = await count_search_results(query)
    if total == 0:
        return None

    books = await search_books(query=query, limit=PAGE_SIZE, offset=offset)
    if not books:
        return None

    lines = ["📚 <b>Topilgan kitoblar:</b>\n"]
    for i, book in enumerate(books, start=1):
        lines.append(f"{i}. <b>{book.title}</b> — {book.author.full_name}")
    text = "\n".join(lines)

    book_ids = [book.id for book in books]
    has_prev = offset > 0
    has_next = offset + PAGE_SIZE < total
    return text, book_ids, has_prev, has_next


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext) -> None:
    query = message.text
    rendered = await _render_results_page(query, offset=0)

    if rendered is None:
        await message.answer(
            "😔 Afsuski, hech narsa topilmadi.\n"
            "Boshqa kalit so'z bilan urinib ko'ring, yoki AI Kutubxonachidan yordam so'rang."
        )
        await state.clear()
        return

    text, book_ids, has_prev, has_next = rendered
    await state.update_data(query=query, offset=0)
    await state.set_state(None)  # matn kutish holatini tugatamiz, lekin ma'lumot (query/offset) saqlanib qoladi
    await message.answer(text, reply_markup=search_results_keyboard(book_ids, has_prev, has_next))


@router.callback_query(F.data.startswith("search:nav:"))
async def handle_pagination(callback: CallbackQuery, state: FSMContext) -> None:
    direction = callback.data.split(":")[2]
    data = await state.get_data()
    query = data.get("query")
    offset = data.get("offset", 0)

    if not query:
        await callback.answer("⚠️ Qidiruv muddati tugagan, qaytadan qidiring.", show_alert=True)
        return

    offset = offset + PAGE_SIZE if direction == "next" else max(0, offset - PAGE_SIZE)
    rendered = await _render_results_page(query, offset)

    if rendered is None:
        await callback.answer("Boshqa natija yo'q.", show_alert=True)
        return

    text, book_ids, has_prev, has_next = rendered
    await state.update_data(offset=offset)
    await callback.message.edit_text(text, reply_markup=search_results_keyboard(book_ids, has_prev, has_next))
    await callback.answer()


@router.callback_query(F.data == "search:noop")
async def handle_noop(callback: CallbackQuery) -> None:
    await callback.answer("Bu chegara — boshqa sahifa yo'q.")


@router.callback_query(F.data == "search:close")
async def handle_close(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith("search:pick:"))
async def handle_pick(callback: CallbackQuery) -> None:
    book_id = int(callback.data.split(":")[2])
    book = await get_book_by_id(book_id)

    if book is None:
        await callback.answer("❌ Kitob topilmadi", show_alert=True)
        return

    caption = f"📖 {book.title} — {book.author.full_name}"

    if book.pdf_file_id:
        await callback.message.answer_document(book.pdf_file_id, caption=caption)
    elif book.pdf_file:
        await callback.message.answer_document(book.pdf_file.name, caption=caption)
    else:
        await callback.answer("❌ Bu kitob uchun PDF hali yuklanmagan", show_alert=True)
        return

    await increment_read_counter(book.id)

    # PDF yuborilgandan keyin — agar audio versiya ham mavjud bo'lsa,
    # o'quvchidan so'raymiz. Audio bo'lmasa, hech narsa qo'shimcha chiqmaydi.
    if book.audio_file_id or book.audio_file:
        await callback.message.answer(
            "🎧 Ushbu kitobning audio versiyasi ham mavjud. Uni ham yuklab olishni xohlaysizmi?",
            reply_markup=audio_offer_keyboard(book.id),
        )

    await callback.answer()