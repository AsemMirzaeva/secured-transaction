import { FormEvent, useState } from "react";
import { requestOtp, verifyOtp } from "../../api/auth";
import { useAuthStore } from "../../store/authStore";

const PHONE_RE = /^\+998\d{9}$/;

export default function LoginForm({ onLoggedIn }: { onLoggedIn: () => void }) {
  const [phone, setPhone] = useState("+998");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const setSession = useAuthStore((s) => s.setSession);

  async function handleRequestOtp(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!PHONE_RE.test(phone)) {
      setError("Telefon raqami +998XXXXXXXXX formatida bo'lishi kerak.");
      return;
    }
    setLoading(true);
    try {
      await requestOtp(phone);
      setStep("code");
    } catch {
      setError("Kodni yuborishda xatolik yuz berdi. Qayta urinib ko'ring.");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyOtp(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { data } = await verifyOtp(phone, code);
      setSession(data.access, data.refresh, data.user);
      onLoggedIn();
    } catch {
      setError("Kod noto'g'ri yoki muddati tugagan.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-card">
      {step === "phone" ? (
        <form onSubmit={handleRequestOtp}>
          <label htmlFor="phone">Telefon raqam</label>
          <input
            id="phone"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+998901234567"
            autoComplete="tel"
          />
          {error && <p className="form-error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? "Yuborilmoqda..." : "Kod yuborish"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOtp}>
          <label htmlFor="code">SMS orqali kelgan kod</label>
          <input
            id="code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="123456"
            inputMode="numeric"
            maxLength={6}
          />
          {error && <p className="form-error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? "Tekshirilmoqda..." : "Tasdiqlash"}
          </button>
        </form>
      )}
    </div>
  );
}