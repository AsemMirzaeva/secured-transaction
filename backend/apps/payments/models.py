import uuid
from django.conf import settings
from django.db import models

from common.validators import validate_positive_amount


class PaymentMethod(models.Model):
    
    PROVIDER_PAYME = "payme"
    PROVIDER_CLICK = "click"
    PROVIDER_STRIPE = "stripe"
    PROVIDER_CHOICES = [
        (PROVIDER_PAYME, "Payme"),
        (PROVIDER_CLICK, "Click"),
        (PROVIDER_STRIPE, "Stripe"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_methods")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_token = models.CharField(max_length=255)   # opaque token from the provider
    masked_pan = models.CharField(max_length=19, blank=True)  # e.g. "8600 06** **** 1234" for display only
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "provider", "provider_token")

    def __str__(self):
        return f"{self.provider}:{self.masked_pan or self.provider_token[:8]}"


class Transaction(models.Model):
    STATUS_PENDING = "pending"
    STATUS_AWAITING_VERIFICATION = "awaiting_verification"
    STATUS_PROCESSING = "processing"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_AWAITING_VERIFICATION, "Awaiting verification"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="transactions")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name="transactions")

    idempotency_key = models.CharField(max_length=64, unique=True)

    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[validate_positive_amount])
    currency = models.CharField(max_length=3, default="UZS")
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_PENDING)

    fraud_score = models.PositiveSmallIntegerField(default=0)   # 0-100, higher = riskier
    provider_reference = models.CharField(max_length=128, blank=True)  # id returned by Payme/Click/Stripe
    failure_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def requires_video_verification(self) -> bool:
        from django.conf import settings as dj_settings
        return (
            self.fraud_score >= dj_settings.FRAUD_SCORE_VERIFICATION_THRESHOLD
            or self.amount >= dj_settings.HIGH_VALUE_TRANSACTION_THRESHOLD
        )

    def __str__(self):
        return f"{self.id} ({self.status}, {self.amount} {self.currency})"


class WebhookEvent(models.Model):
  

    provider = models.CharField(max_length=20)
    event_id = models.CharField(max_length=128)  # provider's own event/request id, for dedup
    payload = models.JSONField()
    signature_valid = models.BooleanField()
    processed_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "event_id")