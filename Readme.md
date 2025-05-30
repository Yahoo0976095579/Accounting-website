# 💸 記帳網站 (Accounting Web App)

一個功能豐富的個人與群組記帳 Web 應用程式，旨在幫助使用者輕鬆追蹤個人收支，並支援未來擴展的群組協同記帳功能。

## ✨ 主要功能

- **使用者認證：** 註冊、登入、登出，以及基於會話的安全認證。
- **個人記帳：**
  - 新增、編輯、刪除、查看交易記錄。
  - 支援按類型、類別、日期範圍、描述進行多條件篩選與搜尋。
  - 交易記錄分頁顯示。
- **類別管理：**
  - 自定義收支類別的 CRUD 功能。
- **儀表板概覽：**
  - 顯示總收入、總支出與當前結餘。
  - 展示收支趨勢與類別分佈資料。
- **使用者體驗優化：**
  - Navbar 響應式設計，小螢幕轉為漢堡選單。
  - 日期篩選器與按鈕適應各裝置。
  - 載入提示與通知訊息設計友善。
  - 模態框點擊外部不關閉，按鈕置中。

## 🚀 技術棧

### 前端 (Client)

- **Vue 3 (Composition API)** - 建構互動式 UI。
- **Vite** - 快速的前端建構工具。
- **Pinia** - Vue 狀態管理。
- **Vue Router** - 頁面導航。
- **Axios** - 與後端 API 溝通。
- **Tailwind CSS (v3.x)** - 快速開發響應式 UI。

### 後端 (Server)

- **Python 3** - 程式語言。
- **Flask** - 輕量級 Web 框架。
- **Flask-SQLAlchemy** - ORM 整合。
- **SQLite** - 本地資料庫。
- **Flask-Login** - 使用者會話與認證管理。
- **Flask-CORS** - 前後端跨域設定。
- **Werkzeug** - 密碼加密。
- **python-dotenv** - 載入 `.env` 環境變數。

## 📦 專案結構

accounting-app/
├── client/ # Vue.js 前端應用
│ ├── public/ # 靜態資產
│ ├── src/
│ │ ├── assets/ # 圖片、圖標等
│ │ ├── components/ # 可重用 UI 元件
│ │ ├── router/ # Vue Router 設定
│ │ ├── stores/ # Pinia 狀態管理
│ │ ├── views/ # 頁面組件
│ │ ├── App.vue # 根元件
│ │ ├── main.js # 入口文件
│ │ └── style.css # 全域樣式 (含 Tailwind)
│ ├── .env.development # 前端環境變數
│ ├── package.json
│ ├── tailwind.config.js
│ └── vite.config.js
├── server/ # Flask 後端應用
│ ├── venv/ # 虛擬環境 (被 .gitignore 忽略)
│ ├── app.py # 主應用檔案
│ ├── site.db # SQLite DB (被 .gitignore 忽略)
│ ├── .env # 環境變數 (被 .gitignore 忽略)
│ └── requirements.txt # Python 套件列表
├── .gitignore
└── README.md

## ⚙️ 如何運行專案

請確保您已安裝好 **Node.js**（含 npm）與 **Python 3**。

### 1️⃣ 克隆專案

```bash
git clone https://github.com/YourGitHubUsername/your-repo-name.git
cd your-repo-name
```

## 2️⃣ 後端設定

cd server

# 建立虛擬環境

python -m venv venv

# 啟用虛擬環境

# Windows:

.\venv\Scripts\activate

# macOS/Linux:

source venv/bin/activate

# 安裝依賴

pip install Flask Flask-SQLAlchemy Flask-CORS python-dotenv Flask-Login Werkzeug

# 儲存依賴

pip freeze > requirements.txt

# 建立 .env 檔案

echo "SECRET_KEY=your_super_secret_key_here" > .env
echo "DATABASE_URL=sqlite:///site.db" >> .env

## 3️⃣ 前端設定

cd ../client
npm install

（若 Tailwind 未正確啟用）
npm install -D tailwindcss@^3.0.0 postcss autoprefixer
npx tailwindcss init -p

# 4️⃣ 同時運行應用程式

## 📡 終端機 1：啟動 Flask 後端

cd server

# 啟動虛擬環境（若尚未啟用）

# Windows: .\venv\Scripts\activate

# macOS/Linux: source venv/bin/activate

python app.py

## 💻 終端機 2：啟動 Vue 前端

cd client
npm run dev

## ✅ 開始使用

開啟瀏覽器訪問 http://localhost:5173

註冊新帳號

登入並開始使用記帳功能：儀表板、交易管理、類別管理

## 🌱 未來功能規劃（群組記帳）

群組建立與邀請成員

處理邀請與通知

群組共享記帳與分析

成員權限管理與審核

## 🤝 貢獻方式

歡迎任何形式的貢獻！
請開 issue 提交建議、錯誤回報或功能請求。

## 📜 授權條款

本專案採用 MIT 授權條款。
