from .views import *
from django.urls import path

urlpatterns = [
    path("gerar_token", GenerateToken.as_view(), name="generate_token")
]