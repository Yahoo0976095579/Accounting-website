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
      <div class="mt-5 sm:mt-6 sm:flex sm:flex-row-reverse">
        <button
          type="button"
          @click="cancel"
          class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm transition-colors duration-200"
        >
          取消
        </button>
        <button
          type="button"
          :class="confirmButtonClass"
          @click="confirm"
          class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-200"
        >
          {{ confirmText }}
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
