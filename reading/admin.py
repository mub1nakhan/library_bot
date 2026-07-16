from django.contrib import admin

from reading.models import AIChatLog, ReadingProgress


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ("reader", "book", "status", "progress_percent", "started_at", "finished_at")
    list_filter = ("status",)
    search_fields = ("reader__full_name", "book__title")


@admin.register(AIChatLog)
class AIChatLogAdmin(admin.ModelAdmin):
    list_display = ("reader", "book", "question_preview", "created_at")
    readonly_fields = ("reader", "book", "question", "answer", "created_at")
    search_fields = ("question", "reader__full_name")

    @admin.display(description="Savol")
    def question_preview(self, obj: AIChatLog) -> str:
        return obj.question[:60] + ("..." if len(obj.question) > 60 else "")

    def has_add_permission(self, request) -> bool:
        # Bu jadval faqat AI Chat orqali avtomatik to'ldiriladi
        return False