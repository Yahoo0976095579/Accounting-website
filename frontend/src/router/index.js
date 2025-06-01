import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/authStore";

// 導入頁面組件
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import Dashboard from "../views/Dashboard.vue";
import Transactions from "../views/Transactions.vue";
import Categories from "../views/Categories.vue";
import NotFound from "../views/NotFound.vue";
import Groups from "../views/Groups.vue";
import GroupDetails from "../views/GroupDetails.vue";
import Settings from "../views/Settings.vue";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: { requiresAuth: false },
  },
  {
    path: "/register",
    name: "Register",
    component: Register,
    meta: { requiresAuth: false },
  },
  {
    path: "/",
    name: "Dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: "/transactions",
    name: "Transactions",
    component: Transactions,
    meta: { requiresAuth: true },
  },
  {
    path: "/categories",
    name: "Categories",
    component: Categories,
    meta: { requiresAuth: true },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: NotFound,
  },
  {
    path: "/groups",
    name: "Groups",
    component: Groups,
    meta: { requiresAuth: true },
  },
  {
    path: "/groups/:id",
    name: "GroupDetails",
    component: GroupDetails,
    meta: { requiresAuth: true },
  },
  {
    path: "/settings",
    name: "Settings",
    component: Settings,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 全局導航守衛：檢查路由是否需要認證
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // 只用 access_token 判斷
  const token = localStorage.getItem("access_token");

  // 如果 Pinia 沒有 user，但有 access_token，則嘗試取得 user
  if (!authStore.user && token) {
    const fetched = await authStore.fetchCurrentUser();
    if (!fetched && to.meta.requiresAuth) {
      // token 失效，導向登入
      return next("/login");
    }
  }

  const isAuthenticated = !!authStore.user;

  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login");
  } else if (
    (to.name === "Login" || to.name === "Register") &&
    isAuthenticated
  ) {
    next("/");
  } else {
    next();
  }
});

export default router;
