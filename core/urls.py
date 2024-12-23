from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

from .api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path("checkout/", include("payments.urls")),
    path("usuarios/", include("accounts.urls")),
    path("otimizador", include("optimizer.urls")),
    path("api/", api.urls, name="api"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)