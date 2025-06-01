import { defineStore } from "pinia";
import axios from "axios";
import { useNotificationStore } from "./notificationStore";
import { API_BASE_URL } from "./config";

export const useGroupTransactionStore = defineStore("groupTransaction", {
  state: () => ({
    groupTransactions: [],
    totalGroupTransactions: 0,
    totalGroupPages: 1,
    currentGroupPage: 1,
    groupTransactionsLoading: false,
    groupTransactionError: null,
    currentGroupFilters: {},
    groupSummary: { total_income: 0, total_expense: 0, balance: 0 },
  }),
  actions: {
    // 取得 JWT token 的 header
    getAuthHeaders() {
      const token = localStorage.getItem("access_token");
      return token ? { Authorization: `Bearer ${token}` } : {};
    },

    async fetchGroupTransactions(
      groupId,
      filters = {}, // 接收外部傳入的篩選器
      page = 1,
      per_page = 10
    ) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        // === 修正點：明確地清理篩選參數 ===
        const cleanedFilters = {};
        for (const key in filters) {
          // 檢查值是否為空字串、null 或 undefined
          // 對於數字型 ID，0 可能是有效值，所以不應該過濾 0
          if (
            filters[key] !== "" &&
            filters[key] !== null &&
            filters[key] !== undefined
          ) {
            cleanedFilters[key] = filters[key];
          }
        }
        // ===============================================

        const params = {
          page,
          per_page,
          ...cleanedFilters, // 將清理後的篩選器作為參數
        };

        console.log("Fetching group transactions with params:", params); // 打印發送的參數

        const response = await axios.get(
          `${API_BASE_URL}/groups/${groupId}/transactions`,
          {
            params,
            headers: this.getAuthHeaders(),
          }
        );
        this.groupTransactions = response.data.transactions;
        this.totalGroupTransactions = response.data.total;
        this.totalGroupPages = response.data.pages;
        this.currentGroupPage = response.data.page;
        this.currentGroupFilters = filters; // 仍然將原始的 filters 儲存到 state 中，用於 UI 顯示

        console.log("Fetched group transactions:", response.data.transactions); // 打印獲取的數據
      } catch (err) {
        this.groupTransactionError =
          err.response?.data?.error || "Failed to fetch group transactions.";
        useNotificationStore().showNotification(
          this.groupTransactionError,
          "error"
        );
        console.error("Fetch group transactions error:", err);
      } finally {
        this.groupTransactionsLoading = false;
      }
    },

    async addGroupTransaction(groupId, transactionData) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/groups/${groupId}/transactions`,
          transactionData,
          {
            headers: this.getAuthHeaders(),
          }
        );
        useNotificationStore().showNotification(
          "群組交易新增成功！",
          "success"
        );
        return { success: true, transaction: response.data };
      } catch (err) {
        this.groupTransactionError =
          err.response?.data?.error || "Failed to add group transaction.";
        useNotificationStore().showNotification(
          this.groupTransactionError,
          "error"
        );
        console.error("Add group transaction error:", err);
        return { success: false, error: this.groupTransactionError };
      } finally {
        this.groupTransactionsLoading = false;
      }
    },

    async updateGroupTransaction(groupId, transactionId, transactionData) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        const response = await axios.put(
          `${API_BASE_URL}/groups/${groupId}/transactions/${transactionId}`,
          transactionData,
          {
            headers: this.getAuthHeaders(),
          }
        );
        useNotificationStore().showNotification(
          "群組交易更新成功！",
          "success"
        );
        return { success: true, transaction: response.data };
      } catch (err) {
        this.groupTransactionError =
          err.response?.data?.error || "Failed to update group transaction.";
        useNotificationStore().showNotification(
          this.groupTransactionError,
          "error"
        );
        console.error("Update group transaction error:", err);
        return { success: false, error: this.groupTransactionError };
      } finally {
        this.groupTransactionsLoading = false;
      }
    },

    async deleteGroupTransaction(groupId, transactionId) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        await axios.delete(
          `${API_BASE_URL}/groups/${groupId}/transactions/${transactionId}`,
          {
            headers: this.getAuthHeaders(),
          }
        );
        useNotificationStore().showNotification(
          "群組交易刪除成功！",
          "success"
        );
        return true;
      } catch (err) {
        this.groupTransactionError =
          err.response?.data?.error || "Failed to delete group transaction.";
        useNotificationStore().showNotification(
          this.groupTransactionError,
          "error"
        );
        console.error("Delete group transaction error:", err);
        return false;
      } finally {
        this.groupTransactionsLoading = false;
      }
    },

    async fetchGroupSummary(groupId) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        const response = await axios.get(
          `${API_BASE_URL}/groups/${groupId}/summary`,
          {
            headers: this.getAuthHeaders(),
          }
        );
        this.groupSummary = response.data;
      } catch (err) {
        this.groupTransactionError =
          err.response?.data?.error || "Failed to fetch group summary.";
        useNotificationStore().showNotification(
          this.groupTransactionError,
          "error"
        );
        console.error("Fetch group summary error:", err);
      } finally {
        this.groupTransactionsLoading = false;
      }
    },

    // 可以在這裡添加 fetchGroupCategoryBreakdown 和 fetchGroupTrendData（如有需要）
  },
});
