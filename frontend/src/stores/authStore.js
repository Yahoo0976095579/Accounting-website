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
    // 取得 JWT token 的 header
    getAuthHeaders() {
      const token = localStorage.getItem("access_token");
      return token ? { Authorization: `Bearer ${token}` } : {};
    },

    async register(username, password) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(`${API_BASE_URL}/register`, {
          username,
          password,
        });
        // 註冊後直接登入，取得 token
        const token = response.data.access_token;
        if (token) {
          localStorage.setItem("access_token", token);
        }
        this.user = response.data.user;
        localStorage.setItem("user", JSON.stringify(this.user));
        router.push("/");
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
        const response = await axios.post(`${API_BASE_URL}/login`, {
          username,
          password,
        });
        const token = response.data.access_token;
        if (token) {
          localStorage.setItem("access_token", token);
        }
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
        // 後端只是回傳訊息，前端直接清除 token
        await axios.get(`${API_BASE_URL}/logout`, {
          headers: this.getAuthHeaders(),
        });
      } catch (err) {
        // 即使失敗也要清理前端狀態
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
        this.user = response.data;
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
        this.user = null;
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");
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
            headers: this.getAuthHeaders(),
          }
        );
        this.user = response.data.user;
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
  },
});
