<!-- client/src/components/CategoryForm.vue -->
<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50"
    @click.self="emit('close')"
  >
    <div
      class="relative p-8 bg-white w-full max-w-md mx-auto rounded-lg shadow-xl"
      @click.stop
    >
      <h2 class="text-2xl font-bold mb-6 text-center">
        {{ isEditMode ? "編輯類別" : "新增類別" }}
      </h2>

      <form @submit.prevent="saveCategory">
        <div class="mb-4">
          <label
            for="categoryName"
            class="block text-gray-700 text-sm font-bold mb-2"
            >類別名稱:</label
          >
          <input
            type="text"
            id="categoryName"
            v-model="form.name"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        <div class="mb-6">
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

        <p v-if="formError" class="text-red-500 text-xs italic mb-4">
          {{ formError }}
        </p>

        <div class="flex items-center justify-center space-x-4">
          <button
            type="submit"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            :disabled="categoryStore.isLoading"
          >
            {{ categoryStore.isLoading ? "儲存中..." : "儲存" }}
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
import { ref, reactive, computed, watch } from "vue";
import { useCategoryStore } from "../stores/categoryStore";
import { useNotificationStore } from "../stores/notificationStore"; // 導入通知 Store

const props = defineProps({
  category: {
    type: Object,
    default: null, // 如果為空表示新增，不為空表示編輯
  },
});

const emit = defineEmits(["close", "saved"]);

const categoryStore = useCategoryStore();
const notificationStore = useNotificationStore();

const isEditMode = computed(() => !!props.category);

const formError = ref(null); // 新增這行：用於表單內部的錯誤訊息

// 表單數據
const form = reactive({
  name: "",
  type: "expense", // 預設支出類型
});

// 監聽 props.category 的變化來填充表單（用於編輯模式）
watch(
  () => props.category,
  (newVal) => {
    if (newVal) {
      form.name = newVal.name;
      form.type = newVal.type;
    } else {
      // 重置表單為預設值 (新增模式)
      form.name = "";
      form.type = "expense";
    }
  },
  { immediate: true }
); // immediate: true 使得組件首次載入時也能觸發 watch

const saveCategory = async () => {
  formError.value = null; // 在每次嘗試保存前清除錯誤
  const payload = { ...form };

  let result; // 接收 store action 的返回結果

  if (isEditMode.value) {
    result = await categoryStore.updateCategory(props.category.id, payload);
  } else {
    result = await categoryStore.addCategory(payload);
  }

  if (result.success) {
    // 檢查返回結果的 success 屬性
    notificationStore.showNotification(
      `類別${isEditMode.value ? "更新" : "新增"}成功！`,
      "success"
    );
    emit("saved"); // 通知父組件保存成功
  } else {
    formError.value = result.error; // 設置表單內部的錯誤訊息
  }
};
</script>

<style scoped>
/* 彈窗背景和定位樣式 */
.fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
