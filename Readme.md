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
- 智能類型關聯與交易表單連動

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

### 1️⃣ 後端 (Flask)

````bash
# 進入後端專案資料夾
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝相依套件
pip install -r requirements.txt


建立 `.env` 檔案，設定：

* `SECRET_KEY`：Flask 密鑰
* `DATABASE_URL`：PostgreSQL URL（如連接 Render）
* `JWT_SECRET_KEY`：JWT 簽名密鑰

```bash
# 執行 Flask 伺服器
python app.py
````

---

### 2️⃣ 前端 (Vue 3)

```bash
# 進入前端專案資料夾
cd frontend

# 安裝依賴
npm install

# 運行開發伺服器
npm run dev
```

- 本地前端網址：[http://localhost:5173](http://localhost:5173)
- 本地後端 API： [http://localhost:5000](http://localhost:5000)

---

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

---

```md
---

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

![畫面預覽](./ReadMeImg/設定.png)
![畫面預覽(響應式)](./ReadMeImg/響應式設定.png)
```
