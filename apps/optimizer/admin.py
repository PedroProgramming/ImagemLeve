from django.contrib import admin
from .models import AccessToken, OptimizingImages, WebhookLog

admin.site.register(WebhookLog)
admin.site.register(AccessToken)
admin.site.register(OptimizingImages)