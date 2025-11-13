import csv, smtplib
from email.mime.text import MIMEText
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from app.storage import DB
from app.agents.models import EmailRecipient

scheduler = BackgroundScheduler()
scheduler.start()

# def load_recipients_from_csv(file_path: str) -> List[EmailRecipient]:
#     recips: List[EmailRecipient] = []
#     with open(file_path, newline="", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             if not row.get("email"): 
#                 continue
#             recips.append(EmailRecipient(name=row.get("name"), email=row["email"]))
#     DB.recipients = recips
#     return recips

import csv
from typing import List
from app.storage import DB
from app.agents.models import EmailRecipient

import csv, io
from typing import List
from app.storage import DB
from app.agents.models import EmailRecipient

import csv, io
from typing import List
from app.storage import DB
from app.agents.models import EmailRecipient

import csv, io, re
from typing import List
from app.storage import DB
from app.agents.models import EmailRecipient

DELIMS = [",", ";", "\t"]

def _detect_delim(first_line: str) -> str:
    # Prefer comma; else semicolon; else tab; else comma
    for d in DELIMS:
        if d in first_line:
            return d
    return ","

def _force_split_if_needed(row: list[str], delim: str) -> list[str]:
    # Sometimes csv.reader gives a single cell containing the whole line
    if len(row) == 1:
        cell = (row[0] or "").strip()
        # If the cell still contains a known delimiter, split it manually
        if any(d in cell for d in DELIMS):
            # Normalize all to comma, then split
            normalized = re.sub(r"[;\t]", ",", cell)
            return [c.strip() for c in normalized.split(",")]
    return row

def load_recipients_from_csv(file_path: str) -> List[EmailRecipient]:
    recips: List[EmailRecipient] = []

    # Read whole file as text; utf-8-sig strips BOM
    with open(file_path, encoding="utf-8-sig", newline="") as f:
        text = f.read()

    # Detect delimiter from the first non-empty line
    first_non_empty = next((ln for ln in text.splitlines() if ln.strip()), "")
    delim = _detect_delim(first_non_empty)

    reader = csv.reader(io.StringIO(text), delimiter=delim)

    # Peek first row
    first = next(reader, None)
    if first is None:
        DB.recipients = []
        return []

    first = _force_split_if_needed([(c or "").strip() for c in first], delim)
    lower = [c.lower() for c in first]
    # Header if it mentions 'email' or 'name' anywhere
    is_header = any(h in {"email", "e-mail", "mail", "name"} for h in lower)

    rows_iter = reader if is_header else iter([first] + list(reader))

    for row in rows_iter:
        if not row:
            continue
        row = _force_split_if_needed([(c or "").strip() for c in row], delim)
        if not row:
            continue

        # Accept [name,email], [email], or more columns (take first two)
        if len(row) == 1:
            email, name = row[0], ""
        else:
            name, email = row[0], row[1]

        if email:
            recips.append(EmailRecipient(name=(name or None), email=email))

    # De-duplicate by email
    seen = set()
    uniq: List[EmailRecipient] = []
    for r in recips:
        if r.email not in seen:
            seen.add(r.email)
            uniq.append(r)

    DB.recipients = uniq
    return uniq



# def send_email_batch(subject: str, body: str, smtp_host: str, smtp_port: int, sender: str, username: str, password: str):
#     msg = MIMEText(body, "plain", "utf-8")
#     msg["Subject"] = subject
#     msg["From"] = sender

#     with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
#         server.login(username, password)
#         for r in DB.recipients:
#             msg["To"] = r.email
#             server.sendmail(sender, [r.email], msg.as_string())

def send_email_batch(subject: str, body: str, smtp_host: str, smtp_port: int,
                     sender: str, username: str, password: str):
    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(username, password)

        for r in DB.recipients:
            msg = MIMEText(body, "plain", "utf-8")  # NEW message each time
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = r.email
            # (optional) msg["Reply-To"] = sender

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
