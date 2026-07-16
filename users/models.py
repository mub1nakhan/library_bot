"""
Reader — Telegram orqali botga kirgan o'quvchi.

MUHIM: bu Django'ning o'rnatilgan auth.User modelidan FARQLI narsa.
auth.User — bu admin panelga kiradigan xodimlar (kutubxonachi, admin) uchun.
Reader — bu Telegram bot orqali kitob o'qiydigan oddiy foydalanuvchilar uchun.
Ular hech qachon Django admin login-parol bilan kirmaydi.
"""

from django.db import models


class Reader(models.Model):
    class Role(models.TextChoices):
        READER = "reader", "O'quvchi"
        MODERATOR = "moderator", "Moderator"

    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.READER)
    language = models.CharField(max_length=8, default="uz")

    # AI Personalized Recommendation shu maydondan foydalanadi
    interests = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "O'quvchi"
        verbose_name_plural = "O'quvchilar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} (@{self.username or 'no_username'})"