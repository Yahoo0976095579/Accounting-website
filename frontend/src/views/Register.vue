<!-- client/src/views/Register.vue -->
<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h1 class="text-2xl font-bold mb-6 text-center">註冊</h1>
      <form @submit.prevent="handleRegister">
        <div class="mb-4">
          <label
            for="username"
            class="block text-gray-700 text-sm font-bold mb-2"
            >使用者名稱:</label
          >
          <input
            type="text"
            id="username-reg"
            v-model="username"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>
        <div class="mb-6">
          <label
            for="password"
            class="block text-gray-700 text-sm font-bold mb-2"
            >密碼:</label
          >
          <input
            type="password"
            id="password-reg"
            v-model="password"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>
        <p v-if="authStore.error" class="text-red-500 text-xs italic mb-4">
          {{ authStore.error }}
        </p>
        <div class="flex items-center justify-between">
          <button
            type="submit"
            class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            :disabled="authStore.isLoading"
          >
            {{ authStore.isLoading ? "註冊中..." : "註冊" }}
          </button>
          <router-link
            to="/login"
            class="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800"
          >
            已有帳號？登入
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "../stores/authStore";

const authStore = useAuthStore();
const username = ref("");
const password = ref("");

const handleRegister = async () => {
  await authStore.register(username.value, password.value);
};
</script>
