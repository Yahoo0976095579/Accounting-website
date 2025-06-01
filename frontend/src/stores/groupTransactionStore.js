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
      filters = {},
      page = 1,
      per_page = 10
    ) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        const params = {
          page,
          per_page,
          ...filters,
        };
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
        this.currentGroupFilters = filters;
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
