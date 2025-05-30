// client/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/authStore"; // 即將創建的認證 store

// 導入頁面組件 (我們會在後面創建這些檔案)
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import Dashboard from "../views/Dashboard.vue";
import Transactions from "../views/Transactions.vue";
import Categories from "../views/Categories.vue";
import NotFound from "../views/NotFound.vue"; // 可選的 404 頁面

const routes = [
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: { requiresAuth: false }, // 不需要認證
  },
  {
    path: "/register",
    name: "Register",
    component: Register,
    meta: { requiresAuth: false }, // 不需要認證
  },
  {
    path: "/",
    name: "Dashboard",
    component: Dashboard,
    meta: { requiresAuth: true }, // 需要認證
  },
  {
    path: "/transactions",
    name: "Transactions",
    component: Transactions,
    meta: { requiresAuth: true }, // 需要認證
  },
  {
    path: "/categories",
    name: "Categories",
    component: Categories,
    meta: { requiresAuth: true }, // 需要認證
  },
  // 捕獲所有未匹配的路由，重定向到 404 頁面
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(), // 使用 HTML5 History 模式
  routes,
});

// 全局導航守衛：檢查路由是否需要認證
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // 嘗試從 localStorage 檢查登入狀態
  const isLoggedInLocally = localStorage.getItem("isLoggedIn") === "true";

  // 如果 Pinia 狀態沒有 user，但 localStorage 顯示已登入，則嘗試從後端獲取使用者資訊
  if (!authStore.user && isLoggedInLocally) {
    console.log(
      "Pinia state empty, but localStorage shows logged in. Attempting to fetch user..."
    );
    const fetched = await authStore.fetchCurrentUser();
    if (!fetched) {
      // 如果獲取失敗（會話過期等），則清除本地狀態並重定向到登入頁
      console.log("Failed to fetch user, redirecting to login.");
      if (to.meta.requiresAuth) {
        // 只有當目標頁面需要認證時才重定向
        return next("/login");
      }
    } else {
      console.log("User successfully fetched from backend.");
    }
  }

  // 再次檢查 isAuthenticated，因為可能在 fetchCurrentUser 後更新了
  const isAuthenticated = !!authStore.user;

  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log(
      `Route ${to.path} requires auth, but user is not authenticated. Redirecting to login.`
    );
    next("/login");
  } else if (
    (to.name === "Login" || to.name === "Register") &&
    isAuthenticated
  ) {
    console.log(
      `User already authenticated, redirecting from ${to.path} to dashboard.`
    );
    next("/");
  } else {
    // 其他情況正常導航
    console.log(
      `Allowing navigation to ${to.path}. Authenticated: ${isAuthenticated}`
    );
    next();
  }
});

export default router;
