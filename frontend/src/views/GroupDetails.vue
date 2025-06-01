<!-- client/src/views/GroupDetails.vue -->
<template>
  <div class="container mx-auto p-4 sm:p-6 lg:p-8">
    <!-- 頂部操作區塊 -->
    <div class="flex flex-row items-center justify-between mb-6 space-x-2">
      <!-- 返回我的群組按鈕 -->
      <button
        @click="$router.back()"
        class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition duration-200 ease-in-out text-sm sm:text-base"
      >
        ← 返回我的群組
      </button>

      <!-- 刪除群組按鈕 -->
      <button
        v-if="groupStore.currentGroup?.your_role === 'admin'"
        @click="confirmDeleteGroup"
        class="bg-red-600 hover:bg-red-800 text-white font-bold py-2 px-4 rounded text-sm sm:text-base transition duration-200 ease-in-out"
      >
        刪除群組
      </button>
    </div>

    <!-- 主標題與描述 -->
    <h1 class="text-3xl sm:text-4xl font-bold text-blue-800 mb-3">
      {{ groupStore.currentGroup?.name || "群組詳情" }}
    </h1>
    <p class="text-gray-600 mb-8 text-base sm:text-lg">
      {{ groupStore.currentGroup?.description || "無描述" }}
    </p>

    <!-- 加載狀態與錯誤信息 -->
    <div
      v-if="groupStore.isLoading && !groupStore.currentGroup"
      class="text-center py-8"
    >
      <LoadingSpinner message="載入群組數據..." />
    </div>
    <div
      v-else-if="groupStore.error && !groupStore.currentGroup"
      class="text-center py-8"
    >
      <p class="text-red-500 text-lg">錯誤：{{ groupStore.error }}</p>
      <p class="text-gray-500 mt-2">
        請確認群組 ID 是否正確或您是否有權限訪問。
      </p>
    </div>
    <div v-else-if="groupStore.currentGroup">
      <!-- 群組概覽卡片 (收入/支出/結餘) -->
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-6 mb-8">
        <div class="bg-white p-4 rounded-lg shadow-md text-center col-span-1">
          <h2 class="text-base sm:text-lg font-semibold mb-1 text-gray-700">
            群組總收入
          </h2>
          <p class="text-green-600 text-xl sm:text-3xl font-bold">
            ${{ groupTransactionStore.groupSummary.total_income.toFixed(2) }}
          </p>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-md text-center col-span-1">
          <h2 class="text-base sm:text-lg font-semibold mb-1 text-gray-700">
            群組總支出
          </h2>
          <p class="text-red-600 text-xl sm:text-3xl font-bold">
            ${{ groupTransactionStore.groupSummary.total_expense.toFixed(2) }}
          </p>
        </div>
        <div
          class="bg-white p-4 rounded-lg shadow-md text-center col-span-2 sm:col-span-1"
        >
          <h2 class="text-base sm:text-lg font-semibold mb-1 text-gray-700">
            群組結餘
          </h2>
          <p
            :class="{
              'text-blue-600': groupTransactionStore.groupSummary.balance >= 0,
              'text-orange-600': groupTransactionStore.groupSummary.balance < 0,
            }"
            class="text-xl sm:text-3xl font-bold"
          >
            ${{ groupTransactionStore.groupSummary.balance.toFixed(2) }}
          </p>
        </div>
      </div>

      <!-- 群組成員卡片 -->
      <div class="bg-white p-6 rounded-lg shadow-md mb-8">
        <div
          class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4"
        >
          <h2 class="text-2xl font-bold text-gray-700 mb-3 sm:mb-0">
            群組成員
          </h2>
          <!-- 邀請成員和退出群組按鈕：手機版左右並排 -->
          <div class="flex flex-row space-x-2 w-full sm:w-auto justify-end">
            <button
              v-if="groupStore.currentGroup?.your_role === 'admin'"
              @click="openInviteMemberModal"
              class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded text-sm transition duration-200 ease-in-out flex-1 sm:flex-auto"
            >
              邀請成員
            </button>
            <button
              @click="confirmLeaveGroup"
              class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded text-sm transition duration-200 ease-in-out flex-1 sm:flex-auto"
            >
              退出群組
            </button>
          </div>
        </div>
        <div
          v-if="groupStore.currentGroup?.members.length === 0"
          class="text-gray-500 py-4 text-center"
        >
          <p>該群組尚未有成員。</p>
        </div>
        <ul v-else class="divide-y divide-gray-200">
          <li
            v-for="member in groupStore.currentGroup?.members"
            :key="member.id"
            class="py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between"
          >
            <!-- 成員名稱和角色 -->
            <div class="flex items-center mb-2 sm:mb-0 w-full sm:w-auto">
              <span
                class="font-semibold text-gray-800 text-base sm:text-lg"
                :class="{
                  'text-blue-700': member.user_id === authStore.user?.id,
                }"
              >
                {{ member.username }}
                <span
                  v-if="member.user_id === authStore.user?.id"
                  class="text-sm text-gray-500"
                  >(您)</span
                >
              </span>
              <span class="text-sm text-gray-600 capitalize ml-2"
                >({{ member.role }})</span
              >
            </div>

            <!-- 管理員操作按鈕組：手機版左右並排，桌面版也左右並排 -->
            <div
              class="flex flex-row space-x-2 ml-auto w-full sm:w-auto justify-end"
            >
              <template v-if="groupStore.currentGroup?.your_role === 'admin'">
                <!-- 賦予/撤銷管理員權限 -->
                <button
                  v-if="member.user_id !== authStore.user?.id"
                  @click="toggleMemberRole(member)"
                  :class="{
                    'bg-indigo-500 hover:bg-indigo-700':
                      member.role === 'member',
                    'bg-yellow-500 hover:bg-yellow-700':
                      member.role === 'admin',
                  }"
                  class="text-white font-bold py-1 px-3 rounded text-sm transition duration-200 ease-in-out flex-1 sm:flex-auto whitespace-nowrap"
                >
                  {{ member.role === "member" ? "設為管理員" : "撤銷管理員" }}
                </button>

                <!-- 移除成員按鈕 (不能移除自己) -->
                <button
                  v-if="member.user_id !== authStore.user?.id"
                  @click="confirmRemoveMember(member.user_id, member.username)"
                  class="bg-red-600 hover:bg-red-800 text-white font-bold py-1 px-3 rounded text-sm transition duration-200 ease-in-out flex-1 sm:flex-auto whitespace-nowrap"
                >
                  移除
                </button>
              </template>
            </div>
          </li>
        </ul>
      </div>

      <!-- 群組交易記錄 -->
      <div class="p-6 rounded-lg shadow-md mb-8 bg-white">
        <div
          class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6"
        >
          <h2 class="text-2xl font-bold text-gray-700 mb-3 sm:mb-0">
            群組交易記錄
          </h2>
        </div>

        <!-- 篩選器與搜索 -->
        <div
          class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 mb-6"
        >
          <!-- 交易類型 (不變) -->
          <div>
            <label
              for="groupFilterType"
              class="block text-gray-700 text-sm font-bold mb-2"
              >交易類型:</label
            >
            <select
              id="groupFilterType"
              v-model="groupFilters.type"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
            >
              <option value="">所有類型</option>
              <option value="income">收入</option>
              <option value="expense">支出</option>
            </select>
          </div>
          <!-- 類別 - 修正點：使用 filteredCategories -->
          <div>
            <label
              for="groupFilterCategory"
              class="block text-gray-700 text-sm font-bold mb-2"
              >類別:</label
            >
            <select
              id="groupFilterCategory"
              v-model="groupFilters.category_id"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
            >
              <option value="">所有類別</option>
              <!-- 修正點：v-for 迭代 filteredCategories -->
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
          <div>
            <label
              for="groupStartDate"
              class="block text-gray-700 text-sm font-bold mb-2"
              >從日期:</label
            >
            <input
              type="date"
              id="groupStartDate"
              v-model="groupFilters.start_date"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
            />
          </div>
          <div>
            <label
              for="groupEndDate"
              class="block text-gray-700 text-sm font-bold mb-2"
              >到日期:</label
            >
            <input
              type="date"
              id="groupEndDate"
              v-model="groupFilters.end_date"
              class="w-full shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
            />
          </div>
          <!-- 搜索 -->
          <div class="col-span-2 md:col-span-1">
            <!-- 讓搜索框在手機上獨佔兩欄，大螢幕正常 -->
            <label
              for="groupSearchTerm"
              class="block text-gray-700 text-sm font-bold mb-2"
              >搜索描述:</label
            >
            <input
              type="text"
              id="groupSearchTerm"
              v-model="groupFilters.search_term"
              placeholder="搜索描述..."
              class="w-full shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline text-sm"
            />
          </div>
          <!-- 搜尋/重置按鈕 - 優化點 -->
          <!-- 在手機上：佔滿兩欄，兩個按鈕左右均分。
               在 MD 螢幕及以上：寬度不再拉伸過長，而是適中。 -->
          <div class="col-span-full flex flex-row gap-2 pt-2">
            <button
              @click="applyGroupFilters"
              type="button"
              class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm transition duration-200 ease-in-out flex-1 md:flex-none md:w-auto md:max-w-[120px]"
            >
              搜尋
            </button>
            <button
              @click="resetGroupFilters"
              type="button"
              class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm transition duration-200 ease-in-out flex-1 md:flex-none md:w-auto md:max-w-[120px]"
            >
              重置篩選
            </button>
          </div>
        </div>

        <!-- 新增群組交易按鈕 - 優化點 -->
        <!-- 這個按鈕在手機上佔滿寬度，但在 PC 畫面時，寬度適中。 -->
        <!-- 為了讓它在大螢幕上與篩選器組對齊，我們將它放在一個新的 flex 容器中 -->
        <div class="flex justify-end mb-6">
          <!-- 新增一個 flex 容器來控制這個按鈕的對齊 -->
          <button
            @click="openAddGroupTransactionModal"
            class="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-base transition duration-200 ease-in-out md:w-auto md:max-w-[160px]"
          >
            新增群組交易
          </button>
        </div>

        <!-- 交易列表 -->
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
          <!-- 桌機版 table (md:block) -->
          <div
            class="hidden md:block bg-white rounded-lg overflow-hidden border border-gray-200"
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
                    <th class="py-3 px-5 text-left">記錄人</th>
                    <th class="py-3 px-5 text-center">操作</th>
                  </tr>
                </thead>
                <tbody class="text-gray-700 text-sm">
                  <tr
                    v-for="transaction in groupTransactionStore.groupTransactions"
                    :key="transaction.id"
                    class="border-b border-gray-200 hover:bg-gray-50"
                  >
                    <td class="py-3 px-5">{{ transaction.date }}</td>
                    <td class="py-3 px-5">
                      {{ transaction.description || "無描述" }}
                    </td>
                    <td class="py-3 px-5">{{ transaction.category_name }}</td>
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
                    <td class="py-3 px-5">
                      {{ transaction.created_by_username }}
                    </td>
                    <td class="py-3 px-5 text-center">
                      <div
                        class="flex flex-col sm:flex-row sm:space-x-2 space-y-1 sm:space-y-0 justify-center"
                      >
                        <button
                          @click="openEditGroupTransactionModal(transaction)"
                          class="text-blue-600 hover:text-blue-900 text-sm py-1 px-2 rounded-md hover:bg-blue-100 transition"
                        >
                          編輯
                        </button>
                        <button
                          @click="confirmDeleteGroupTransaction(transaction.id)"
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
              v-if="groupTransactionStore.totalGroupPages > 1"
              class="flex justify-center items-center space-x-4 py-4 bg-gray-100 rounded-b-lg border-t border-gray-200"
            >
              <button
                @click="
                  changeGroupPage(groupTransactionStore.currentGroupPage - 1)
                "
                :disabled="!groupTransactionStore.has_prev"
                class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                上一頁
              </button>
              <span class="text-gray-700 text-sm sm:text-base">
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
                class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                下一頁
              </button>
            </div>
          </div>
          <!-- 手機版卡片 (md:hidden) -->
          <div class="space-y-4 md:hidden">
            <div
              v-for="transaction in groupTransactionStore.groupTransactions"
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
                <span
                  >金額：
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
              <div
                class="text-xs text-gray-500 border-t border-gray-100 pt-2 mt-2"
              >
                記錄人：{{ transaction.created_by_username }}
              </div>
              <div class="flex justify-end space-x-3 pt-2">
                <button
                  @click="openEditGroupTransactionModal(transaction)"
                  class="text-blue-600 hover:text-blue-900 text-sm py-1 px-2 rounded-md hover:bg-blue-100 transition"
                >
                  編輯
                </button>
                <button
                  @click="confirmDeleteGroupTransaction(transaction.id)"
                  class="text-red-600 hover:text-red-900 text-sm py-1 px-2 rounded-md hover:bg-red-100 transition"
                >
                  刪除
                </button>
              </div>
            </div>
            <!-- 手機版分頁控制 (與桌機版相同，只是在 md:hidden 內) -->
            <div
              v-if="groupTransactionStore.totalGroupPages > 1"
              class="flex justify-center items-center space-x-4 py-4 bg-gray-100 rounded-b-lg border-t border-gray-200"
            >
              <button
                @click="
                  changeGroupPage(groupTransactionStore.currentGroupPage - 1)
                "
                :disabled="!groupTransactionStore.has_prev"
                class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                上一頁
              </button>
              <span class="text-gray-700 text-sm sm:text-base">
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
                class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                下一頁
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 模態框 (不變) -->
      <InviteMemberModal
        v-if="showInviteMemberModal"
        :group-id="currentGroupId"
        @close="closeInviteMemberModal"
        @invited="handleMemberInvited"
      />

      <GroupTransactionForm
        v-if="showGroupTransactionModal"
        :group-id="currentGroupId"
        :transaction="currentGroupTransaction"
        @close="closeGroupTransactionModal"
        @saved="handleGroupTransactionSaved"
      />

      <ConfirmationModal
        v-if="showConfirmDeleteGroupTransactionModal"
        title="刪除群組交易確認"
        message="您確定要刪除這筆群組交易記錄嗎？此操作無法撤銷。"
        confirmText="刪除"
        confirmButtonClass="bg-red-600 hover:bg-red-800 text-white"
        @confirm="handleDeleteGroupTransactionConfirmed"
        @cancel="handleDeleteGroupTransactionCanceled"
      />

      <ConfirmationModal
        v-if="showConfirmDeleteGroupModal"
        title="刪除群組確認"
        :message="`您確定要永久刪除此群組嗎？\n此操作無法撤銷，且群組內所有數據將被刪除。`"
        confirmText="確認刪除群組"
        confirmButtonClass="bg-red-600 hover:bg-red-800 text-white"
        @confirm="handleDeleteGroupConfirmed"
        @cancel="handleDeleteGroupCanceled"
      />

      <ConfirmationModal
        v-if="showConfirmRemoveMemberModal"
        :title="`移除成員 ${memberToRemoveUsername} 確認`"
        :message="`您確定要將 ${memberToRemoveUsername} 從此群組中移除嗎？`"
        confirmText="確認移除"
        confirmButtonClass="bg-red-600 hover:bg-red-800 text-white"
        @confirm="handleRemoveMemberConfirmed"
        @cancel="handleRemoveMemberCanceled"
      />
      <ConfirmationModal
        v-if="showConfirmLeaveGroupModal"
        title="退出群組確認"
        message="您確定要退出此群組嗎？退出後您將無法再查看或記錄此群組的收支。"
        confirmText="確認退出"
        confirmButtonClass="bg-red-600 hover:bg-red-800 text-white"
        @confirm="handleLeaveGroupConfirmed"
        @cancel="handleLeaveGroupCanceled"
      />
    </div>
  </div>
