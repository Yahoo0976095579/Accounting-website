<!-- Notification.vue -->
<template>
  <transition name="fade">
    <div
      v-if="notification.isVisible"
      :class="[
        'fixed z-50 bottom-6 right-6 min-w-[220px] max-w-xs px-4 py-3 rounded shadow-lg flex items-center',
        notification.type === 'success' ? 'bg-green-500 text-white' : '',
        notification.type === 'error' ? 'bg-red-500 text-white' : '',
        notification.type === 'info' ? 'bg-blue-500 text-white' : '',
        notification.type === 'warning' ? 'bg-yellow-400 text-black' : '',
      ]"
      style="pointer-events: auto"
    >
      <span class="flex-1">{{ notification.message }}</span>
      <button class="ml-4 text-xl" @click="notification.hideNotification">
        ×
      </button>
    </div>
  </transition>
</template>

<script setup>
import { useNotificationStore } from "../stores/notificationStore";
const notification = useNotificationStore();
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
