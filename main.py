from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="軟體工程期中作業 - 稿件管理系統")

# 設定樣板目錄
templates = Jinja2Templates(directory="templates")

# 資料模型 (Pydantic 驗證)
class ArticleCreate(BaseModel):
    author: str
    category: str
    title: str
    content: str

class ArticleUpdateStatus(BaseModel):
    status: str  # draft, reviewing, approved

# 模擬記憶體資料庫
articles_db = [
    {
        "id": 1,
        "author": "王小明",
        "category": "技術",
        "title": "FastAPI 快速入門",
        "content": "這是文章內容...",
        "status": "draft"
    },
    {
        "id": 2,
        "author": "李大華",
        "category": "生活",
        "title": "我的期中專案日誌",
        "content": "這是內容...",
        "status": "reviewing"
    }
]

# 1. 首頁路由：回傳前端 HTML 畫面
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")

# 2. API: 取得所有稿件
@app.get("/api/articles")
async def get_articles():
    return articles_db

# 3. API: 新增稿件 (預設狀態為編輯中 draft)
@app.post("/api/articles")
async def create_article(article: ArticleCreate):
    new_id = max([a["id"] for a in articles_db], default=0) + 1
    new_item = {
        "id": new_id,
        "author": article.author,
        "category": article.category,
        "title": article.title,
        "content": article.content,
        "status": "draft"  # 狀態: 編輯中
    }
    articles_db.append(new_item)
    return {"success": True, "article": new_item}

# 4. API: 刪除稿件 (僅限狀態為 draft 編輯中)
@app.delete("/api/articles/{article_id}")
async def delete_article(article_id: int):
    global articles_db
    article = next((a for a in articles_db if a["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="找不到該稿件")
    if article["status"] != "draft":
        raise HTTPException(status_code=400, detail="只能刪除編輯中的稿件")
    
    articles_db = [a for a in articles_db if a["id"] != article_id]
    return {"success": True, "message": "刪除成功"}

# 5. API: 更新稿件狀態 (送出審查、通過、退回)
@app.patch("/api/articles/{article_id}/status")
async def update_status(article_id: int, body: ArticleUpdateStatus):
    article = next((a for a in articles_db if a["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="找不到該稿件")
    
    article["status"] = body.status
    return {"success": True, "article": article}