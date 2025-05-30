<!-- client/src/views/Dashboard.vue (在 <template> 內部) -->
<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6">記帳儀表板</h1>

    <p class="mb-6 text-gray-700">
      歡迎，<span class="font-semibold">{{ authStore.user?.username }}</span
      >！這裡是您的財務概覽。
    </p>

    <!-- client/src/views/Dashboard.vue (在 <template> 內部) -->
    <div v-if="summaryStore.isLoading" class="text-center py-8">
      <LoadingSpinner message="正在載入儀表板數據..." />
    </div>
    <!-- 這裡從 summaryStore.error 改為 summaryStore.fetchError -->
    <div v-else-if="summaryStore.fetchError" class="text-center py-8">
      <p class="text-red-500 text-lg">錯誤：{{ summaryStore.fetchError }}</p>
    </div>
    <div v-else>
      <!-- 總覽卡片 (保持不變) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="bg-white p-6 rounded-lg shadow-md text-center">
          <h2 class="text-xl font-semibold mb-2 text-gray-700">總收入</h2>
          <p class="text-green-600 text-4xl font-bold">
            ${{ summaryStore.totalIncome.toFixed(2) }}
          </p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md text-center">
          <h2 class="text-xl font-semibold mb-2 text-gray-700">總支出</h2>
          <p class="text-red-600 text-4xl font-bold">
            ${{ summaryStore.totalExpense.toFixed(2) }}
          </p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md text-center">
          <h2 class="text-xl font-semibold mb-2 text-gray-700">總結餘</h2>
          <p
            :class="{
              'text-blue-600': summaryStore.balance >= 0,
              'text-orange-600': summaryStore.balance < 0,
            }"
            class="text-4xl font-bold"
          >
            ${{ summaryStore.balance.toFixed(2) }}
          </p>
        </div>
      </div>

      <!-- 這是唯一的「過濾器」div，其中包含所有篩選控制項 -->
      <div
        class="mb-6 p-4 bg-white rounded-lg shadow-sm flex flex-wrap items-center gap-4"
      >
        <h3 class="text-lg font-semibold text-gray-700 mr-2">數據篩選:</h3>
        <!-- 區間選擇 -->
        <div class="flex items-center space-x-2">
          <label for="trendInterval" class="text-gray-700 text-sm font-bold"
            >區間:</label
          >
          <select
            id="trendInterval"
            v-model="chartFilters.interval"
            @change="loadDashboardData"
            class="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
          >
            <option value="month">按月</option>
            <option value="week">按週</option>
            <option value="day">按日</option>
          </select>
        </div>

        <!-- 日期範圍篩選和重置按鈕的容器 -->
        <div
          class="flex flex-col sm:flex-row sm:items-center sm:space-x-2 space-y-2 sm:space-y-0 w-full sm:w-auto"
        >
          <div class="flex items-center space-x-2 w-full">
            <label
              for="chartStartDate"
              class="text-gray-700 text-sm font-bold whitespace-nowrap"
              >從:</label
            >
            <input
              type="date"
              id="chartStartDate"
              v-model="chartFilters.start_date"
              @change="loadDashboardData"
              class="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm flex-grow min-w-[140px]"
            />
          </div>
          <div class="flex items-center space-x-2 w-full">
            <label
              for="chartEndDate"
              class="text-gray-700 text-sm font-bold whitespace-nowrap"
              >到:</label
            >
            <input
              type="date"
              id="chartEndDate"
              v-model="chartFilters.end_date"
              @change="loadDashboardData"
              class="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm flex-grow min-w-[140px]"
            />
          </div>
          <div class="w-full sm:w-auto">
            <!-- 這個父 div 可以保留，確保在小螢幕下佔用一行 -->
            <button
              @click="resetChartFilters"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm whitespace-nowrap flex-shrink-0 mx-auto sm:mx-0"
            >
              重置日期
            </button>
          </div>
        </div>
      </div>
      <!-- <-- 第二個「過濾器」div 結束標籤 -->

      <!-- 數據列表區塊 (取代圖表) -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h2 class="text-2xl font-bold mb-4 text-gray-700">
            收支趨勢 (按{{
              chartFilters.interval === "month"
                ? "月"
                : chartFilters.interval === "week"
                ? "週"
                : "日"
            }})
          </h2>
          <div v-if="summaryStore.trendData.length > 0">
            <ul class="divide-y divide-gray-200">
              <li
                v-for="item in summaryStore.trendData"
                :key="item.period"
                class="py-2 flex justify-between items-center"
              >
                <span class="font-semibold text-gray-800">{{
                  item.period
                }}</span>
                <div>
                  <span class="text-green-600 mr-4"
                    >收入: ${{ item.income.toFixed(2) }}</span
                  >
                  <span class="text-red-600"
                    >支出: ${{ item.expense.toFixed(2) }}</span
                  >
                  <span
                    :class="{
                      'text-blue-600': item.balance >= 0,
                      'text-orange-600': item.balance < 0,
                    }"
                    class="ml-4 font-bold"
                    >結餘: ${{ item.balance.toFixed(2) }}</span
                  >
                </div>
              </li>
            </ul>
          </div>
          <p v-else class="text-center text-gray-500 py-8">
            沒有足夠的數據來顯示收支趨勢。
          </p>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-md">
          <h2 class="text-2xl font-bold mb-4 text-gray-700">支出類別分佈</h2>
          <div v-if="summaryStore.categoryBreakdown.length > 0">
            <ul class="divide-y divide-gray-200">
              <li
                v-for="item in summaryStore.categoryBreakdown"
                :key="item.category_name"
                class="py-2 flex justify-between items-center"
              >
                <span class="font-semibold text-gray-800">{{
                  item.category_name
                }}</span>
                <span class="text-red-600 font-bold"
                  >${{ item.total_amount.toFixed(2) }}</span
                >
              </li>
            </ul>
          </div>
          <p v-else class="text-center text-gray-500 py-8">
            沒有足夠的支出數據來顯示類別分佈。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<!-- client/src/views/Dashboard.vue (在 <script setup> 內部) -->
