<!-- client/src/components/NotificationBar.vue -->
<template>
  <transition name="fade">
    <div
      v-if="notificationStore.isVisible"
      :class="notificationClass"
      class="fixed top-0 left-0 right-0 z-50 p-4 text-center text-white font-bold shadow-md"
    >
      {{ notificationStore.message }}
    </div>
  </transition>
</template>

<script setup>
import { computed } from "vue";
import { useNotificationStore } from "../stores/notificationStore";

const notificationStore = useNotificationStore();

const notificationClass = computed(() => {
  switch (notificationStore.type) {
    case "success":
      return "bg-green-500";
    case "error":
      return "bg-red-500";
    case "info":
      return "bg-blue-500";
    case "warning":
      return "bg-yellow-500";
    default:
      return "bg-gray-500";
  }
});
</script>

<style scoped>
/* 過渡動畫 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.8s ease, transform 0.8s ease; /* 增加過渡時間和 transform 效果 */
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px); /* 從上方滑入/滑出效果 */
}
</style>
