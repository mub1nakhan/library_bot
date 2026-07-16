"""
ReadingProgress — bitta o'quvchi va bitta kitob orasidagi o'qish holati.

AI Personalized Recommendation (Bosqich 4) aynan shu jadvaldagi
ma'lumotlardan foydalanadi: qaysi kitoblar tugallangan, qaysilari
tashlab qo'yilgan va h.k.
"""

from django.db import models

from catalog.models import Book
from users.models import Reader


class ReadingProgress(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "Jarayonda"
        COMPLETED = "completed", "Tugallangan"
        ABANDONED = "abandoned", "Tashlab qo'yilgan"

    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name="reading_progress")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reading_progress")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.IN_PROGRESS)
    progress_percent = models.PositiveSmallIntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "O'qish jarayoni"
        verbose_name_plural = "O'qish jarayonlari"
        constraints = [
            models.UniqueConstraint(fields=["reader", "book"], name="uq_reader_book")
        ]

    def __str__(self) -> str:
        return f"{self.reader} — {self.book} ({self.get_status_display()})"


class AIChatLog(models.Model):
    """
    AI Chat suhbatlarini saqlaydi. Bosqich 3 (AI Chat) va Bosqich 6
    (AI Analytics — eng ko'p so'raladigan savollar) uchun tayyorlab qo'yiladi.
    """
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name="ai_chat_logs")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_chat_logs")
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AI suhbat yozuvi"
        verbose_name_plural = "AI suhbat yozuvlari"
        ordering = ["-created_at"]