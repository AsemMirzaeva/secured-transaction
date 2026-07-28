from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import User, OTPCode
from .serializers import (
    PhoneRequestOTPSerializer,
    VerifyOTPSerializer,
    UserSerializer,
    tokens_for_user,
)
from .services import generate_otp, verify_otp


class RequestOTPView(APIView):
 
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp"

    def post(self, request):
        serializer = PhoneRequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]

        user, _ = User.objects.get_or_create(phone=phone)
        generate_otp(user, purpose=OTPCode.PURPOSE_LOGIN)

        return Response({"detail": "Tasdiqlash kodi yuborildi."}, status=status.HTTP_200_OK)


class VerifyOTPLoginView(APIView):
   
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]

        user = get_object_or_404(User, phone=phone)

        if not verify_otp(user, code, purpose=OTPCode.PURPOSE_LOGIN):
            request.audit(
                "auth.login_failed", object_type="user", object_id=user.id, metadata={"phone": phone}
            )
            return Response(
                {"detail": "Kod noto'g'ri yoki muddati tugagan."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.phone_verified = True
        user.save(update_fields=["phone_verified"])

        request.audit("auth.login_success", object_type="user", object_id=user.id)

        tokens = tokens_for_user(user)
        return Response({**tokens, "user": UserSerializer(user).data}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)