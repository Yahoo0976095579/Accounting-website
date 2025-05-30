<!-- client/src/components/Navbar.vue -->
<!-- client/src/components/Navbar.vue -->
<template>
  <nav class="bg-blue-600 p-4 shadow-md">
    <div
      class="container mx-auto flex items-center justify-between lg:justify-start"
    >
      <!-- lg:justify-start for desktop, justify-between for mobile -->
      <!-- Logo/品牌 (保持在左側) -->
      <router-link to="/" class="text-white text-2xl font-bold lg:mr-6"
        >記帳網站</router-link
      >

      <!-- 漢堡菜單按鈕 (只在小螢幕顯示) -->
      <div class="lg:hidden">
        <button @click="toggleMobileMenu" class="text-white focus:outline-none">
          <svg
            class="w-8 h-8"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              v-if="!isMobileMenuOpen"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            ></path>
            <path
              v-else
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>

      <!-- 桌面版導航 (在 lg 螢幕以上顯示) -->
      <div class="hidden lg:flex items-center flex-grow">
        <!-- flex-grow 只在桌面版生效 -->
        <template v-if="authStore.isAuthenticated">
          <!-- 核心導航連結組 -->
          <div class="flex items-center space-x-4">
            <router-link
              to="/"
              class="router-link-item text-white hover:text-blue-200 py-1 px-2 rounded hover:bg-blue-700 transition duration-300"
              >儀表板</router-link
            >
            <router-link
              to="/transactions"
              class="router-link-item text-white hover:text-blue-200 py-1 px-2 rounded hover:bg-blue-700 transition duration-300"
              >交易記錄</router-link
            >
            <router-link
              to="/categories"
              class="router-link-item text-white hover:text-blue-200 py-1 px-2 rounded hover:bg-blue-700 transition duration-300"
              >類別管理</router-link
            >
            <router-link
              to="/groups"
              class="router-link-item text-white hover:text-blue-200 py-1 px-2 rounded hover:bg-blue-700 transition duration-300"
              >我的群組</router-link
            >
            <router-link
              to="/settings"
              class="router-link-item text-white hover:text-blue-200 py-1 px-2 rounded hover:bg-blue-700 transition duration-300"
              >設定</router-link
            >
          </div>

          <!-- 使用 flex-grow 佔據所有剩餘空間，將登出按鈕推到最右邊 (只在桌面版生效) -->
          <div class="flex-grow"></div>

          <!-- 登出按鈕 (被推到最右邊) -->
          <div>
            <button
              @click="handleLogout"
              class="text-white hover:text-blue-200 px-4 py-2 rounded-full border border-white hover:border-blue-200 hover:bg-blue-700 transition duration-300"
            >
              登出
            </button>
          </div>
        </template>
        <template v-else>
          <!-- 登入/註冊連結組 (使用 ml-auto 將其推到最右邊) -->
          <div class="flex items-center space-x-4 ml-auto">
            <router-link
              to="/login"
              class="router-link-item text-white hover:text-blue-200 py-1 px-2 rounded hover:bg-blue-700 transition duration-300"
              >登入</router-link
            >
            <router-link
              to="/register"
              class="router-link-item text-white hover:text-blue-200 py-1 px-2 rounded hover:bg-blue-700 transition duration-300"
              >註冊</router-link
            >
          </div>
        </template>
      </div>
    </div>

    <!-- 手機版菜單 (只在小螢幕顯示，通過 v-if 控制顯示/隱藏) -->
    <div
      v-if="isMobileMenuOpen"
      class="lg:hidden bg-blue-700 py-2 mt-2 rounded shadow-lg"
    >
      <template v-if="authStore.isAuthenticated">
        <router-link
          to="/"
          @click="closeMobileMenu"
          class="block text-white hover:text-blue-200 px-4 py-2 hover:bg-blue-800"
          >儀表板</router-link
        >
        <router-link
          to="/transactions"
          @click="closeMobileMenu"
          class="block text-white hover:text-blue-200 px-4 py-2 hover:bg-blue-800"
          >交易記錄</router-link
        >
        <router-link
          to="/categories"
          @click="closeMobileMenu"
          class="block text-white hover:text-blue-200 px-4 py-2 hover:bg-blue-800"
          >類別管理</router-link
        >
        <router-link
          to="/groups"
          @click="closeMobileMenu"
          class="block text-white hover:text-blue-200 px-4 py-2 hover:bg-blue-800"
          >我的群組</router-link
        >
        <router-link
          to="/settings"
          @click="closeMobileMenu"
          class="block text-white hover:text-blue-200 px-4 py-2 hover:bg-blue-800"
          >設定</router-link
        >
        <!-- <-- 新增這行 -->
        <div class="px-4 py-2">
          <button
            @click="handleLogoutAndCloseMenu"
            class="w-full text-white hover:text-blue-200 px-4 py-2 rounded-full border border-white hover:border-blue-200 hover:bg-blue-800 transition duration-300"
          >
            登出
          </button>
        </div>
      </template>
      <template v-else>
        <router-link
          to="/login"
          @click="closeMobileMenu"
          class="block text-white hover:text-blue-200 px-4 py-2 hover:bg-blue-800"
          >登入</router-link
        >
        <router-link
          to="/register"
          @click="closeMobileMenu"
          class="block text-white hover:text-blue-200 px-4 py-2 hover:bg-blue-800"
          >註冊</router-link
        >
      </template>
    </div>
  </nav>
</template>

<!-- Script setup and style scoped remain the same as your last working version -->
<!-- client/src/components/Navbar.vue (在 <script setup> 內部) -->
<script setup>
import { ref } from "vue"; // 引入 ref
import { useAuthStore } from "../stores/authStore";

const authStore = useAuthStore();

const isMobileMenuOpen = ref(false); // 控制手機菜單的顯示/隱藏

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};

const handleLogout = async () => {
  console.log("Attempting to log out...");
  await authStore.logout();
};

const handleLogoutAndCloseMenu = async () => {
  // 登出並關閉菜單
  await handleLogout();
  closeMobileMenu();
};
</script>

<style scoped>
.router-link-active {
  color: theme("colors.white"); /* 保持白色文字 */
  font-weight: theme("fontWeight.bold"); /* 加粗 */
  padding-bottom: 6px; /* 調整 padding 以避免邊框緊貼文字 */
}

.router-link-item {
  /* 為所有連結添加通用過渡類 */
  transition: background-color 0.3s ease, color 0.3s ease;
}
.router-link-item:hover {
  background-color: theme("colors.blue.700"); /* 懸停時的背景色 */
  color: theme("colors.blue.200"); /* 懸停時的文字顏色 */
}
.router-link-active.router-link-item:hover {
  /* 活躍狀態下懸停的特殊樣式，防止衝突 */
  background-color: theme("colors.blue.700");
  color: theme("colors.white");
}
</style>
