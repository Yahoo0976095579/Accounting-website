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
    currentFilters: {},
    has_next: false,
    has_prev: false,
    summary: { income: 0, expense: 0, balance: 0 },
  }),
  actions: {
    // 取得 JWT token 的 header
    getAuthHeaders() {
      const token = localStorage.getItem("access_token");
      return token ? { Authorization: `Bearer ${token}` } : {};
    },

    /**
     * 獲取交易記錄列表，支持篩選和分頁
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
          headers: this.getAuthHeaders(),
        });
        this.transactions = response.data.transactions;
        this.totalTransactions = response.data.total;
        this.totalPages = response.data.pages;
        this.currentPage = response.data.page;
        this.currentFilters = filters;
        this.has_next = response.data.has_next;
        this.has_prev = response.data.has_prev;
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
     */
    async addTransaction(transactionData) {
      const notificationStore = useNotificationStore();
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/transactions`,
          transactionData,
          {
            headers: this.getAuthHeaders(),
          }
        );
        notificationStore.showNotification("交易新增成功！", "success");
        await this.fetchTransactions(this.currentFilters, this.currentPage, 10);
        return true;
      } catch (err) {
        this.error = err.response?.data?.error || "Failed to add transaction.";
        notificationStore.showNotification(this.error, "error");
        console.error("Add transaction error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 更新一筆交易記錄
     */
    async updateTransaction(id, transactionData) {
      const notificationStore = useNotificationStore();
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.put(
          `${API_BASE_URL}/transactions/${id}`,
          transactionData,
          {
            headers: this.getAuthHeaders(),
          }
        );
        const index = this.transactions.findIndex((t) => t.id === id);
        if (index !== -1) {
          this.transactions[index] = response.data;
        }
        notificationStore.showNotification("交易更新成功！", "success");
        await this.fetchTransactions(this.currentFilters, this.currentPage, 10);
        return true;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to update transaction.";
        notificationStore.showNotification(this.error, "error");
        console.error("Update transaction error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 刪除一筆交易記錄
     */
    async deleteTransaction(id) {
      const notificationStore = useNotificationStore();
      this.isLoading = true;
      this.error = null;
      try {
        await axios.delete(`${API_BASE_URL}/transactions/${id}`, {
          headers: this.getAuthHeaders(),
        });
        this.transactions = this.transactions.filter((t) => t.id !== id);
        this.totalTransactions--;

        if (this.transactions.length === 0 && this.currentPage > 1) {
          this.currentPage--;
        }
        notificationStore.showNotification("交易刪除成功！", "success");
        await this.fetchTransactions(this.currentFilters, this.currentPage, 10);
        return true;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to delete transaction.";
        notificationStore.showNotification(this.error, "error");
        console.error("Delete transaction error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    setCurrentFilters(filters) {
      this.currentFilters = filters;
    },

    async fetchSummary(filters) {
      const res = await axios.get(`${API_BASE_URL}/transactions/summary`, {
        params: filters,
        headers: this.getAuthHeaders(),
      });
      this.summary = res.data;
    },
  },
});