</template>

<script setup>
// === 修正點：確保從 'vue' 導入 computed ===
import { ref, onMounted, reactive, watch, computed } from "vue";
// ==========================================

import { useRoute } from "vue-router";
import { useGroupStore } from "../stores/groupStore";
import { useGroupTransactionStore } from "../stores/groupTransactionStore";
import { useCategoryStore } from "../stores/categoryStore";
import { useAuthStore } from "../stores/authStore";
import LoadingSpinner from "../components/LoadingSpinner.vue";
import InviteMemberModal from "../components/InviteMemberModal.vue";
import GroupTransactionForm from "../components/GroupTransactionForm.vue";
import ConfirmationModal from "../components/ConfirmationModal.vue";

const route = useRoute();
const groupStore = useGroupStore();
const groupTransactionStore = useGroupTransactionStore();
const categoryStore = useCategoryStore();
const authStore = useAuthStore();

const currentGroupId = ref(null);

const showInviteMemberModal = ref(false);
const showGroupTransactionModal = ref(false);
const currentGroupTransaction = ref(null);

const showConfirmDeleteGroupTransactionModal = ref(false);
const groupTransactionToDeleteId = ref(null);

const showConfirmDeleteGroupModal = ref(false);

const showConfirmRemoveMemberModal = ref(false);
const memberToRemoveId = ref(null);
const memberToRemoveUsername = ref("");

