import os
import sys
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from scheduler import run_daily_mailtrap_dispatch, start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("StandaloneScheduler")

if __name__ == "__main__":
    print("====================================================")
    print("      STELAR INTERIORS — STANDALONE SCHEDULER      ")
    print("====================================================\n")

    schedule_time = os.getenv("EMAIL_SCHEDULE_TIME", "14:00")
    print(f"⏰ Daily Batch Schedule Target: {schedule_time} PM")
    print(f"📧 Mailtrap Receiver: {os.getenv('MAILTRAP_RECEIVER_EMAIL', '')}")
    print(f"🔑 API Token Status: {'CONFIGURED' if os.getenv('MAIL_TRAP_API_TOKEN') else 'MISSING'}\n")
    print("Running background scheduler daemon... Press Ctrl+C to stop.\n")

    # Start APScheduler in standalone mode
    scheduler = start_scheduler()

    # Perform initial check on launch
    print("Performing startup check for any pending consultations...")
    res = run_daily_mailtrap_dispatch()
    print(f"Startup Check Result: {res}\n")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\nStopping Standalone Scheduler Daemon...")
        if scheduler:
            scheduler.shutdown()
        print("Scheduler stopped.")
