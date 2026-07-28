import hashlib
import secrets
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import OTPCode
from .tasks import send_sms_task


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def generate_otp(user, purpose=OTPCode.PURPOSE_LOGIN) -> OTPCode:
    code = f"{secrets.randbelow(10**6):06d}"
    otp = OTPCode.objects.create(
        user=user,
        code_hash=_hash_code(code),
        purpose=purpose,
        expires_at=timezone.now() + timedelta(seconds=settings.OTP_TTL_SECONDS),
    )
    send_sms_task.delay(user.phone, f"Tasdiqlash kodi: {code}")
    return otp


def verify_otp(user, code: str, purpose=OTPCode.PURPOSE_LOGIN) -> bool:
    otp = (
        OTPCode.objects.filter(user=user, purpose=purpose, consumed_at__isnull=True)
        .order_by("-created_at")
        .first()
    )
    if otp is None or not otp.is_valid:
        return False
    if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
        return False

    otp.attempts += 1
    otp.save(update_fields=["attempts"])

    if otp.code_hash != _hash_code(code):
        return False

    otp.consumed_at = timezone.now()
    otp.save(update_fields=["consumed_at"])
    return True