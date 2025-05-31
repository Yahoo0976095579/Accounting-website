// client/src/stores/groupStore.js
import { defineStore } from "pinia";
import axios from "axios";
import { useNotificationStore } from "./notificationStore";

import { API_BASE_URL } from "./config";

export const useGroupStore = defineStore("group", {
  state: () => ({
    groups: [], // 使用者所屬的群組列表
    currentGroup: null, // 當前查看的群組詳情
    invitations: [], // 收到的群組邀請
    isLoading: false,
    error: null,
  }),
  actions: {
    async inviteMember(groupId, username) {
      this.isLoading = true;
      this.error = null; // 清除全局錯誤
      try {
        const response = await axios.post(
          `${API_BASE_URL}/groups/${groupId}/invite`,
          { username },
          {
            withCredentials: true,
          }
        );
        useNotificationStore().showNotification(
          response.data.message,
          "success"
        );
        return { success: true };
      } catch (err) {
        this.error = err.response?.data?.error || "發送邀請失敗。"; // 全局錯誤，用於外部組件
        console.error("Invite member error:", err);
        return { success: false, error: this.error }; // 返回錯誤給調用者
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUserGroups() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await axios.get(`${API_BASE_URL}/groups`, {
          withCredentials: true,
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
          withCredentials: true,
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
          withCredentials: true,
        });
        this.groups.push(response.data.group); // 將新群組添加到列表
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
          withCredentials: true,
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
            withCredentials: true,
          }
        );
        // 移除已接受的邀請，並重新載入群組列表
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
            withCredentials: true,
          }
        );
        // 移除已拒絕的邀請
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
  },
});
