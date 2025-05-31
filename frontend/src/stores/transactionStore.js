// client/src/stores/transactionStore.js
import { defineStore } from "pinia";
import axios from "axios";
import { useNotificationStore } from "./notificationStore";

import { API_BASE_URL } from "./config";

export const useTransactionStore = defineStore("transaction", {
  state: () => ({
    transactions: [],
    totalTransactions: 0,
    totalPages: 1,
    currentPage: 1,
    isLoading: false,
    error: null,
    currentFilters: {}, // 確保這裡有一個 currentFilters 狀態用於存儲篩選條件
    has_next: false, // <--- 新增
    has_prev: false, // <--- 新增
    summary: { income: 0, expense: 0, balance: 0 }, // <--- 新增這行
  }),
  actions: {
    /**
     * 獲取交易記錄列表，支持篩選和分頁
     * @param {Object} filters - 篩選條件
     * @param {string} [filters.type] - 交易類型 ('income' or 'expense')
     * @param {number} [filters.category_id] - 類別ID
     * @param {string} [filters.start_date] - 開始日期 (YYYY-MM-DD)
     * @param {string} [filters.end_date] - 結束日期 (YYYY-MM-DD)
     * @param {string} [filters.search_term] - 搜索關鍵詞 (新增)
     * @param {number} [page=1] - 當前頁碼
     * @param {number} [per_page=10] - 每頁數量
     */
    async fetchTransactions(filters = {}, page = 1, per_page = 10) {
      this.isLoading = true;
      this.error = null;
      try {
        const params = {
          page,
          per_page,
          ...filters,
        };
        const response = await axios.get(`${API_BASE_URL}/transactions`, {
          params,
          withCredentials: true,
        });
        this.transactions = response.data.transactions;
        this.totalTransactions = response.data.total;
        this.totalPages = response.data.pages;
        this.currentPage = response.data.page;
        // 在這裡更新 currentFilters，因為 fetchTransactions 可能會被外部調用
        this.currentFilters = filters; // 更新篩選條件
        this.has_next = response.data.has_next; // <--- 新增
        this.has_prev = response.data.has_prev; // <--- 新增
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to fetch transactions.";
        console.error("Fetch transactions error:", err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 新增一筆交易記錄
     * @param {Object} transactionData - 交易數據 (amount, type, category_id, description, date)
     */
    async addTransaction(transactionData) {
      const notificationStore = useNotificationStore(); // 在 action 內部獲取實例
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/transactions`,
          transactionData,
          {
            withCredentials: true,
          }
        );
        // 顯示成功通知
        notificationStore.showNotification("交易新增成功！", "success");
        // 重新載入當前頁面和篩選條件的列表
        await this.fetchTransactions(this.currentFilters, this.currentPage, 10);
        return true;
      } catch (err) {
        this.error = err.response?.data?.error || "Failed to add transaction.";
        notificationStore.showNotification(this.error, "error"); // 顯示錯誤通知
        console.error("Add transaction error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 更新一筆交易記錄
     * @param {number} id - 交易ID
     * @param {Object} transactionData - 更新的交易數據
     */
    async updateTransaction(id, transactionData) {
      const notificationStore = useNotificationStore(); // 在 action 內部獲取實例
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.put(
          `${API_BASE_URL}/transactions/${id}`,
          transactionData,
          {
            withCredentials: true,
          }
        );
        // 更新 Store 中的對應交易
        const index = this.transactions.findIndex((t) => t.id === id);
        if (index !== -1) {
          this.transactions[index] = response.data;
        }
        // 顯示成功通知
        notificationStore.showNotification("交易更新成功！", "success");
        // 由於更新可能改變排序或篩選，最好也重新載入列表
        await this.fetchTransactions(this.currentFilters, this.currentPage, 10);
        return true;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to update transaction.";
        notificationStore.showNotification(this.error, "error"); // 顯示錯誤通知
        console.error("Update transaction error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 刪除一筆交易記錄
     * @param {number} id - 交易ID
     */
    async deleteTransaction(id) {
      const notificationStore = useNotificationStore(); // 在 action 內部獲取實例
      this.isLoading = true;
      this.error = null;
      try {
        await axios.delete(`${API_BASE_URL}/transactions/${id}`, {
          withCredentials: true,
        });
        // 從 Store 中移除該交易 (視覺上立即移除，但實際列表可能需要重新獲取)
        this.transactions = this.transactions.filter((t) => t.id !== id);
        this.totalTransactions--; // 總數減少

        // 如果當前頁面刪完，且不是第一頁，回到上一頁
        if (this.transactions.length === 0 && this.currentPage > 1) {
          this.currentPage--;
        }
        // 顯示成功通知
        notificationStore.showNotification("交易刪除成功！", "success");
        // 重新載入以確保數據一致性 (考慮分頁和篩選)
        await this.fetchTransactions(this.currentFilters, this.currentPage, 10);
        return true;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to delete transaction.";
        notificationStore.showNotification(this.error, "error"); // 顯示錯誤通知
        console.error("Delete transaction error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // 在這裡儲存當前的篩選條件，以便在新增/刪除後重新載入時使用
    // 注意：這個方法現在在 fetchTransactions 內部自動調用，確保 currentFilters 總是最新
    setCurrentFilters(filters) {
      this.currentFilters = filters;
    },
    async fetchSummary(filters) {
      const res = await axios.get(`${API_BASE_URL}/transactions/summary`, {
        params: filters,
        withCredentials: true,
      });
      this.summary = res.data;
    },
  },
});
