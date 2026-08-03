import axios from "axios";
import { auth } from "../firebase";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// Every outgoing request grabs a fresh Firebase ID token and attaches it.
// getIdToken() automatically refreshes if the cached one is close to expiry.
apiClient.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const submitAssessment = (payload) =>
  apiClient.post("/assessments", payload).then((res) => res.data);

export const fetchHistory = () =>
  apiClient.get("/history").then((res) => res.data);

export const fetchAssessment = (id) =>
  apiClient.get(`/history/${id}`).then((res) => res.data);

export const syncUser = () =>
  apiClient.post("/auth/sync").then((res) => res.data);

export const downloadReportUrl = (id) =>
  `${import.meta.env.VITE_API_BASE_URL}/reports/${id}/pdf`;

export default apiClient;
