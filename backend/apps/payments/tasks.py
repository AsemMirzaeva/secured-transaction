import logging

from celery import shared_task
from django.db import transaction as db_transaction

logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def process_charge_task(self, transaction_id: str):
   
    from .models import Transaction
    from .services import get_provider_client, PaymentProviderError

    try:
        txn = Transaction.objects.select_related("payment_method").get(id=transaction_id)
    except Transaction.DoesNotExist:
        logger.error("process_charge_task: transaction %s not found", transaction_id)
        return

    if txn.status != Transaction.STATUS_PROCESSING:
        logger.info("Transaction %s not in processing state (%s) — skipping", transaction_id, txn.status)
        return

    try:
        client = get_provider_client(txn.payment_method.provider)
        result = client.charge(
            provider_token=txn.payment_method.provider_token,
            amount=txn.amount,
            currency=txn.currency,
            idempotency_key=txn.idempotency_key,
        )
    except PaymentProviderError as exc:
        txn.status = Transaction.STATUS_FAILED
        txn.failure_reason = str(exc)
        txn.save(update_fields=["status", "failure_reason", "updated_at"])
        return
    except Exception as exc:
        raise self.retry(exc=exc)

    with db_transaction.atomic():
        txn.refresh_from_db()
        txn.status = Transaction.STATUS_SUCCESS if result.success else Transaction.STATUS_FAILED
        txn.provider_reference = result.provider_reference
        txn.save(update_fields=["status", "provider_reference", "updated_at"])

    notify_transaction_status_task.delay(str(txn.id))


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def notify_transaction_status_task(self, transaction_id: str):
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    from .models import Transaction

    try:
        txn = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{txn.user_id}",
        {
            "type": "transaction.update",
            "transaction_id": str(txn.id),
            "status": txn.status,
        },
    )


@shared_task
def run_fraud_check_task(transaction_id: str):
  
    from .models import Transaction

    try:
        txn = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return

    score = 30
    txn.fraud_score = score
    if txn.requires_video_verification():
        txn.status = Transaction.STATUS_AWAITING_VERIFICATION
    else:
        txn.status = Transaction.STATUS_PROCESSING
        process_charge_task.delay(str(txn.id))
    txn.save(update_fields=["fraud_score", "status", "updated_at"])