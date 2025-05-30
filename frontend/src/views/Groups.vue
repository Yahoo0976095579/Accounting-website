<template>
  <div class="container mx-auto p-4">
    <h1
      class="text-3xl font-bold mb-10 text-center text-blue-700 tracking-wide border-b-2 border-blue-200 pb-4"
    >
      我的群組
    </h1>

    <!-- 創建群組按鈕 -->
    <div class="mb-10 flex justify-end max-w-3xl mx-auto">
      <button
        @click="openCreateGroupModal"
        class="bg-blue-600 hover:bg-blue-800 text-white font-bold py-2 px-6 rounded-lg shadow transition"
      >
        ＋ 創建新群組
      </button>
    </div>

    <!-- 待處理邀請 -->
    <div class="max-w-3xl mx-auto mb-12">
      <h2
        class="text-xl font-bold mb-4 text-gray-700 border-l-4 border-blue-400 pl-3"
      >
        待處理的邀請
      </h2>
      <div
        v-if="
          groupStore.isLoading &&
          !groupStore.groups.length &&
          !groupStore.invitations.length
        "
        class="text-center py-8"
      >
        <LoadingSpinner message="載入邀請中..." />
      </div>
      <div v-else-if="groupStore.error" class="text-center py-8">
        <p class="text-red-500 text-lg">錯誤：{{ groupStore.error }}</p>
      </div>
      <div v-else>
        <div
          v-if="groupStore.invitations.length === 0"
          class="bg-white p-6 rounded-xl shadow text-gray-400 text-center"
        >
          沒有新的群組邀請
        </div>
        <div v-else class="bg-white shadow rounded-xl overflow-hidden">
          <ul class="divide-y divide-gray-200">
            <li
              v-for="invitation in groupStore.invitations"
              :key="invitation.id"
              class="px-6 py-4 flex flex-col md:flex-row md:items-center md:justify-between hover:bg-gray-50 transition"
            >
              <div>
                <p class="font-semibold text-gray-800">
                  您被
                  <span class="text-blue-600">{{
                    invitation.invited_by_username
                  }}</span>
                  邀請加入群組：
                  <span class="text-lg font-bold">{{
                    invitation.group_name
                  }}</span>
                </p>
                <p class="text-xs text-gray-400 mt-1">
                  邀請時間：{{
                    new Date(invitation.created_at).toLocaleDateString()
                  }}
                </p>
              </div>
              <div class="flex space-x-2 mt-3 md:mt-0">
                <button
                  @click="acceptInvitation(invitation.id)"
                  class="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-4 rounded text-sm shadow"
                >
                  接受
                </button>
                <button
                  @click="rejectInvitation(invitation.id)"
                  class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-4 rounded text-sm shadow"
                >
                  拒絕
                </button>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 我所屬的群組 -->
    <div class="max-w-3xl mx-auto">
      <h2
        class="text-xl font-bold mb-4 text-gray-700 border-l-4 border-blue-400 pl-3"
      >
        我所屬的群組
      </h2>
      <div
        v-if="
          groupStore.isLoading &&
          !groupStore.invitations.length &&
          !groupStore.groups.length
        "
        class="text-center py-8"
      >
        <LoadingSpinner message="載入群組中..." />
      </div>
      <div v-else-if="groupStore.error" class="text-center py-8">
        <p class="text-red-500 text-lg">錯誤：{{ groupStore.error }}</p>
      </div>
      <div v-else>
        <div
          v-if="groupStore.groups.length === 0"
          class="bg-white p-6 rounded-xl shadow text-gray-400 text-center"
        >
          您尚未加入任何群組。您可以創建一個或等待邀請。
        </div>
        <div v-else class="bg-white shadow rounded-xl overflow-hidden">
          <ul class="divide-y divide-gray-200">
            <li
              v-for="group in groupStore.groups"
              :key="group.id"
              class="px-6 py-4 flex flex-col md:flex-row md:items-center md:justify-between hover:bg-gray-50 transition"
            >
              <div>
                <router-link
                  :to="`/groups/${group.id}`"
                  class="text-lg font-bold text-blue-600 hover:underline"
                  >{{ group.name }}</router-link
                >
                <p class="text-sm text-gray-500 mt-1">
                  {{ group.description || "無描述" }}
                </p>
                <p class="text-xs text-gray-400 mt-1">
                  成員：{{ group.member_count }}人 | 您的角色：<span
                    class="capitalize"
                    >{{ group.your_role }}</span
                  >
                </p>
              </div>
              <div class="flex space-x-2 mt-3 md:mt-0">
                <router-link
                  :to="`/groups/${group.id}`"
                  class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-4 rounded text-sm shadow"
                >
                  查看詳情
                </router-link>
                <!-- 其他管理功能按鈕可加在這裡 -->
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 創建群組模態框 -->
    <CreateGroupModal
      v-if="showCreateGroupModal"
      @close="closeCreateGroupModal"
      @created="handleGroupCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useGroupStore } from "../stores/groupStore";
import LoadingSpinner from "../components/LoadingSpinner.vue";
import CreateGroupModal from "../components/CreateGroupModal.vue"; // 即將創建

const groupStore = useGroupStore();

const showCreateGroupModal = ref(false);

onMounted(() => {
  groupStore.fetchUserGroups(); // 獲取使用者所屬群組
  groupStore.fetchInvitations(); // 獲取待處理邀請
});

const openCreateGroupModal = () => {
  showCreateGroupModal.value = true;
};

const closeCreateGroupModal = () => {
  showCreateGroupModal.value = false;
};

const handleGroupCreated = async (newGroup) => {
  // 群組已在 store 中添加，這裡只需關閉模態框
  closeCreateGroupModal();
};

const acceptInvitation = async (invitationId) => {
  const success = await groupStore.acceptInvitation(invitationId);
  if (success) {
    // 通知已在 store 中處理
  }
};

const rejectInvitation = async (invitationId) => {
  const success = await groupStore.rejectInvitation(invitationId);
  if (success) {
    // 通知已在 store 中處理
  }
};

// TODO: 編輯群組 (留給未來)
// TODO: 邀請成員 (留給未來)
// TODO: 退出群組 (留給未來)
// TODO: 刪除群組 (留給未來)
</script>
