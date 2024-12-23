from datetime import date
from .payment_enum import BillingType
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, List


@dataclass
class CreditCard:
    holderName: str
    number: str
    expiryMonth: str
    expiryYear: str
    ccv: str

    def __post_init__(self):
        self.validate_ccv()

    def validate_ccv(self):
        if len(self.ccv) < 3 or len(self.ccv) > 3:
            raise ValueError('O ccv deve conter 3 caracters')


@dataclass
class CreditCardHolderInfo:
    """
    Atributos fora da PEP 8 para manter as especificações do AsaaS
    """

    name: str
    email: str
    cpfCnpj: str
    postalCode: str
    addressNumber: str
    phone: str
    addressComplement: Optional[str] = ''
    mobilePhone: Optional[str] = ''


@dataclass
class Discount:
    value: float
    dueDateLimitDays: Optional[int] = None
    type_value: Optional[str] = None   # Porcentagem ou Fixed


@dataclass
class Interest:
    value: float   # Percentual de juros ao mês


@dataclass
class Fine:
    value: float   # Percentual de multa
    type_value: str   # FIXED ou outro tipo


@dataclass
class Split:
    walletId: str
    fixedValue: Optional[float] = None
    percentualValue: Optional[float] = None
    totalFixedValue: Optional[float] = None
    externalReference: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Callback:
    successUrl: str
    autoRedirect: Optional[bool] = True   # Padrão é True


@dataclass
class Billing:
    customer: str   # Identificador único do cliente no Asaas
    billingType: BillingType   # Forma de pagamento
    value: float   # Valor de cobrança
    dueDate: date   # Data de vencimento da cobrança
    description: Optional[str] = field(
        default=None
    )   # Descrição máximo de 500 caractéres
    daysAfterDueDataToRegistrationCancellation: Optional[
        int
    ] = None   # Cancelamento após vencimento
    externalReference: Optional[str] = None   # Campo livre para busca
    installmentCount: Optional[int] = None   # Número de parcelas (Caso haja)
    discount: Optional[Union[Discount, Dict]] = field(
        default_factory=dict
    )   # Informações de desconto
    interest: Optional[Union[Interest, Dict]] = field(
        default_factory=dict
    )   # Informações de juros
    fine: Optional[Fine] = None   # Informações de multa
    postalService: Optional[bool] = False   # Envio via Correios
    split: Optional[List[Split]] = None   # Configurações do splitdiscount
    callback: Optional[Union[Callback, Dict]] = field(
        default_factory=dict
    )   # Informações de redirecionamento

    def __post_init__(self):
        if self.description and len(self.description.strip()) > 500:
            raise ValueError('A descrição não pode excerder 500 caractéres.')
