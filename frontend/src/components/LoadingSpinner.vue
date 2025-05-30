<!-- client/src/components/LoadingSpinner.vue -->
<template>
  <div class="flex flex-col items-center justify-center p-8 text-gray-500">
    <div
      class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-gray-400 mb-2"
    ></div>
    <p>{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: "載入中，請稍候...",
  },
});
</script>

<style scoped>
/* 你可以在這裡添加 spinner 的額外樣式，但 Tailwind 的 animate-spin 已經足夠 */
</style>
