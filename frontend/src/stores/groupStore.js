import { defineStore } from "pinia";
import axios from "axios";
import { useNotificationStore } from "./notificationStore";
import { API_BASE_URL } from "./config";
import router from "../router"; // 導入 router，因為刪除群組後需要重定向

export const useGroupStore = defineStore("group", {
  state: () => ({
    groups: [], // 使用者所屬的群組列表
    currentGroup: null, // 當前查看的群組詳情
    invitations: [], // 收到的群組邀請
    isLoading: false,
    error: null,
  }),
  actions: {
    // 取得 JWT token 的 header
    getAuthHeaders() {
      const token = localStorage.getItem("access_token");
      return token ? { Authorization: `Bearer ${token}` } : {};
    },

    async inviteMember(groupId, username) {
      this.isLoading = true; // 或設置一個更細粒度的 loading 狀態，如 isInvitingMember
      // this.error = null; // 清除錯誤狀態
      const notificationStore = useNotificationStore();
      try {
        const response = await axios.post(
          `${API_BASE_URL}/groups/${groupId}/invite`,
          { username },
          {
            headers: this.getAuthHeaders(),
          }
        );
        // 邀請成功後，可能需要刷新邀請列表，或者只是顯示成功通知
        notificationStore.showNotification(
          response.data.message || `已成功向 ${username} 發送邀請！`,
          "success"
        );
        // 如果你在 GroupDetails.vue 中需要刷新成員列表（儘管邀請後成員還不是正式成員），可以這麼做：
        await this.fetchGroupDetails(groupId); // 刷新群組詳情，以更新成員列表
        return { success: true };
      } catch (err) {
        // === 修正點：使用 notificationStore 顯示錯誤，並清除 groupStore.error ===
        const errorMessage = err.response?.data?.error || "發送邀請失敗。";
        notificationStore.showNotification(errorMessage, "error");
        this.error = null; // 確保清除任何可能導致全頁顯示的錯誤
        // ===================================================================
        console.error("Invite member error:", err);
        return { success: false, error: errorMessage };
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUserGroups() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/groups`, {
          headers: this.getAuthHeaders(),
        });
        this.groups = response.data;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to fetch user groups.";
        useNotificationStore().showNotification(this.error, "error");
        console.error("Fetch user groups error:", err);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchGroupDetails(groupId) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/groups/${groupId}`, {
          headers: this.getAuthHeaders(),
        });
        this.currentGroup = response.data;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to fetch group details.";
        useNotificationStore().showNotification(this.error, "error");
        console.error("Fetch group details error:", err);
        this.currentGroup = null;
      } finally {
        this.isLoading = false;
      }
    },

    async createGroup(groupData) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(`${API_BASE_URL}/groups`, groupData, {
          headers: this.getAuthHeaders(),
        });
        this.groups.push(response.data.group);
        useNotificationStore().showNotification("群組創建成功！", "success");
        return { success: true, group: response.data.group };
      } catch (err) {
        this.error = err.response?.data?.error || "Failed to create group.";
        useNotificationStore().showNotification(this.error, "error");
        console.error("Create group error:", err);
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async fetchInvitations() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/invitations`, {
          headers: this.getAuthHeaders(),
        });
        this.invitations = response.data;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to fetch invitations.";
        useNotificationStore().showNotification(this.error, "error");
        console.error("Fetch invitations error:", err);
      } finally {
        this.isLoading = false;
      }
    },

    async acceptInvitation(invitationId) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/invitations/${invitationId}/accept`,
          {},
          {
            headers: this.getAuthHeaders(),
          }
        );
        this.invitations = this.invitations.filter(
          (inv) => inv.id !== invitationId
        );
        await this.fetchUserGroups();
        useNotificationStore().showNotification(
          response.data.message,
          "success"
        );
        return true;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to accept invitation.";
        useNotificationStore().showNotification(this.error, "error");
        console.error("Accept invitation error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    async rejectInvitation(invitationId) {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/invitations/${invitationId}/reject`,
          {},
          {
            headers: this.getAuthHeaders(),
          }
        );
        this.invitations = this.invitations.filter(
          (inv) => inv.id !== invitationId
        );
        useNotificationStore().showNotification(
          response.data.message,
          "success"
        );
        return true;
      } catch (err) {
        this.error =
          err.response?.data?.error || "Failed to reject invitation.";
        useNotificationStore().showNotification(this.error, "error");
        console.error("Reject invitation error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },
    // 新增：刪除群組
    // 刪除群組
    // 刪除群組
    async deleteGroup(groupId) {
      this.isLoading = true;
      // this.error = null; // 在這裡清除 error 狀態是好的
      const notificationStore = useNotificationStore();
      try {
        await axios.delete(`${API_BASE_URL}/groups/${groupId}`, {
          headers: this.getAuthHeaders(),
        });
        this.groups = this.groups.filter((group) => group.id !== groupId);
        this.currentGroup = null;
        notificationStore.showNotification("群組已成功刪除！", "success");
        router.push("/groups"); // 重定向到群組列表頁面
        return true;
      } catch (err) {
        // === 修正點：使用 notificationStore 顯示錯誤 ===
        const errorMessage = err.response?.data?.error || "刪除群組失敗。";
        notificationStore.showNotification(errorMessage, "error");
        // 你可以選擇是否在此處設置 groupStore.error
        // 如果你希望在通知顯示後，這個錯誤不再影響頁面布局，就不設置 this.error
        // 或者設置一個短暫的 this.error 並在一段時間後清除
        // 為了讓你的模板不再顯示大塊錯誤，我們不設置 this.error
        this.error = null; // 確保清除任何潛在的舊錯誤
        // ===============================================
        console.error("Delete group error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },

    // 移除群組成員 (確認此處已有 fetchGroupDetails)
    async removeMember(groupId, memberId) {
      this.isLoading = true;
      this.error = null;
      const notificationStore = useNotificationStore();
      try {
        await axios.delete(
          `${API_BASE_URL}/groups/${groupId}/members/${memberId}`,
          {
            headers: this.getAuthHeaders(),
          }
        );

        // === 確認此處的修正：重新獲取群組詳情以更新畫面 ===
        await this.fetchGroupDetails(groupId);
        // ===============================================

        notificationStore.showNotification("成員已成功移除！", "success");
        return true;
      } catch (err) {
        this.error = err.response?.data?.error || "移除成員失敗。";
        notificationStore.showNotification(this.error, "error");
        console.error("Remove member error:", err);
        return false;
      } finally {
        this.isLoading = false;
      }
    },
    // 新增：更新成員角色
    async updateMemberRole(groupId, memberId, newRole) {
      this.isLoading = true; // 可能需要更細粒度的 loading
      this.error = null;
      const notificationStore = useNotificationStore();
      try {
        const response = await axios.put(
          `${API_BASE_URL}/groups/${groupId}/members/${memberId}/role`,
          { role: newRole },
          { headers: this.getAuthHeaders() }
        );
        notificationStore.showNotification(response.data.message, "success");
        await this.fetchGroupDetails(groupId); // 刷新群組詳情以更新成員列表和角色
        return { success: true };
      } catch (err) {
        const errorMessage = err.response?.data?.error || "更新成員角色失敗。";
        notificationStore.showNotification(errorMessage, "error");
        this.error = null;
        console.error("Update member role error:", err);
        return { success: false, error: errorMessage };
      } finally {
        this.isLoading = false;
      }
    },

    // 新增：退出群組
    async leaveGroup(groupId) {
      this.isLoading = true;
      this.error = null;
      const notificationStore = useNotificationStore();
      try {
        const response = await axios.post(
          `${API_BASE_URL}/groups/${groupId}/leave`,
          {},
          {
            headers: this.getAuthHeaders(),
          }
        );
        notificationStore.showNotification(response.data.message, "success");
        // 退出群組後，需要刷新用戶的群組列表並重定向到群組總覽頁
        await this.fetchUserGroups(); // 刷新我所屬的群組列表
        this.currentGroup = null; // 清除當前群組詳情
        router.push("/groups"); // 重定向到群組列表頁面
        return { success: true };
      } catch (err) {
        const errorMessage = err.response?.data?.error || "退出群組失敗。";
        notificationStore.showNotification(errorMessage, "error");
        this.error = null;
        console.error("Leave group error:", err);
        return { success: false, error: errorMessage };
      } finally {
        this.isLoading = false;
      }
    },
  },
});
