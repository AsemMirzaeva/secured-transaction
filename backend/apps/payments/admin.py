from django.contrib import admin
from .models import PaymentMethod, Transaction, WebhookEvent


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "provider", "masked_pan", "is_default")
    search_fields = ("user__phone", "masked_pan")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount", "currency", "status", "fraud_score", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("id", "idempotency_key", "provider_reference", "user__phone")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("provider", "event_id", "signature_valid", "processed_at", "received_at")
    list_filter = ("provider", "signature_valid")

    def has_change_permission(self, request, obj=None):
        return False