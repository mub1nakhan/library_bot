"""
Asosiy menyu va kitob kartochkasi uchun inline klaviaturalar.
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Kitob qidirish", callback_data="menu:search")
    builder.button(text="📚 Kategoriyalar", callback_data="menu:categories")
    builder.button(text="🤖 AI Kutubxonachi", callback_data="menu:ai_librarian")
    builder.button(text="⭐ Tavsiyalar", callback_data="menu:recommend")
    builder.button(text="👤 Mening profilim", callback_data="menu:profile")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def book_card_keyboard(book_id: int, formats: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for fmt in formats:
        builder.button(text=f"⬇️ {fmt.upper()} yuklab olish", callback_data=f"book:download:{book_id}:{fmt}")
    builder.button(text="💬 AI bilan suhbat", callback_data=f"book:ai_chat:{book_id}")
    builder.button(text="📝 AI Xulosa", callback_data=f"book:summary:{book_id}")
    builder.button(text="🔗 O'xshash kitoblar", callback_data=f"book:similar:{book_id}")
    builder.adjust(1)
    return builder.as_markup()


def search_results_keyboard(book_ids: list[int], has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    """
    Qidiruv natijalari uchun raqamli klaviatura (1-rasmdagi ko'rinish kabi):
    har bir natija tartib raqami bilan tugma bo'lib chiqadi (5 tadan qatorda),
    pastda esa ⬅️ / ❌ / ➡️ navigatsiya qatori turadi.

    Sahifaning oxiri/boshi bo'lsa, tegishli ⬅️/➡️ tugma "search:noop" ga
    bog'lanadi — bosilganda hech narsa o'zgarmaydi, faqat qisqa xabar chiqadi.
    """
    builder = InlineKeyboardBuilder()
    for i, book_id in enumerate(book_ids, start=1):
        builder.button(text=str(i), callback_data=f"search:pick:{book_id}")

    builder.button(text="⬅️", callback_data="search:nav:prev" if has_prev else "search:noop")
    builder.button(text="❌", callback_data="search:close")
    builder.button(text="➡️", callback_data="search:nav:next" if has_next else "search:noop")

    number_rows = []
    remaining = len(book_ids)
    while remaining > 0:
        chunk = min(5, remaining)
        number_rows.append(chunk)
        remaining -= chunk
    builder.adjust(*number_rows, 3)
    return builder.as_markup()


def audio_offer_keyboard(book_id: int) -> InlineKeyboardMarkup:
    """
    PDF yuborilgandan so'ng, agar kitobning audio versiyasi ham mavjud bo'lsa,
    o'quvchiga uni ham olishni xohlaydimi deb so'rash uchun klaviatura.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🎧 Ha, audio versiyasini ham yubor", callback_data=f"book:audio:{book_id}:yes")
    builder.button(text="🙅 Yo'q, kerak emas", callback_data=f"book:audio:{book_id}:no")
    builder.adjust(1)
    return builder.as_markup()