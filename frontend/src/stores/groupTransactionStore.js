// client/src/stores/groupTransactionStore.js
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
    currentGroupFilters: {}, // 用於保存當前篩選條件
    groupSummary: { total_income: 0, total_expense: 0, balance: 0 },
  }),
  actions: {
    /**
     * 獲取指定群組的交易記錄列表，支持篩選和分頁
     * @param {number} groupId - 群組ID
     * @param {Object} filters - 篩選條件
     * @param {string} [filters.type] - 交易類型
     * @param {number} [filters.category_id] - 類別ID
     * @param {string} [filters.start_date] - 開始日期
     * @param {string} [filters.end_date] - 結束日期
     * @param {string} [filters.search_term] - 搜索關鍵詞
     * @param {number} [page=1] - 當前頁碼
     * @param {number} [per_page=10] - 每頁數量
     */
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
            withCredentials: true,
          }
        );
        this.groupTransactions = response.data.transactions;
        this.totalGroupTransactions = response.data.total;
        this.totalGroupPages = response.data.pages;
        this.currentGroupPage = response.data.page;
        this.currentGroupFilters = filters; // 保存當前篩選條件
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

    /**
     * 新增一筆群組交易記錄
     * @param {number} groupId - 群組ID
     * @param {Object} transactionData - 交易數據 (amount, type, category_id, description, date, created_by_user_id)
     */
    async addGroupTransaction(groupId, transactionData) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/groups/${groupId}/transactions`,
          transactionData,
          {
            withCredentials: true,
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

    /**
     * 更新一筆群組交易記錄
     * @param {number} groupId - 群組ID
     * @param {number} transactionId - 交易ID
     * @param {Object} transactionData - 更新的交易數據
     */
    async updateGroupTransaction(groupId, transactionId, transactionData) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        const response = await axios.put(
          `${API_BASE_URL}/groups/${groupId}/transactions/${transactionId}`,
          transactionData,
          {
            withCredentials: true,
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

    /**
     * 刪除一筆群組交易記錄
     * @param {number} groupId - 群組ID
     * @param {number} transactionId - 交易ID
     */
    async deleteGroupTransaction(groupId, transactionId) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        await axios.delete(
          `${API_BASE_URL}/groups/${groupId}/transactions/${transactionId}`,
          {
            withCredentials: true,
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

    /**
     * 獲取指定群組的摘要數據
     * @param {number} groupId - 群組ID
     */
    async fetchGroupSummary(groupId) {
      this.groupTransactionsLoading = true;
      this.groupTransactionError = null;
      try {
        const response = await axios.get(
          `${API_BASE_URL}/groups/${groupId}/summary`,
          {
            withCredentials: true,
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

    // 在這裡可以添加 fetchGroupCategoryBreakdown 和 fetchGroupTrendData (如果需要)
  },
});
