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
    async loadAllDashboardData(groupId = null, chartFilters) {
      // groupId 預設為 null
      this.isLoading = true;
      this.fetchError = null;
      this.isDataReady = false;

      // 根據 groupId 是否存在，決定使用個人 API 還是群組 API 的函數
      const fetchOverallSummary = groupId
        ? () => this.fetchOverallSummaryInternal(groupId)
        : () => this.fetchPersonalOverallSummaryInternal(); // 新增個人總覽函數

      const fetchTrendData = groupId
        ? () => this.fetchTrendDataInternal(groupId, chartFilters)
        : () => this.fetchPersonalTrendDataInternal(chartFilters); // 新增個人趨勢函數

      const fetchExpenseBreakdown = groupId
        ? () =>
            this.fetchCategoryBreakdownInternal(groupId, {
              type: "expense",
              ...chartFilters,
            })
        : () =>
            this.fetchPersonalCategoryBreakdownInternal({
              type: "expense",
              ...chartFilters,
            }); // 新增個人類別細分函數

      const fetchIncomeBreakdown = groupId
        ? () =>
            this.fetchCategoryBreakdownInternal(groupId, {
              type: "income",
              ...chartFilters,
            })
        : () =>
            this.fetchPersonalCategoryBreakdownInternal({
              type: "income",
              ...chartFilters,
            }); // 新增個人類別細分函數

      try {
        await Promise.all([
          fetchOverallSummary(),
          fetchTrendData(),
          fetchExpenseBreakdown(),
          fetchIncomeBreakdown(),
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

    // ===== 新增：個人總覽 API 調用函數 =====
    async fetchPersonalOverallSummaryInternal() {
      try {
        const response = await axios.get(`${API_BASE_URL}/summary`, {
          // 個人總覽路由
          headers: this.getAuthHeaders(),
        });
        this.totalIncome = response.data.total_income;
        this.totalExpense = response.data.total_expense;
        this.balance = response.data.balance;
      } catch (err) {
        throw err;
      }
    },
    // ===================================

    // ===== 新增：個人類別細分 API 調用函數 =====
    async fetchPersonalCategoryBreakdownInternal(filters) {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/summary/category_breakdown`, // 個人類別細分路由
          { params: cleanFilters(filters), headers: this.getAuthHeaders() }
        );
        // 這裡可能需要根據 income/expense 類型來更新不同的狀態，
        // 或者將它們合併到一個更通用的 categoryBreakdown 狀態中。
        // 為了簡潔，先假設你只用一個 categoryBreakdown，或者根據 filter.type 決定賦值
        if (filters.type === "expense") {
          this.categoryBreakdown = response.data; // 用於支出
        } else if (filters.type === "income") {
          this.incomeCategoryBreakdown = response.data; // 用於收入
        }
      } catch (err) {
        throw err;
      }
    },
    // ===================================

    // ===== 新增：個人趨勢 API 調用函數 =====
    async fetchPersonalTrendDataInternal(filters) {
      try {
        const response = await axios.get(`${API_BASE_URL}/summary/trend`, {
          // 個人趨勢路由
          params: cleanFilters(filters),
          headers: this.getAuthHeaders(),
        });
        this.trendData = response.data;
      } catch (err) {
        throw err;
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
      return this.fetchCategoryBreakdownInternal(groupId, {
        ...filters,
        type: "income",
      });
    },
  },
});
