<!-- client/src/components/CreateGroupModal.vue -->
<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50"
  >
    <div
      class="relative p-8 bg-white w-full max-w-md mx-auto rounded-lg shadow-xl"
      @click.stop
    >
      <h2 class="text-2xl font-bold mb-6 text-center">創建新群組</h2>

      <form @submit.prevent="createGroup">
        <div class="mb-4">
          <label
            for="groupName"
            class="block text-gray-700 text-sm font-bold mb-2"
            >群組名稱:</label
          >
          <input
            type="text"
            id="groupName"
            v-model="form.name"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        <div class="mb-6">
          <label
            for="groupDescription"
            class="block text-gray-700 text-sm font-bold mb-2"
            >描述 (可選):</label
          >
          <textarea
            id="groupDescription"
            v-model="form.description"
            rows="3"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          ></textarea>
        </div>

        <p
          v-if="groupStore.error"
          class="text-red-500 text-xs italic mb-4 text-center"
        >
          {{ groupStore.error }}
        </p>

        <div class="flex items-center justify-center space-x-4">
          <button
            type="submit"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            :disabled="groupStore.isLoading"
          >
            {{ groupStore.isLoading ? "創建中..." : "創建" }}
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
import { reactive } from "vue";
import { useGroupStore } from "../stores/groupStore";

const emit = defineEmits(["close", "created"]);

const groupStore = useGroupStore();

const form = reactive({
  name: "",
  description: "",
});

const createGroup = async () => {
  const result = await groupStore.createGroup(form);
  if (result.success) {
    emit("created", result.group); // 傳遞新創建的群組數據
  }
  // 錯誤訊息會由 groupStore.error 狀態綁定在表單內顯示，並由 notificationStore 彈出
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
