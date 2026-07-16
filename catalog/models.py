"""
Kutubxona katalogi: Category, Author, Book.

Fayllar (PDF/EPUB/Audio) hozircha Django'ning oddiy FileField orqali
lokal diskka saqlanadi. Bosqich keyingisida bu S3/MinIO'ga ko'chiriladi —
FileField'ning storage backend'ini almashtirish yetarli, model
strukturasi deyarli o'zgarmaydi.
"""

import uuid

from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = "Muallif"
        verbose_name_plural = "Mualliflar"
        ordering = ["full_name"]

    def __str__(self) -> str:
        return self.full_name


def book_file_upload_path(instance: "Book", filename: str) -> str:
    return f"books/{instance.id or 'new'}/{filename}"


def book_qr_upload_path(instance: "Book", filename: str) -> str:
    return f"qrcodes/{instance.qr_token}.png"


def book_cover_upload_path(instance: "Book", filename: str) -> str:
    return f"covers/{instance.id or 'new'}/{filename}"


class Book(models.Model):
    class Language(models.TextChoices):
        UZ = "uz", "O'zbekcha"
        RU = "ru", "Ruscha"
        EN = "en", "Inglizcha"

    title = models.CharField(max_length=500, db_index=True)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="books")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books")
    description = models.TextField(blank=True)
    language = models.CharField(max_length=8, choices=Language.choices, default=Language.UZ)

    # Fayllar — admin panel orqali lokal yuklash (ixtiyoriy, zaxira variant)
    pdf_file = models.FileField(upload_to=book_file_upload_path, blank=True, null=True)
    epub_file = models.FileField(upload_to=book_file_upload_path, blank=True, null=True)
    audio_file = models.FileField(upload_to=book_file_upload_path, blank=True, null=True)
    cover_image = models.ImageField(upload_to=book_cover_upload_path, blank=True, null=True)

    # --- Telegram Storage Channel orqali kelgan fayllar (asosiy usul) ---
    # Fayl kanalda qoladi, biz faqat Telegram'ning file_id'sini saqlaymiz.
    # file_id orqali istalgan vaqt botdan qayta yuborish mumkin — hech qanday
    # cloud storage (S3/MinIO) shart emas.
    pdf_file_id = models.CharField(max_length=255, blank=True, null=True)
    pdf_channel_message_id = models.BigIntegerField(blank=True, null=True)
    audio_file_id = models.CharField(max_length=255, blank=True, null=True)
    audio_channel_message_id = models.BigIntegerField(blank=True, null=True)

    # QR / Deep Link uchun unikal token — https://t.me/Bot?start=<qr_token>
    qr_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    # QR kodning tayyor rasm fayli — kitob birinchi marta saqlanganda
    # avtomatik generatsiya qilinadi (pastdagi save() metodiga qarang).
    qr_image = models.ImageField(upload_to=book_qr_upload_path, blank=True, null=True, editable=False)

    # AI uchun: vector DB'dagi (Bosqich 3) embedding yozuvi identifikatori
    embedding_id = models.CharField(max_length=128, blank=True, null=True)

    total_reads = models.PositiveIntegerField(default=0)
    total_downloads = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} — {self.author}"

    def save(self, *args, **kwargs) -> None:
        if not self.qr_image:
            from catalog.services import generate_qr_code_file

            deep_link = self.deep_link(settings.BOT_USERNAME)
            content_file = generate_qr_code_file(deep_link)
            # save=False — hozircha faylni xotiraga bog'laymiz, DB yozuvi
            # pastdagi super().save() bilan birga, bitta so'rovda amalga oshadi
            self.qr_image.save(f"{self.qr_token}.png", content_file, save=False)
        super().save(*args, **kwargs)

    def available_formats(self) -> list[str]:
        formats = []
        if self.pdf_file or self.pdf_file_id:
            formats.append("pdf")
        if self.epub_file:
            formats.append("epub")
        if self.audio_file or self.audio_file_id:
            formats.append("audio")
        return formats

    def deep_link(self, bot_username: str) -> str:
        return f"https://t.me/{bot_username}?start={self.qr_token}"