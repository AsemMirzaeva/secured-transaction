import { apiClient } from "./client";

export interface User {
  id: string;
  phone: string;
  full_name: string;
  phone_verified: boolean;
  is_operator: boolean;
}

export const requestOtp = (phone: string) =>
  apiClient.post<{ detail: string }>("/accounts/otp/request/", { phone });

export const verifyOtp = (phone: string, code: string) =>
  apiClient.post<{ access: string; refresh: string; user: User }>(
    "/accounts/otp/verify/",
    { phone, code }
  );

export const fetchMe = () => apiClient.get<User>("/accounts/me/");