import { defineStore } from "pinia";
import axios from "axios";
import { API_BASE_URL } from "./config";

export const useSummaryStore = defineStore("summary", {
  state: () => ({
    totalIncome: 0,
    totalExpense: 0,
    balance: 0,
    categoryBreakdown: [],
    incomeCategoryBreakdown: [],
    trendData: [],
    isLoading: false,
    fetchError: null,
    isDataReady: false,
  }),
  actions: {
    // 取得 JWT token 的 header
    getAuthHeaders() {
      const token = localStorage.getItem("access_token");
      return token ? { Authorization: `Bearer ${token}` } : {};
    },

    async loadAllDashboardData(chartFilters) {
      this.isLoading = true;
      this.fetchError = null;
      this.isDataReady = false;

      try {
        await Promise.all([
          this.fetchOverallSummaryInternal(),
          this.fetchTrendDataInternal(chartFilters),
          this.fetchCategoryBreakdownInternal({
            type: "expense",
            ...chartFilters,
          }),
          this.fetchIncomeCategoryBreakdownInternal(chartFilters),
        ]);
        this.isDataReady = true;
      } catch (err) {
        this.fetchError =
          this.fetchError || "Failed to load all dashboard data.";
        console.error("Load all dashboard data error:", err);
        this.isDataReady = false;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchOverallSummaryInternal() {
      try {
        const response = await axios.get(`${API_BASE_URL}/summary`, {
          headers: this.getAuthHeaders(),
        });
        this.totalIncome = response.data.total_income;
        this.totalExpense = response.data.total_expense;
        this.balance = response.data.balance;
      } catch (err) {
        throw err;
      }
    },

    async fetchCategoryBreakdownInternal(filters) {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/summary/category_breakdown`,
          { params: filters, headers: this.getAuthHeaders() }
        );
        this.categoryBreakdown = response.data;
      } catch (err) {
        throw err;
      }
    },

    async fetchTrendDataInternal(filters) {
      try {
        const response = await axios.get(`${API_BASE_URL}/summary/trend`, {
          params: filters,
          headers: this.getAuthHeaders(),
        });
        this.trendData = response.data;
      } catch (err) {
        throw err;
      }
    },

    async fetchIncomeCategoryBreakdownInternal(filters) {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/summary/category_breakdown`,
          {
            params: { ...filters, type: "income" },
            headers: this.getAuthHeaders(),
          }
        );
        this.incomeCategoryBreakdown = response.data;
      } catch (err) {
        throw err;
      }
    },
  },
});
