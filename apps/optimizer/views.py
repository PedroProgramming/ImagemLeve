from django.views import View
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.http import HttpRequest, HttpResponse

from .models import AccessToken

class GenerateToken(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        instance, created = AccessToken.objects.get_or_create(
            user=request.user,
            defaults={"token": AccessToken.gen_token(request.user.id)}
        )

        if not created:
            instance.token = AccessToken.gen_token(request.user.id)
            instance.save()
        
        messages.add_message(request, constants.SUCCESS, "Token atualizado com sucesso")
        return redirect(reverse("perfil"))
