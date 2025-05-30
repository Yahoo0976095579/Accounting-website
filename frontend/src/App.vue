<!-- client/src/App.vue -->
<template>
  <div id="app" class="min-h-screen bg-gray-100 flex flex-col">
    <Navbar />
    <!-- 我們即將創建的導航欄組件 -->
    <NotificationBar />
    <!-- 新增這一行 -->
    <main class="flex-grow">
      <router-view />
      <!-- 這裡顯示當前路由匹配的組件 -->
    </main>
  </div>
</template>

<script setup>
import Navbar from "./components/Navbar.vue"; // 導入導航欄組件
import NotificationBar from "./components/NotificationBar.vue"; // 新增導入
import { useAuthStore } from "./stores/authStore";
import { onMounted } from "vue";

const authStore = useAuthStore();

// 在應用程式啟動時嘗試獲取當前使用者資訊，以處理頁面刷新後的登入狀態
onMounted(() => {
  if (localStorage.getItem("isLoggedIn") === "true" && !authStore.user) {
    authStore.fetchCurrentUser();
  }
});
</script>

<style>
/* 你可以在這裡添加一些全局樣式，或者完全依賴 Tailwind CSS */
</style>
