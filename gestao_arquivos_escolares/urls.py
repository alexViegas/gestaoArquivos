from django.contrib import admin
from django.urls import path, include

from gestao_arquivos_escolares import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("localizador.urls")), # Includes the app's URLs
]

# Habilita arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

