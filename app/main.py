from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os, uuid

from app.storage import DB
from app.agents.models import ArticleCreate, ArticleUpdate, ScheduleRequest
from app.agents.crawler import fetch_rss_articles, fetch_html_article
from app.agents.emailer import load_recipients_from_csv, schedule_email_job

app = FastAPI(title="News Multi-Agent POC")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse("app/static/index.html")

# --------- Crawl endpoints ----------
@app.post("/crawl")
def crawl(source: Optional[str] = None, limit: int = 10):
    sources = [source] if source else ["BBC", "CNN", "FOX"]
    added = []
    for src in sources:
        items = fetch_rss_articles(src, limit=limit)
        for it in items:
            content = it["content"]
            # Optionally pull full content:
            # content = fetch_html_article(it["url"])
            art = DB.add_article(src, it["title"], it["url"], content)
            added.append(art)
    return {"added": len(added)}

# --------- Articles CRUD ----------
@app.get("/articles")
def list_articles():
    return DB.list_articles()

@app.put("/articles/{article_id}")
def update_article(article_id: int, payload: ArticleUpdate):
    art = DB.update_article(article_id, payload.title, payload.content)
    if not art: return {"error": "not found"}
    return art

@app.delete("/articles/{article_id}")
def delete_article(article_id: int):
    ok = DB.delete_article(article_id)
    return {"deleted": ok}

# --------- Emails ----------
@app.post("/upload-recipients")
def upload_recipients(file: UploadFile = File(...)):
    tmp = f"/tmp/{uuid.uuid4()}_{file.filename}"
    with open(tmp, "wb") as f:
        f.write(file.file.read())
    recips = load_recipients_from_csv(tmp)
    os.remove(tmp)
    return {"loaded": len(recips)}

@app.post("/schedule-email")
def schedule_email(req: ScheduleRequest,
                   smtp_host: str = Form(...),
                   smtp_port: int = Form(465),
                   sender: str = Form(...),
                   username: str = Form(...),
                   password: str = Form(...)):
    schedule_email_job(
        subject=req.subject,
        body_template=req.body_template,
        cron=req.cron,
        smtp_cfg={"host": smtp_host, "port": smtp_port, "sender": sender, "username": username, "password": password}
    )
    return {"status": "scheduled" if req.cron else "sent-once"}
