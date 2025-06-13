# 💸 記帳網站 (Accounting Web App)

一個功能豐富、支援個人與群組的記帳 Web 應用程式，旨在幫助使用者輕鬆追蹤與分析收支。
本專案具備強大的多條件篩選、分頁、自定義類別管理、協作式群組記帳、即時通知，並採用響應式設計與現代化 UI/UX，確保在任何裝置上都能提供流暢的體驗。

- 前端：Vue 3
- 後端：Python Flask
- 資料庫：PostgreSQL
- 部署：Vercel (前端)、Render (後端與資料庫)
- 🔗 網站連結：[https://yahoo0976095579.github.io/Accounting-website/](https://yahoo0976095579.github.io/Accounting-website/)

---

## ✨ 主要功能亮點

### 🔐 安全使用者認證

- 完整的註冊、登入、登出流程
- JWT 身份驗證，確保 API 請求安全
- JWT 過期自動登出並導回登入頁面

### 🧾 靈活的個人記帳

- 交易 CRUD 操作
- 多條件篩選與分頁
- 即時更新統計與交易列表

### 👥 協作式群組記帳

- 群組建立/解散、成員管理與邀請
- 可重複邀請、權限管理、智能退出
- 群組內共享交易，支援篩選與分頁

### 📊 直觀的儀表板

- 收支與結餘概覽
- 趨勢圖表（日/週/月）
- 類別分佈視覺化分析

### 🗂 高效的類別管理

- 自定義收支類別

### 🔔 即時通知與提示

- 全局非阻斷式提示 (成功/錯誤/過期等)
- 載入動畫與確認刪除彈窗

### 📱 卓越的響應式設計

- 支援桌機與手機
- 卡片模式表格、按鈕與欄位優化

### 🎨 現代化介面

- 使用 Tailwind CSS 打造簡潔美觀 UI

---

## ⚙️ 安裝與啟動

先將 github 專案 clone 下來再推送到自己的 github 專案。
(對部屬較方便)

### 1️⃣ 後端 (Flask)部屬 render

註冊並登入 Render
https://render.com/

## 新增 web service 專案後選取對應 github。

1.render 內部的 name 自取 <br> 2.語言選 python 3 <br> 3.分支選 main<br>
4.Region 選新加坡<br>
5.Root Directory 選 backend<br>
6.Build Command 寫 pip install -r requirements.txt<br>
7.Instance Type 選 FREE<br>
8.Environment Variables 寫 DATABASE_URL<br>
9.Environment Variables value 寫 postgresql://accweb_y3ga_user:nfuMKgZoHO2T07GmajLWN2tbzftUfTR7@dpg-d0tf5vu3jp1c73ehgdo0-a.singapore-postgres.render.com/accweb_y3ga<br>

### 2️⃣ 資料庫(PostgreSQL) 部屬 render

註冊並登入 Render
https://render.com/

## 新增 Postgres 專案。

1.Name 自取<br>
2.Region 選新加坡<br>
3.Plan Options 選 FREE<br>

##render 後端就會連到 render 資料庫

### 前端 (Vue 3)部屬 vercel

註冊並登入 Velcel
https://vercel.com/

先將 github 專案 clone 下來再推送到自己的 github 專案。
(對部屬較方便)

1.建立專案 2.選擇對應的 github 專案
3.Framework Preset 選 Vite
4.Root Directory 選 frontend

## 創立後就可以連到 render 後端

## 🔗 前後端互動邏輯

### ✅ 認證流程

1. 使用者註冊/登入 → 發送 POST `/api/register` 或 `/api/login`
2. 後端回傳 JWT
3. 前端存入 `localStorage` 並在 API 請求時加入 `Authorization: Bearer <token>`
4. Axios 攔截器處理 401，自動登出與重導登入頁

---

### 🔄 交易 CRUD 與篩選

- **新增/編輯交易**
  → `/api/transactions` 或 `/api/groups/{group_id}/transactions`

- **刪除交易**
  → `DELETE /api/transactions/{id}` 或群組交易路由

- **篩選與分頁查詢**
  → `GET /api/transactions?type=income&...`

- **智能類別聯動**：類型變更自動過濾對應類別

---

### 📈 儀表板資料取得

- `/api/summary`
- `/api/summary/trend`
- `/api/summary/category_breakdown`

---

### 🧑‍🤝‍🧑 群組協作邏輯

- **建立群組**：`POST /api/groups`
- **邀請成員**：`POST /api/groups/{id}/invite`
- **回覆邀請**：`POST /api/invitations/{id}/accept|reject`
- **角色管理**：`PUT /api/groups/{group_id}/members/{member_id}/role`
- **退出群組**：`POST /api/groups/{id}/leave`

---

## 📑 API 範例

### 登入 (取得 JWT)

`POST /api/login`

**Request**

```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response**

```json
{
  "message": "Logged in successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "testuser",
    "created_at": "2024-01-01T10:00:00",
    "is_active": true
  }
}
```

## 📷 預覽圖

# 登入與註冊

![畫面預覽](./ReadMeImg/登入.png)
![畫面預覽](./ReadMeImg/註冊.png)

## 首頁

![畫面預覽](./ReadMeImg/首頁.png)
![畫面預覽(響應式)](./ReadMeImg/響應式設計首頁.png)

## 交易紀錄

![畫面預覽](./ReadMeImg/交易紀錄.png)
![畫面預覽(響應式)](./ReadMeImg/響應式交易紀錄.png)

## 類別管理

![畫面預覽](./ReadMeImg/類別管理.png)
![畫面預覽(響應式)](./ReadMeImg/響應式類別管理.png)

## 群組記帳

![畫面預覽](./ReadMeImg/群組記帳.png)
![畫面預覽(響應式)](./ReadMeImg/響應式群組記帳.png)

## 群組記帳內部

![畫面預覽](./ReadMeImg/群組記帳內部.png)
![畫面預覽(響應式)](./ReadMeImg/響應式群組記帳內部.png)

## 設定

![畫面預覽(響應式)](./ReadMeImg/響應式設定.png)
