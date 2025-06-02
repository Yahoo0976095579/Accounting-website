<!-- client/src/views/Transactions.vue -->
<template>
  <div class="container mx-auto p-4 sm:p-6 lg:p-8">
    <h1 class="text-3xl sm:text-4xl font-bold mb-6 text-gray-800">交易記錄</h1>

    <!-- 統計概覽卡片區 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-6">
      <div class="bg-green-100 rounded-lg p-3 sm:p-4 text-center shadow">
        <div class="text-green-700 font-bold text-base sm:text-lg">
          本月收入
        </div>
        <div class="text-xl sm:text-2xl font-extrabold text-green-600 mt-1">
          ${{ transactionStore.summary?.income?.toFixed(2) ?? "0.00" }}
        </div>
      </div>
      <div class="bg-red-100 rounded-lg p-3 sm:p-4 text-center shadow">
        <div class="text-red-700 font-bold text-base sm:text-lg">本月支出</div>
        <div class="text-xl sm:text-2xl font-extrabold text-red-600 mt-1">
          ${{ transactionStore.summary?.expense?.toFixed(2) ?? "0.00" }}
        </div>
      </div>
      <div class="bg-blue-100 rounded-lg p-3 sm:p-4 text-center shadow">
        <div class="text-blue-700 font-bold text-base sm:text-lg">本月結餘</div>
        <div
          class="text-xl sm:text-2xl font-extrabold mt-1"
          :class="
            (transactionStore.summary?.balance ?? 0) >= 0
              ? 'text-blue-600'
              : 'text-orange-600'
          "
        >
          ${{ transactionStore.summary?.balance?.toFixed(2) ?? "0.00" }}
        </div>
      </div>
      <div class="bg-gray-100 rounded-lg p-3 sm:p-4 text-center shadow">
        <div class="text-gray-700 font-bold text-base sm:text-lg">交易筆數</div>
        <div class="text-xl sm:text-2xl font-extrabold text-gray-800 mt-1">
          {{ transactionStore.totalTransactions ?? 0 }}
        </div>
      </div>
    </div>

    <!-- 篩選器與新增交易按鈕區塊 -->
    <div class="bg-white p-4 sm:p-6 rounded-lg shadow-md mb-8">
      <div
        class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6"
      >
        <h2 class="text-2xl font-bold text-gray-700 mb-3 sm:mb-0">篩選交易</h2>
      </div>

      <!-- 篩選器組件 -->
      <div
        class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 mb-6"
      >
        <!-- 交易類型篩選 -->
        <div>
          <label
            for="filterType"
            class="block text-gray-700 text-sm font-bold mb-2"
            >交易類型:</label
          >
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
        <div>
          <label
            for="filterCategory"
            class="block text-gray-700 text-sm font-bold mb-2"
            >類別:</label
          >
          <select
            id="filterCategory"
            v-model="filters.category_id"
            class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
          >
            <option value="">所有類別</option>
            <option
              v-for="category in filteredCategories"
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
            載入類別失敗: {{ categoryStore.error }}
          </p>
        </div>

        <!-- 日期範圍篩選 -->
        <div>
          <label
            for="startDate"
            class="block text-gray-700 text-sm font-bold mb-2"
            >從日期:</label
          >
          <input
            type="date"
            id="startDate"
            v-model="filters.start_date"
            class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
          />
        </div>

        <div>
          <label
            for="endDate"
            class="block text-gray-700 text-sm font-bold mb-2"
            >到日期:</label
          >
          <input
            type="date"
            id="endDate"
            v-model="filters.end_date"
            class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
          />
        </div>

        <!-- 搜索欄 -->
        <div class="col-span-2 md:col-span-1">
          <label
            for="searchTerm"
            class="block text-gray-700 text-sm font-bold mb-2"
            >搜索描述:</label
          >
          <input
            type="text"
            id="searchTerm"
            v-model="filters.search_term"
            placeholder="搜索描述..."
            class="w-full shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
          />
        </div>

        <!-- 搜尋/重置按鈕 -->
        <div class="col-span-full flex flex-row gap-2 pt-2">
          <button
            @click="applyFilters"
            type="button"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm transition duration-200 ease-in-out flex-1 md:flex-none md:w-auto md:max-w-[120px]"
          >
            搜尋
          </button>
          <button
            @click="resetFilters"
            type="button"
            class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm transition duration-200 ease-in-out flex-1 md:flex-none md:w-auto md:max-w-[120px]"
          >
            重置篩選
          </button>
        </div>
      </div>

      <!-- 新增交易按鈕 -->
      <div class="flex justify-center mb-6">
        <button
          @click="openAddTransactionModal"
          class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-base transition duration-200 ease-in-out md:w-auto md:max-w-[160px]"
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
          class="hidden md:block bg-white shadow-md rounded-lg overflow-hidden border border-gray-200"
        >
          <div class="overflow-x-auto">
            <table class="min-w-full leading-normal">
              <thead>
                <tr
                  class="bg-gray-100 text-gray-600 uppercase text-sm leading-normal"
                >
                  <th class="py-3 px-5 text-left">日期</th>
                  <th class="py-3 px-5 text-left">描述</th>
                  <th class="py-3 px-5 text-left">類別</th>
                  <th class="py-3 px-5 text-center">類型</th>
                  <th class="py-3 px-5 text-right">金額</th>
                  <th class="py-3 px-5 text-center">操作</th>
                </tr>
              </thead>
              <tbody class="text-gray-700 text-sm">
                <tr
                  v-for="transaction in transactionStore.transactions"
                  :key="transaction.id"
                  class="border-b border-gray-200 hover:bg-gray-50"
                >
                  <td class="py-3 px-5">
                    {{ transaction.date }}
                  </td>
                  <td class="py-3 px-5">
                    {{ transaction.description || "無描述" }}
                  </td>
                  <td class="py-3 px-5">
                    {{ transaction.category_name }}
                  </td>
                  <td class="py-3 px-5 text-center">
                    <span
                      :class="{
                        'text-green-600': transaction.type === 'income',
                        'text-red-600': transaction.type === 'expense',
                      }"
                      class="capitalize font-semibold"
                    >
                      {{ transaction.type === "income" ? "收入" : "支出" }}
                    </span>
                  </td>
                  <td
                    class="py-3 px-5 text-right font-bold"
                    :class="{
                      'text-green-600': transaction.type === 'income',
                      'text-red-600': transaction.type === 'expense',
                    }"
                  >
                    {{ transaction.type === "income" ? "+" : "-" }}${{
                      transaction.amount.toFixed(2)
                    }}
                  </td>
                  <td class="py-3 px-5 text-center">
                    <div
                      class="flex flex-col sm:flex-row sm:space-x-2 space-y-1 sm:space-y-0 justify-center"
                    >
                      <button
                        @click="openEditTransactionModal(transaction)"
                        class="text-blue-600 hover:text-blue-900 text-sm py-1 px-2 rounded-md hover:bg-blue-100 transition"
                      >
                        編輯
                      </button>
                      <button
                        @click="confirmDeleteTransaction(transaction.id)"
                        class="text-red-600 hover:text-red-900 text-sm py-1 px-2 rounded-md hover:bg-red-100 transition"
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
            class="flex justify-center items-center space-x-4 py-4 bg-gray-100 rounded-b-lg border-t border-gray-200"
          >
            <button
              @click="changePage(transactionStore.currentPage - 1)"
              :disabled="!transactionStore.has_prev"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              上一頁
            </button>
            <span class="text-gray-700 text-sm sm:text-base">
              第 {{ transactionStore.currentPage }} 頁 / 共
              {{ transactionStore.totalPages }} 頁 ({{
                transactionStore.totalTransactions
              }}
              筆)
            </span>
            <button
              @click="changePage(transactionStore.currentPage + 1)"
              :disabled="!transactionStore.has_next"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
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
            class="bg-white rounded-lg shadow-md p-4 flex flex-col space-y-2 border border-gray-200"
          >
            <div class="flex justify-between items-center">
              <span class="font-bold text-gray-700 text-base">{{
                transaction.date
              }}</span>
              <span
                :class="{
                  'text-green-600': transaction.type === 'income',
                  'text-red-600': transaction.type === 'expense',
                }"
                class="capitalize font-bold text-lg"
              >
                {{ transaction.type === "income" ? "收入" : "支出" }}
              </span>
            </div>
            <div class="text-gray-800 text-lg font-semibold">
              {{ transaction.description || "無描述" }}
            </div>
            <div class="flex justify-between text-sm text-gray-600">
              <span>類別：{{ transaction.category_name }}</span>
              <span>
                金額：
                <span
                  :class="{
                    'text-green-600': transaction.type === 'income',
                    'text-red-600': transaction.type === 'expense',
                  }"
                  class="font-bold"
                >
                  {{ transaction.type === "income" ? "+" : "-" }}${{
                    transaction.amount.toFixed(2)
                  }}
                </span>
              </span>
            </div>
            <div class="flex justify-end space-x-3 pt-2">
              <button
                @click="openEditTransactionModal(transaction)"
                class="text-blue-600 hover:text-blue-900 text-sm py-1 px-2 rounded-md hover:bg-blue-100 transition"
              >
                編輯
              </button>
              <button
                @click="confirmDeleteTransaction(transaction.id)"
                class="text-red-600 hover:text-red-900 text-sm py-1 px-2 rounded-md hover:bg-red-100 transition"
              >
                刪除
              </button>
            </div>
          </div>
          <!-- 分頁控制 -->
          <div
            v-if="transactionStore.totalPages > 1"
            class="flex justify-center items-center space-x-4 py-4 bg-gray-100 rounded-b-lg border-t border-gray-200"
          >
            <button
              @click="changePage(transactionStore.currentPage - 1)"
              :disabled="!transactionStore.has_prev"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              上一頁
            </button>
            <span class="text-gray-700 text-sm sm:text-base">
              第 {{ transactionStore.currentPage }} 頁 / 共
              {{ transactionStore.totalPages }} 頁 ({{
                transactionStore.totalTransactions
              }}
              筆)
            </span>
            <button
              @click="changePage(transactionStore.currentPage + 1)"
              :disabled="!transactionStore.has_next"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              下一頁
            </button>
          </div>
        </div>
      </div>
    </div>

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
import { ref, onMounted, reactive, watch, computed } from "vue"; // 確保導入 computed
import { useTransactionStore } from "../stores/transactionStore";
import { useCategoryStore } from "../stores/categoryStore";
import TransactionForm from "../components/TransactionForm.vue";
import ConfirmationModal from "../components/ConfirmationModal.vue";
import LoadingSpinner from "../components/LoadingSpinner.vue";

