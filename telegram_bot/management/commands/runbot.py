"""
Telegram botni Django orqali ishga tushirish uchun buyruq.

Ishlatilishi:
    python manage.py runbot

Bu Django app'lari (users, catalog, reading) ni to'liq ishga tushirilgan
holatda (ORM, settings, va h.k.) aiogram botiga bog'laydi. Alohida server
yoki jarayon menejeri kerak emas — bitta buyruq bilan bot ishga tushadi.
"""

import asyncio

from django.core.management.base import BaseCommand

from telegram_bot.bot.factory import create_bot, create_dispatcher


class Command(BaseCommand):
    help = "AI Smart Library Telegram botini polling rejimida ishga tushiradi"

    def handle(self, *args, **options) -> None:
        self.stdout.write(self.style.SUCCESS("🤖 Bot ishga tushmoqda..."))
        try:
            asyncio.run(self._run_bot())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Bot to'xtatildi."))

    async def _run_bot(self) -> None:
        bot = create_bot()
        dp = create_dispatcher()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)