from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]

# Development rejimida media fayllarni (kitob PDF/audio) to'g'ridan-to'g'ri
# Django orqali xizmat ko'rsatish. Production'da bu nginx/S3 orqali bo'ladi.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)