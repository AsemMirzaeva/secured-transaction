from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import Transaction
from apps.payments.tasks import process_charge_task
from common.permissions import IsOperator

from .models import VerificationSession
from .serializers import VerificationSessionSerializer, VerificationDecisionSerializer
from .livekit_client import generate_room_name, create_access_token


class StartVerificationSessionView(APIView):
   

    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        txn = get_object_or_404(Transaction, id=transaction_id, user=request.user)

        if txn.status != Transaction.STATUS_AWAITING_VERIFICATION:
            return Response(
                {"detail": "Bu tranzaksiya video tekshiruvni talab qilmaydi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session, _ = VerificationSession.objects.get_or_create(
            transaction=txn,
            defaults={"livekit_room_name": generate_room_name(txn.id)},
        )

        token = create_access_token(
            room_name=session.livekit_room_name,
            identity=str(request.user.id),
            name=request.user.full_name or request.user.phone,
            is_operator=False,
        )

        request.audit(
            "verification.session_started",
            object_type="verification_session", object_id=session.id,
        )

        return Response(
            {
                "session": VerificationSessionSerializer(session).data,
                "livekit_url": _livekit_public_url(),
                "livekit_token": token,
            }
        )


class OperatorJoinView(APIView):
  
    permission_classes = [IsAuthenticated, IsOperator]

    def post(self, request, session_id):
        session = get_object_or_404(VerificationSession, id=session_id)
        session.operator = request.user
        session.status = VerificationSession.STATUS_ACTIVE
        session.save(update_fields=["operator", "status", "updated_at"])

        token = create_access_token(
            room_name=session.livekit_room_name,
            identity=f"operator-{request.user.id}",
            name=request.user.full_name or request.user.phone,
            is_operator=True,
        )
        return Response({"livekit_url": _livekit_public_url(), "livekit_token": token})


class VerificationDecisionView(APIView):
  

    permission_classes = [IsAuthenticated, IsOperator]

    def post(self, request, session_id):
        serializer = VerificationDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = get_object_or_404(VerificationSession, id=session_id)
        txn = session.transaction

        if serializer.validated_data["approve"]:
            session.status = VerificationSession.STATUS_APPROVED
            txn.status = Transaction.STATUS_PROCESSING
            process_charge_task.delay(str(txn.id))
        else:
            session.status = VerificationSession.STATUS_REJECTED
            txn.status = Transaction.STATUS_FAILED
            txn.failure_reason = "Video-KYC rad etildi."

        session.decision_reason = serializer.validated_data.get("reason", "")
        session.save(update_fields=["status", "decision_reason", "updated_at"])
        txn.save(update_fields=["status", "failure_reason", "updated_at"])

        request.audit(
            "verification.decision", object_type="verification_session", object_id=session.id,
            metadata={"approved": serializer.validated_data["approve"]},
        )

        return Response(VerificationSessionSerializer(session).data)


def _livekit_public_url() -> str:
    from django.conf import settings
    return settings.LIVEKIT_URL