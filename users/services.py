"""
Users service qatlami.

Bu yerda Telegram bot handler'lari to'g'ridan-to'g'ri Django ORM bilan
ishlamaydi — buning o'rniga shu servis funksiyalarini chaqiradi.
Bu qatlam "Fat models, thin views" printsipining davomi: bot handler'lar
ham "thin" bo'lishi kerak, biznes logika esa bitta joyda jamlanadi.

Django 5+ dagi async ORM (aget_or_create va h.k.) tufayli aiogram'ning
async handler'lari ichida to'g'ridan-to'g'ri chaqirish mumkin — alohida
sync_to_async o'raш shart emas.
"""

from users.models import Reader


async def register_reader(
    telegram_id: int,
    full_name: str,
    username: str | None = None,
    language: str = "uz",
) -> tuple[Reader, bool]:
    """
    Foydalanuvchini ro'yxatdan o'tkazadi, agar allaqachon mavjud bo'lsa — topib qaytaradi.

    Returns: (reader, is_new_user)
    """
    reader, created = await Reader.objects.aget_or_create(
        telegram_id=telegram_id,
        defaults={
            "full_name": full_name,
            "username": username,
            "language": language,
        },
    )
    return reader, created


async def get_reader_by_telegram_id(telegram_id: int) -> Reader | None:
    return await Reader.objects.filter(telegram_id=telegram_id).afirst()


async def update_reader_interests(telegram_id: int, interests: list[str]) -> Reader:
    reader = await Reader.objects.aget(telegram_id=telegram_id)
    reader.interests = interests
    await reader.asave(update_fields=["interests"])
    return reader