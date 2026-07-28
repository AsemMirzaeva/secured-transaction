import logging

from celery import shared_task
from django.conf import settings

logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_sms_task(self, phone: str, message: str):

    try:
        logger.info("SMS -> %s: %s", phone, message)
    except Exception as exc:
        raise self.retry(exc=exc)