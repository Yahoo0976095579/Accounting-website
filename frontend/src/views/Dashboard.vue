<template>
  <div class="container mx-auto p-4">
    <h1
      class="text-3xl font-bold mb-6 text-center text-blue-700 tracking-wide border-b-2 border-blue-200 pb-4 flex items-center justify-center gap-2"
    >
      <svg
        class="w-8 h-8 text-blue-400"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        viewBox="0 0 24 24"
      >
        <path d="M12 8v4l3 3"></path>
        <circle cx="12" cy="12" r="10"></circle>
      </svg>
      記帳儀表板
    </h1>

    <p class="mb-8 text-gray-700 text-center text-lg">
      歡迎，<span class="font-semibold text-blue-600">{{
        authStore.user?.username
      }}</span
      >！這裡是您的財務概覽。
    </p>

    <div v-if="summaryStore.isLoading" class="text-center py-12">
      <LoadingSpinner message="正在載入儀表板數據..." />
    </div>
    <div v-else-if="summaryStore.fetchError" class="text-center py-12">
      <p class="text-red-500 text-lg">錯誤：{{ summaryStore.fetchError }}</p>
    </div>
    <div v-else>
      <!-- 總覽卡片 -->
      <!-- filepath: c:\Users\yahoo\OneDrive\Desktop\python程式設計\記帳網站\frontend\src\views\Dashboard.vue -->
      <!-- filepath: c:\Users\yahoo\OneDrive\Desktop\python程式設計\記帳網站\frontend\src\views\Dashboard.vue -->
      <div
        class="grid grid-cols-2 grid-rows-2 gap-3 sm:grid-cols-2 sm:grid-rows-2 lg:grid-cols-3 lg:grid-rows-1 sm:gap-4 lg:gap-6 mb-6 lg:mb-10"
      >
        <!-- 總收入 -->
        <div
          class="bg-gradient-to-br from-green-100 to-green-50 p-4 sm:p-6 lg:p-8 rounded-lg sm:rounded-xl lg:rounded-2xl shadow text-center hover:scale-105 transition col-span-1 row-span-1"
        >
          <h2
            class="text-base sm:text-lg font-semibold mb-1 sm:mb-2 text-green-700 flex items-center justify-center gap-2"
          >
            <svg
              class="w-4 h-4 sm:w-5 sm:h-5 text-green-400"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path d="M12 8v4l3 3"></path>
              <circle cx="12" cy="12" r="10"></circle>
            </svg>
            總收入
          </h2>
          <p
            class="text-green-600 text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-wide"
          >
            ${{ summaryStore.totalIncome.toFixed(2) }}
          </p>
        </div>
        <!-- 總支出 -->
        <div
          class="bg-gradient-to-br from-red-100 to-red-50 p-4 sm:p-6 lg:p-8 rounded-lg sm:rounded-xl lg:rounded-2xl shadow text-center hover:scale-105 transition col-span-1 row-span-1"
        >
          <h2
            class="text-base sm:text-lg font-semibold mb-1 sm:mb-2 text-red-700 flex items-center justify-center gap-2"
          >
            <svg
              class="w-4 h-4 sm:w-5 sm:h-5 text-red-400"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path d="M12 8v4l3 3"></path>
              <circle cx="12" cy="12" r="10"></circle>
            </svg>
            總支出
          </h2>
          <p
            class="text-red-600 text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-wide"
          >
            ${{ summaryStore.totalExpense.toFixed(2) }}
          </p>
        </div>
        <!-- 總結餘 -->
        <div
          class="bg-gradient-to-br from-blue-100 to-blue-50 p-4 sm:p-6 lg:p-8 rounded-lg sm:rounded-xl lg:rounded-2xl shadow text-center hover:scale-105 transition col-span-2 row-span-1 sm:col-span-2 sm:row-span-1 lg:col-span-1 lg:row-span-1 flex flex-col justify-center"
        >
          <h2
            class="text-base sm:text-lg font-semibold mb-1 sm:mb-2 text-blue-700 flex items-center justify-center gap-2"
          >
            <svg
              class="w-4 h-4 sm:w-5 sm:h-5 text-blue-400"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path d="M12 8v4l3 3"></path>
              <circle cx="12" cy="12" r="10"></circle>
            </svg>
            總結餘
          </h2>
          <p
            :class="
              summaryStore.balance >= 0 ? 'text-blue-600' : 'text-orange-600'
            "
            class="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-wide"
          >
            ${{ summaryStore.balance.toFixed(2) }}
          </p>
        </div>
      </div>

      <!-- filepath: c:\Users\yahoo\OneDrive\Desktop\python程式設計\記帳網站\frontend\src\views\Dashboard.vue -->
      <div
        class="mb-8 p-6 bg-white rounded-2xl shadow flex flex-col gap-4 border border-blue-100 sm:flex-row sm:items-center sm:gap-6"
      >
        <h3 class="text-lg font-semibold text-gray-700 mr-2 min-w-[90px]">
          數據篩選:
        </h3>
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-2">
          <label for="trendInterval" class="text-gray-700 text-sm font-bold"
            >區間:</label
          >
          <select
            id="trendInterval"
            v-model="chartFilters.interval"
            class="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm min-w-[90px]"
          >
            <option value="day">按日</option>
            <option value="week">按週</option>
            <option value="month">按月</option>
          </select>
        </div>
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-2">
          <label for="chartStartDate" class="text-gray-700 text-sm font-bold"
            >從:</label
          >
          <input
            type="date"
            id="chartStartDate"
            v-model="chartFilters.start_date"
            class="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm min-w-[120px]"
          />
          <label for="chartEndDate" class="text-gray-700 text-sm font-bold"
            >到:</label
          >
          <input
            type="date"
            id="chartEndDate"
            v-model="chartFilters.end_date"
            class="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm min-w-[120px]"
          />
        </div>
        <div class="flex flex-row gap-2 mt-2 sm:mt-0">
          <button
            @click="loadDashboardData"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm"
          >
            搜尋
          </button>
          <button
            @click="resetChartFilters"
            class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm"
          >
            重置
          </button>
        </div>
      </div>
      <!-- 過濾器區塊
      <div
        class="mb-8 p-6 bg-white rounded-2xl shadow flex flex-wrap items-center gap-4 border border-blue-100"
      >
        <h3 class="text-lg font-semibold text-gray-700 mr-2">數據篩選:</h3>
        <div class="flex items-center space-x-2">
          <label for="trendInterval" class="text-gray-700 text-sm font-bold"
            >區間:</label
          >
          <select
            id="trendInterval"
            v-model="chartFilters.interval"
            class="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
          >
            <option value="month">按月</option>
            <option value="week">按週</option>
            <option value="day">按日</option>
          </select>
        </div>
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
              class="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm flex-grow min-w-[140px]"
            />
          </div>
          <button
            @click="loadDashboardData"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm whitespace-nowrap"
          >
            搜尋
          </button>
          <div class="w-full sm:w-auto">
            <button
              @click="resetChartFilters"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm whitespace-nowrap flex-shrink-0 mx-auto sm:mx-0"
            >
              重置日期
            </button>
          </div>
        </div>
      </div> -->

      <!-- 
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="bg-white p-6 rounded-2xl shadow-lg">
          <h2
            class="text-2xl font-bold mb-4 text-gray-700 flex items-center gap-2"
          >
            <svg
              class="w-6 h-6 text-blue-400"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path d="M3 17l6-6 4 4 8-8"></path>
            </svg>
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
                <div
                  class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4"
                >
                  <span class="text-green-600"
                    >收入: ${{ item.income.toFixed(2) }}</span
                  >
                  <span class="text-red-600"
                    >支出: ${{ item.expense.toFixed(2) }}</span
                  >
                  <span
                    :class="
                      item.balance >= 0 ? 'text-blue-600' : 'text-orange-600'
                    "
                    class="font-bold"
                  >
                    結餘: ${{ item.balance.toFixed(2) }}
                  </span>
                </div>
              </li>
            </ul>
          </div>
          <div
            v-else
            class="text-center text-gray-400 py-12 flex flex-col items-center"
          >
            <svg
              class="w-12 h-12 mb-2 text-gray-300"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 12h8"></path>
            </svg>
            沒有足夠的數據來顯示收支趨勢。
          </div>
        </div>


        <div class="bg-white p-6 rounded-2xl shadow-lg">
          <h2
            class="text-2xl font-bold mb-4 text-gray-700 flex items-center gap-2"
          >
            <svg
              class="w-6 h-6 text-red-400"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path d="M4 17h16M4 12h16M4 7h16"></path>
            </svg>
            支出類別分佈
          </h2>
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
          <div
            v-else
            class="text-center text-gray-400 py-12 flex flex-col items-center"
          >
            <svg
              class="w-12 h-12 mb-2 text-gray-300"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 12h8"></path>
            </svg>
            沒有足夠的支出數據來顯示類別分佈。
          </div>
        </div>
      </div>
    </div>
  </div>
