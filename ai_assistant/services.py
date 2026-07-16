"""
Claude API bilan ishlovchi markaziy servis.

Bu app'dagi funksiyalar loyihadagi BARCHA AI vazifalarini bajaradi:
- kanaldagi caption'dan kitob ma'lumotini ajratish (parse_book_caption)
- kitob haqida savol-javob (ask_about_book)

Kelajakda AI Summary, AI Quiz, Intelligent Search shu faylga funksiya
sifatida qo'shiladi — Claude client yaratish logikasi bir joyda qoladi.
"""

import json

from anthropic import AsyncAnthropic
from django.conf import settings

_client: AsyncAnthropic | None = None


def get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError(
                "ANTHROPIC_API_KEY sozlanmagan. .env fayliga ANTHROPIC_API_KEY=... qo'shing."
            )
        _client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


PARSE_CAPTION_SYSTEM_PROMPT = """\
Sen kutubxona botining yordamchisisan. Foydalanuvchi Telegram kanaliga \
kitob fayli (PDF yoki audio) yuborganda, unga yozilgan caption matnidan \
kitob haqidagi ma'lumotlarni ajratib olishing kerak.

Faqat quyidagi formatda, boshqa hech qanday matnsiz, sof JSON qaytar:
{"title": "...", "author": "...", "category": "...", "description": "..."}

Qoidalar:
- Agar muallif aniq ko'rsatilmagan bo'lsa, "Noma'lum muallif" deb yoz.
- Agar kategoriya aniq bo'lmasa, matn mazmuniga qarab eng mos kategoriyani \
o'zing tanla (masalan: "Dasturlash", "Tarix", "Roman", "Psixologiya" va h.k.).
- description — caption asosida 1-2 gapli qisqa tavsif, agar caption juda \
qisqa bo'lsa description'ni title asosida qisqa yoz.
- Javobda hech qanday izoh, markdown belgisi (```), yoki qo'shimcha matn bo'lmasin.
"""


async def parse_book_caption(caption: str) -> dict | None:
    """
    Kanalga yuborilgan xabar caption'idan kitob ma'lumotlarini ajratadi.

    Returns: {"title": ..., "author": ..., "category": ..., "description": ...}
             yoki agar AI javobini JSON sifatida o'qib bo'lmasa — None.
    """
    client = get_client()
    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=500,
        system=PARSE_CAPTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": caption}],
    )
    raw_text = "".join(block.text for block in response.content if block.type == "text")

    try:
        return json.loads(raw_text.strip())
    except (json.JSONDecodeError, ValueError):
        return None


ASK_ABOUT_BOOK_SYSTEM_PROMPT = """\
Sen "AI Smart Library" platformasining shaxsiy AI kutubxonachisisan. \
Foydalanuvchi senga kutubxonadagi bitta kitob haqida savol beryapti. \
Faqat sizga berilgan kitob ma'lumotlari (nomi, muallifi, tavsifi) asosida \
javob ber. Agar savolga javob berish uchun ma'lumot yetarli bo'lmasa, \
buni ochiq tan ol va taxmin qilib gapirma. Javobing qisqa, aniq va \
o'zbek tilida bo'lsin.
"""


async def ask_about_book(question: str, book) -> str:
    """
    Kitob haqida foydalanuvchi savoliga Claude orqali javob qaytaradi.

    Hozircha kontekst sifatida faqat kitobning nomi/muallifi/tavsifi
    ishlatiladi (Bosqich hozirgi). Kelajakda bu RAG (kitob matnidan
    semantik qidiruv orqali topilgan bo'laklar) bilan kengaytiriladi —
    funksiya imzosi o'zgarmaydi.
    """
    client = get_client()
    context = (
        f"Kitob nomi: {book.title}\n"
        f"Muallif: {book.author.full_name}\n"
        f"Kategoriya: {book.category.name}\n"
        f"Tavsif: {book.description or 'Tavsif kiritilmagan.'}"
    )
    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=600,
        system=ASK_ABOUT_BOOK_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Kitob ma'lumotlari:\n{context}\n\nSavol: {question}"}
        ],
    )
    return "".join(block.text for block in response.content if block.type == "text")