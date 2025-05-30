<!-- client/src/components/ConfirmationModal.vue -->
<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50"
  >
    <div
      class="relative p-8 bg-white w-full max-w-sm mx-auto rounded-lg shadow-xl"
      @click.stop
    >
      <h3 class="text-xl font-bold mb-4 text-center text-gray-800">
        {{ title }}
      </h3>
      <p class="text-gray-700 mb-6 text-center">{{ message }}</p>

      <div class="flex justify-center space-x-4">
        <button
          @click="emit('confirm')"
          :class="confirmButtonClass"
          class="font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          {{ confirmText }}
        </button>
        <button
          @click="emit('cancel')"
          class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  title: {
    type: String,
    default: "確認操作",
  },
  message: {
    type: String,
    default: "您確定要執行此操作嗎？",
  },
  confirmText: {
    type: String,
    default: "確定",
  },
  confirmButtonClass: {
    type: String,
    default: "bg-red-500 hover:bg-red-700 text-white", // 預設紅色危險操作
  },
});

const emit = defineEmits(["confirm", "cancel"]);
</script>

<style scoped>
/* 彈窗背景和定位樣式，與 TransactionForm 類似 */
.fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
