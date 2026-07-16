from django.contrib import admin
from django.utils.html import format_html

from catalog.models import Author, Book, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ("full_name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "language",
        "formats_badge",
        "total_reads",
        "total_downloads",
        "qr_token",
    )
    list_filter = ("category", "language")
    search_fields = ("title", "author__full_name")
    readonly_fields = (
        "qr_token",
        "qr_preview",
        "total_reads",
        "total_downloads",
        "created_at",
        "pdf_file_id",
        "pdf_channel_message_id",
        "audio_file_id",
        "audio_channel_message_id",
    )
    autocomplete_fields = ("author", "category")

    fieldsets = (
        (None, {"fields": ("title", "author", "category", "language", "description")}),
        ("Fayllar (qo'lda yuklash, ixtiyoriy)", {"fields": ("pdf_file", "epub_file", "audio_file", "cover_image")}),
        (
            "Telegram kanal orqali kelgan fayllar (avtomatik)",
            {"fields": ("pdf_file_id", "pdf_channel_message_id", "audio_file_id", "audio_channel_message_id")},
        ),
        ("AI / QR", {"fields": ("qr_token", "qr_preview", "embedding_id")}),
        ("Statistika", {"fields": ("total_reads", "total_downloads", "created_at")}),
    )

    @admin.display(description="QR kod")
    def qr_preview(self, obj: Book) -> str:
        if not obj.qr_image:
            return "—"
        return format_html(
            '<img src="{}" style="width:160px;height:160px;border:1px solid #444;padding:4px;background:#fff" />',
            obj.qr_image.url,
        )

    @admin.display(description="Formatlar")
    def formats_badge(self, obj: Book) -> str:
        formats = obj.available_formats()
        if not formats:
            return format_html('<span style="color:#999">yo\u2018q</span>')
        return format_html(", ".join(f"<b>{f.upper()}</b>" for f in formats))