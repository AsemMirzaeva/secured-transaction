from rest_framework import serializers

from .models import Transaction, PaymentMethod


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["id", "provider", "masked_pan", "is_default", "created_at"]
        read_only_fields = fields


class CreateTransactionSerializer(serializers.ModelSerializer):
    idempotency_key = serializers.CharField(max_length=64)

    class Meta:
        model = Transaction
        fields = ["id", "payment_method", "idempotency_key", "amount", "currency", "status"]
        read_only_fields = ["id", "status"]

    def validate_payment_method(self, value):
        request = self.context["request"]
        if value.user_id != request.user.id:
            raise serializers.ValidationError("Bu to'lov usuli sizga tegishli emas.")
        return value


class TransactionSerializer(serializers.ModelSerializer):
    requires_video_verification = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id", "payment_method", "amount", "currency", "status",
            "fraud_score", "requires_video_verification", "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_requires_video_verification(self, obj):
        return obj.requires_video_verification()