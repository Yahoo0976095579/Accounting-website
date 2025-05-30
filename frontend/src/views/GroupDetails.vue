<!-- client/src/views/GroupDetails.vue -->
<template>
  <div class="container mx-auto p-4">
    <button
      @click="$router.back()"
      class="mb-4 bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded"
    >
      ← 返回我的群組
    </button>

    <h1 class="text-3xl font-bold mb-4 text-blue-800">
      {{ groupStore.currentGroup?.name || "群組詳情" }}
    </h1>
    <p class="text-gray-600 mb-6">
      {{ groupStore.currentGroup?.description || "無描述" }}
    </p>

    <div v-if="groupStore.isLoading" class="text-center py-8">
      <LoadingSpinner message="載入群組數據..." />
    </div>
    <div
      v-else-if="
        groupStore.error || groupTransactionStore.groupTransactionError
      "
      class="text-center py-8"
    >
      <p class="text-red-500 text-lg">
        錯誤：{{
          groupStore.error || groupTransactionStore.groupTransactionError
        }}
      </p>
    </div>
    <div v-else>
      <!-- 群組概覽卡片 -->
      <!-- filepath: c:\Users\yahoo\OneDrive\Desktop\python程式設計\記帳網站\frontend\src\views\GroupDetails.vue -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-6 sm:mb-8">
        <div
          class="bg-white p-3 sm:p-6 rounded-md sm:rounded-lg shadow text-center"
        >
          <h2
            class="text-base sm:text-xl font-semibold mb-1 sm:mb-2 text-gray-700"
          >
            群組總收入
          </h2>
          <p class="text-green-600 text-2xl sm:text-4xl font-bold">
            ${{ groupTransactionStore.groupSummary.total_income.toFixed(2) }}
          </p>
        </div>
        <div
          class="bg-white p-3 sm:p-6 rounded-md sm:rounded-lg shadow text-center"
        >
          <h2
            class="text-base sm:text-xl font-semibold mb-1 sm:mb-2 text-gray-700"
          >
            群組總支出
          </h2>
          <p class="text-red-600 text-2xl sm:text-4xl font-bold">
            ${{ groupTransactionStore.groupSummary.total_expense.toFixed(2) }}
          </p>
        </div>
        <div
          class="bg-white p-3 sm:p-6 rounded-md sm:rounded-lg shadow text-center"
        >
          <h2
            class="text-base sm:text-xl font-semibold mb-1 sm:mb-2 text-gray-700"
          >
            群組結餘
          </h2>
          <p
            :class="{
              'text-blue-600': groupTransactionStore.groupSummary.balance >= 0,
              'text-orange-600': groupTransactionStore.groupSummary.balance < 0,
            }"
            class="text-2xl sm:text-4xl font-bold"
          >
            ${{ groupTransactionStore.groupSummary.balance.toFixed(2) }}
          </p>
        </div>
      </div>

      <!-- 群組成員和邀請 -->
      <div class="bg-white p-6 rounded-lg shadow-md mb-8">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold text-gray-700">群組成員</h2>
          <button
            v-if="groupStore.currentGroup?.your_role === 'admin'"
            @click="openInviteMemberModal"
            class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            邀請成員
          </button>
        </div>
        <div
          v-if="groupStore.currentGroup?.members.length === 0"
          class="text-gray-500"
        >
          <p>該群組尚未有成員。</p>
        </div>
        <ul v-else class="divide-y divide-gray-200">
          <li
            v-for="member in groupStore.currentGroup?.members"
            :key="member.id"
            class="py-2 flex justify-between items-center"
          >
            <span class="font-semibold">{{ member.username }}</span>
            <span class="text-sm text-gray-600 capitalize"
              >({{ member.role }})</span
            >
            <!-- TODO: 添加移除成員按鈕 (只有管理員且不是自己) -->
          </li>
        </ul>
      </div>

      <!-- 群組交易記錄 -->
      <div
        class="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-4 bg-white rounded-lg shadow-sm"
      >
        <!-- 左側：篩選器 -->
        <div
          class="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 flex-1"
        >
          <!-- 交易類型 -->
          <div class="w-full md:w-auto">
            <label for="groupFilterType" class="sr-only">交易類型</label>
            <select
              id="groupFilterType"
              v-model="groupFilters.type"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            >
              <option value="">所有類型</option>
              <option value="income">收入</option>
              <option value="expense">支出</option>
            </select>
          </div>
          <!-- 類別 -->
          <div class="w-full md:w-auto">
            <label for="groupFilterCategory" class="sr-only">類別</label>
            <select
              id="groupFilterCategory"
              v-model="groupFilters.category_id"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
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
            <p
              v-if="categoryStore.isLoading"
              class="text-xs text-gray-500 mt-1"
            >
              載入類別中...
            </p>
            <p
              v-if="categoryStore.fetchError"
              class="text-xs text-red-500 mt-1"
            >
              載入類別失敗: {{ categoryStore.fetchError }}
            </p>
          </div>
          <!-- 日期範圍 -->
          <div
            class="flex flex-col sm:flex-row sm:items-center gap-2 w-full md:w-auto"
          >
            <div class="flex items-center gap-2 w-full">
              <label
                for="groupStartDate"
                class="text-gray-700 text-sm font-bold whitespace-nowrap"
                >從:</label
              >
              <input
                type="date"
                id="groupStartDate"
                v-model="groupFilters.start_date"
                class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm min-w-[120px]"
              />
            </div>
            <div class="flex items-center gap-2 w-full">
              <label
                for="groupEndDate"
                class="text-gray-700 text-sm font-bold whitespace-nowrap"
                >到:</label
              >
              <input
                type="date"
                id="groupEndDate"
                v-model="groupFilters.end_date"
                class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm min-w-[120px]"
              />
            </div>
          </div>
          <!-- 搜索 -->
          <div class="w-full md:w-auto">
            <label for="groupSearchTerm" class="sr-only">搜索描述</label>
            <input
              type="text"
              id="groupSearchTerm"
              v-model="groupFilters.search_term"
              placeholder="搜索描述..."
              class="w-full shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
          </div>
          <!-- 搜尋/重置 -->
          <div class="flex gap-2 w-full md:w-auto">
            <button
              @click="applyGroupFilters"
              type="button"
              class="w-full md:w-auto bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm whitespace-nowrap"
            >
              搜尋
            </button>
            <button
              @click="resetGroupFilters"
              type="button"
              class="w-full md:w-auto bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm whitespace-nowrap"
            >
              重置篩選
            </button>
          </div>
        </div>
        <!-- 右側：新增群組交易按鈕 -->
        <div class="flex-shrink-0">
          <button
            @click="openAddGroupTransactionModal"
            class="w-full md:w-auto bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline min-w-max"
          >
            新增群組交易
          </button>
        </div>
      </div>

      <!-- 群組交易列表 -->
      <!-- 只針對交易列表顯示 loading -->
      <div
        v-if="groupTransactionStore.groupTransactionsLoading"
        class="text-center py-8"
      >
        <LoadingSpinner message="載入群組交易記錄..." />
      </div>
      <div v-else>
        <div
          v-if="groupTransactionStore.groupTransactions.length === 0"
          class="text-center py-8 text-gray-500"
        >
          <p>該群組尚未有交易記錄。</p>
          <p class="mt-2">點擊 "新增群組交易" 按鈕來添加第一筆交易吧！</p>
        </div>
        <!-- 桌機版 table -->
        <div
          class="hidden md:block bg-white shadow-md rounded-lg overflow-hidden"
        >
          <div class="overflow-x-auto">
            <table class="min-w-full leading-normal">
              <thead>
                <tr>
                  <th class="px-5 py-3 ...">日期</th>
                  <th class="px-5 py-3 ...">描述</th>
                  <th class="px-5 py-3 ...">類別</th>
                  <th class="px-5 py-3 ...">類型</th>
                  <th class="px-5 py-3 ...">金額</th>
                  <th class="px-5 py-3 ...">記錄人</th>
                  <th class="px-5 py-3 ...">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="transaction in groupTransactionStore.groupTransactions"
                  :key="transaction.id"
                  class="hover:bg-gray-50"
                >
                  <td class="px-5 py-5 text-center ...">
                    {{ transaction.date }}
                  </td>
                  <td class="px-5 py-5 text-center ...">
                    {{ transaction.description || "無描述" }}
                  </td>
                  <td class="px-5 py-5 text-center ...">
                    {{ transaction.category_name }}
                  </td>
                  <td class="px-5 py-5 text-center ...">
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
                    class="px-5 py-5 text-center ..."
                    :class="{
                      'text-green-600': transaction.type === 'income',
                      'text-red-600': transaction.type === 'expense',
                    }"
                  >
                    {{ transaction.type === "income" ? "+" : "-" }}${{
                      transaction.amount.toFixed(2)
                    }}
                  </td>
                  <td class="px-5 py-5 text-center ...">
                    {{ transaction.created_by_username }}
                  </td>
                  <td class="px-5 py-5 text-center ...">
                    <div
                      class="flex flex-col space-y-1 sm:flex-row sm:space-x-2 sm:space-y-0 justify-center"
                    >
                      <button
                        @click="openEditGroupTransactionModal(transaction)"
                        class="text-blue-600 hover:text-blue-900"
                      >
                        編輯
                      </button>
                      <button
                        @click="confirmDeleteGroupTransaction(transaction.id)"
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
            v-if="groupTransactionStore.totalGroupPages > 1"
            class="flex justify-center items-center space-x-4 py-4 bg-gray-100 rounded-b-lg"
          >
            <button
              @click="
                changeGroupPage(groupTransactionStore.currentGroupPage - 1)
              "
              :disabled="!groupTransactionStore.has_prev"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一頁
            </button>
            <span class="text-gray-700">
              第 {{ groupTransactionStore.currentGroupPage }} 頁 / 共
              {{ groupTransactionStore.totalGroupPages }} 頁 ({{
                groupTransactionStore.totalGroupTransactions
              }}
              筆)
            </span>
            <button
              @click="
                changeGroupPage(groupTransactionStore.currentGroupPage + 1)
              "
              :disabled="!groupTransactionStore.has_next"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一頁
            </button>
          </div>
        </div>
        <!-- 手機版卡片 -->
        <div class="space-y-4 md:hidden">
          <div
            v-for="transaction in groupTransactionStore.groupTransactions"
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
              <span
                >金額：
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
            <div class="text-xs text-gray-400">
              記錄人：{{ transaction.created_by_username }}
            </div>
            <div class="flex space-x-4 pt-2">
              <button
                @click="openEditGroupTransactionModal(transaction)"
                class="text-blue-600 hover:text-blue-900"
              >
                編輯
              </button>
              <button
                @click="confirmDeleteGroupTransaction(transaction.id)"
                class="text-red-600 hover:text-red-900"
              >
                刪除
              </button>
            </div>
          </div>
          <!-- 分頁控制 -->
          <div
            v-if="groupTransactionStore.totalGroupPages > 1"
            class="flex justify-center items-center space-x-4 py-4 bg-gray-100 rounded-b-lg"
          >
            <button
              @click="
                changeGroupPage(groupTransactionStore.currentGroupPage - 1)
              "
              :disabled="!groupTransactionStore.has_prev"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一頁
            </button>
            <span class="text-gray-700">
              第 {{ groupTransactionStore.currentGroupPage }} 頁 / 共
              {{ groupTransactionStore.totalGroupPages }} 頁 ({{
                groupTransactionStore.totalGroupTransactions
              }}
              筆)
            </span>
            <button
              @click="
                changeGroupPage(groupTransactionStore.currentGroupPage + 1)
              "
              :disabled="!groupTransactionStore.has_next"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一頁
            </button>
          </div>
        </div>
      </div>

      <!-- 邀請成員模態框 -->
      <InviteMemberModal
        v-if="showInviteMemberModal"
        :group-id="currentGroupId"
        @close="closeInviteMemberModal"
        @invited="handleMemberInvited"
      />

      <!-- 群組交易表單模態框 -->
      <GroupTransactionForm
        v-if="showGroupTransactionModal"
        :group-id="currentGroupId"
        :transaction="currentGroupTransaction"
        @close="closeGroupTransactionModal"
        @saved="handleGroupTransactionSaved"
      />

      <!-- 確認刪除群組交易模態框 -->
      <ConfirmationModal
        v-if="showConfirmDeleteGroupTransactionModal"
        title="刪除群組交易確認"
        message="您確定要刪除這筆群組交易記錄嗎？此操作無法撤銷。"
        confirmText="刪除"
        confirmButtonClass="bg-red-600 hover:bg-red-800 text-white"
        @confirm="handleDeleteGroupTransactionConfirmed"
        @cancel="handleDeleteGroupTransactionCanceled"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from "vue";
