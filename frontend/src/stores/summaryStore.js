import { defineStore } from "pinia";
import axios from "axios";
import { API_BASE_URL } from "./config";

// 工具函數：過濾掉空字串、undefined、null 的參數
function cleanFilters(filters) {
  const cleaned = {};
  for (const key in filters) {
    if (
      filters[key] !== "" &&
      filters[key] !== undefined &&
      filters[key] !== null
    ) {
      cleaned[key] = filters[key];
    }
  }
  return cleaned;
}

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

    // 修正點 1: 接收 groupId 參數
    async loadAllDashboardData(groupId, chartFilters) {
      this.isLoading = true;
      this.fetchError = null;
      this.isDataReady = false;

      // 檢查 groupId 是否存在
      if (!groupId) {
        this.fetchError = "Group ID is required to load dashboard data.";
        console.error(this.fetchError);
        this.isLoading = false;
        this.isDataReady = false;
        return; // 終止執行
      }

      try {
        await Promise.all([
          // 修正點 2: 將 groupId 傳遞給內部函數
          this.fetchOverallSummaryInternal(groupId),
          this.fetchTrendDataInternal(groupId, chartFilters),
          this.fetchCategoryBreakdownInternal(groupId, {
            type: "expense",
            ...chartFilters,
          }),
          this.fetchIncomeCategoryBreakdownInternal(groupId, chartFilters),
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

    // 修正點 3: 接收 groupId 並修正 URL
    async fetchOverallSummaryInternal(groupId) {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/groups/${groupId}/summary`,
          {
            headers: this.getAuthHeaders(),
          }
        );
        this.totalIncome = response.data.total_income;
        this.totalExpense = response.data.total_expense;
        this.balance = response.data.balance;
      } catch (err) {
        throw err;
      }
    },

    // 修正點 4: 接收 groupId 並修正 URL
    async fetchCategoryBreakdownInternal(groupId, filters) {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/groups/${groupId}/summary/category_breakdown`, // 修正 URL
          { params: cleanFilters(filters), headers: this.getAuthHeaders() }
        );
        this.categoryBreakdown = response.data;
      } catch (err) {
        throw err;
      }
    },

    // 修正點 5: 接收 groupId 並修正 URL
    async fetchTrendDataInternal(groupId, filters) {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/groups/${groupId}/summary/trend`,
          {
            // 修正 URL
            params: cleanFilters(filters),
            headers: this.getAuthHeaders(),
          }
        );
        this.trendData = response.data;
      } catch (err) {
        throw err;
      }
    },

    // 修正點 6: 接收 groupId 並修正 URL (此函數也調用 fetchCategoryBreakdownInternal，但其 URL 也已修正)
    async fetchIncomeCategoryBreakdownInternal(groupId, filters) {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/groups/${groupId}/summary/category_breakdown`, // 修正 URL
          {
            params: cleanFilters({ ...filters, type: "income" }),
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
