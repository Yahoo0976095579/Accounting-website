<!-- client/src/views/Transactions.vue -->
<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6">交易記錄</h1>
    <!-- 統計概覽卡片區 -->
    <!-- filepath: c:\Users\yahoo\OneDrive\Desktop\python程式設計\記帳網站\frontend\src\views\Transactions.vue -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4 mb-4 md:mb-6">
      <div
        class="bg-green-100 rounded-lg md:rounded-xl p-2 md:p-4 text-center shadow"
      >
        <div class="text-green-700 font-bold text-base md:text-lg">
          本月收入
        </div>
        <div
          class="text-lg md:text-2xl font-extrabold text-green-600 mt-0.5 md:mt-1"
        >
          ${{ transactionStore.summary?.income?.toFixed(2) ?? "0.00" }}
        </div>
      </div>
      <div
        class="bg-red-100 rounded-lg md:rounded-xl p-2 md:p-4 text-center shadow"
      >
        <div class="text-red-700 font-bold text-base md:text-lg">本月支出</div>
        <div
          class="text-lg md:text-2xl font-extrabold text-red-600 mt-0.5 md:mt-1"
        >
          ${{ transactionStore.summary?.expense?.toFixed(2) ?? "0.00" }}
        </div>
      </div>
      <div
        class="bg-blue-100 rounded-lg md:rounded-xl p-2 md:p-4 text-center shadow"
      >
        <div class="text-blue-700 font-bold text-base md:text-lg">本月結餘</div>
        <div
          class="text-lg md:text-2xl font-extrabold mt-0.5 md:mt-1"
          :class="
            (transactionStore.summary?.balance ?? 0) >= 0
              ? 'text-blue-600'
              : 'text-orange-600'
          "
        >
          ${{ transactionStore.summary?.balance?.toFixed(2) ?? "0.00" }}
        </div>
      </div>
      <div
        class="bg-gray-100 rounded-lg md:rounded-xl p-2 md:p-4 text-center shadow"
      >
        <div class="text-gray-700 font-bold text-base md:text-lg">交易筆數</div>
        <div
          class="text-lg md:text-2xl font-extrabold text-gray-800 mt-0.5 md:mt-1"
        >
          {{ transactionStore.totalTransactions ?? 0 }}
        </div>
      </div>
    </div>
    <!-- filepath: c:\Users\yahoo\OneDrive\Desktop\python程式設計\記帳網站\frontend\src\views\Transactions.vue -->
    <div
      class="mb-6 flex flex-col gap-3 p-2 bg-white rounded-lg shadow-sm md:flex-row md:items-center md:justify-between md:gap-4 md:p-4"
    >
      <!-- 左側：篩選器 -->
      <div
        class="flex flex-col gap-2 w-full md:flex-row md:items-center md:gap-4 md:flex-1"
      >
        <!-- 交易類型篩選 -->
        <div class="w-full md:w-auto">
          <select
            id="filterType"
            v-model="filters.type"
            class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
          >
            <option value="">所有類型</option>
            <option value="income">收入</option>
            <option value="expense">支出</option>
          </select>
        </div>
        <!-- 類別篩選 -->
        <div class="w-full md:w-auto">
          <select
            id="filterCategory"
            v-model="filters.category_id"
            class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
          >
            <option value="">所有類別</option>
            <option
              v-for="category in categoryStore.categories"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }} ({{
                category.type === "income" ? "收入" : "支出"
              }})
            </option>
          </select>
          <p v-if="categoryStore.isLoading" class="text-xs text-gray-500 mt-1">
            載入類別中...
          </p>
          <p v-if="categoryStore.error" class="text-xs text-red-500 mt-1">
            載入類別失敗
          </p>
        </div>
        <!-- 日期範圍篩選 -->
        <div
          class="flex flex-col gap-2 w-full sm:flex-row sm:items-center md:w-auto"
        >
          <div class="flex items-center gap-2 w-full">
            <label
              for="startDate"
              class="text-gray-700 text-xs font-bold whitespace-nowrap"
              >從:</label
            >
            <input
              type="date"
              id="startDate"
              v-model="filters.start_date"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-xs min-w-[100px]"
            />
          </div>
          <div class="flex items-center gap-2 w-full">
            <label
              for="endDate"
              class="text-gray-700 text-xs font-bold whitespace-nowrap"
              >到:</label
            >
            <input
              type="date"
              id="endDate"
              v-model="filters.end_date"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-xs min-w-[100px]"
            />
          </div>
        </div>
        <!-- 搜索欄 -->
        <div class="w-full md:w-auto">
          <input
            type="text"
            id="searchTerm"
            v-model="filters.search_term"
            placeholder="搜索描述..."
            class="w-full shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
          />
        </div>
        <!-- 搜尋/重置 -->
        <div class="flex gap-2 w-full md:w-auto">
          <button
            @click="applyFilters"
            type="button"
            class="w-full md:w-auto bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm whitespace-nowrap"
          >
            搜尋
          </button>
          <button
            @click="resetFilters"
            type="button"
            class="w-full md:w-auto bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm whitespace-nowrap"
          >
            重置篩選
          </button>
        </div>
      </div>
      <!-- 右側：新增交易按鈕 -->
      <div class="flex-shrink-0 w-full md:w-auto">
        <button
          @click="openAddTransactionModal"
          class="w-full md:w-auto bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline min-w-max"
        >
          新增交易
        </button>
      </div>
    </div>

    <div>
      <div v-if="transactionStore.isLoading" class="text-center py-8">
        <LoadingSpinner message="正在載入交易記錄..." />
      </div>
      <div v-else-if="transactionStore.error" class="text-center py-8">
        <p class="text-red-500 text-lg">錯誤：{{ transactionStore.error }}</p>
      </div>
      <div v-else>
        <div
          v-if="transactionStore.transactions.length === 0"
          class="text-center py-8 text-gray-500"
        >
          <p>尚無交易記錄。</p>
          <p class="mt-2">點擊 "新增交易" 按鈕來添加第一筆交易吧！</p>
        </div>
        <!-- 桌機版 table -->
        <div
          class="hidden md:block bg-white shadow-md rounded-lg overflow-hidden"
        >
          <div class="overflow-x-auto">
            <table class="min-w-full leading-normal">
              <!-- filepath: c:\Users\yahoo\OneDrive\Desktop\python程式設計\記帳網站\frontend\src\views\Transactions.vue -->
              <thead>
                <tr>
                  <th
                    class="px-5 py-3 border-b-2 border-blue-300 bg-blue-50 text-center text-lg font-bold text-blue-700 uppercase tracking-wider"
                  >
                    日期
                  </th>
                  <th
                    class="px-5 py-3 border-b-2 border-blue-300 bg-blue-50 text-center text-lg font-bold text-blue-700 uppercase tracking-wider"
                  >
                    描述
                  </th>
                  <th
                    class="px-5 py-3 border-b-2 border-blue-300 bg-blue-50 text-center text-lg font-bold text-blue-700 uppercase tracking-wider"
                  >
                    類別
                  </th>
                  <th
                    class="px-5 py-3 border-b-2 border-blue-300 bg-blue-50 text-center text-lg font-bold text-blue-700 uppercase tracking-wider"
                  >
                    類型
                  </th>
                  <th
                    class="px-5 py-3 border-b-2 border-blue-300 bg-blue-50 text-center text-lg font-bold text-blue-700 uppercase tracking-wider"
                  >
                    金額
                  </th>
                  <th
                    class="px-5 py-3 border-b-2 border-blue-300 bg-blue-50 text-center text-lg font-bold text-blue-700 uppercase tracking-wider"
                  >
                    操作
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="transaction in transactionStore.transactions"
                  :key="transaction.id"
                  class="hover:bg-gray-50"
                >
                  <td
                    class="px-5 py-5 border-b border-gray-200 bg-white text-sm text-center"
                  >
                    {{ transaction.date }}
                  </td>
                  <td
                    class="px-5 py-5 border-b border-gray-200 bg-white text-sm text-center"
                  >
                    {{ transaction.description || "無描述" }}
                  </td>
                  <td
                    class="px-5 py-5 border-b border-gray-200 bg-white text-sm text-center"
                  >
                    {{ transaction.category_name }}
                  </td>
                  <td
                    class="px-5 py-5 border-b border-gray-200 bg-white text-sm text-center"
                  >
                    <span
                      :class="{
                        'text-green-600': transaction.type === 'income',
                        'text-red-600': transaction.type === 'expense',
                      }"
                      class="capitalize"
                    >
                      {{ transaction.type === "income" ? "收入" : "支出" }}
                    </span>
                  </td>
                  <td
                    class="px-5 py-5 border-b border-gray-200 bg-white text-sm text-center"
                    :class="{
                      'text-green-600': transaction.type === 'income',
                      'text-red-600': transaction.type === 'expense',
                    }"
                  >
                    {{ transaction.type === "income" ? "+" : "-" }}${{
                      transaction.amount.toFixed(2)
                    }}
                  </td>
                  <td
                    class="px-5 py-5 border-b border-gray-200 bg-white text-sm text-center"
                  >
                    <div
                      class="flex flex-col items-center space-y-1 sm:flex-row sm:space-x-2 sm:space-y-0 justify-center"
                    >
                      <button
                        @click="openEditTransactionModal(transaction)"
                        class="text-blue-600 hover:text-blue-900"
                      >
                        編輯
                      </button>
                      <button
                        @click="confirmDeleteTransaction(transaction.id)"
                        class="text-red-600 hover:text-red-900"
                      >
                        刪除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- 分頁控制 -->
          <div
            v-if="transactionStore.totalPages > 1"
            class="flex justify-center items-center space-x-4 py-4 bg-gray-100 rounded-b-lg"
          >
            <button
              @click="changePage(transactionStore.currentPage - 1)"
              :disabled="!transactionStore.has_prev"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一頁
            </button>
            <span class="text-gray-700">
              第 {{ transactionStore.currentPage }} 頁 / 共
              {{ transactionStore.totalPages }} 頁 ({{
                transactionStore.totalTransactions
              }}
              筆)
            </span>
            <button
              @click="changePage(transactionStore.currentPage + 1)"
              :disabled="!transactionStore.has_next"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一頁
            </button>
          </div>
        </div>
        <!-- 手機版卡片 -->
        <div class="space-y-4 md:hidden">
          <div
            v-for="transaction in transactionStore.transactions"
            :key="transaction.id"
            class="bg-white rounded-lg shadow p-4 flex flex-col space-y-2"
          >
            <div class="flex justify-between">
              <span class="font-bold text-gray-700">{{
                transaction.date
              }}</span>
              <span
                :class="{
                  'text-green-600': transaction.type === 'income',
                  'text-red-600': transaction.type === 'expense',
                }"
                class="capitalize font-bold"
              >
                {{ transaction.type === "income" ? "收入" : "支出" }}
              </span>
            </div>
            <div class="text-gray-600">
              {{ transaction.description || "無描述" }}
            </div>
            <div class="flex justify-between text-sm text-gray-500">
              <span>類別：{{ transaction.category_name }}</span>
              <span>
                金額：
                <span
                  :class="{
                    'text-green-600': transaction.type === 'income',
                    'text-red-600': transaction.type === 'expense',
                  }"
                >
                  {{ transaction.type === "income" ? "+" : "-" }}${{
                    transaction.amount.toFixed(2)
                  }}
                </span>
              </span>
            </div>
            <div class="flex space-x-4 pt-2">
              <button
                @click="openEditTransactionModal(transaction)"
                class="text-blue-600 hover:text-blue-900"
              >
                編輯
              </button>
              <button
                @click="confirmDeleteTransaction(transaction.id)"
                class="text-red-600 hover:text-red-900"
              >
                刪除
              </button>
            </div>
          </div>
          <!-- 分頁控制 -->
          <div
            v-if="transactionStore.totalPages > 1"
            class="flex justify-center items-center space-x-4 py-4 bg-gray-100 rounded-b-lg"
          >
            <button
              @click="changePage(transactionStore.currentPage - 1)"
              :disabled="!transactionStore.has_prev"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一頁
            </button>
            <span class="text-gray-700">
              第 {{ transactionStore.currentPage }} 頁 / 共
              {{ transactionStore.totalPages }} 頁 ({{
                transactionStore.totalTransactions
              }}
              筆)
            </span>
            <button
              @click="changePage(transactionStore.currentPage + 1)"
              :disabled="!transactionStore.has_next"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一頁
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 交易表單彈窗 (待創建組件) -->
    <!-- 交易表單彈窗 -->
    <!-- 交易表單彈窗 -->
    <TransactionForm
      v-if="showTransactionModal"
      :transaction="currentTransaction"
      @close="closeTransactionModal"
      @saved="handleTransactionSaved"
    />

    <!-- 自定義確認刪除彈窗 -->
    <ConfirmationModal
      v-if="showConfirmDeleteModal"
      title="刪除確認"
      message="您確定要刪除這筆交易記錄嗎？此操作無法撤銷。"
      confirmText="刪除"
      confirmButtonClass="bg-red-600 hover:bg-red-800 text-white"
      @confirm="handleDeleteConfirmed"
      @cancel="handleDeleteCanceled"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from "vue"; // 新增 reactive 和 watch
