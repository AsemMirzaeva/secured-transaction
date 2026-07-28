from rest_framework import serializers
from .models import VerificationSession


class VerificationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationSession
        fields = ["id", "transaction", "status", "livekit_room_name", "decision_reason", "created_at"]
        read_only_fields = fields


class VerificationDecisionSerializer(serializers.Serializer):
    approve = serializers.BooleanField()
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True)