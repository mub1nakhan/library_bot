"""
Catalog service qatlami — kitob qidiruv va olish bilan bog'liq biznes logika.

Bosqich 2 (hozirgi): oddiy ILIKE-based (icontains) qidiruv.
Bosqich 3: shu yerga AI Intelligent Search qo'shiladi — agar oddiy qidiruv
natija bermasa yoki so'rov "gapiruvchi" jumla bo'lsa, Claude API orqali
foydalanuvchi maqsadi aniqlanadi va shunga mos kitoblar qaytariladi.
Bu funksiyalarning imzosi (signature) o'zgarmaydi, faqat ichki logikasi kengayadi.
"""

import io

import qrcode
from django.core.files.base import ContentFile
from django.db.models import F, Q, QuerySet
from django.utils.text import slugify

from catalog.models import Author, Book, Category


def generate_qr_code_file(data: str) -> ContentFile:
    """
    Berilgan matn (odatda kitobning Telegram deep-link havolasi) asosida
    QR kod rasm faylini generatsiya qiladi va Django FileField'ga
    to'g'ridan-to'g'ri biriktirish mumkin bo'lgan ContentFile qaytaradi.
    """
    qr_img = qrcode.make(data, box_size=10, border=2)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())


async def search_books(query: str, limit: int = 10) -> list[Book]:
    query = query.strip()
    if not query:
        return []

    qs: QuerySet[Book] = (
        Book.objects.select_related("author", "category")
        .filter(Q(title__icontains=query) | Q(author__full_name__icontains=query))[:limit]
    )
    return [book async for book in qs]


async def get_book_by_qr_token(qr_token: str) -> Book | None:
    return await (
        Book.objects.select_related("author", "category")
        .filter(qr_token=qr_token)
        .afirst()
    )


async def list_books_by_category(category_id: int, limit: int = 20, offset: int = 0) -> list[Book]:
    qs = (
        Book.objects.select_related("author", "category")
        .filter(category_id=category_id)[offset : offset + limit]
    )
    return [book async for book in qs]


async def most_popular_books(limit: int = 10) -> list[Book]:
    qs = Book.objects.select_related("author").order_by("-total_reads")[:limit]
    return [book async for book in qs]


async def increment_read_counter(book_id: int) -> None:
    await Book.objects.filter(id=book_id).aupdate(total_reads=F("total_reads") + 1)


async def get_book_by_id(book_id: int) -> Book | None:
    return await Book.objects.select_related("author", "category").filter(id=book_id).afirst()


async def attach_channel_file(
    parsed: dict,
    file_type: str,
    file_id: str,
    channel_message_id: int,
) -> Book:
    """
    Telegram Storage Channel'dan kelgan faylni kitobga biriktiradi.

    `parsed` — AI (yoki caption parser) tomonidan ajratilgan lug'at:
        {"title": ..., "author": ..., "category": ..., "description": ...}

    Agar shu nom+muallif bilan kitob mavjud bo'lmasa — avtomatik yaratiladi.
    Agar mavjud bo'lsa — topilib, shu faylning file_id'si qo'shiladi
    (masalan avval PDF, keyin audio alohida xabar bilan yuborilgan bo'lishi mumkin).
    """
    author_name = (parsed.get("author") or "Noma'lum muallif").strip()
    author, _ = await Author.objects.aget_or_create(full_name=author_name)

    category_name = (parsed.get("category") or "Umumiy").strip()
    category_slug = slugify(category_name) or "umumiy"
    category, _ = await Category.objects.aget_or_create(
        slug=category_slug, defaults={"name": category_name}
    )

    title = (parsed.get("title") or "Nomsiz kitob").strip()
    book, _created = await Book.objects.aget_or_create(
        title=title,
        author=author,
        defaults={
            "category": category,
            "description": parsed.get("description", "") or "",
        },
    )

    if file_type == "pdf":
        book.pdf_file_id = file_id
        book.pdf_channel_message_id = channel_message_id
    elif file_type == "audio":
        book.audio_file_id = file_id
        book.audio_channel_message_id = channel_message_id

    await book.asave()
    return book