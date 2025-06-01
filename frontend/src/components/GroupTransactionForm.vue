<!-- client/src/components/GroupTransactionForm.vue -->
<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50"
  >
    <div
      class="relative p-8 bg-white w-full max-w-md mx-auto rounded-lg shadow-xl"
      @click.stop
    >
      <h2 class="text-2xl font-bold mb-6 text-center">
        {{ isEditMode ? "編輯群組交易" : "新增群組交易" }}
      </h2>

      <form @submit.prevent="saveGroupTransaction">
        <div class="mb-4">
          <label
            for="groupAmount"
            class="block text-gray-700 text-sm font-bold mb-2"
            >金額:</label
          >
          <input
            type="number"
            id="groupAmount"
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
            for="groupCategory"
            class="block text-gray-700 text-sm font-bold mb-2"
            >類別:</label
          >
          <select
            id="groupCategory"
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
          <p v-if="categoryStore.fetchError" class="text-xs text-red-500 mt-1">
            載入類別失敗: {{ categoryStore.fetchError }}
          </p>
        </div>

        <div class="mb-4">
          <label
            for="groupDescription"
            class="block text-gray-700 text-sm font-bold mb-2"
            >描述 (可選):</label
          >
          <input
            type="text"
            id="groupDescription"
            v-model="form.description"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>

        <div class="mb-6">
          <label
            for="groupDate"
            class="block text-gray-700 text-sm font-bold mb-2"
            >日期:</label
          >
          <input
            type="date"
            id="groupDate"
            v-model="form.date"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        <p
          v-if="groupTransactionError"
          class="text-red-500 text-xs italic mb-4 text-center"
        >
          {{ groupTransactionError }}
        </p>

        <div class="flex items-center justify-center space-x-4">
          <button
            type="submit"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            :disabled="
              groupTransactionStore.groupTransactionsLoading ||
              categoryStore.isLoading
            "
          >
            {{
              groupTransactionStore.groupTransactionsLoading
                ? "儲存中..."
                : "儲存"
            }}
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
import { useGroupTransactionStore } from "../stores/groupTransactionStore";
import { useCategoryStore } from "../stores/categoryStore";
import { useNotificationStore } from "../stores/notificationStore";

const props = defineProps({
  groupId: {
    type: Number,
    required: true,
  },
  transaction: {
    type: Object,
    default: null, // 如果為空表示新增，不為空表示編輯
  },
});

const emit = defineEmits(["close", "saved"]);

const groupTransactionStore = useGroupTransactionStore();
const categoryStore = useCategoryStore();
const notificationStore = useNotificationStore(); // 雖然在這裡不直接用於錯誤通知，但可以保留

const isEditMode = computed(() => !!props.transaction);

const form = reactive({
  amount: 0,
  type: "expense", // 預設支出
  category_id: "",
  description: "",
  date: new Date().toISOString().slice(0, 10), // 預設今天日期 YYYY-MM-DD
});

const groupTransactionError = ref(null); // 用於模態框內部的錯誤訊息

// 根據交易類型篩選類別
const filteredCategories = computed(() => {
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
      form.date = newVal.date;
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
);

// 在組件掛載時獲取類別列表 (如果還沒有載入)
onMounted(() => {
  if (categoryStore.categories.length === 0) {
    categoryStore.fetchCategories();
  }
});

const saveGroupTransaction = async () => {
  groupTransactionError.value = null; // 在每次嘗試保存前清除錯誤
  const payload = { ...form };

  let result;

  if (isEditMode.value) {
    result = await groupTransactionStore.updateGroupTransaction(
      props.groupId,
      props.transaction.id,
      payload
    );
  } else {
    result = await groupTransactionStore.addGroupTransaction(
      props.groupId,
      payload
    );
  }

  if (result.success) {
    // 通知由 groupTransactionStore 統一處理
    emit("saved"); // 通知父組件保存成功
  } else {
    groupTransactionError.value = result.error; // 設置模態框內部的錯誤訊息
  }
};
</script>

<style scoped>
.fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