import { useTransactionStore } from "../stores/transactionStore";
import { useCategoryStore } from "../stores/categoryStore";
import TransactionForm from "../components/TransactionForm.vue";
import ConfirmationModal from "../components/ConfirmationModal.vue"; // 新增：導入
import LoadingSpinner from "../components/LoadingSpinner.vue"; // <-- 新增導入

const transactionStore = useTransactionStore();
const categoryStore = useCategoryStore();

// 篩選狀態
const filters = reactive({
  type: "", // 'income', 'expense', or '' for all
  category_id: "", // category ID, or '' for all
  start_date: "", // YYYY-MM-DD
  end_date: "", // YYYY-MM-DD
  search_term: "", // <-- 新增：搜索詞
});

// 模態框相關狀態 (後續 TransactionForm 組件會用到)
const showTransactionModal = ref(false);
const currentTransaction = ref(null); // 用於編輯時傳遞交易數據

// 新增：確認模態框相關狀態
const showConfirmDeleteModal = ref(false);
const transactionToDeleteId = ref(null); // 儲存要刪除的交易ID

// applyFilters 函數現在只會在點擊「搜尋」按鈕時調用
const applyFilters = () => {
  console.log("Applying filters (manually triggered)");
  transactionStore.fetchTransactions(filters, 1); // 應用篩選，回到第一頁
  transactionStore.setCurrentFilters(filters); // 儲存當前篩選條件到 Store
  transactionStore.fetchSummary(filters);
};

