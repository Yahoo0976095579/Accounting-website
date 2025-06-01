<!-- filepath: c:\Users\yahoo\OneDrive\Desktop\python程式設計\記帳網站\frontend\src\views\Categories.vue -->
<template>
  <div class="container mx-auto p-4">
    <h1
      class="text-3xl font-bold mb-10 text-center text-blue-700 tracking-wide"
    >
      類別管理
    </h1>
    <div
      class="flex flex-col md:flex-row md:space-x-8 space-y-8 md:space-y-0 max-w-5xl mx-auto"
    >
      <!-- 收入類別卡片 -->
      <div class="flex-1 bg-white rounded-xl shadow-lg p-6 flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-green-700">收入類別</h2>
          <button
            @click="openAddCategoryModal('income')"
            class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded shadow"
          >
            ＋ 新增收入類別
          </button>
        </div>
        <div class="flex-1">
          <div v-if="categoryStore.isLoading" class="text-center py-8">
            <LoadingSpinner message="正在載入..." />
          </div>
          <div v-else>
            <div
              v-if="incomeCategories.length === 0"
              class="text-center text-gray-400 py-8"
            >
              尚無收入類別
            </div>
            <table v-else class="min-w-full leading-normal">
              <thead>
                <tr>
                  <th
                    class="px-4 py-2 border-b bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase"
                  >
                    名稱
                  </th>
                  <th
                    class="px-4 py-2 border-b bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase"
                  >
                    操作
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="category in incomeCategories"
                  :key="category.id"
                  class="hover:bg-gray-50 transition"
                >
                  <td class="px-4 py-3 border-b">{{ category.name }}</td>
                  <td class="px-4 py-3 border-b">
                    <button
                      @click="openEditCategoryModal(category)"
                      class="text-blue-600 hover:text-blue-900 font-semibold mr-2"
                    >
                      編輯
                    </button>
                    <button
                      @click="confirmDeleteCategory(category)"
                      class="text-red-600 hover:text-red-900 font-semibold"
                    >
                      刪除
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <!-- 支出類別卡片 -->
      <div class="flex-1 bg-white rounded-xl shadow-lg p-6 flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-red-700">支出類別</h2>
          <button
            @click="openAddCategoryModal('expense')"
            class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded shadow"
          >
            ＋ 新增支出類別
          </button>
        </div>
        <div class="flex-1">
          <div v-if="categoryStore.isLoading" class="text-center py-8">
            <LoadingSpinner message="正在載入..." />
          </div>
          <div v-else>
            <div
              v-if="expenseCategories.length === 0"
              class="text-center text-gray-400 py-8"
            >
              尚無支出類別
            </div>
            <table v-else class="min-w-full leading-normal">
              <thead>
                <tr>
                  <th
                    class="px-4 py-2 border-b bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase"
                  >
                    名稱
                  </th>
                  <th
                    class="px-4 py-2 border-b bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase"
                  >
                    操作
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="category in expenseCategories"
                  :key="category.id"
                  class="hover:bg-gray-50 transition"
                >
                  <td class="px-4 py-3 border-b">{{ category.name }}</td>
                  <td class="px-4 py-3 border-b">
                    <button
                      @click="openEditCategoryModal(category)"
                      class="text-blue-600 hover:text-blue-900 font-semibold mr-2"
                    >
                      編輯
                    </button>
                    <button
                      @click="confirmDeleteCategory(category)"
                      class="text-red-600 hover:text-red-900 font-semibold"
                    >
                      刪除
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 類別表單彈窗 (用於新增和編輯) -->
    <CategoryForm
      v-if="showCategoryModal"
      :category="currentCategory"
      :defaultType="addCategoryType"
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
import { ref, computed, onMounted } from "vue";
import { useCategoryStore } from "../stores/categoryStore";
import { useNotificationStore } from "../stores/notificationStore";
import ConfirmationModal from "../components/ConfirmationModal.vue";
import CategoryForm from "../components/CategoryForm.vue";
import LoadingSpinner from "../components/LoadingSpinner.vue";

const categoryStore = useCategoryStore();
const notificationStore = useNotificationStore();

const showCategoryModal = ref(false);
const currentCategory = ref(null);
const addCategoryType = ref("income"); // 新增時預設類型

const showConfirmDeleteModal = ref(false);
const categoryToDelete = ref(null);

onMounted(() => {
  categoryStore.fetchCategories();
});

const incomeCategories = computed(() =>
  categoryStore.categories.filter((c) => c.type === "income")
);
const expenseCategories = computed(() =>
  categoryStore.categories.filter((c) => c.type === "expense")
);

const openAddCategoryModal = (type) => {
  currentCategory.value = null;
  addCategoryType.value = type; // 這個 type 值會傳遞給 CategoryForm
  showCategoryModal.value = true;
};

const openEditCategoryModal = (category) => {
  currentCategory.value = { ...category };
  addCategoryType.value = category.type;
  showCategoryModal.value = true;
};

const closeCategoryModal = () => {
  showCategoryModal.value = false;
  currentCategory.value = null;
};

const handleCategorySaved = async () => {
  await categoryStore.fetchCategories();
  closeCategoryModal();
};

const confirmDeleteCategory = (category) => {
  categoryToDelete.value = category;
  showConfirmDeleteModal.value = true;
};

const handleDeleteConfirmed = async () => {
  showConfirmDeleteModal.value = false;
  if (categoryToDelete.value && categoryToDelete.value.id) {
    await categoryStore.deleteCategory(categoryToDelete.value.id);
    categoryToDelete.value = null;
  }
};

const handleDeleteCanceled = () => {
  showConfirmDeleteModal.value = false;
  categoryToDelete.value = null;
};
</script>
