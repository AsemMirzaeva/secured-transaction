from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class PhoneRequestOTPSerializer(serializers.Serializer):
    phone = serializers.RegexField(r"^\+998\d{9}$")


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.RegexField(r"^\+998\d{9}$")
    code = serializers.RegexField(r"^\d{6}$")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone", "full_name", "phone_verified", "is_operator"]
        read_only_fields = fields


def tokens_for_user(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}