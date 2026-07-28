import { useState } from "react";
import { useAuthStore } from "./store/authStore";
import LoginForm from "./features/auth/LoginForm";
import PaymentForm from "./features/payments/PaymentForm";
import PaymentStatus from "./features/payments/PaymentStatus";
import type { Transaction } from "./api/payments";
import "./app.css";

// Demo payment method id — in a full build this comes from a
// "PaymentMethod qo'shish" flow (tokenizing a card via Payme/Click's SDK).
const DEMO_PAYMENT_METHOD_ID = "a3d9d7cb-a332-45b3-b941-04c6c05f55fa";
export default function App() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [, forceRerender] = useState(0);

  if (!user) {
    return (
      <main className="app-shell">
        <h1>Xavfsiz To'lov Tizimi</h1>
        <LoginForm onLoggedIn={() => forceRerender((n) => n + 1)} />
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <h1>Xavfsiz To'lov Tizimi</h1>
        <button className="link-button" onClick={logout}>
          Chiqish
        </button>
      </header>

      {!transaction ? (
        <PaymentForm
          paymentMethodId={DEMO_PAYMENT_METHOD_ID}
          onTransactionCreated={setTransaction}
        />
      ) : (
        <PaymentStatus transaction={transaction} />
      )}
    </main>
  );
}