<!-- client/src/components/TransactionForm.vue -->
<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50"
  >
    <div
      class="relative p-8 bg-white w-full max-w-md mx-auto rounded-lg shadow-xl"
      @click.stop
    >
      <h2 class="text-2xl font-bold mb-6 text-center">
        {{ isEditMode ? "編輯交易" : "新增交易" }}
      </h2>

      <form @submit.prevent="saveTransaction">
        <div class="mb-4">
          <label for="amount" class="block text-gray-700 text-sm font-bold mb-2"
            >金額:</label
          >
          <input
            type="number"
            id="amount"
            v-model.number="form.amount"
            step="0.01"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2"
            >類型:</label
          >
          <div class="mt-2">
            <label class="inline-flex items-center mr-4">
              <input
                type="radio"
                v-model="form.type"
                value="income"
                class="form-radio text-green-600"
              />
              <span class="ml-2 text-green-600 font-semibold">收入</span>
            </label>
            <label class="inline-flex items-center">
              <input
                type="radio"
                v-model="form.type"
                value="expense"
                class="form-radio text-red-600"
              />
              <span class="ml-2 text-red-600 font-semibold">支出</span>
            </label>
          </div>
        </div>

        <div class="mb-4">
          <label
            for="category"
            class="block text-gray-700 text-sm font-bold mb-2"
            >類別:</label
          >
          <select
            id="category"
            v-model="form.category_id"
            class="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          >
            <option value="" disabled>請選擇類別</option>
            <option
              v-for="category in filteredCategories"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
          <p v-if="categoryStore.isLoading" class="text-xs text-gray-500 mt-1">
            載入類別中...
          </p>
          <p v-if="categoryStore.error" class="text-xs text-red-500 mt-1">
            載入類別失敗: {{ categoryStore.error }}
          </p>
        </div>

        <div class="mb-4">
          <label
            for="description"
            class="block text-gray-700 text-sm font-bold mb-2"
            >描述 (可選):</label
          >
          <input
            type="text"
            id="description"
            v-model="form.description"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>

        <div class="mb-6">
          <label for="date" class="block text-gray-700 text-sm font-bold mb-2"
            >日期:</label
          >
          <input
            type="date"
            id="date"
            v-model="form.date"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        <p
          v-if="transactionStore.error"
          class="text-red-500 text-xs italic mb-4"
        >
          {{ transactionStore.error }}
        </p>

        <div class="flex items-center justify-center space-x-4">
          <button
            type="submit"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            :disabled="transactionStore.isLoading || categoryStore.isLoading"
          >
            {{ transactionStore.isLoading ? "儲存中..." : "儲存" }}
          </button>
          <button
            type="button"
            @click="emit('close')"
            class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            取消
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from "vue";
import { useTransactionStore } from "../stores/transactionStore";
import { useCategoryStore } from "../stores/categoryStore";

const props = defineProps({
  transaction: {
    type: Object,
    default: null, // 如果為空表示新增，不為空表示編輯
  },
});

const emit = defineEmits(["close", "saved"]);

const transactionStore = useTransactionStore();
const categoryStore = useCategoryStore();

const isEditMode = computed(() => !!props.transaction);

// 表單數據
const form = reactive({
  amount: 0,
  type: "expense", // 預設支出
  category_id: "", // 預設空
  description: "",
  date: new Date().toISOString().slice(0, 10), // 預設今天日期 YYYY-MM-DD
});

// 根據交易類型篩選類別
const filteredCategories = computed(() => {
  // 確保 categoryStore.categories 已經載入，並且 form.type 有值
  if (!categoryStore.categories || !form.type) {
    return [];
  }
  return categoryStore.categories.filter((cat) => cat.type === form.type);
});

// 監聽 props.transaction 的變化來填充表單（用於編輯模式）
watch(
  () => props.transaction,
  (newVal) => {
    if (newVal) {
      form.amount = newVal.amount;
      form.type = newVal.type;
      form.category_id = newVal.category_id;
      form.description = newVal.description;
      form.date = newVal.date; // 日期格式已經是 YYYY-MM-DD
    } else {
      // 重置表單為預設值 (新增模式)
      form.amount = 0;
      form.type = "expense";
      form.category_id = "";
      form.description = "";
      form.date = new Date().toISOString().slice(0, 10);
    }
  },
  { immediate: true }
); // immediate: true 使得組件首次載入時也能觸發 watch

// 在組件掛載時獲取類別列表
onMounted(() => {
  if (categoryStore.categories.length === 0) {
    categoryStore.fetchCategories();
  }
});

const saveTransaction = async () => {
  let success = false;
  const payload = { ...form }; // 創建副本防止修改 form 響應式對象

  if (isEditMode.value) {
    success = await transactionStore.updateTransaction(
      props.transaction.id,
      payload
    );
  } else {
    success = await transactionStore.addTransaction(payload);
  }

  if (success) {
    emit("saved"); // 通知父組件保存成功
  } else {
    // 錯誤訊息會由 transactionStore 顯示，這裡不需要額外處理
  }
};
</script>

<style scoped>
/* 半透明背景和彈窗位置 */
.fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
