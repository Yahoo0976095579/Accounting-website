// client/src/stores/categoryStore.js
import { defineStore } from "pinia";
import axios from "axios";
import { useNotificationStore } from "./notificationStore";
import { API_BASE_URL } from "./config";

export const useCategoryStore = defineStore("category", {
  state: () => ({
    categories: [],
    isLoading: false,
    fetchError: null, // 將獲取類別的錯誤單獨命名
  }),
  actions: {
    async fetchCategories() {
      this.isLoading = true;
      this.fetchError = null; // 清除獲取錯誤
      try {
        const response = await axios.get(`${API_BASE_URL}/categories`, {
          withCredentials: true,
        });
        this.categories = response.data;
      } catch (err) {
        this.fetchError =
          err.response?.data?.error || "Failed to fetch categories.";
        console.error("Fetch categories error:", err);
      } finally {
        this.isLoading = false;
      }
    },

    async addCategory(categoryData) {
      this.isLoading = true;
      // 這裡不設置 this.fetchError，而是讓錯誤拋出給 CategoryForm 處理
      try {
        const response = await axios.post(
          `${API_BASE_URL}/categories`,
          categoryData,
          {
            withCredentials: true,
          }
        );
        this.categories.push(response.data);
        return { success: true }; // 返回一個物件，表示成功
      } catch (err) {
        console.error("Add category error:", err);
        // 返回錯誤訊息給調用者
        return {
          success: false,
          error: err.response?.data?.error || "Failed to add category.",
        };
      } finally {
        this.isLoading = false;
      }
    },

    async updateCategory(id, categoryData) {
      this.isLoading = true;
      try {
        const response = await axios.put(
          `${API_BASE_URL}/categories/${id}`,
          categoryData,
          {
            withCredentials: true,
          }
        );
        const index = this.categories.findIndex((c) => c.id === id);
        if (index !== -1) {
          this.categories[index] = response.data;
        }
        return { success: true }; // 返回一個物件，表示成功
      } catch (err) {
        console.error("Update category error:", err);
        // 返回錯誤訊息給調用者
        return {
          success: false,
          error: err.response?.data?.error || "Failed to update category.",
        };
      } finally {
        this.isLoading = false;
      }
    },

    async deleteCategory(id) {
      const notificationStore = useNotificationStore(); // 刪除操作仍然使用全局通知
      this.isLoading = true;
      // 不設置 this.fetchError
      try {
        await axios.delete(`${API_BASE_URL}/categories/${id}`, {
          withCredentials: true,
        });
        this.categories = this.categories.filter((c) => c.id !== id);
        notificationStore.showNotification("類別刪除成功！", "success");
        return true;
      } catch (err) {
        const errorMessage =
          err.response?.data?.error || "Failed to delete category.";
        notificationStore.showNotification(errorMessage, "error");
        console.error("Delete category error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
