import os
import json
import logging
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from tools.storage_tools import send_email_consultation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StelarScheduler")

QUEUE_FILE = os.path.join("consultations", "pending_queue.json")


def load_queue() -> list[dict]:
    if not os.path.exists(QUEUE_FILE):
        return []
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_queue(queue: list[dict]):
    os.makedirs("consultations", exist_ok=True)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)


def add_to_queue(session_id: str, email: str, filepath: str, brief_text: str):
    queue = load_queue()
    filename = os.path.basename(filepath) if filepath else "stelar_consultation.txt"
    entry = {
        "session_id": session_id,
        "email": email or os.getenv("MAILTRAP_RECEIVER_EMAIL", "@gmail.com"),
        "filepath": filepath,
        "filename": filename,
        "brief_text": brief_text,
        "status": "PENDING",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    queue.append(entry)
    save_queue(queue)
    logger.info(f"Queued consultation summary for {filename} -> {email}")
    return entry


def run_daily_mailtrap_dispatch():
    """
    Sweeps all PENDING consultation briefs in pending_queue.json, summarizes them, and sends via Mailtrap API.
    Triggered automatically at 2:00 PM daily.
    """
    logger.info("Starting scheduled 2:00 PM Mailtrap API batch dispatch...")
    queue = load_queue()
    pending_items = [item for item in queue if item.get("status") == "PENDING"]

    if not pending_items:
        logger.info("No pending consultations found for 2:00 PM dispatch.")
        return "No pending consultations in queue."

    dispatched_count = 0
    for item in pending_items:
        email = item.get("email", os.getenv("MAILTRAP_RECEIVER_EMAIL", ""))
        brief_text = item.get("brief_text", "")
        filename = item.get("filename", os.path.basename(item.get("filepath", "stelar_consultation.txt")))
        res = send_email_consultation(email, brief_text, filename=filename)
        item["status"] = "DISPATCHED"
        item["dispatched_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item["dispatch_notes"] = res
        dispatched_count += 1

    save_queue(queue)
    status_msg = f"Successfully dispatched {dispatched_count} consultation summaries via Mailtrap SDK."
    logger.info(status_msg)
    return status_msg


_scheduler_instance = None


def start_scheduler():
    global _scheduler_instance
    if _scheduler_instance is not None:
        return _scheduler_instance

    schedule_time = os.getenv("EMAIL_SCHEDULE_TIME", "14:00")
    try:
        hour, minute = map(int, schedule_time.split(":"))
    except ValueError:
        hour, minute = 14, 0

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        run_daily_mailtrap_dispatch,
        trigger="cron",
        hour=hour,
        minute=minute,
        id="mailtrap_2pm_dispatch",
        replace_existing=True
    )
    scheduler.start()
    _scheduler_instance = scheduler
    logger.info(f"Background Scheduler started for Mailtrap API daily dispatch at {schedule_time} ({hour:02d}:{minute:02d}).")
    return scheduler
