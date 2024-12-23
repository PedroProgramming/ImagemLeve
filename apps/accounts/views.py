from django.views import View
from django.urls import reverse
from django.core.cache import cache
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.messages import constants
from optimizer.models import AccessToken, WebhookLog
from django.utils.decorators import method_decorator
from payments.asaas.asaas_payment import AsaasInvoice
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect

from .forms import UserCreationForm


class Register(View):
    template_name = "register.html"
    form = UserCreationForm

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, {"form": self.form()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = self.form(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        return render(request, self.template_name, {"form": form})

@method_decorator([login_required], "dispatch")
class Perfil(View):
    template_name = "perfil.html"
    
    def get(self, request: HttpRequest) -> HttpResponse:
        asaas = AsaasInvoice()
        
        cache_key = f"invoices_{request.user.id}"

        invoices = cache.get(cache_key)
        if not invoices:
            invoices = asaas.list_invoices(request.user.customer_id)
            cache.set(cache_key, invoices, 60 * 5)

        logs = WebhookLog.objects.filter(user=request.user)
        access_token = AccessToken.objects.filter(user=request.user).first()
        return render(request, self.template_name, {"invoices": invoices["data"], "token_api": access_token, "logs": logs})
    
@method_decorator([login_required], "dispatch")
class SetWebhook(View):

    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        url = request.GET.get("webhook")
        request.user.webhook = url
        request.user.save()
        messages.add_message(request, constants.SUCCESS, "Webhook definido com sucesso")
        return redirect(reverse("perfil"))

@method_decorator([login_required], "dispatch")
class ViewLog(View):
    template_name = "view_log.html"

    def get(self, request: HttpRequest, log_id: int):
        log = get_object_or_404(WebhookLog, id=log_id)
        return render(request, self.template_name, {"log": log})