// client/src/stores/authStore.js
import { defineStore } from "pinia";
import axios from "axios";
import router from "../router/index.js"; // 導入 router，用於登入後重定向
import { useNotificationStore } from "./notificationStore"; // 根據你的 notificationStore 實際路徑
import { API_BASE_URL } from "./config";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: JSON.parse(localStorage.getItem("user")) || null, // 從 localStorage 載入使用者資訊
    isLoading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user, // 判斷使用者是否登入
  },
  actions: {
    async register(username, password) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/register`,
          { username, password },
          {
            withCredentials: true, // 允許發送和接收 cookie
          }
        );
        this.user = response.data.user;
        localStorage.setItem("user", JSON.stringify(this.user)); // 儲存使用者資訊到 localStorage
        localStorage.setItem("isLoggedIn", "true"); // 設置登入標記
        router.push("/"); // 註冊成功後導航到儀表板
        return true;
      } catch (err) {
        this.error = err.response?.data?.error || "Registration failed.";
        console.error("Registration error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async login(username, password) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/login`,
          { username, password },
          {
            withCredentials: true, // 允許發送和接收 cookie
          }
        );
        this.user = response.data.user;
        localStorage.setItem("user", JSON.stringify(this.user)); // 儲存使用者資訊到 localStorage
        localStorage.setItem("isLoggedIn", "true"); // 設置登入標記
        router.push("/"); // 登入成功後導航到儀表板
        return true;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Invalid username or password.";
        console.error("Login error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async logout() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/logout`, {
          // 確認這裡是 GET 請求
          withCredentials: true, // 確保這裡有 withCredentials
        });
        this.user = null;
        localStorage.removeItem("user");
        localStorage.removeItem("isLoggedIn");
        router.push("/login"); // 確保這裡有重定向
        console.log("Logout successful:", response.data.message); // 添加成功日誌
        return true;
      } catch (err) {
        this.error = err.response?.data?.error || "Logout failed.";
        console.error("Logout error:", err); // 添加錯誤日誌
        // 如果登出失敗，可能是因為會話已經無效，但前端狀態需要清理
        this.user = null;
        localStorage.removeItem("user");
        localStorage.removeItem("isLoggedIn");
        router.push("/login"); // 即使失敗也嘗試跳轉到登入頁，確保前端狀態一致
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchCurrentUser() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/user`, {
          withCredentials: true,
        });
        this.user = response.data;
        localStorage.setItem("user", JSON.stringify(this.user));
        // localStorage.setItem('isLoggedIn', 'true'); // 這行其實可以移除，因為 user 存在就代表登入
        return true;
      } catch (err) {
        // 如果後端返回 401 (未授權) 或其他錯誤，說明會話無效
        if (err.response && err.response.status === 401) {
          console.warn(
            "Backend session expired or unauthorized. Clearing local auth state."
          );
        } else {
          console.error("Failed to fetch current user:", err);
        }
        // 清理本地儲存，強制使用者重新登入
        this.user = null;
        localStorage.removeItem("user");
        localStorage.removeItem("isLoggedIn"); // 確保這個也被移除
        return false;
      } finally {
        this.isLoading = false;
      }
    },
    async updateUsername(newUsername) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.put(
          `${API_BASE_URL}/user/username`,
          { new_username: newUsername },
          {
            withCredentials: true,
          }
        );
        this.user = response.data.user; // 更新本地 user 狀態
        localStorage.setItem("user", JSON.stringify(this.user)); // 更新 localStorage
        useNotificationStore().showNotification(
          "使用者名稱更新成功！",
          "success"
        );
        return { success: true };
      } catch (err) {
        this.error = err.response?.data?.error || "更新使用者名稱失敗。";
        useNotificationStore().showNotification(this.error, "error");
        console.error("Update username error:", err);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async updatePassword(oldPassword, newPassword) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.put(
          `${API_BASE_URL}/user/password`,
          { old_password: oldPassword, new_password: newPassword },
          {
            withCredentials: true,
          }
        );
        // 密碼更新成功後，不返回 user 信息，只顯示通知
        useNotificationStore().showNotification("密碼更新成功！", "success");
        return { success: true };
      } catch (err) {
        this.error = err.response?.data?.error || "更新密碼失敗。";
        useNotificationStore().showNotification(this.error, "error");
        console.error("Update password error:", err);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },
  },
});
