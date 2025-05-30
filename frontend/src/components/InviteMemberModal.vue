<!-- client/src/components/InviteMemberModal.vue -->
<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50"
  >
    <div
      class="relative p-8 bg-white w-full max-w-md mx-auto rounded-lg shadow-xl"
      @click.stop
    >
      <h2 class="text-2xl font-bold mb-6 text-center">邀請成員加入群組</h2>

      <form @submit.prevent="sendInvitation">
        <div class="mb-4">
          <label
            for="inviteUsername"
            class="block text-gray-700 text-sm font-bold mb-2"
            >被邀請者的使用者名稱:</label
          >
          <input
            type="text"
            id="inviteUsername"
            v-model="usernameToInvite"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
          />
        </div>

        <p
          v-if="inviteError"
          class="text-red-500 text-xs italic mb-4 text-center"
        >
          {{ inviteError }}
        </p>
        <p
          v-if="groupStore.isLoading"
          class="text-gray-500 text-xs italic mb-4 text-center"
        >
          發送中...
        </p>

        <div class="flex items-center justify-center space-x-4">
          <button
            type="button"
            @click="emit('close')"
            class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            取消
          </button>
          <button
            type="submit"
            class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            :disabled="groupStore.isLoading"
          >
            發送邀請
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useGroupStore } from "../stores/groupStore";
import { useNotificationStore } from "../stores/notificationStore";

const props = defineProps({
  groupId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["close", "invited"]);

const groupStore = useGroupStore();
// const notificationStore = useNotificationStore();

const usernameToInvite = ref("");
const inviteError = ref(null); // 用於模態框內部的錯誤訊息

const sendInvitation = async () => {
  inviteError.value = null; // 清除之前的錯誤

  // 調用 groupStore 的 inviteMember action
  const result = await groupStore.inviteMember(
    props.groupId,
    usernameToInvite.value
  );

  if (result.success) {
    // 成功通知由 groupStore 統一處理
    emit("invited"); // 通知父組件邀請已發送
    usernameToInvite.value = ""; // 清空輸入框
  } else {
    inviteError.value = result.error; // 將錯誤訊息設置到模態框內部的狀態
  }
};

// Note: API_BASE_URL is not defined in this component.
// It should be imported from a common config or defined locally,
// or better, handled directly in the groupStore action.
// Let's modify groupStore to handle the axios call.
</script>

<style scoped>
.fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
