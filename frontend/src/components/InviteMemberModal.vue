<!-- client/src/components/InviteMemberModal.vue (假設這是你的邀請成員模態框) -->
<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <h2 class="text-xl font-bold mb-4">邀請成員</h2>
      <form @submit.prevent="submitInvite">
        <div class="mb-4">
          <label
            for="inviteUsername"
            class="block text-gray-700 text-sm font-bold mb-2"
            >用戶名:</label
          >
          <input
            type="text"
            id="inviteUsername"
            v-model="inviteUsername"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            required
            placeholder="輸入要邀請的用戶名"
          />
        </div>
        <p v-if="inviteError" class="text-red-500 text-xs italic mb-4">
          {{ inviteError }}
        </p>
        <div class="flex justify-end">
          <button
            type="submit"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2"
            :disabled="groupStore.isLoading"
          >
            邀請
          </button>
          <button
            type="button"
            @click="close"
            class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded"
          >
            取消
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from "vue";
import { useGroupStore } from "../stores/groupStore"; // 確保導入 groupStore

const props = defineProps({
  groupId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["close", "invited"]);

const groupStore = useGroupStore();
const inviteUsername = ref("");
const inviteError = ref(null);

const submitInvite = async () => {
  inviteError.value = null;
  const result = await groupStore.inviteMember(
    props.groupId,
    inviteUsername.value
  );
  if (result.success) {
    emit("invited"); // 觸發父組件的 invited 事件
    close();
  } else {
    inviteError.value = result.error; // 這裡將錯誤顯示在模態框內，同時 notificationStore 也會顯示通知
  }
};

const close = () => {
  emit("close");
};
</script>

<style scoped>
/* 模態框樣式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 400px;
}
</style>
