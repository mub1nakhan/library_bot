"""
Kitob faylini yuborish handleri.

Foydalanuvchi kitob kartochkasidagi "⬇️ PDF/AUDIO yuklab olish" tugmasini
bosganda ishga tushadi. Fayl serverda saqlanmaydi — Telegram'ning o'z
file_id mexanizmi orqali to'g'ridan-to'g'ri Storage Channel'dan foydalanuvchiga
qayta yuboriladi.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from catalog.services import get_book_by_id, increment_read_counter

router = Router(name="download")


@router.callback_query(F.data.startswith("book:download:"))
async def handle_download(callback: CallbackQuery) -> None:
    _, _, book_id_str, fmt = callback.data.split(":")
    book = await get_book_by_id(int(book_id_str))

    if book is None:
        await callback.answer("❌ Kitob topilmadi", show_alert=True)
        return

    if fmt == "pdf" and book.pdf_file_id:
        await callback.message.answer_document(book.pdf_file_id, caption=f"📖 {book.title}")
    elif fmt == "audio" and book.audio_file_id:
        await callback.message.answer_audio(book.audio_file_id, caption=f"🎧 {book.title}")
    elif fmt == "pdf" and book.pdf_file:
        await callback.message.answer_document(book.pdf_file.name, caption=f"📖 {book.title}")
    else:
        await callback.answer("❌ Bu format uchun fayl hali yuklanmagan", show_alert=True)
        return

    await increment_read_counter(book.id)
    await callback.answer()


@router.callback_query(F.data.startswith("book:audio:"))
async def handle_audio_offer(callback: CallbackQuery) -> None:
    """
    Qidiruv orqali PDF yuborilgandan keyin chiqadigan "audio versiyasini
    ham xohlaysizmi?" so'roviga javob. Faqat o'quvchi "Ha" desa audio
    yuboriladi — "Yo'q" desa yoki bu tugma umuman ko'rsatilmagan bo'lsa,
    hech qanday audio fayl yuborilmaydi.
    """
    _, _, book_id_str, choice = callback.data.split(":")

    if choice == "no":
        await callback.message.edit_text("Yaxshi 👍 Agar keyinchalik audio kerak bo'lsa, kitobni qayta qidiring.")
        await callback.answer()
        return

    book = await get_book_by_id(int(book_id_str))
    if book is None:
        await callback.answer("❌ Kitob topilmadi", show_alert=True)
        return

    if book.audio_file_id:
        await callback.message.answer_audio(book.audio_file_id, caption=f"🎧 {book.title}")
    elif book.audio_file:
        await callback.message.answer_audio(book.audio_file.name, caption=f"🎧 {book.title}")
    else:
        await callback.answer("❌ Audio fayl topilmadi", show_alert=True)
        return

    await callback.message.edit_text(f"✅ \"{book.title}\" kitobining audio versiyasi yuborildi.")
    await callback.answer()