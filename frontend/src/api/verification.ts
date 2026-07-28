import { apiClient } from "./client";

export interface StartVerificationResponse {
  session: {
    id: string;
    status: string;
    livekit_room_name: string;
  };
  livekit_url: string;
  livekit_token: string;
}

export const startVerificationSession = (transactionId: string) =>
  apiClient.post<StartVerificationResponse>(
    `/verification/transactions/${transactionId}/start/`
  );