const showConfirmLeaveGroupModal = ref(false);

const groupFilters = reactive({
  type: "", // 'income', 'expense', or ''
  category_id: "",
  start_date: "",
  end_date: "",
  search_term: "",
});

// === 新增：計算屬性 filteredCategories ===
const filteredCategories = computed(() => {
  const selectedType = groupFilters.type;
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

// === 新增：監聽 groupFilters.type 的變化，並重置 category_id ===
watch(
  () => groupFilters.type,
  (newType, oldType) => {
    // 只有當類型從有值變為無值，或從無值變為有值時，才重置 category_id
    // 避免在類型篩選變更時， category_id 仍然指向一個不合法的類別
    if (newType !== oldType) {
      // 檢查當前選擇的 category_id 是否在新的 filteredCategories 中
      // 如果不在，則重置
      const currentCategoryId = groupFilters.category_id;
      if (currentCategoryId) {
        const categoryExistsInNewFilter = filteredCategories.value.some(
          (cat) => cat.id === currentCategoryId
        );
        if (!categoryExistsInNewFilter) {
          groupFilters.category_id = ""; // 重置類別選擇
        }
      }
      // 不自動觸發 applyGroupFilters，讓用戶手動點擊「搜尋」
      // applyGroupFilters(); // 如果希望自動搜尋，可以取消註釋這行
    }
  }
);

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
    router.push("/groups");
    return;
  }

  const detailsFetched = await groupStore.fetchGroupDetails(
    currentGroupId.value
  );

  if (detailsFetched) {
    await Promise.all([
      groupTransactionStore.fetchGroupSummary(currentGroupId.value),
      categoryStore.fetchCategories(),
    ]);
    applyGroupFilters();
  }
});

