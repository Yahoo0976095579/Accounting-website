<!-- client/src/views/Categories.vue -->
<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6">類別管理</h1>

    <!-- 新增類別按鈕 -->
    <div class="mb-6 text-right">
      <button
        @click="openAddCategoryModal"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      >
        新增類別
      </button>
    </div>

    <!-- client/src/views/Categories.vue (在 <template> 內部) -->
    <div v-if="categoryStore.isLoading" class="text-center py-8">
      <LoadingSpinner message="正在載入類別數據..." />
    </div>
    <div v-else-if="categoryStore.fetchError" class="text-center py-8">
      <p class="text-red-500 text-lg">錯誤：{{ categoryStore.fetchError }}</p>
    </div>

    <div v-else>
      <div
        v-if="categoryStore.categories.length === 0"
        class="text-center py-8 text-gray-500"
      >
        <p>尚無自定義類別。您可以點擊 "新增類別" 按鈕來添加。</p>
        <p class="mt-2 text-sm">（預設類別已自動為您創建）</p>
      </div>
      <div v-else class="bg-white shadow-md rounded-lg overflow-hidden">
        <table class="min-w-full leading-normal">
          <thead>
            <tr>
              <th
                class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                名稱
              </th>
              <th
                class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                類型
              </th>
              <th
                class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
              >
                操作
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="category in categoryStore.categories"
              :key="category.id"
              class="hover:bg-gray-50"
            >
              <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                {{ category.name }}
              </td>
              <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                <span
                  :class="{
                    'text-green-600': category.type === 'income',
                    'text-red-600': category.type === 'expense',
                  }"
                  class="capitalize"
                >
                  {{ category.type === "income" ? "收入" : "支出" }}
                </span>
              </td>
              <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                <div class="flex space-x-2">
                  <button
                    @click="openEditCategoryModal(category)"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    編輯
                  </button>
                  <button
                    @click="confirmDeleteCategory(category)"
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
    </div>

    <!-- 類別表單彈窗 (用於新增和編輯) -->
    <CategoryForm
      v-if="showCategoryModal"
      :category="currentCategory"
      @close="closeCategoryModal"
      @saved="handleCategorySaved"
    />

    <!-- 自定義確認刪除彈窗 -->
    <ConfirmationModal
      v-if="showConfirmDeleteModal"
      title="刪除類別確認"
      :message="`您確定要刪除類別「${categoryToDelete?.name}」嗎？此操作無法撤銷。`"
      confirmText="刪除"
      confirmButtonClass="bg-red-600 hover:bg-red-800 text-white"
      @confirm="handleDeleteConfirmed"
      @cancel="handleDeleteCanceled"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from "vue";
import { useCategoryStore } from "../stores/categoryStore";
import { useNotificationStore } from "../stores/notificationStore"; // 導入通知 Store
import ConfirmationModal from "../components/ConfirmationModal.vue"; // 導入確認模態框
// 我們將創建一個新的 CategoryForm 組件
import CategoryForm from "../components/CategoryForm.vue";
import LoadingSpinner from "../components/LoadingSpinner.vue"; // <-- 新增導入

const categoryStore = useCategoryStore();
const notificationStore = useNotificationStore();

// 模態框相關狀態
const showCategoryModal = ref(false);
const currentCategory = ref(null); // 用於編輯時傳遞類別數據

// 確認刪除模態框相關狀態
const showConfirmDeleteModal = ref(false);
const categoryToDelete = ref(null); // 儲存要刪除的類別物件

onMounted(() => {
  // 在組件載入時獲取類別列表
  categoryStore.fetchCategories();
});

// 打開新增類別模態框
const openAddCategoryModal = () => {
  currentCategory.value = null; // 新增時清空數據
  showCategoryModal.value = true;
};

// 打開編輯類別模態框
const openEditCategoryModal = (category) => {
  currentCategory.value = { ...category }; // 編輯時傳遞類別數據副本
  showCategoryModal.value = true;
};

// 關閉類別模態框
const closeCategoryModal = () => {
  showCategoryModal.value = false;
  currentCategory.value = null;
};

// 處理類別新增或更新成功
const handleCategorySaved = async () => {
  await categoryStore.fetchCategories(); // 重新載入類別列表
  closeCategoryModal();
};

// 打開刪除確認模態框
const confirmDeleteCategory = (category) => {
  categoryToDelete.value = category; // 儲存要刪除的類別物件
  showConfirmDeleteModal.value = true;
};

// 處理確認刪除的操作
const handleDeleteConfirmed = async () => {
  showConfirmDeleteModal.value = false; // 關閉確認模態框
  if (categoryToDelete.value && categoryToDelete.value.id) {
    const success = await categoryStore.deleteCategory(
      categoryToDelete.value.id
    );
    if (success) {
      // 通知已經在 store 中處理
    } else {
      // 錯誤通知已經在 store 中處理
    }
    categoryToDelete.value = null; // 清除
  }
};

// 處理取消刪除的操作
const handleDeleteCanceled = () => {
  showConfirmDeleteModal.value = false;
  categoryToDelete.value = null;
};
</script>
