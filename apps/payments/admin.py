from django.contrib import admin
from .models import CreditCards, ProcessedWebhook

admin.site.register(CreditCards)
admin.site.register(ProcessedWebhook)