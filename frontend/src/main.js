// client/src/main.js
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router/index.js"; // 正確的路由導入路徑
import { createPinia } from "pinia";
import "./style.css"; // 我們之後會引入 Tailwind CSS，或者你自己的基礎樣式
// src/main.js 或 src/main.ts

import { setupAxiosInterceptors } from "./plugins/axios"; // 導入攔截器設置函數

const app = createApp(App);
const pinia = createPinia();

app.use(router);
app.use(pinia);
setupAxiosInterceptors();
app.mount("#app");
//新增