<script setup>
import { ref, onMounted, reactive, watch } from "vue"; // 移除 computed 導入
import { useAuthStore } from "../stores/authStore";
import { useSummaryStore } from "../stores/summaryStore"; // 確保這個路徑正確
import LoadingSpinner from "../components/LoadingSpinner.vue"; // <-- 新增導入

// 移除所有 Chart.js 和 vue-chartjs 的導入
// import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, ArcElement } from "chart.js";
// import { Line as LineChart, Doughnut as DoughnutChart } from "vue-chartjs";
// 移除 ChartJS.register()

const authStore = useAuthStore();
const summaryStore = useSummaryStore();

const chartFilters = reactive({
  interval: "month",
  start_date: "",
  end_date: "",
});

// 統一的數據載入函數
async function loadDashboardData() {
  // 修改回 loadDashboardData
  console.log("Loading dashboard data with filters:", chartFilters);
  await summaryStore.loadAllDashboardData(chartFilters); // 調用 summaryStore 中的新方法
  console.log("Dashboard data loaded.");
}

onMounted(async () => {
  console.log("Dashboard onMounted: Initializing dashboard data.");
  await loadDashboardData(); // 初始載入數據
});

watch(chartFilters, loadDashboardData, { deep: true }); // 監聽篩選變化並重新載入數據

const resetChartFilters = () => {
  chartFilters.start_date = "";
  chartFilters.end_date = "";
  // watch 會觸發 loadDashboardData
};

// 移除所有圖表相關的 computed 屬性
// const lineChartData = computed(() => { /* ... */ });
// const lineChartOptions = { /* ... */ };
// const doughnutChartData = computed(() => { /* ... */ });
// const doughnutChartOptions = { /* ... */ };
</script>
