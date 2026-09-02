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

// A plain <a href> to this endpoint would 401 -- the backend requires the
// Firebase bearer token, which only apiClient's interceptor attaches, and
// browser-native link navigation can't add custom headers. So this fetches
// the PDF as an authenticated blob and triggers the download manually via
// a throwaway <a>, instead of returning a URL to link to directly.
export const downloadReport = (id) =>
  apiClient
    .get(`/reports/${id}/pdf`, { responseType: "blob" })
    .then((res) => {
      const blobUrl = window.URL.createObjectURL(res.data);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `healthlens_${id.slice(0, 8)}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    });

export default apiClient;
