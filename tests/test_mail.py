import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from scheduler import add_to_queue, run_daily_mailtrap_dispatch, load_queue
from tools.storage_tools import save_consultation, send_email_consultation

print("====================================================")
print("       STELAR INTERIORS — MAILTRAP TEST SUITE        ")
print("====================================================\n")

recipient = os.getenv("MAILTRAP_RECEIVER_EMAIL", "")
print(f"Target Email: {recipient}")
print(f"API Token Configured: {'YES' if os.getenv('MAIL_TRAP_API_TOKEN') else 'NO'}")
print(f"Schedule Time: {os.getenv('EMAIL_SCHEDULE_TIME', '14:00')} PM\n")

# 1. Create a sample consultation brief file
sample_brief = f"""====================================================
                STELAR INTERIORS
             AI DESIGN CONSULTATION
====================================================
DATE: 2026-08-16 23:35:00
SESSION ID: TEST-MAILTRAP-001

CLIENT SPECS:
Room: Living Room
Dimensions: 12 x 16 ft
Style: Warm Modern
Budget: Rs 3,00,000 INR
Client Email: {recipient}

PALETTE & MATERIALS:
Palette: Warm Modern Neutral (#D8C3A5, #5A3825, #C76B4A)
Materials: American Walnut Veneer, Lime Wash Paint, Travertine Stone.

LAYOUT RECOMMENDATION:
Footprint Fit: Validated (55% floor coverage limit maintained)
Arrangement: North wall sofa, Center coffee table, South wall TV unit.
====================================================
END OF CONSULTATION
====================================================
"""

filepath = save_consultation(sample_brief, client_identifier="TEST_MAILTRAP")
print(f"Generated Test Brief File: {filepath}")

# 2. Add to Pending Queue for batch dispatch
entry = add_to_queue("TEST-MAILTRAP-001", recipient, filepath, sample_brief)
print(f"Queued Entry in pending_queue.json: {entry['filename']} (Status: {entry['status']})\n")

# 3. Direct Send Test
print("Testing Direct Mailtrap Delivery...")
direct_res = send_email_consultation(recipient, sample_brief, filename=os.path.basename(filepath))
print(f"Direct Mail Output: {direct_res}\n")

# 4. Batch Dispatcher Test
print("Testing Batch Dispatcher (run_daily_mailtrap_dispatch)...")
batch_res = run_daily_mailtrap_dispatch()
print(f"Batch Dispatcher Output: {batch_res}\n")

print("====================================================")
print("TEST COMPLETED. Check pending_queue.json status.")
print("====================================================")