import { useRoute } from "vue-router"; // 引入 useRoute
import { useGroupStore } from "../stores/groupStore";
import { useGroupTransactionStore } from "../stores/groupTransactionStore"; // 新增
import { useCategoryStore } from "../stores/categoryStore"; // 新增
import LoadingSpinner from "../components/LoadingSpinner.vue";
import InviteMemberModal from "../components/InviteMemberModal.vue"; // 即將創建
import GroupTransactionForm from "../components/GroupTransactionForm.vue"; // 即將創建
import ConfirmationModal from "../components/ConfirmationModal.vue"; // 引入確認模態框

const route = useRoute(); // 獲取路由實例
const groupStore = useGroupStore();
const groupTransactionStore = useGroupTransactionStore(); // 實例化
const categoryStore = useCategoryStore(); // 實例化

const currentGroupId = ref(null); // 當前群組的ID

// 模態框狀態
const showInviteMemberModal = ref(false);
const showGroupTransactionModal = ref(false);
const currentGroupTransaction = ref(null); // 用於編輯群組交易

// 確認刪除模態框狀態
const showConfirmDeleteGroupTransactionModal = ref(false);
const groupTransactionToDeleteId = ref(null);

// 群組交易篩選狀態
const groupFilters = reactive({
  type: "",
  category_id: "",
  start_date: "",
  end_date: "",
  search_term: "",
});

