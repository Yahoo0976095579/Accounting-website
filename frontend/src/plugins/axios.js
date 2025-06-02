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
      // 並且不是登入/註冊接口本身，避免登入失敗時也觸發重定向
      // 並且不是 /logout 接口本身 (避免循環或不必要的攔截)
      // 並且沒有被重試過 (防止無限循環重定向或重試)
      if (
        error.response?.status === 401 &&
        !originalRequest.url.includes("/login") &&
        !originalRequest.url.includes("/register") &&
        !originalRequest.url.includes("/logout") && // === 新增：排除 /logout 接口 ===
        !originalRequest._retry
      ) {
        originalRequest._retry = true;

        const authStore = useAuthStore();
        const notificationStore = useNotificationStore();

        if (authStore.isAuthenticated) {
          console.warn(
            "Axios Interceptor: Received 401 Unauthorized. Session expired, performing automatic logout."
          );
          notificationStore.showNotification(
            "會話已過期，請重新登入。",
            "warning"
          );

          // 直接調用 authStore.logout()，它會處理清除 token 和重定向
          await authStore.logout(); // 等待登出完成，包括重定向

          // 返回一個空的 Promise.reject，這樣錯誤就不會傳播到原始請求的 catch 塊，
          // 並且重定向已經被處理。
          return Promise.reject(); // === 修正：返回 Promise.reject() ===
        }
      }

      return Promise.reject(error);
    }
  );
}