</template> -->

      <!-- 三卡片橫向排列 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 收支趨勢 -->
        <!-- 收支趨勢區塊優化 -->
        <div class="bg-white p-6 rounded-2xl shadow-lg">
          <h2
            class="text-2xl font-bold mb-2 text-gray-700 flex items-center gap-2"
          >
            <svg
              class="w-6 h-6 text-blue-400"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path d="M3 17l6-6 4 4 8-8"></path>
            </svg>
            收支趨勢 (按{{
              chartFilters.interval === "month"
                ? "月"
                : chartFilters.interval === "week"
                ? "週"
                : "日"
            }})
          </h2>
          <div class="border-b border-blue-100 mb-4"></div>
          <div v-if="summaryStore.trendData.length > 0">
            <ul class="space-y-3">
              <li
                v-for="item in summaryStore.trendData"
                :key="item.period"
                class="flex flex-col md:flex-row md:items-center md:justify-between bg-blue-50 rounded-lg px-4 py-3 shadow-sm"
              >
                <span class="font-bold text-blue-700 text-lg w-24">{{
                  item.period
                }}</span>
                <div
                  class="flex flex-row flex-wrap items-center gap-x-4 gap-y-1 md:gap-x-6 flex-1 justify-end"
                >
                  <span class="text-green-600 font-semibold whitespace-nowrap">
                    收入: ${{ item.income.toFixed(2) }}
                  </span>
                  <span class="text-red-600 font-semibold whitespace-nowrap">
                    支出: ${{ item.expense.toFixed(2) }}
                  </span>
                  <span
                    :class="
                      item.balance >= 0 ? 'text-blue-600' : 'text-orange-600'
                    "
                    class="font-bold whitespace-nowrap"
                  >
                    結餘: ${{ item.balance.toFixed(2) }}
                  </span>
                </div>
              </li>
            </ul>
          </div>
          <div
            v-else
            class="text-center text-gray-400 py-12 flex flex-col items-center"
          >
            <svg
              class="w-12 h-12 mb-2 text-gray-300"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 12h8"></path>
            </svg>
            沒有足夠的數據來顯示收支趨勢。
          </div>
        </div>

        <!-- 收入類別分佈 -->
        <div class="bg-white p-6 rounded-2xl shadow-lg">
          <h2
            class="text-2xl font-bold mb-4 text-gray-700 flex items-center gap-2"
          >
            <svg
              class="w-6 h-6 text-green-400"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path d="M4 17h16M4 12h16M4 7h16"></path>
            </svg>
            收入類別分佈
          </h2>
          <div
            v-if="
              summaryStore.incomeCategoryBreakdown &&
              summaryStore.incomeCategoryBreakdown.length > 0
            "
          >
            <ul class="divide-y divide-gray-200">
              <li
                v-for="item in summaryStore.incomeCategoryBreakdown"
                :key="item.category_name"
                class="py-2 flex justify-between items-center"
              >
                <span class="font-semibold text-gray-800">{{
                  item.category_name
                }}</span>
                <span class="text-green-600 font-bold"
                  >${{ item.total_amount.toFixed(2) }}</span
                >
              </li>
            </ul>
          </div>
          <div
            v-else
            class="text-center text-gray-400 py-12 flex flex-col items-center"
          >
            <svg
              class="w-12 h-12 mb-2 text-gray-300"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 12h8"></path>
            </svg>
            沒有足夠的收入數據來顯示類別分佈。
          </div>
        </div>

        <!-- 支出類別分佈 -->
        <div class="bg-white p-6 rounded-2xl shadow-lg">
          <h2
            class="text-2xl font-bold mb-4 text-gray-700 flex items-center gap-2"
          >
            <svg
              class="w-6 h-6 text-red-400"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <path d="M4 17h16M4 12h16M4 7h16"></path>
            </svg>
            支出類別分佈
          </h2>
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
          <div
            v-else
            class="text-center text-gray-400 py-12 flex flex-col items-center"
          >
            <svg
              class="w-12 h-12 mb-2 text-gray-300"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              viewBox="0 0 24 24"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 12h8"></path>
            </svg>
            沒有足夠的支出數據來顯示類別分佈。
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<!-- client/src/views/Dashboard.vue (在 <script setup> 內部) -->
<script setup>
import { ref, onMounted, reactive, watch } from "vue";
import { useAuthStore } from "../stores/authStore"; // 確保這個路徑正確
import { useSummaryStore } from "../stores/summaryStore"; // 確保這個路徑正確
import LoadingSpinner from "../components/LoadingSpinner.vue";

