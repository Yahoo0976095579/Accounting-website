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
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.post(
          `${API_BASE_URL}/groups/${groupId}/invite`,
          { username },
          {
            headers: this.getAuthHeaders(),
          }
        );
        useNotificationStore().showNotification(
          response.data.message,
          "success"
        );
        return { success: true };
      } catch (err) {
        this.error = err.response?.data?.error || "發送邀請失敗。";
        console.error("Invite member error:", err);
        return { success: false, error: this.error };
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
    async deleteGroup(groupId) {
      this.isLoading = true;
      this.error = null;
      const notificationStore = useNotificationStore();
      try {
        await axios.delete(`${API_BASE_URL}/groups/${groupId}`, {
          headers: this.getAuthHeaders(),
        });
        this.groups = this.groups.filter((group) => group.id !== groupId); // 從列表中移除
        this.currentGroup = null; // 清除當前群組詳情
        notificationStore.showNotification("群組已成功刪除！", "success");
        router.push("/groups"); // 重定向到群組列表頁面，會導致頁面刷新
        return true;
      } catch (err) {
        this.error = err.response?.data?.error || "刪除群組失敗。";
        notificationStore.showNotification(this.error, "error");
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
  },
});