// applyGroupFilters 函數現在只會在點擊「搜尋」按鈕時調用
const applyGroupFilters = () => {
  console.log("Applying group filters (manually triggered)");
  groupTransactionStore.fetchGroupTransactions(
    currentGroupId.value,
    groupFilters,
    1
  );
  groupTransactionStore.currentGroupFilters = groupFilters;
};

onMounted(async () => {
  currentGroupId.value = parseInt(route.params.id);
  if (isNaN(currentGroupId.value)) {
    console.error("無效的群組ID");
    return;
  }

  // 同時獲取群組詳情、群組摘要和群組交易
  await Promise.all([
    groupStore.fetchGroupDetails(currentGroupId.value),
    groupTransactionStore.fetchGroupSummary(currentGroupId.value),
    // 初始載入群組交易，這裡也調用 applyGroupFilters
    // 這將確保在組件載入時就執行一次初始搜尋
    // groupTransactionStore.fetchGroupTransactions(currentGroupId.value, groupFilters, 1)
  ]);
  await categoryStore.fetchCategories();
  applyGroupFilters(); // 載入時應用初始篩選 (即無篩選)
});
// 重置篩選條件
const resetGroupFilters = () => {
  groupFilters.type = "";
  groupFilters.category_id = "";
  groupFilters.start_date = "";
  groupFilters.end_date = "";
  groupFilters.search_term = "";
  applyGroupFilters(); // 重置後自動應用篩選
};

