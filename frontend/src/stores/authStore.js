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
    isLoggingOut: false, // === 新增：登出中旗標 ===
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

    // src/stores/authStore.js
    async logout() {
      if (this.isLoggingOut) {
        // 如果已經在登出中，直接返回，避免重複執行
        console.warn("Already logging out, preventing duplicate logout calls.");
        return;
      }
      this.isLoggingOut = true; // 設置登出中旗標

      this.isLoading = true;
      this.error = null;
      try {
        // 發送 logout 請求，但這裡不 await，讓它非同步執行，
        // 即使失敗也快速進入 finally 塊進行本地清理和重定向。
        // 或者，可以選擇完全移除這個後端 logout 請求，
        // 因為 JWT 的關鍵在於前端清除 token。
        axios
          .get(`${API_BASE_URL}/logout`, {
            headers: this.getAuthHeaders(),
          })
          .catch((err) => {
            // 捕獲錯誤，但不阻止 finally 塊執行
            console.error(
              "Logout API call failed, but proceeding with local cleanup:",
              err
            );
          });
      } catch (err) {
        // 這裡的 catch 塊可能不會被執行，因為我們上面沒有 await axios.get
        this.error = err.response?.data?.error || "Logout failed locally.";
        console.error("Logout error (local catch):", err);
      } finally {
        this.user = null;
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");
        console.log("Performing local logout cleanup and redirect.");
        router.push("/login"); // 確保重定向
        this.isLoading = false;
        this.isLoggingOut = false; // 清除登出中旗標
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
        // 全局攔截器現在會處理 401 Unauthorized 錯誤，並觸發登出
        // 所以在這裡，我們只需要處理非 401 的錯誤，或者在 401 時清除本地狀態即可
        if (err.response && err.response.status !== 401) {
          console.error("Failed to fetch current user (non-401 error):", err);
          this.error = err.response?.data?.error || "獲取用戶信息失敗。";
          // 可以選擇是否顯示通知：useNotificationStore().showNotification(this.error, "error");
        } else if (err.response && err.response.status === 401) {
          // 如果是 401，攔截器已經處理了重定向和通知。
          // 這裡只需要確保本地狀態被清除。
          console.warn(
            "Fetch current user received 401. Interceptor handled logout/redirect."
          );
        } else {
          // 網路錯誤或其他未知錯誤
          console.error(
            "Failed to fetch current user (network or other error):",
            err
          );
          this.error = "無法連接到伺服器或發生未知錯誤。";
        }

        // 無論何種錯誤，都清除本地存儲的用戶信息，確保會話失效
        this.user = null;
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");
        // 不需要在此處再次重定向，因為攔截器已經處理了
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
      const notificationStore = useNotificationStore();

      try {
        await axios.delete(`${API_BASE_URL}/user`, {
          // 調用後端新的 DELETE /api/user
          headers: this.getAuthHeaders(),
        });

        // 成功刪除後，清除所有用戶數據並重定向
        this.user = null;
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");

        notificationStore.showNotification("帳號已成功刪除。", "success");
        router.push("/register"); // 重定向到註冊頁面或登入頁面
        return { success: true };
      } catch (err) {
        // === 修正點：使用 notificationStore 顯示錯誤 ===
        const errorMessage = err.response?.data?.error || "刪除帳號失敗。";
        notificationStore.showNotification(errorMessage, "error");
        this.error = null; // 確保清除任何可能導致全頁顯示的錯誤
        // ===============================================
        console.error("Delete account error:", err);
        return { success: false, error: errorMessage };
      } finally {
        this.isLoading = false;
      }
    },
  },
});
