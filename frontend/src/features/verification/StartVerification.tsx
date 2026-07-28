import { useState } from "react";
import { startVerificationSession, StartVerificationResponse } from "../../api/verification";
import VideoCallRoom from "./VideoCallRoom";

interface Props {
  transactionId: string;
  onSessionEnded: () => void;
}

export default function StartVerification({ transactionId, onSessionEnded }: Props) {
  const [session, setSession] = useState<StartVerificationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleStart() {
    setLoading(true);
    setError(null);
    try {
      const { data } = await startVerificationSession(transactionId);
      setSession(data);
    } catch {
      setError("Video tekshiruv sessiyasini boshlab bo'lmadi.");
    } finally {
      setLoading(false);
    }
  }

  if (session) {
    return (
      <VideoCallRoom
        livekitUrl={session.livekit_url}
        token={session.livekit_token}
        onLeave={() => {
          setSession(null);
          onSessionEnded();
        }}
      />
    );
  }

  return (
    <div className="verification-prompt">
      <p>
        Ushbu to'lov qo'shimcha identifikatsiyani talab qiladi. Davom etish
        uchun operator bilan qisqa video-qo'ng'iroqqa qo'shiling.
      </p>
      {error && <p className="form-error">{error}</p>}
      <button onClick={handleStart} disabled={loading}>
        {loading ? "Ulanmoqda..." : "Video tekshiruvni boshlash"}
      </button>
    </div>
  );
}