const changeGroupPage = (newPage) => {
  if (newPage > 0 && newPage <= groupTransactionStore.totalGroupPages) {
    groupTransactionStore.fetchGroupTransactions(
      currentGroupId.value,
      groupFilters,
      newPage
    );
  }
};

// 邀請成員模態框操作
const openInviteMemberModal = () => {
  showInviteMemberModal.value = true;
};
const closeInviteMemberModal = () => {
  showInviteMemberModal.value = false;
};
const handleMemberInvited = async () => {
  await groupStore.fetchGroupDetails(currentGroupId.value); // 邀請後刷新成員列表
  closeInviteMemberModal();
};

// 群組交易模態框操作
const openAddGroupTransactionModal = () => {
  currentGroupTransaction.value = null;
  showGroupTransactionModal.value = true;
};
const openEditGroupTransactionModal = (transaction) => {
  currentGroupTransaction.value = { ...transaction };
  showGroupTransactionModal.value = true;
};
const closeGroupTransactionModal = () => {
  showGroupTransactionModal.value = false;
  currentGroupTransaction.value = null;
};
const handleGroupTransactionSaved = async () => {
  // 保存後刷新交易列表和群組摘要
  await groupTransactionStore.fetchGroupTransactions(
    currentGroupId.value,
    groupFilters,
    groupTransactionStore.currentGroupPage
  );
  await groupTransactionStore.fetchGroupSummary(currentGroupId.value);
  closeGroupTransactionModal();
};

// 刪除群組交易確認模態框操作
const confirmDeleteGroupTransaction = (id) => {
  groupTransactionToDeleteId.value = id;
  showConfirmDeleteGroupTransactionModal.value = true;
};
const handleDeleteGroupTransactionConfirmed = async () => {
  showConfirmDeleteGroupTransactionModal.value = false;
  if (groupTransactionToDeleteId.value) {
    await groupTransactionStore.deleteGroupTransaction(
      currentGroupId.value,
      groupTransactionToDeleteId.value
    );
    // 刪除後刷新交易列表和群組摘要
    await groupTransactionStore.fetchGroupTransactions(
      currentGroupId.value,
      groupFilters,
      groupTransactionStore.currentGroupPage
    );
    await groupTransactionStore.fetchGroupSummary(currentGroupId.value);
    groupTransactionToDeleteId.value = null;
  }
};
const handleDeleteGroupTransactionCanceled = () => {
  showConfirmDeleteGroupTransactionModal.value = false;
  groupTransactionToDeleteId.value = null;
};
</script>
