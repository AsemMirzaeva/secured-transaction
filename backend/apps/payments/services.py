
import hashlib
import hmac
import logging
import time
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger("apps")


class PaymentProviderError(Exception):
    pass


@dataclass
class ChargeResult:
    success: bool
    provider_reference: str
    raw_response: dict


class BaseProviderClient:
    provider_name = "base"

    def charge(self, *, provider_token: str, amount, currency: str, idempotency_key: str) -> ChargeResult:
        raise NotImplementedError

    def verify_webhook_signature(self, *, payload: bytes, signature: str, timestamp: str) -> bool:
        raise NotImplementedError


class PaymeClient(BaseProviderClient):
    provider_name = "payme"

    def __init__(self):
        self.merchant_id = settings.PAYME_MERCHANT_ID
        self.secret_key = settings.PAYME_SECRET_KEY

    def charge(self, *, provider_token, amount, currency, idempotency_key) -> ChargeResult:

        logger.info("Payme charge requested: key=%s amount=%s", idempotency_key, amount)
        return ChargeResult(success=True, provider_reference=f"payme_{idempotency_key}", raw_response={})

    def verify_webhook_signature(self, *, payload: bytes, signature: str, timestamp: str) -> bool:
        return _verify_hmac(payload, signature, timestamp, self.secret_key)


class ClickClient(BaseProviderClient):
    provider_name = "click"

    def __init__(self):
        self.merchant_id = settings.CLICK_MERCHANT_ID
        self.secret_key = settings.CLICK_SECRET_KEY

    def charge(self, *, provider_token, amount, currency, idempotency_key) -> ChargeResult:
        logger.info("Click charge requested: key=%s amount=%s", idempotency_key, amount)
        return ChargeResult(success=True, provider_reference=f"click_{idempotency_key}", raw_response={})

    def verify_webhook_signature(self, *, payload: bytes, signature: str, timestamp: str) -> bool:
        return _verify_hmac(payload, signature, timestamp, self.secret_key)


def _verify_hmac(payload: bytes, signature: str, timestamp: str, secret: str) -> bool:
   
    if not signature or not timestamp:
        return False

    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return False

    if abs(time.time() - ts) > settings.WEBHOOK_HMAC_TOLERANCE_SECONDS:
        return False

    signed_payload = timestamp.encode() + b"." + payload
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def get_provider_client(provider: str) -> BaseProviderClient:
    clients = {
        PaymeClient.provider_name: PaymeClient,
        ClickClient.provider_name: ClickClient,
    }
    client_cls = clients.get(provider)
    if client_cls is None:
        raise PaymentProviderError(f"Noma'lum to'lov provayderi: {provider}")
    return client_cls()