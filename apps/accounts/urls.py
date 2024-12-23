from .views import *
from django.urls import path


urlpatterns = [
    path("cadastro/", Register.as_view(), name="register"),
    path("perfil/", Perfil.as_view(), name="perfil"),

    path("set_webhook", SetWebhook.as_view(), name="set_webhook"),
    path("ver_log/<int:log_id>", ViewLog.as_view(), name="view_log"),
]