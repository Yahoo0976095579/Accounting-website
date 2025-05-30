<!-- client/src/views/Settings.vue -->
<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-center">帳戶設定</h1>

    <div v-if="authStore.isLoading" class="text-center py-8">
      <LoadingSpinner message="處理中..." />
    </div>
    <div v-else>
      <!-- 修改使用者名稱 -->
      <div class="bg-white p-6 rounded-lg shadow-md mb-8 max-w-xl mx-auto">
        <h2 class="text-2xl font-bold mb-4 text-gray-700">修改使用者名稱</h2>
        <p class="text-gray-600 mb-4">
          目前的名稱：<span class="font-semibold text-blue-600">{{
            authStore.user?.username
          }}</span>
        </p>
        <form @submit.prevent="updateUsername">
          <div class="mb-4">
            <label
              for="newUsername"
              class="block text-gray-700 text-sm font-bold mb-2"
              >新的使用者名稱:</label
            >
            <input
              type="text"
              id="newUsername"
              v-model="newUsername"
              class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
              :placeholder="authStore.user?.username"
            />
          </div>
          <p v-if="usernameError" class="text-red-500 text-xs italic mb-4">
            {{ usernameError }}
          </p>
          <div class="flex items-center justify-end">
            <button
              type="submit"
              class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              :disabled="
                authStore.isLoading || newUsername === authStore.user?.username
              "
            >
              更新使用者名稱
            </button>
          </div>
        </form>
      </div>

      <!-- 修改密碼 -->
      <div class="bg-white p-6 rounded-lg shadow-md max-w-xl mx-auto">
        <h2 class="text-2xl font-bold mb-4 text-gray-700">修改密碼</h2>
        <form @submit.prevent="updatePassword">
          <div class="mb-4">
            <label
              for="oldPassword"
              class="block text-gray-700 text-sm font-bold mb-2"
              >舊密碼:</label
            >
            <input
              type="password"
              id="oldPassword"
              v-model="oldPassword"
              class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>
          <div class="mb-4">
            <label
              for="newPassword"
              class="block text-gray-700 text-sm font-bold mb-2"
              >新密碼:</label
            >
            <input
              type="password"
              id="newPassword"
              v-model="newPassword"
              class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>
          <div class="mb-6">
            <label
              for="confirmPassword"
              class="block text-gray-700 text-sm font-bold mb-2"
              >確認新密碼:</label
            >
            <input
              type="password"
              id="confirmPassword"
              v-model="confirmPassword"
              class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
              required
            />
          </div>
          <p v-if="passwordError" class="text-red-500 text-xs italic mb-4">
            {{ passwordError }}
          </p>
          <p v-if="passwordSuccess" class="text-green-600 text-xs italic mb-4">
            {{ passwordSuccess }}
          </p>
          <div class="flex items-center justify-end">
            <button
              type="submit"
              class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              :disabled="authStore.isLoading"
            >
              更新密碼
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useAuthStore } from "../stores/authStore";
import LoadingSpinner from "../components/LoadingSpinner.vue";

const authStore = useAuthStore();

// 修改使用者名稱相關
const newUsername = ref(authStore.user?.username || "");
const usernameError = ref(null);

// 當 authStore.user 更新時，同步 newUsername
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      newUsername.value = newUser.username;
    }
  },
  { immediate: true }
);

const updateUsername = async () => {
  usernameError.value = null; // 清除錯誤
  if (newUsername.value === authStore.user?.username) {
    usernameError.value = "新的使用者名稱不能與目前的名稱相同。";
    return;
  }
  const result = await authStore.updateUsername(newUsername.value);
  if (result.success) {
    // 通知已在 store 中處理
    // newUsername.value 會由 watch 同步更新
  } else {
    usernameError.value = result.error;
  }
};

// 修改密碼相關
const oldPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref(""); // 新增
const passwordError = ref(null);
const passwordSuccess = ref(null);

const updatePassword = async () => {
  console.log("submit updatePassword");
  passwordError.value = null;
  passwordSuccess.value = null;
  if (!oldPassword.value || !newPassword.value || !confirmPassword.value) {
    passwordError.value = "請完整填寫所有欄位。";
    return;
  }
  if (oldPassword.value === newPassword.value) {
    passwordError.value = "新密碼不能與舊密碼相同。";
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = "新密碼與確認新密碼不一致。";
    return;
  }
  const result = await authStore.updatePassword(
    oldPassword.value,
    newPassword.value
  );
  if (result.success) {
    passwordSuccess.value = "密碼更新成功！";
    oldPassword.value = "";
    newPassword.value = "";
    confirmPassword.value = "";
  } else {
    passwordError.value = result.error || "密碼更新失敗";
    oldPassword.value = "";
    newPassword.value = "";
    confirmPassword.value = "";
  }
};
</script>
