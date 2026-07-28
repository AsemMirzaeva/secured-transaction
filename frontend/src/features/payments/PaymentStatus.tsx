import { useEffect, useState } from "react";
import { Transaction, getTransaction } from "../../api/payments";
import { useAuthStore } from "../../store/authStore";
import StartVerification from "../verification/StartVerification";

const STATUS_LABELS: Record<Transaction["status"], string> = {
  pending: "Kutilmoqda",
  awaiting_verification: "Video tekshiruv talab qilinadi",
  processing: "Ishlanmoqda",
  success: "Muvaffaqiyatli",
  failed: "Rad etildi",
};

export default function PaymentStatus({ transaction }: { transaction: Transaction }) {
  const [txn, setTxn] = useState(transaction);
  const accessToken = useAuthStore((s) => s.accessToken);

  // Live updates over WebSocket; falls back to nothing if the socket drops —
  // the user can always refresh, since getTransaction is idempotent (GET).
  useEffect(() => {
    if (!accessToken) return;

    const wsBase = import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost/ws";
    const socket = new WebSocket(`${wsBase}/transactions/?token=${accessToken}`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "transaction.update" && data.transaction_id === txn.id) {
        getTransaction(txn.id).then((res) => setTxn(res.data));
      }
    };

    return () => socket.close();
  }, [accessToken, txn.id]);

  return (
    <div className="payment-status">
      <p>
        Holat: <strong>{STATUS_LABELS[txn.status]}</strong>
      </p>
      <p>
        Summa: {txn.amount} {txn.currency}
      </p>

      {txn.status === "awaiting_verification" && (
        <StartVerification
          transactionId={txn.id}
          onSessionEnded={() => getTransaction(txn.id).then((res) => setTxn(res.data))}
        />
      )}
    </div>
  );
}