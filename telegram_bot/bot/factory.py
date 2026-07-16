"""
Bot va Dispatcher instance'larini yaratish, barcha routerlarni ulash.

FSM holatlari uchun hozircha MemoryStorage ishlatiladi (development uchun
yetarli). Agar botni bir nechta worker/process bilan ishga tushirmoqchi
bo'lsangiz yoki qayta ishga tushganda foydalanuvchi holati saqlanishi kerak
bo'lsa, buni RedisStorage bilan almashtiring: `pip install redis` va
`from aiogram.fsm.storage.redis import RedisStorage`.
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings

from telegram_bot.bot.handlers import ai_chat, channel_intake, download, search, start


def create_bot() -> Bot:
    if not settings.BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN sozlanmagan. .env fayliga BOT_TOKEN=... qatorini qo'shing."
        )
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # Yangi modul (handler) qo'shilganda faqat shu yerga bitta qator qo'shiladi
    dp.include_router(start.router)
    dp.include_router(search.router)
    dp.include_router(download.router)
    dp.include_router(ai_chat.router)
    dp.include_router(channel_intake.router)

    return dp