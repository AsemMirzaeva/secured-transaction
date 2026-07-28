import { apiClient } from "./client";

export interface Transaction {
  id: string;
  payment_method: string;
  amount: string;
  currency: string;
  status:
    | "pending"
    | "awaiting_verification"
    | "processing"
    | "success"
    | "failed";
  fraud_score: number;
  requires_video_verification: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTransactionPayload {
  payment_method: string;
  amount: string;
  currency?: string;
  idempotency_key: string;
}

export const createTransaction = (payload: CreateTransactionPayload) =>
  apiClient.post<Transaction>("/payments/transactions/", payload);

export const getTransaction = (id: string) =>
  apiClient.get<Transaction>(`/payments/transactions/${id}/`);

export const listTransactions = () =>
  apiClient.get<{ results: Transaction[] }>("/payments/transactions/list/");

// A stable-per-payment-attempt key so retries never double-charge.
export const generateIdempotencyKey = () =>
  crypto.randomUUID();