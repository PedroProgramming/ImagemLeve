from .views import *
from django.urls import path


urlpatterns = [
    path("step-1/", Step1.as_view(), name="step1"),
    path("step-2/<str:invoice_id>", Step2.as_view(), name="step2"),

    path("webhook/", Webhook.as_view(), name="webhook")
]