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