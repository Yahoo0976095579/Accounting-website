// src/plugins/axios.js
import axios from "axios";
import router from "../router"; // 引入 Vue Router 實例
import { useAuthStore } from "../stores/authStore"; // 引入你的 authStore
import { useNotificationStore } from "../stores/notificationStore"; // 引入通知 Store

// 這個函數將在應用程式啟動時被調用一次
export function setupAxiosInterceptors() {
  axios.interceptors.response.use(
    (response) => response, // 對於成功的響應，直接返回
    async (error) => {
      const originalRequest = error.config; // 獲取原始請求配置

      // 判斷是否為 401 Unauthorized 錯誤
      // 並且不是登入/註冊接口本身，避免登入失敗時也觸發重定向
      // 並且沒有被重試過 (防止無限循環重定向或重試)
      if (
        error.response?.status === 401 &&
        !originalRequest.url.includes("/login") &&
        !originalRequest.url.includes("/register") &&
        !originalRequest._retry
      ) {
        // _retry 是一個自定義標誌，防止無限重定向

        originalRequest._retry = true; // 標記此請求已被攔截器處理過

        const authStore = useAuthStore(); // 獲取 authStore 實例
        const notificationStore = useNotificationStore(); // 獲取通知 Store 實例

        // 只有當用戶在本地被認為是登入狀態時才執行自動登出，避免在已登出狀態下重複提示
        if (authStore.isAuthenticated) {
          console.warn(
            "Axios Interceptor: Received 401 Unauthorized. Session expired, performing automatic logout."
          );
          notificationStore.showNotification(
            "會話已過期，請重新登入。",
            "warning"
          );

          // 執行 authStore 的登出動作，它會清除 token 和用戶數據，並重定向到登入頁面
          await authStore.logout();
        }
        // 返回一個被拒絕的 Promise，阻止錯誤繼續傳播到原始請求的 catch 塊
        return Promise.reject(error);
      }

      // 對於其他類型的錯誤 (例如 404, 500) 或非登入/註冊接口的 401 錯誤，直接返回錯誤
      return Promise.reject(error);
    }
  );
}
//載
