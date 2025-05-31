// client/src/stores/summaryStore.js
import { defineStore } from "pinia";
import axios from "axios";

import { API_BASE_URL } from "./stores/config";

export const useSummaryStore = defineStore("summary", {
  state: () => ({
    totalIncome: 0,
    totalExpense: 0,
    balance: 0,
    categoryBreakdown: [],
    incomeCategoryBreakdown: [], // 新增這行
    trendData: [],
    isLoading: false,
    fetchError: null,
    isDataReady: false, // 這個狀態仍然可以保留，但現在它只是標記數據是否完成載入，不會直接影響渲染
  }),
  actions: {
    // fetchOverallSummary, fetchCategoryBreakdown, fetchTrendData 這些方法保持不變，但不會再從 Dashboard.vue 直接調用

    async loadAllDashboardData(chartFilters) {
      this.isLoading = true;
      this.fetchError = null;
      this.isDataReady = false;

      try {
        // 並行發送所有請求
        await Promise.all([
          this.fetchOverallSummaryInternal(),
          this.fetchTrendDataInternal(chartFilters),
          this.fetchCategoryBreakdownInternal({
            type: "expense",
            ...chartFilters,
          }),
          this.fetchIncomeCategoryBreakdownInternal(chartFilters), // 新增這行
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
    // 為了讓 loadAllDashboardData 能調用內部方法，我們需要將原本的 fetch... 方法改為內部方法
    async fetchOverallSummaryInternal() {
      // 這是新的內部方法名稱
      try {
        const response = await axios.get(`${API_BASE_URL}/summary`, {
          withCredentials: true,
        });
        this.totalIncome = response.data.total_income;
        this.totalExpense = response.data.total_expense;
        this.balance = response.data.balance;
      } catch (err) {
        throw err; // 拋出錯誤，讓 loadAllDashboardData 捕獲
      }
    },
    async fetchCategoryBreakdownInternal(filters) {
      // 這是新的內部方法名稱
      try {
        const response = await axios.get(
          `${API_BASE_URL}/summary/category_breakdown`,
          { params: filters, withCredentials: true }
        );
        this.categoryBreakdown = response.data;
      } catch (err) {
        throw err;
      }
    },
    async fetchTrendDataInternal(filters) {
      // 這是新的內部方法名稱
      try {
        const response = await axios.get(`${API_BASE_URL}/summary/trend`, {
          params: filters,
          withCredentials: true,
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
          { params: { ...filters, type: "income" }, withCredentials: true }
        );
        this.incomeCategoryBreakdown = response.data;
      } catch (err) {
        throw err;
      }
    },
  },
});
