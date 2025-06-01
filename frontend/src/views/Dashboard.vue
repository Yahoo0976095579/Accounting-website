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
        class="mb-8 p-4 sm:p-6 bg-white rounded-lg shadow-md border border-blue-100"
      >
        <h3 class="text-xl sm:text-2xl font-bold text-gray-700 mb-4">
          數據篩選
        </h3>

        <!-- 篩選器輸入組 -->
        <!-- 使用 grid 佈局，手機上至少兩列，中等螢幕三列，大螢幕更多 -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
          <!-- 區間篩選 -->
          <div>
            <label
              for="trendInterval"
              class="block text-gray-700 text-sm font-bold mb-2"
            >
              區間:
            </label>
            <select
              id="trendInterval"
              v-model="chartFilters.interval"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
            >
              <option value="day">按日</option>
              <option value="week">按週</option>
              <option value="month">按月</option>
            </select>
          </div>
          <div></div>
          <!-- 從日期 -->
          <div>
            <label
              for="chartStartDate"
              class="block text-gray-700 text-sm font-bold mb-2"
            >
              從日期:
            </label>
            <input
              type="date"
              id="chartStartDate"
              v-model="chartFilters.start_date"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
            />
          </div>

          <!-- 到日期 -->
          <div>
            <label
              for="chartEndDate"
              class="block text-gray-700 text-sm font-bold mb-2"
            >
              到日期:
            </label>
            <input
              type="date"
              id="chartEndDate"
              v-model="chartFilters.end_date"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
            />
          </div>

          <!-- 搜尋/重置按鈕 -->
          <!-- 讓按鈕組佔據底部所有可用空間，並左右均分 -->
          <div class="col-span-full flex flex-row gap-2 pt-2">
            <button
              @click="loadDashboardData"
              class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm transition duration-200 ease-in-out flex-1 md:flex-none md:w-auto md:max-w-[120px]"
            >
              搜尋
            </button>
            <button
              @click="resetChartFilters"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm transition duration-200 ease-in-out flex-1 md:flex-none md:w-auto md:max-w-[120px]"
            >
              重置
            </button>
          </div>
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

<script setup>
import { ref, onMounted, reactive, watch } from "vue";
import { useAuthStore } from "../stores/authStore";
import { useSummaryStore } from "../stores/summaryStore";
import LoadingSpinner from "../components/LoadingSpinner.vue";
// import router from '../router'; // 如果不需要重定向，可以移除此導入

const authStore = useAuthStore();
const summaryStore = useSummaryStore();

// 核心修正：selectedGroupId 始終預設為 null，表示個人模式
const selectedGroupId = ref(null);

const chartFilters = reactive({
  interval: "month",
  start_date: "",
  end_date: "",
});

let isInitialDataLoaded = false;

// 統一的數據載入函數
async function loadDashboardData() {
  console.log(
    `Loading dashboard data. Current Mode: ${
      selectedGroupId.value ? "Group" : "Personal"
    }`
  );
  console.log(`Current Group ID: ${selectedGroupId.value}`); // 如果是 null，會顯示 'Current Group ID: null'
  console.log("Filters:", chartFilters);

  // 將 selectedGroupId (可能是 null) 傳遞給 summaryStore 的 loadAllDashboardData
  try {
    // 這裡不再檢查 currentGroupId 是否存在，因為 selectedGroupId 為 null 時表示個人數據
    await summaryStore.loadAllDashboardData(
      selectedGroupId.value,
      chartFilters
    );
    console.log("Dashboard data loaded.");
  } catch (err) {
    console.error("Load all dashboard data error:", err);
    // 這裡可以根據需要顯示錯誤訊息給用戶
  }
}

onMounted(async () => {
  console.log("Dashboard onMounted: Component mounted.");
  await authStore.initializeAuth(); // 確保 authStore.user 被載入
  // selectedGroupId 預設為 null，所以 loadDashboardData 會調用個人 API
});

// 監聽 authStore.user 的變化，確保數據在用戶資訊載入後才開始載入
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser && !isInitialDataLoaded) {
      console.log("authStore.user detected, loading dashboard data...");

      // === 關鍵修正：這裡不再基於 newUser.default_group_id 或 groups 設置 selectedGroupId ===
      // 保持 selectedGroupId 初始值為 null，以確保預設顯示個人數據。
      // 如果用戶希望查看群組數據，他們需要手動通過 UI 選擇群組。

      loadDashboardData(); // 觸發數據載入
      isInitialDataLoaded = true;
    }
  },
  { immediate: true }
);

const resetChartFilters = () => {
  chartFilters.start_date = "";
  chartFilters.end_date = "";
};

// 你需要在模板中添加一個群組選擇器，讓用戶手動切換到群組模式
/*
<template>
  <div>
    <h2>儀表板</h2>
    <div class="mode-selector">
      <button @click="selectedGroupId = null; loadDashboardData();" 
              :class="{ 'active': selectedGroupId === null }">個人記帳</button>
      <select v-model="selectedGroupId" @change="loadDashboardData" v-if="authStore.user && authStore.user.groups && authStore.user.groups.length > 0">
        <option disabled value="">選擇群組記帳</option>
        <option v-for="group in authStore.user.groups" :key="group.id" :value="group.id">
          {{ group.name }}
        </option>
      </select>
      <span v-else>您沒有任何群組，請創建或加入群組。</span>
    </div>
    
    <LoadingSpinner v-if="summaryStore.isLoading" />
    <div v-else-if="summaryStore.fetchError">
      <p class="error-message">錯誤: {{ summaryStore.fetchError }}</p>
      <p v-if="selectedGroupId !== null && authStore.user && authStore.user.groups && authStore.user.groups.length === 0">
        您尚未加入任何群組。請前往群組管理頁面創建或加入群組。
      </p>
    </div>
    <div v-else-if="summaryStore.isDataReady">
      <h3>總覽</h3>
      <p>總收入: {{ summaryStore.totalIncome }}</p>
      <p>總支出: {{ summaryStore.totalExpense }}</p>
      <p>餘額: {{ summaryStore.balance }}</p>

      <h3>類別細分 (支出)</h3>
      <ul>
        <li v-for="item in summaryStore.categoryBreakdown" :key="item.category_name">
          {{ item.category_name }}: {{ item.total_amount }}
        </li>
      </ul>

      <h3>類別細分 (收入)</h3>
      <ul>
        <li v-for="item in summaryStore.incomeCategoryBreakdown" :key="item.category_name">
          {{ item.category_name }}: {{ item.total_amount }}
        </li>
      </ul>

      <h3>趨勢圖</h3>
      <p>趨勢數據：{{ summaryStore.trendData.length }} 條</p>
      <pre>{{ JSON.stringify(summaryStore.trendData, null, 2) }}</pre>
    </div>
  </div>
</template>
*/
</script>