const transactionStore = useTransactionStore();
const categoryStore = useCategoryStore();

const filters = reactive({
  type: "", // 'income', 'expense', or '' for all
  category_id: "", // category ID, or '' for all
  start_date: "", // YYYY-MM-DD
  end_date: "", // YYYY-MM-DD
  search_term: "", // <-- 新增：搜索詞
});

const showTransactionModal = ref(false);
const currentTransaction = ref(null);

const showConfirmDeleteModal = ref(false);
const transactionToDeleteId = ref(null);

// === 新增：計算屬性 filteredCategories ===
const filteredCategories = computed(() => {
  const selectedType = filters.type;
  if (!selectedType) {
    // 如果沒有選擇交易類型，顯示所有類別
    return categoryStore.categories;
  } else {
    // 否則，只顯示與所選類型匹配的類別
    return categoryStore.categories.filter(
      (category) => category.type === selectedType
    );
  }
});

// === 新增：監聽 filters.type 的變化，並重置 category_id ===
watch(
  () => filters.type,
  (newType, oldType) => {
    if (newType !== oldType) {
      const currentCategoryId = filters.category_id;
      if (currentCategoryId) {
        const categoryExistsInNewFilter = filteredCategories.value.some(
          (cat) => cat.id === currentCategoryId
        );
        if (!categoryExistsInNewFilter) {
          filters.category_id = "";
        }
      }
    }
  }
);

