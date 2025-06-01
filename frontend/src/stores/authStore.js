import { defineStore } from "pinia";
import axios from "axios";
import router from "../router/index.js";
import { useNotificationStore } from "./notificationStore";
import { API_BASE_URL } from "./config";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: JSON.parse(localStorage.getItem("user")) || null,
    isLoading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user,
  },
  actions: {
    getAuthHeaders() {
      const token = localStorage.getItem("access_token");
      return token ? { Authorization: `Bearer ${token}` } : {};
    },

    // 新增的初始化動作
    async initializeAuth() {
      const token = localStorage.getItem("access_token");
      if (token && !this.user) {
        // 如果有 token 但 user 狀態是空的 (例如，刷新頁面)
        console.log("Initializing auth: Token found, fetching user profile...");
        await this.fetchCurrentUser(); // 嘗試從後端獲取用戶資料
      } else if (this.user) {
        console.log("Initializing auth: User data already present.");
      } else {
        console.log("Initializing auth: No token or user data found.");
      }
    },

    async register(username, password) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(`${API_BASE_URL}/register`, {
          username,
          password,
        });
        const token = response.data.access_token;
        if (token) {
          localStorage.setItem("access_token", token);
          // 註冊後，如果後端返回了完整的 user 物件，則直接設置
          // 如果沒有，你可能需要再調用 fetchCurrentUser()
          this.user = response.data.user; // 假設後端註冊成功後也返回了 user 資訊
          localStorage.setItem("user", JSON.stringify(this.user));
          router.push("/");
          return true;
        } else {
          // 如果註冊成功但沒返回 token，可能需要手動登入一次
          console.warn(
            "Register success but no token returned. Attempting login."
          );
          return await this.login(username, password); // 嘗試登入
        }
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
        const response = await axios.post(`${API_BASE_URL}/login`, {
          username,
          password,
        });
        const token = response.data.access_token;
        if (token) {
          localStorage.setItem("access_token", token);
        }
        // 確保這裡的 response.data.user 包含群組 ID
        this.user = response.data.user;
        localStorage.setItem("user", JSON.stringify(this.user));
        router.push("/");
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
        await axios.get(`${API_BASE_URL}/logout`, {
          headers: this.getAuthHeaders(),
        });
      } catch (err) {
        this.error = err.response?.data?.error || "Logout failed.";
        console.error("Logout error:", err);
      } finally {
        this.user = null;
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");
        router.push("/login");
        this.isLoading = false;
      }
    },

    async fetchCurrentUser() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/user`, {
          headers: this.getAuthHeaders(),
        });
        this.user = response.data; // 這裡的 response.data 必須包含群組 ID
        localStorage.setItem("user", JSON.stringify(this.user));
        return true;
      } catch (err) {
        if (err.response && err.response.status === 401) {
          console.warn(
            "Backend session expired or unauthorized. Clearing local auth state."
          );
        } else {
          console.error("Failed to fetch current user:", err);
        }
        this.user = null; // 獲取失敗則清除用戶資料
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // ... (其他更新用戶資訊的動作不變)
    async updateUsername(newUsername) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.put(
          `${API_BASE_URL}/user/username`,
          { new_username: newUsername },
          {
            headers: this.getAuthHeaders(),
          }
        );
        this.user = response.data.user; // 更新後的 user 資料
        localStorage.setItem("user", JSON.stringify(this.user));
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
        await axios.put(
          `${API_BASE_URL}/user/password`,
          { old_password: oldPassword, new_password: newPassword },
          {
            headers: this.getAuthHeaders(),
          }
        );
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
    async deleteAccount() {
      this.isLoading = true;
      this.error = null;
      const notificationStore = useNotificationStore(); // 實例化通知 Store

      try {
        const response = await axios.delete(`${API_BASE_URL}/user`, {
          headers: this.getAuthHeaders(),
        });

        // 成功刪除後，清除所有用戶數據並重定向
        this.user = null;
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");

        notificationStore.showNotification("帳號已成功刪除。", "success");
        router.push("/register"); // 或重定向到登入頁面
        return { success: true };
      } catch (err) {
        this.error = err.response?.data?.error || "刪除帳號失敗。";
        notificationStore.showNotification(this.error, "error");
        console.error("Delete account error:", err);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },
  },
});
