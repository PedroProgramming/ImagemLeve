from django.db import models
from .managers import UserManager
from .models_validators import validate_cpf_cnpj
from django.contrib.auth.models import AbstractUser, UserManager

class User(AbstractUser):
    username = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True)

    customer_id = models.CharField(max_length=50, null=True, blank=True)
    cpf_cnpj = models.CharField(max_length=50, null=True, blank=True, validators=[validate_cpf_cnpj])

    balance = models.DecimalField(default="0.00", max_digits=10, decimal_places=2)

    webhook = models.URLField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    objects = UserManager()

    def __str__(self) -> str:
        return self.email