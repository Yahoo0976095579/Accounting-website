// src/plugins/axios.js
import axios from "axios";
import router from "../router";
import { useAuthStore } from "../stores/authStore";
import { useNotificationStore } from "../stores/notificationStore";

export function setupAxiosInterceptors() {
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // 判斷是否為 401 Unauthorized 錯誤
      // 並且不是登入/註冊接口本身
      // 並且沒有被重試過 (防止無限循環)
      if (
        error.response?.status === 401 &&
        !originalRequest.url.includes("/login") &&
        !originalRequest.url.includes("/register") &&
        !originalRequest._retry
      ) {
        const authStore = useAuthStore();

        // === 修正點：檢查 isLoggingOut 旗標 ===
        if (authStore.isLoggingOut) {
          console.log(
            "Interceptor: Already in logout process, ignoring duplicate 401."
          );
          return Promise.reject(error); // 阻止錯誤傳播，但不觸發新的登出
        }
        // ===================================

        originalRequest._retry = true; // 標記此請求已被攔截器處理過

        const notificationStore = useNotificationStore();

        if (authStore.isAuthenticated) {
          // 再次檢查 isAuthenticated，確保是真的會話過期
          console.warn(
            "Axios Interceptor: Received 401 Unauthorized. Session expired, performing automatic logout."
          );
          notificationStore.showNotification(
            "會話已過期，請重新登入。",
            "warning"
          );

          await authStore.logout(); // 觸發登出流程 (現在有了 isLoggingOut 旗標保護)

          // 返回一個被拒絕的 Promise，阻止錯誤傳播到原始請求的 catch 塊，
          // 並且重定向已經被處理。
          return Promise.reject(error);
        }
      }

      return Promise.reject(error);
    }
  );
}