// 在組件載入時，先獲取類別，然後再獲取交易（因為交易篩選可能需要類別數據）
onMounted(async () => {
  await categoryStore.fetchCategories();
  // 在這裡調用一次 applyFilters，確保初始頁面載入時有數據
  applyFilters(); // 載入時應用初始篩選
});

// 重置篩選條件
const resetFilters = () => {
  filters.type = "";
  filters.category_id = "";
  filters.start_date = "";
  filters.end_date = "";
  filters.search_term = "";
  applyFilters(); // 重置後自動應用篩選
};

// 處理分頁
const changePage = (newPage) => {
  if (newPage > 0 && newPage <= transactionStore.totalPages) {
    transactionStore.fetchTransactions(filters, newPage);
  }
};

const openAddTransactionModal = () => {
  currentTransaction.value = null; // 新增時清空數據
  showTransactionModal.value = true;
};

const openEditTransactionModal = (transaction) => {
  currentTransaction.value = { ...transaction }; // 編輯時傳遞交易數據副本
  showTransactionModal.value = true;
};

const closeTransactionModal = () => {
  showTransactionModal.value = false;
  currentTransaction.value = null;
};

const handleTransactionSaved = async () => {
  // 只刷新交易列表，不刷新整頁
  await transactionStore.fetchTransactions(
    transactionStore.currentFilters,
    transactionStore.currentPage,
    10
  );
  closeTransactionModal();
};

const confirmDeleteTransaction = (id) => {
  transactionToDeleteId.value = id; // 儲存要刪除的ID
  showConfirmDeleteModal.value = true; // 顯示確認模態框
};

// 新增：處理確認刪除的操作
const handleDeleteConfirmed = async () => {
  showConfirmDeleteModal.value = false; // 關閉確認模態框
  if (transactionToDeleteId.value) {
    await transactionStore.deleteTransaction(transactionToDeleteId.value);
    transactionToDeleteId.value = null; // 清除 ID
  }
};

// 新增：處理取消刪除的操作
const handleDeleteCanceled = () => {
  showConfirmDeleteModal.value = false;
  transactionToDeleteId.value = null;
};
</script>