const resetGroupFilters = () => {
  groupFilters.type = "";
  groupFilters.category_id = "";
  groupFilters.start_date = "";
  groupFilters.end_date = "";
  groupFilters.search_term = "";
  applyGroupFilters();
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

const openInviteMemberModal = () => {
  showInviteMemberModal.value = true;
};
const closeInviteMemberModal = () => {
  showInviteMemberModal.value = false;
};
const handleMemberInvited = async () => {
  await groupStore.fetchGroupDetails(currentGroupId.value);
  closeInviteMemberModal();
};

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
  await groupTransactionStore.fetchGroupTransactions(
    currentGroupId.value,
    groupFilters,
    groupTransactionStore.currentGroupPage
  );
  await groupTransactionStore.fetchGroupSummary(currentGroupId.value);
  closeGroupTransactionModal();
};

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

const confirmDeleteGroup = () => {
  showConfirmDeleteGroupModal.value = true;
};

const handleDeleteGroupConfirmed = async () => {
  showConfirmDeleteGroupModal.value = false;
  if (currentGroupId.value) {
    await groupStore.deleteGroup(currentGroupId.value);
  }
};
const handleDeleteGroupCanceled = () => {
  showConfirmDeleteGroupModal.value = false;
};

const confirmRemoveMember = (memberId, username) => {
  memberToRemoveId.value = memberId;
  memberToRemoveUsername.value = username;
  showConfirmRemoveMemberModal.value = true;
};

const handleRemoveMemberConfirmed = async () => {
  showConfirmRemoveMemberModal.value = false;
  if (memberToRemoveId.value && currentGroupId.value) {
    await groupStore.removeMember(currentGroupId.value, memberToRemoveId.value);
    memberToRemoveId.value = null;
    memberToRemoveUsername.value = "";
  }
};
const handleRemoveMemberCanceled = () => {
  showConfirmRemoveMemberModal.value = false;
  memberToRemoveId.value = null;
  memberToRemoveUsername.value = "";
};

const toggleMemberRole = async (member) => {
  const newRole = member.role === "member" ? "admin" : "member";
  await groupStore.updateMemberRole(
    currentGroupId.value,
    member.user_id,
    newRole
  );
};

const confirmLeaveGroup = () => {
  showConfirmLeaveGroupModal.value = true;
};

const handleLeaveGroupConfirmed = async () => {
  showConfirmLeaveGroupModal.value = false;
  if (currentGroupId.value) {
    await groupStore.leaveGroup(currentGroupId.value);
  }
};

const handleLeaveGroupCanceled = () => {
  showConfirmLeaveGroupModal.value = false;
};
</script>
