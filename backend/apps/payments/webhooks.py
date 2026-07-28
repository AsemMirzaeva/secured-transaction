
import logging

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone

from .models import WebhookEvent, Transaction
from .services import get_provider_client

logger = logging.getLogger("apps")


def _handle_webhook(request, provider: str):
    signature = request.headers.get("X-Signature", "")
    timestamp = request.headers.get("X-Timestamp", "")
    raw_body = request.body

    try:
        client = get_provider_client(provider)
    except Exception:
        return JsonResponse({"error": "unknown provider"}, status=400)

    signature_valid = client.verify_webhook_signature(
        payload=raw_body, signature=signature, timestamp=timestamp
    )

    payload = request.POST.dict() or _safe_json(raw_body)
    event_id = str(payload.get("event_id") or payload.get("id") or timestamp)

    event, created = WebhookEvent.objects.get_or_create(
        provider=provider,
        event_id=event_id,
        defaults={"payload": payload, "signature_valid": signature_valid},
    )

    if not signature_valid:
        logger.warning("Webhook signature invalid: provider=%s event_id=%s", provider, event_id)
        return JsonResponse({"error": "invalid signature"}, status=401)

    if not created:
        return JsonResponse({"status": "already processed"}, status=200)

    _apply_webhook(provider, payload)
    event.processed_at = timezone.now()
    event.save(update_fields=["processed_at"])

    return JsonResponse({"status": "ok"}, status=200)


def _apply_webhook(provider: str, payload: dict):
    provider_reference = payload.get("transaction_id") or payload.get("provider_reference")
    new_status = payload.get("status")

    if not provider_reference:
        logger.warning("Webhook payload missing provider reference: %s", payload)
        return

    txn = Transaction.objects.filter(provider_reference=provider_reference).first()
    if txn is None:
        logger.warning("Webhook for unknown transaction: %s", provider_reference)
        return

    status_map = {
        "success": Transaction.STATUS_SUCCESS,
        "paid": Transaction.STATUS_SUCCESS,
        "failed": Transaction.STATUS_FAILED,
        "cancelled": Transaction.STATUS_FAILED,
    }
    mapped = status_map.get(new_status)
    if mapped:
        txn.status = mapped
        txn.save(update_fields=["status", "updated_at"])

        from .tasks import notify_transaction_status_task
        notify_transaction_status_task.delay(str(txn.id))


def _safe_json(raw_body: bytes) -> dict:
    import json
    try:
        return json.loads(raw_body or b"{}")
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@require_POST
def payme_webhook(request):
    return _handle_webhook(request, "payme")


@csrf_exempt
@require_POST
def click_webhook(request):
    return _handle_webhook(request, "click")