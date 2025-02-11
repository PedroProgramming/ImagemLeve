import json
from decimal import Decimal
from django.views import View
from django.db.models import Q
from django.urls import reverse
from accounts.models import User
from django.conf import settings
from django.db import transaction 
from datetime import date, timedelta
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.messages import constants
from payments.asaas.payment_enum import BillingType
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from payments.asaas.asaas_payment import AsaasInvoice
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from payments.asaas.payments_dataclasses import CreditCard, CreditCardHolderInfo, Billing

from .forms import CheckoutCreditCard
from .models import CreditCards, ProcessedWebhook


@method_decorator([login_required], "dispatch")
class Step1(View):
    template_name = "step1.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)
    
    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        value = float(request.POST.get("value").replace("R$", "").replace(".","").replace(",","."))
        billing_type = request.POST.get("billing_type")
        due_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        asaas = AsaasInvoice()
        billing = Billing(
            request.user.customer_id, billing_type, value, due_date, externalReference="IMAGEM_LEVE_ADD_SALDO"
        )
        response = asaas.create_invoice(billing)
        return redirect(reverse("step2", kwargs={"invoice_id": response["id"]}))
    
@method_decorator([login_required], "dispatch")
class Step2(View):
    template_name = 'step2.html'

    def get(self, request: HttpRequest, invoice_id: str) -> HttpResponse:
        asaas = AsaasInvoice()
        invoice = asaas.get_invoice(invoice_id)

        if invoice['customer'] != request.user.customer_id:
            raise Http404()

        pix_data = None
        if invoice['billingType'] == BillingType.PIX.value:
            pix_data = asaas.get_pix_invoice(invoice_id)
            print(pix_data)

        credit_cards = None
        if invoice['billingType'] == BillingType.CREDIT_CARD.value:
            credit_cards = CreditCards.objects.filter(user=request.user)

        form = CheckoutCreditCard()

        return render(
            request,
            self.template_name,
            {
                'pix_data': pix_data,
                'invoice': invoice,
                'credit_cards': credit_cards,
                'form': form,
            },
        )

    def post(self, request: HttpRequest, invoice_id: str) -> HttpResponseRedirect:
        asaas = AsaasInvoice()
        invoice = asaas.get_invoice(invoice_id)

        if invoice['customer'] != request.user.customer_id:
            raise Http404()

        if credit_card_token := request.POST.get('credit_card_token'):
            card = CreditCards.objects.get(credit_card_token=credit_card_token)

            if card.user != request.user:
                raise Http404()

            response = asaas.pay_invoice(
                invoice_id, None, None, credit_card_token
            )
            return redirect(reverse('home'))
        else:
            form = CheckoutCreditCard(request.POST)

            if form.is_valid():
                expiration_month, expiration_year = form.cleaned_data[
                    'expiration_date'
                ].split('/')
                credit_card = CreditCard(
                    form.cleaned_data['holder_name'],
                    form.cleaned_data['card_number'],
                    expiration_month,
                    expiration_year,
                    form.cleaned_data['cvc'],
                )
                holder_info = CreditCardHolderInfo(
                    request.user.first_name,
                    request.user.email,
                    request.user.cpf_cnpj,
                    form.cleaned_data['postal_code'],
                    form.cleaned_data['house_number'],
                    form.cleaned_data['phone'],
                )
                response = asaas.pay_invoice(
                    invoice_id, credit_card, holder_info)

                try:
                    tokenize = asaas.tokenize_credit_card(
                        request.user.customer_id,
                        credit_card,
                        holder_info,
                        request.META['REMOTE_ADDR'],
                    )
                    credit_cards = CreditCards(
                        last_numbers_credit_card=tokenize['creditCardNumber'],
                        credit_card_brand=tokenize['creditCardBrand'],
                        credit_card_token=tokenize['creditCardToken'],
                        user=request.user,
                    )
                    credit_cards.save()
                except:
                    pass

        if response.status_code != 200:
            for error in response.json()['errors']:
                messages.add_message(
                    request, constants.ERROR, error['description']
                )

            return redirect(
                reverse('step2', kwargs={'invoice_id': invoice_id})
            )

        return redirect(reverse('home'))

@method_decorator([csrf_exempt], "dispatch")
class Webhook(View):
    def post(self, request: HttpRequest):

        if request.META.get("HTTP_ASAAS_ACCESS_TOKEN") != settings.WEBHOOK_TOKEN:
            return Http404()
        payload = json.loads(request.body)
        event = payload.get("event")

        external_reference = payload.get("payment", {}).get("externalReference")
        customer_id = payload.get("payment", {}).get("customer")
        value = payload.get("payment", {}).get("value")
        invoice_id = payload.get("payment", {}).get("id")

        if ProcessedWebhook.objects.filter(Q(event_id=payload.get("id")) | (Q(invoice_id=invoice_id) & Q(event_in=["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]))).exists():
            return HttpResponse(status=200)

        with transaction.atomic():
            processed_webhook = ProcessedWebhook(
                event_id=payload.get("id"),
                invoice_id=invoice_id,
                event=event,
                payload=payload
            )
            processed_webhook.save()

            if event in ("PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"):
                

                if external_reference == "IMAGEM_LEVE_ADD_SALDO":
                    user = User.objects.get(customer_id=customer_id)
                    user.balance += Decimal(value)
                    user.save()

        return HttpResponse(status=200)