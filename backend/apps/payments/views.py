from django.db import IntegrityError
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Transaction
from .serializers import CreateTransactionSerializer, TransactionSerializer
from .tasks import run_fraud_check_task


class CreateTransactionView(APIView):
   

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "payment"

    def post(self, request):
        serializer = CreateTransactionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        try:
            txn = serializer.save(user=request.user, status=Transaction.STATUS_PENDING)
        except IntegrityError:
            existing = Transaction.objects.filter(
                idempotency_key=serializer.validated_data["idempotency_key"]
            ).first()
            if existing:
                return Response(TransactionSerializer(existing).data, status=status.HTTP_200_OK)
            raise

        request.audit("payment.created", object_type="transaction", object_id=txn.id, metadata={"amount": str(txn.amount)})
        run_fraud_check_task.delay(str(txn.id))

        return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by("-created_at")