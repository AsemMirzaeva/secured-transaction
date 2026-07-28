import uuid
from django.conf import settings
from django.db import models

from apps.payments.models import Transaction


class VerificationSession(models.Model):
    STATUS_PENDING = "pending"          
    STATUS_ACTIVE = "active"            
    STATUS_APPROVED = "approved"        
    STATUS_REJECTED = "rejected"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_EXPIRED, "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="verification_session")
    livekit_room_name = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="handled_verifications",
    )
    decision_reason = models.CharField(max_length=255, blank=True)
    recording_egress_id = models.CharField(max_length=128, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VerificationSession({self.livekit_room_name}, {self.status})"