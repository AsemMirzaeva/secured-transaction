import axios from "axios";
import { useAuthStore } from "../store/authStore";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Attach the access token to every request.
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On a 401, try once to refresh the token before giving up and logging out.
let isRefreshing = false;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry && !isRefreshing) {
      originalRequest._retry = true;
      isRefreshing = true;
      try {
        const refreshed = await useAuthStore.getState().refreshAccessToken();
        isRefreshing = false;
        if (refreshed) {
          originalRequest.headers.Authorization = `Bearer ${useAuthStore.getState().accessToken}`;
          return apiClient(originalRequest);
        }
      } catch {
        isRefreshing = false;
      }
      useAuthStore.getState().logout();
    }

    return Promise.reject(error);
  }
);