import csv, smtplib
from email.mime.text import MIMEText
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from app.storage import DB
from app.agents.models import EmailRecipient

scheduler = BackgroundScheduler()
scheduler.start()

def load_recipients_from_csv(file_path: str) -> List[EmailRecipient]:
    recips: List[EmailRecipient] = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("email"): 
                continue
            recips.append(EmailRecipient(name=row.get("name"), email=row["email"]))
    DB.recipients = recips
    return recips

def send_email_batch(subject: str, body: str, smtp_host: str, smtp_port: int, sender: str, username: str, password: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(username, password)
        for r in DB.recipients:
            msg["To"] = r.email
            server.sendmail(sender, [r.email], msg.as_string())

def schedule_email_job(subject: str, body_template: str, cron: str | None, smtp_cfg: dict):
    # Build headlines body
    headlines = "\n".join([f"- {a.source}: {a.title}" for a in DB.list_articles()[:10]]) or "No headlines."
    body = body_template.format(headlines=headlines)

    if cron:
        # cron format: "*/30 * * * *" (every 30 min)
        minute, hour, day, month, weekday = cron.split()
        scheduler.add_job(
            send_email_batch,
            "cron",
            args=[subject, body, smtp_cfg["host"], smtp_cfg["port"], smtp_cfg["sender"], smtp_cfg["username"], smtp_cfg["password"]],
            minute=minute, hour=hour, day=day, month=month, day_of_week=weekday,
            replace_existing=True, id="news_email_job",
        )
    else:
        send_email_batch(subject, body, smtp_cfg["host"], smtp_cfg["port"], smtp_cfg["sender"], smtp_cfg["username"], smtp_cfg["password"])
