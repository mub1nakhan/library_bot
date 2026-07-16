"""
Storage Channel handler.

Bu handler siz belgilagan yopiq Telegram kanaliga PDF yoki audio fayl
yuborilganda ishga tushadi (bot o'sha kanalda admin bo'lishi shart).

Ishlash tartibi:
1. Fayl caption'i AI (Claude) orqali tahlil qilinadi — kitob nomi,
   muallifi, kategoriyasi va qisqa tavsifi ajratib olinadi.
2. Shu ma'lumot asosida bazada kitob avtomatik yaratiladi (yoki mavjudi
   topiladi, agar avval boshqa format allaqachon yuborilgan bo'lsa).
3. Faylning o'zi HECH QAYERGA ko'chirilmaydi — faqat Telegram file_id'si
   saqlanadi. Fayl har doim shu kanalda, Telegram serverida qoladi.
4. Kanalga tasdiqlovchi javob yoziladi (kitob nomi + QR havola).

MUHIM: faqat .env faylida STORAGE_CHANNEL_ID sifatida ko'rsatilgan
kanaldan kelgan xabarlar qabul qilinadi — boshqa har qanday kanal e'tiborga olinmaydi.
"""

from aiogram import F, Router
from aiogram.types import Message
from django.conf import settings

from ai_assistant.services import parse_book_caption
from catalog.services import attach_channel_file

router = Router(name="channel_intake")


def _is_storage_channel(message: Message) -> bool:
    if not settings.STORAGE_CHANNEL_ID:
        return False
    return str(message.chat.id) == str(settings.STORAGE_CHANNEL_ID)


@router.channel_post(F.document)
async def handle_channel_document(message: Message) -> None:
    if not _is_storage_channel(message):
        return

    if message.document.mime_type != "application/pdf":
        await message.reply("⚠️ Hozircha faqat PDF hujjatlar qabul qilinadi.")
        return

    await _process_channel_file(
        message=message,
        file_type="pdf",
        file_id=message.document.file_id,
    )


@router.channel_post(F.audio)
async def handle_channel_audio(message: Message) -> None:
    if not _is_storage_channel(message):
        return

    await _process_channel_file(
        message=message,
        file_type="audio",
        file_id=message.audio.file_id,
    )


async def _process_channel_file(message: Message, file_type: str, file_id: str) -> None:
    caption = (message.caption or "").strip()

    if not caption:
        await message.reply(
            "⚠️ Caption yozilmagan. Iltimos, faylni qayta yuboring va "
            "caption'ga kitob nomi, muallifi va mavzusini yozing.\n\n"
            "<i>Masalan: \"Clean Code — Robert Martin. Toza kod yozish "
            "bo'yicha dasturlash kitobi.\"</i>"
        )
        return

    try:
        parsed = await parse_book_caption(caption)
    except Exception as exc:  # AI xizmati vaqtincha ishlamasa ham botni to'xtatmaslik uchun
        await message.reply(f"❌ AI xizmatiga ulanishda xatolik: {exc}")
        return

    if not parsed:
        await message.reply(
            "❌ Caption'dan kitob ma'lumotlarini ajratib bo'lmadi. "
            "Iltimos, aniqroq yozib qayta yuboring."
        )
        return

    book = await attach_channel_file(
        parsed=parsed,
        file_type=file_type,
        file_id=file_id,
        channel_message_id=message.message_id,
    )

    deep_link = book.deep_link(settings.BOT_USERNAME)
    await message.reply(
        f"✅ <b>{book.title}</b>\n"
        f"✍️ Muallif: {book.author.full_name}\n"
        f"📂 Kategoriya: {book.category.name}\n"
        f"📎 Format: {file_type.upper()}\n\n"
        f"🔗 QR havola: {deep_link}"
    )