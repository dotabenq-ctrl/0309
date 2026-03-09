import os
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="Supabase Render Web App")
templates = Jinja2Templates(directory="templates")

# Supabase 設定
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("Warning: SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables.")

# 建立 Supabase client (此處使用 anon key，對於單純新增與讀取來說已足夠)
supabase: Client = create_client(SUPABASE_URL or "", SUPABASE_ANON_KEY or "")

class NumberInput(BaseModel):
    value: int

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """使用者輸入頁面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """後台管理頁面"""
    # 將環境變數傳給前端，因為前端需要直接連線 Supabase Realtime
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_ANON_KEY": SUPABASE_ANON_KEY
    })

@app.post("/api/numbers")
async def create_number(data: NumberInput):
    """API 接收數字並寫入 Supabase"""
    try:
        response = supabase.table("numbers").insert({"value": data.value}).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/numbers")
async def get_numbers():
    """API 讀取最新 50 筆資料"""
    try:
        response = supabase.table("numbers").select("*").order("created_at", desc=True).limit(50).execute()
        return {"status": "success", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