const applyFilters = () => {
  console.log("Applying filters (manually triggered)");
  transactionStore.fetchTransactions(filters, 1);
  transactionStore.setCurrentFilters(filters);
  transactionStore.fetchSummary(filters);
};

onMounted(async () => {
  await categoryStore.fetchCategories();
  applyFilters();
});

const resetFilters = () => {
  filters.type = "";
  filters.category_id = "";
  filters.start_date = "";
  filters.end_date = "";
  filters.search_term = "";
  applyFilters();
};

const changePage = (newPage) => {
  if (newPage > 0 && newPage <= transactionStore.totalPages) {
    transactionStore.fetchTransactions(filters, newPage);
  }
};

const openAddTransactionModal = () => {
  currentTransaction.value = null;
  showTransactionModal.value = true;
};

const openEditTransactionModal = (transaction) => {
  currentTransaction.value = { ...transaction };
  showTransactionModal.value = true;
};

const closeTransactionModal = () => {
  showTransactionModal.value = false;
  currentTransaction.value = null;
};

const handleTransactionSaved = async () => {
  await transactionStore.fetchTransactions(
    transactionStore.currentFilters,
    transactionStore.currentPage,
    10
  );
  closeTransactionModal();
};

const confirmDeleteTransaction = (id) => {
  transactionToDeleteId.value = id;
  showConfirmDeleteModal.value = true;
};

const handleDeleteConfirmed = async () => {
  showConfirmDeleteModal.value = false;
  if (transactionToDeleteId.value) {
    await transactionStore.deleteTransaction(transactionToDeleteId.value);
    transactionToDeleteId.value = null;
  }
};

const handleDeleteCanceled = () => {
  showConfirmDeleteModal.value = false;
  transactionToDeleteId.value = null;
};
</script>
