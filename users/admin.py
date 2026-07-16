from django.contrib import admin

from users.models import Reader


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ("full_name", "username", "telegram_id", "role", "language", "created_at")
    list_filter = ("role", "language")
    search_fields = ("full_name", "username", "telegram_id")
    readonly_fields = ("telegram_id", "created_at")
    ordering = ("-created_at",)