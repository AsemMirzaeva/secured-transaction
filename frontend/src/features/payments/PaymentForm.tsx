import { FormEvent, useState } from "react";
import {
  createTransaction,
  generateIdempotencyKey,
  Transaction,
} from "../../api/payments";

interface Props {
  paymentMethodId: string;
  onTransactionCreated: (txn: Transaction) => void;
}

export default function PaymentForm({ paymentMethodId, onTransactionCreated }: Props) {
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generated once per mount (per payment attempt), not per click — so a
  // double-click or a retried network request reuses the same key instead
  // of creating two transactions.
  const [idempotencyKey] = useState(generateIdempotencyKey);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    const numericAmount = Number(amount);
    if (!numericAmount || numericAmount <= 0) {
      setError("Summani to'g'ri kiriting.");
      return;
    }

    setLoading(true);
    try {
      const { data } = await createTransaction({
        payment_method: paymentMethodId,
        amount: numericAmount.toFixed(2),
        currency: "UZS",
        idempotency_key: idempotencyKey,
      });
      onTransactionCreated(data);
    } catch {
      setError("To'lovni boshlashda xatolik yuz berdi. Qayta urinib ko'ring.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="payment-form">
      <label htmlFor="amount">Summa (so'm)</label>
      <input
        id="amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        inputMode="decimal"
        placeholder="100000"
      />
      {error && <p className="form-error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? "Yuborilmoqda..." : "To'lovni boshlash"}
      </button>
    </form>
  );
}