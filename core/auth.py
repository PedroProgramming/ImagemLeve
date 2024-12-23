from ninja.errors import HttpError
from django.http import HttpRequest
from ninja.security import APIKeyHeader

from optimizer.models import AccessToken

class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request: HttpRequest, key: str):
        try:
            return AccessToken.objects.get(token=key).user
        except AccessToken.DoesNotExist:
            raise HttpError(401, "X-API-Key não informado ou inválido")