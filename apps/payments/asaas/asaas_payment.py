import requests
from dataclasses import asdict
from django.conf import settings
from .payment_enum import BillingType
from datetime import date, timedelta
from urllib.parse import urlencode, urljoin
from .payments_dataclasses import CreditCard, CreditCardHolderInfo, Billing


class AsaasBasePayment:
    def __init__(self):
        self._BASE_URL = 'https://sandbox.asaas.com/api/v3/'
        self._API_KEY = '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwOTUyNDg6OiRhYWNoX2Q3MWYxZTAwLWFmYmEtNGQwMy1iYjFlLTExOWJjZTVlMTI4Nw=='
        """
        self._API_KEY = settings.API_KEY_ASAAS
        self._BASE_URL = (
            "https://api.asaas.com/"
            if not settings.DEBUG
            else "https://sandbox.asaas.com/api/v3/"
        )
        """

    def _send_request(
        self,
        path: str,
        method='GET',
        body=None,
        headers={},
        params_url={},
        use_api_key=True,
    ):
        method.upper()
        url = self._mount_url(path, params_url)

        if not isinstance(headers, dict):
            headers = {}

        if use_api_key:
            headers['access_token'] = str(self._API_KEY)

        headers['Content-Type'] = 'application/json'
        match method:
            case 'GET':
                response = requests.get(url, headers=headers, json=body)
            case 'POST':
                response = requests.post(url, headers=headers, json=body)
            case 'PUT':
                response = requests.put(url, headers=headers, json=body)
            case 'DELETE':
                response = requests.delete(url, headers=headers, json=body)
        return response

    def _mount_url(self, path: str, params_url: dict):
        if isinstance(params_url, dict):
            parameters = urlencode(params_url)

        url = urljoin(self._BASE_URL, path)
        if parameters:
            url = url + '?' + parameters
        return url


class AsaasCustomer(AsaasBasePayment):
    def create_customer(self, **kwargs):
        """
        Possibilidades de paramentros para kwargs
        https://docs.asaas.com/reference/criar-novo-cliente
        """

        if 'name' not in kwargs.keys() or 'cpfCnpj' not in kwargs.keys():
            raise KeyError('name e cpfCnpj são campos obrigatórios')

        return self._send_request(
            path='customers', method='POST', body=kwargs
        ).json()

    def list_customer(self, **kwargs):
        """
        kwargs representão os params_url. Confira as possibilidades em
        https://docs.asaas.com/reference/listar-clientes
        """

        return self._send_request(path='customers', params_url=kwargs).json()

    def get_customer(self, customer_id: str):
        return self._send_request(path=f'customers/{customer_id}').json()


class AsaasInvoice(AsaasBasePayment):
    def tokenize_credit_card(
        self,
        customer_id: str,
        credit_card: CreditCard,
        credit_card_holder_info: CreditCardHolderInfo,
        remote_ip: float,
    ):
        payload = {
            'customer': customer_id,
            'creditCard': asdict(credit_card),
            'creditCardHolderInfo': asdict(credit_card_holder_info),
            'remoteIp': remote_ip,
        }
        return self._send_request(
            path='creditCard/tokenizeCreditCard', method='POST', body=payload
        ).json()

    def create_invoice(self, billing: Billing):
        return self._send_request(
            path='payments', method='POST', body=asdict(billing)
        ).json()

    def get_invoice(self, invoice_id: str):
        return self._send_request(path=f'payments/{invoice_id}').json()

    def list_invoices(self, customer_id: str):
        return self._send_request(path=f"payments?customer={customer_id}").json()

    def pay_invoice(
        self,
        invoice_id,
        credit_card: CreditCard,
        credit_card_holder_info: CreditCardHolderInfo,
        credit_card_token=None,
    ):

        payload = {
            'creditCardToken': credit_card_token,
        }

        if not credit_card_token:
            payload['creditCard'] = asdict(credit_card)
            payload['creditCardHolderInfo'] = asdict(credit_card_holder_info)

        return self._send_request(
            path=f'payments/{invoice_id}/payWithCreditCard',
            method='POST',
            body=payload,
        )
    def get_pix_invoice(self, invoice_id: str):
        return self._send_request(path=f"payments/{invoice_id}/pixQrCode").json()


#asaas = AsaasInvoice()


#due_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
#billing = Billing(
#    'cus_000006359964',
#    BillingType.BOLET.value,
#    45,
#    str(due_date)
# )
#response = asaas.create_invoice(billing)
#print(response)
#response = asaas.get_invoice("pay_yonhi5qfg754dhkc")

'''response = asaas.pay_invoive(
    'pay_yonhi5qfg754dhkc',
    CreditCard('Lucas', '000000000000000', '8', '26', '123'),
    CreditCardHolderInfo(
        'pedro',
        'pedrogallotti2006@gmail.com',
        '47896097826',
        '11045400',
        '36',
        '13974270299',
    ),
)'''


# response = x.get_customer(customer_id="cus_000006359964")

"""
response = x.tokenize_credit_card("cus_000006359964",
                                  CreditCard("Pedro", "0000000000000000", "12", "25", "000"),
                                  CreditCardHolderInfo(
                                      "pedro",
                                      "pedrogallotti2006@gmail.com",
                                      "47896097826",
                                      "11045400",
                                      "36",
                                      "13974270299",
                                    ),
                                    '127.0.0.1',
                                )
"""


#response = asaas.get_pix_invoice("pay_sl4bhjei42g4wue6")
#print(response)