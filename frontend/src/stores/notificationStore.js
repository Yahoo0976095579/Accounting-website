// client/src/stores/notificationStore.js
import { defineStore } from "pinia";
import { ref } from "vue";

export const useNotificationStore = defineStore("notification", () => {
  const message = ref("");
  const type = ref("success"); // 'success', 'error', 'info', 'warning'
  const isVisible = ref(false);
  let timeoutId = null;

  function showNotification(msg, msgType = "success", duration = 3000) {
    message.value = msg;
    type.value = msgType;
    isVisible.value = true;

    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      hideNotification();
    }, duration);
  }

  function hideNotification() {
    isVisible.value = false;
    message.value = "";
    type.value = "success"; // 重置為預設
  }

  return { message, type, isVisible, showNotification, hideNotification };
});
