<!-- client/src/components/ConfirmationModal.vue -->
<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-50"
    @click.self="cancel"
  >
    <div
      class="bg-white rounded-lg shadow-xl p-6 w-full max-w-sm mx-auto transform transition-all sm:my-8 sm:align-middle"
    >
      <div class="text-center">
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-2">
          {{ title }}
        </h3>
        <div class="mt-2">
          <p class="text-sm text-gray-500">
            {{ message }}
          </p>
        </div>
      </div>
      <div class="flex items-center justify-center space-x-4">
        <button
          type="button"
          :class="confirmButtonClass"
          @click="confirm"
          class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          {{ confirmText }}
        </button>
        <button
          type="button"
          @click="cancel"
          class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from "vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  message: {
    type: String,
    required: true,
  },
  confirmText: {
    type: String,
    default: "確認",
  },
  confirmButtonClass: {
    type: String,
    default: "bg-blue-600 hover:bg-blue-700",
  },
});

const emit = defineEmits(["confirm", "cancel"]);

const confirm = () => {
  emit("confirm");
};

const cancel = () => {
  emit("cancel");
};
</script>
