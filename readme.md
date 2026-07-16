# AI Smart Library Platform (Django + aiogram)

AI asosida ishlaydigan Telegram kutubxona platformasi. Django framework
ustida qurilgan — bu Admin panel, ORM va migratsiyalarni tayyor holda beradi.

## Arxitektura

```
config/                  # Django loyiha sozlamalari
├── settings.py            # PostgreSQL, .env, INSTALLED_APPS
├── urls.py
└── wsgi.py / asgi.py

users/                   # O'quvchilar (Telegram foydalanuvchilari)
├── models.py              # Reader
├── services.py            # Biznes logika (register_reader va h.k.)
└── admin.py

catalog/                 # Kutubxona katalogi
├── models.py              # Book, Author, Category
├── services.py            # search_books, get_book_by_qr_token va h.k.
└── admin.py

reading/                 # O'qish tarixi va AI suhbat loglari
├── models.py              # ReadingProgress, AIChatLog
└── admin.py

telegram_bot/            # Telegram bot (aiogram)
├── bot/
│   ├── factory.py          # Bot va Dispatcher yaratish
│   ├── handlers/           # /start, qidiruv va h.k.
│   └── keyboards/          # Inline klaviaturalar
└── management/commands/
    └── runbot.py            # `python manage.py runbot`
```

### Nega bu tuzilish?

- Har bir Django app o'z ichida `models.py` (ma'lumot) va `services.py`
  (biznes logika) ga ega. Bot handler'lar hech qachon to'g'ridan-to'g'ri
  ORM bilan ishlamaydi — faqat `services.py` orqali. Shu tufayli ertaga
  Web Dashboard yoki REST API qo'shilsa, xuddi shu servis funksiyalari
  qayta ishlatiladi.
- Django 6 ning **async ORM** imkoniyatlari (`aget`, `acreate`,
  `aget_or_create`, `async for`) tufayli aiogram'ning async handler'lari
  ichida ORM'ni to'g'ridan-to'g'ri, `sync_to_async` o'rashsiz chaqirish mumkin.
- Bot Django management command sifatida ishga tushadi (`runbot`) —
  alohida server, alohida process manager shart emas.

## O'rnatish (Docker'siz, lokal)

### 1. PostgreSQL tayyorlash

Sizda PostgreSQL allaqachon o'rnatilgan. Faqat DB va user yarating:

```bash
sudo -u postgres psql -c "CREATE USER library_user WITH PASSWORD 'library_pass' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE smart_library OWNER library_user;"
```

### 2. Virtual environment va kutubxonalar

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Konfiguratsiya

```bash
cp .env.example .env
```

`.env` faylini oching va to'ldiring:
- `BOT_TOKEN` — @BotFather'dan olingan token
- `DATABASE_URL` — agar user/parol boshqacha bo'lsa, moslang
- `ANTHROPIC_API_KEY` — Claude API kaliti (Bosqich 3 uchun kerak bo'ladi)

### 4. Migratsiyalar

```bash
python manage.py migrate
python manage.py createsuperuser   # Admin panelga kirish uchun
```

### 5. Ishga tushirish

Ikkita alohida terminalda:

```bash
# Terminal 1 — Django admin panel (http://127.0.0.1:8000/admin)
python manage.py runserver

# Terminal 2 — Telegram bot
python manage.py runbot
```

Shu bilan tamom — Docker, alohida servis, hech narsa kerak emas.

## Admin panelda nima qilish mumkin?

`/admin` ga kiring va:
- **Kategoriyalar** va **Mualliflar** qo'shing
- **Kitob** qo'shing — PDF/EPUB/Audio fayllarni to'g'ridan-to'g'ri
  admin panel orqali yuklashingiz mumkin, QR token avtomatik generatsiya bo'ladi
- **O'quvchilar** ro'yxatini ko'ring (ular Telegram orqali o'zi qo'shiladi)

## Hozirgi holat (Bosqich 1 — Poydevor)

- ✅ Django loyiha strukturasi (app'larga bo'lingan, services qatlami bilan)
- ✅ PostgreSQL: Reader, Category, Author, Book, ReadingProgress, AIChatLog
- ✅ Django Admin panel — kitob/kategoriya/muallif boshqaruvi tayyor
- ✅ Telegram bot: `/start`, ro'yxatdan o'tish, QR/deep-link orqali kitob ochish
- ✅ Oddiy kitob qidiruv (keyword-based)

## Keyingi bosqichlar

| Bosqich | Mazmuni |
|---|---|
| 2 | QR kod rasm generatsiyasi, media fayllarni S3/MinIO'ga ko'chirish |
| 3 | AI Chat, RAG, Intelligent Search (Claude API + vector DB) |
| 4 | Personalized Recommendation, AI Librarian |
| 5 | AI Summary, AI Explain, AI Quiz |
| 6 | AI Analytics (admin panelda statistik dashboard) |
| 7 | Web Dashboard / Mobile App uchun Django REST Framework API |