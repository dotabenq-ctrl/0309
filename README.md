# FastAPI + Supabase + Render MVP 專案

這是一個簡單的 Python Web App MVP，提供使用者輸入數字，並在後台使用 Supabase Realtime 即時顯示數字列表與危險狀態判斷。可直接部署到 Render。

## 技術與架構選型
* **後端**: Python 3.12 / FastAPI
* **資料庫**: Supabase (PostgreSQL)
* **前端**: HTML + JS (使用 Jinja2 模板引擎與 Supabase JS SDK)
* **部署**: Render

### 架構決策與取捨說明
1. **直接暴露 `SUPABASE_ANON_KEY` 給前端**:
   * 為了實作最順暢的 Supabase Realtime 訂閱，前端需要載入 Supabase JS SDK 並連線。
   * 此處使用的是 `anon key`，並配合 Supabase 上的 RLS (Row Level Security) 確保前端只擁有 `SELECT` 與接收 `INSERT` 事件的權限，這是官方建議的做法。
2. **沒有實作後台登入驗證**:
   * 根據需求建立 MVP。若為正式上線專案，強烈建議在 `/admin` 頁面加入 Auth 驗證（如 Supabase Auth 或 JWT），或者透過中介軟體保護路由。
3. **沒有用 React/Vue**:
   * 根據需求「簡單 HTML+JavaScript，不必使用 React」，減少前端打包建置步驟，簡化部署流程。

## 專案目錄結構
```
/
├── app/
│   └── main.py              # FastAPI 程式進入點與 API
├── templates/
│   ├── index.html           # 使用者輸入頁
│   └── admin.html           # 後台管理頁 (包含 Realtime 訂閱)
├── sql/
│   └── init.sql             # Supabase 資料表建置與 RLS 設定指令碼
├── requirements.txt         # Python 依賴套件表
├── render.yaml              # Render 藍圖部署設定檔
├── .env.example             # 環境變數範例檔
└── README.md                # 專案文件
```

---

## 本機測試步驟

### 1. 安裝環境與依賴
確保你已安裝 Python 3.12。
```bash
# 建立虛擬環境並啟動
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# 安裝套件
pip install -r requirements.txt
```

### 2. 初始化 Supabase
1. 註冊並登入 [Supabase](https://supabase.com/).
2. 建立新專案。
3. 進入左側選單 `SQL Editor`，貼上並執行 `sql/init.sql` 的內容，這將會：
   * 建立 `numbers` 資料表
   * 啟用 RLS 與對應的 Policy
   * 啟用 `supabase_realtime` publication。
4. 進入 `Project Settings` -> `Data API`：
   * 複製 `Project URL` 並且貼到 `.env` 的 `SUPABASE_URL`。
   * 找到 `anon` `public` API Key，複製並貼到 `.env` 的 `SUPABASE_ANON_KEY`。

### 3. 設定環境變數
複製 `.env.example` 為 `.env`，並填入剛剛拿到的 Key:
```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhb...
APP_ENV=development
PORT=8000
```

### 4. 啟動伺服器
```bash
uvicorn app.main:app --reload --port 8000
```
或直接執行 Python 檔若有設定：
```bash
python app/main.py
```
* **輸入頁面**: http://localhost:8000/
* **管理頁面**: http://localhost:8000/admin

---

## Render 部署步驟

本專案提供 `render.yaml` 支援 Blueprint 部署。

1. 將本專案推送到您的 GitHub 儲存庫。
2. 註冊並登入 [Render](https://render.com/).
3. 點選 **"New"** -> **"Blueprint"**。
4. 連結您的 GitHub 儲存庫。
5. Render 會自動讀取 `render.yaml` 設定，準備建立 FastAPI Web 服務。
6. 在 Render 的 Dashboard 面板中，輸入必要的環境變數 (Environment Variables)：
   * `SUPABASE_URL`: 填入與本機相同的 Supabase URL
   * `SUPABASE_ANON_KEY`: 填入與本機相同的 Supabase Anon Key
7. 部署完成後，即可點選 Render 產生的 URL 瀏覽應用程式。

---

## 驗收項目
- [x] 本機可正常啟動與執行。
- [x] 首頁具備數字輸入框與驗證。
- [x] API (`POST /api/numbers`) 成功將資料寫入 Supabase。
- [x] 後台 `/admin` 可讀取最新資料 (`GET /api/numbers`)。
- [x] **即時更新**: 採用 Supabase Realtime websocket，前端接收廣播自動加入最新列，不需 F5 重整。
- [x] 當數值 >= 55 時顯示「危險」(紅色)，< 55 顯示「正常」(綠色)。
- [x] 妥善分離敏感變數，透過 `.env` / Render environment 控制。
- [x] 附帶 `render.yaml` 與完整 README 指南供快速部署 Render。

## 尚未完成或正式上線前建議補強項目
1. **管理後台登入機制**: 目前 `/admin` 將直接暴露所有紀錄（因為使用的 Anon key 的 Policy 目前為全開 `true`）。上線前需修改 RLS 並加入登入 Auth。
2. **CORS 設定**: 若前後端分離部署，FastAPI 需要設定 `CORSMiddleware`。
3. **資料分頁**: 若資料量非常大，`/admin` 目前只拉最新 50 筆並用 Realtime 往前推。應加入更完整的分頁/虛擬捲動機制。