const authStore = useAuthStore();
const summaryStore = useSummaryStore();

const chartFilters = reactive({
  interval: "month",
  start_date: "",
  end_date: "",
});

// 統一的數據載入函數
async function loadDashboardData() {
  // 在這裡獲取 groupId
  // 假設你的 authStore 儲存了當前用戶的群組 ID，例如 authStore.user.current_group_id
  // 或者你可能需要從 authStore.user.groups 陣列中取第一個群組的 ID
  const currentGroupId =
    authStore.user?.default_group_id || authStore.user?.groups?.[0]?.id; // 範例：獲取群組 ID 的邏輯

  if (!currentGroupId) {
    console.error(
      "無法獲取群組 ID，無法載入儀表板資料。請確認用戶已登入且有群組資訊。"
    );
    // 這裡可以設置一個錯誤狀態，或者引導用戶到群組選擇/創建頁面
    summaryStore.fetchError =
      "Group ID is missing. Please select or create a group.";
    return; // 終止執行
  }

  console.log(
    `Loading dashboard data for group ID: ${currentGroupId} with filters:`,
    chartFilters
  );

  try {
    // 將 currentGroupId 作為第一個參數傳遞
    await summaryStore.loadAllDashboardData(currentGroupId, chartFilters);
    console.log("Dashboard data loaded.");
  } catch (err) {
    console.error("Load all dashboard data error:", err);
    // summaryStore 內部應該已經捕獲並設置了 fetchError，這裡可以選擇進一步處理
  }
}

onMounted(async () => {
  console.log("Dashboard onMounted: Initializing dashboard data.");
  // 確保 authStore 中的用戶資訊已經載入
  // 如果 authStore.user 是異步載入的，你可能需要等待它
  // 或者在登入成功後，將 group_id 存入某個響應式變數

  // 這裡需要確保 authStore.user 已經有值
  // 如果 authStore 在初始化時會異步載入用戶資料，你可能需要等待 authStore.user 有值後再調用 loadDashboardData
  // 例如，如果 authStore 有一個 isUserLoaded 的屬性
  // watchEffect(() => {
  //   if (authStore.isUserLoaded) {
  //     loadDashboardData();
  //   }
  // });

  // 目前先假設 authStore.user 在 onMounted 時是可用的
  await loadDashboardData(); // 初始載入數據
});

const resetChartFilters = () => {
  chartFilters.start_date = "";
  chartFilters.end_date = "";
  // 這裡不自動查詢，讓使用者按「搜尋」才查詢
};
</script>
