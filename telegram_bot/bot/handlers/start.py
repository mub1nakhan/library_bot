"""
/start handler.

Ikki holatni qamrab oladi:
1. Oddiy /start — foydalanuvchini ro'yxatdan o'tkazadi, asosiy menyuni ko'rsatadi.
2. /start <qr_token> — QR kod skaner qilinganda keladigan deep link,
   to'g'ridan-to'g'ri kitob sahifasini ochadi.

Handler'lar Django ORM bilan bevosita ishlamaydi — barcha DB operatsiyalari
users/catalog app'laridagi services.py orqali amalga oshiriladi. Shu tufayli
bot kodi "thin" bo'lib qoladi, biznes logika esa qayta ishlatiladigan joyda turadi.
"""

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

from catalog.services import get_book_by_qr_token
from telegram_bot.bot.keyboards.main_menu import book_card_keyboard, main_menu_keyboard
from users.services import register_reader

router = Router(name="start")


@router.message(CommandStart(deep_link=True))
async def handle_start_with_deeplink(message: Message, command: CommandObject) -> None:
    qr_token = command.args

    await register_reader(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        language=message.from_user.language_code or "uz",
    )

    book = await get_book_by_qr_token(qr_token)
    if book is None:
        await message.answer(
            "❌ Kechirasiz, bu QR kod eskirgan yoki noto'g'ri.\n"
            "Iltimos, /start buyrug'i orqali botni qaytadan boshlang."
        )
        return

    text = (
        f"📖 <b>{book.title}</b>\n"
        f"✍️ Muallif: {book.author.full_name}\n"
        f"📂 Kategoriya: {book.category.name}\n\n"
        f"{book.description or 'Tavsif hali qo\u2018shilmagan.'}"
    )
    await message.answer(text, reply_markup=book_card_keyboard(book.id, book.available_formats()))


@router.message(CommandStart())
async def handle_start_plain(message: Message) -> None:
    reader, is_new = await register_reader(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        language=message.from_user.language_code or "uz",
    )

    if is_new:
        greeting = (
            f"👋 Salom, {reader.full_name}!\n\n"
            "<b>AI Smart Library</b> platformasiga xush kelibsiz.\n"
            "Men sizning shaxsiy AI kutubxonachingizman — kerakli kitobni topishga, "
            "tavsiyalar berishga va kitoblar haqidagi savollaringizga javob berishga tayyorman.\n\n"
            "Nima bilan boshlaymiz?"
        )
    else:
        greeting = f"👋 Xush kelibsiz, {reader.full_name}! Davom etamizmi?"

    await message.answer(greeting, reply_markup=main_menu_keyboard())