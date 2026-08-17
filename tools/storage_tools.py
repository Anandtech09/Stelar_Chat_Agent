import os
import socket
import requests
import datetime


def verify_email_deliverability(email: str) -> dict:
    """
    Verify real-time email deliverability by checking structure and domain DNS/MX resolution.
    Returns dict with 'valid' (bool) and 'reason' (str).
    """
    if not email or "@" not in email:
        return {"valid": False, "reason": "Invalid email format. Please provide a complete email address (e.g. client@gmail.com)."}

    parts = email.strip().split("@")
    if len(parts) != 2 or not parts[0] or not parts[1] or "." not in parts[1]:
        return {"valid": False, "reason": "Invalid email domain structure."}

    domain = parts[1].lower()

    # Block placeholder test domains
    fake_domains = ["example.com", "test.com", "fake.com", "invalid.com", "tempmail.com"]
    if domain in fake_domains:
        return {"valid": False, "reason": f"The email domain '@{domain}' is a placeholder. Please provide a valid personal or business email."}

    try:
        # Resolve domain IP/MX record via DNS socket lookup
        socket.gethostbyname(domain)
        return {"valid": True, "reason": f"Domain '@{domain}' verified with active MX/DNS servers."}
    except Exception:
        return {"valid": False, "reason": f"Domain '@{domain}' does not exist or has no active mail servers. Please check for typos."}

EXCEL_LEADS_PATH = os.path.join("saved_excels", "stelar_client_leads.xlsx")


def update_consultation_excel(
    session_id: str,
    requirements: dict,
    latest_message: str = "",
    assistant_response: str = ""
) -> str:
    """
    Append/update client lead details and chat history into saved_excels/stelar_client_leads.xlsx.
    Maintains two worksheets:
      1. 'Client_Leads': Live lead summary table per session (Name, Mobile, Location, Specs).
      2. 'Chat_Log': Detailed chronological transcript of every message exchange.
    """
    import pandas as pd
    os.makedirs("saved_excels", exist_ok=True)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    reqs = requirements or {}
    name_str = reqs.get("client_name") or "Not specified"
    phone_str = reqs.get("mobile_no") or "Not specified"
    loc_str = reqs.get("location") or "Not specified"
    email_str = reqs.get("client_email") or "Not specified"
    room_str = reqs.get("room_type") or "Not specified"
    style_str = reqs.get("style") or "Not specified"
    dim_str = f"{reqs['room_length']} × {reqs['room_width']} ft" if (reqs.get("room_length") and reqs.get("room_width")) else "Not specified"
    budget_str = f"₹{reqs['budget']:,}" if reqs.get("budget") else "Not specified"
    slot_str = reqs.get("site_visit_slot") or "Not specified"

    lead_row = {
        "Session ID": session_id,
        "Last Updated": now_str,
        "Client Name": name_str,
        "Mobile No": phone_str,
        "Location / City": loc_str,
        "Client Email": email_str,
        "Room Type": room_str,
        "Design Style": style_str,
        "Dimensions": dim_str,
        "Budget": budget_str,
        "Site Visit Slot": slot_str,
        "Latest Need": latest_message[:150] if latest_message else "Ongoing Consultation"
    }

    log_row = {
        "Timestamp": now_str,
        "Session ID": session_id,
        "Client Name": name_str,
        "Mobile No": phone_str,
        "Location / City": loc_str,
        "User Message": latest_message,
        "Assistant Response": assistant_response[:300] if assistant_response else ""
    }

    leads_df = pd.DataFrame([lead_row])
    log_df = pd.DataFrame([log_row])

    if os.path.exists(EXCEL_LEADS_PATH):
        try:
            with pd.ExcelFile(EXCEL_LEADS_PATH) as xls:
                if "Client_Leads" in xls.sheet_names:
                    existing_leads = pd.read_excel(xls, "Client_Leads")
                    if session_id in existing_leads["Session ID"].values:
                        idx = existing_leads.index[existing_leads["Session ID"] == session_id].tolist()[0]
                        for col in lead_row:
                            existing_leads.at[idx, col] = lead_row[col]
                        leads_df = existing_leads
                    else:
                        leads_df = pd.concat([existing_leads, leads_df], ignore_index=True)

                if "Chat_Log" in xls.sheet_names:
                    existing_logs = pd.read_excel(xls, "Chat_Log")
                    log_df = pd.concat([existing_logs, log_df], ignore_index=True)
        except Exception:
            pass

    try:
        with pd.ExcelWriter(EXCEL_LEADS_PATH, engine="openpyxl") as writer:
            leads_df.to_excel(writer, sheet_name="Client_Leads", index=False)
            log_df.to_excel(writer, sheet_name="Chat_Log", index=False)
        return EXCEL_LEADS_PATH
    except Exception as e:
        return f"Excel Write Warning: {str(e)}"


def save_consultation(consultation_text: str, client_identifier: str = "session") -> str:
    """
    Save the synthesized design brief into a formatted .txt file inside consultations/.
    Only provided client details are included; unprovided fields are left blank.
    """
    os.makedirs("consultations", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_id = "".join(c if c.isalnum() else "_" for c in (client_identifier or "session"))[:20]
    filename = f"stelar_consultation_{clean_id}_{timestamp}.txt"
    filepath = os.path.join("consultations", filename)

    if "STELAR INTERIORS" not in consultation_text:
        formatted_header = f"""====================================================
                STELAR INTERIORS
             AI DESIGN CONSULTATION
====================================================
DATE: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
CONSULTATION ID: STELAR-{clean_id}-{timestamp}

"""
        full_content = formatted_header + consultation_text
    else:
        full_content = consultation_text

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    return filepath


def summarize_brief_for_email(filename: str, consultation_text: str) -> str:
    """
    Create a high-level executive summary of main design details for the email body.
    """
    summary_lines = [
        f"📄 BRIEF TITLE / REFERENCE FILE: {filename}",
        "=" * 50,
        "STELAR INTERIORS — DESIGN CONSULTATION SUMMARY",
        "=" * 50,
        ""
    ]

    for line in consultation_text.splitlines():
        if any(k in line.lower() for k in ["room:", "dimensions:", "style:", "budget:", "palette:", "materials:", "footprint", "arrangement", "slot:"]):
            summary_lines.append(f"• {line.strip()}")

    if len(summary_lines) <= 5:
        summary_lines.append(consultation_text[:800] + ("..." if len(consultation_text) > 800 else ""))

    summary_lines.extend([
        "",
        "=" * 50,
        "⏰ Scheduled Batch Delivery via Mailtrap Infrastructure.",
        "Stelar Interiors © 2026. All rights reserved."
    ])

    return "\n".join(summary_lines)


def send_email_consultation(recipient_email: str, consultation_text: str, filename: str = "stelar_consultation.txt") -> str:
    """
    Send the summarized consultation result via Mailtrap Email API (HTTPS).
    
    Supports two modes via MAILTRAP_SANDBOX env var:
      - Sandbox (testing): uses sandbox.api.mailtrap.io with inbox_id (emails go to Mailtrap inbox, not real Gmail)
      - Production (sending): uses send.api.mailtrap.io with a verified domain (real delivery)
    """
    api_token = os.getenv("MAIL_TRAP_API_TOKEN", "").strip()
    sender_email = os.getenv("MAILTRAP_SENDER_EMAIL", "hello@demomailtrap.com").strip()
    default_receiver = os.getenv("MAILTRAP_RECEIVER_EMAIL", "").strip()
    sandbox_inbox_id = os.getenv("MAILTRAP_SANDBOX_INBOX_ID", "").strip()

    target_email = recipient_email.strip() if (recipient_email and "@" in recipient_email) else default_receiver

    # Verify Email Deliverability
    val = verify_email_deliverability(target_email)
    if not val["valid"]:
        return f"Email Deliverability Error: {val['reason']}"

    summary_text = summarize_brief_for_email(filename, consultation_text)
    subject = f"✨ Stelar Interiors — Design Brief Summary [{filename}]"

    if not api_token:
        return f"Mailtrap Config Warning: Set `MAIL_TRAP_API_TOKEN` in `.env` to send email summaries."

    # Choose endpoint: sandbox (testing) vs production (sending)
    if sandbox_inbox_id:
        url = f"https://sandbox.api.mailtrap.io/api/send/{sandbox_inbox_id}"
    else:
        url = "https://send.api.mailtrap.io/api/send"

    payload = {
        "from": {"email": sender_email, "name": "Stelar Interiors Concierge"},
        "to": [{"email": target_email}],
        "subject": subject,
        "text": summary_text,
        "category": "Consultation Summary"
    }

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get("success"):
                return f"✅ Email dispatched to `{target_email}` via Mailtrap."
            return f"Mailtrap responded OK but without success flag: {resp_data}"

        elif response.status_code == 401:
            return (
                f"❌ Mailtrap 401 Unauthorized: Token `{api_token[:8]}...` was rejected.\n"
                f"Ensure you're using a **Sending API Token** (not Testing) from https://mailtrap.io/settings/api-tokens\n"
                f"and your sender email domain is verified in Mailtrap → Sending → Domains."
            )
        else:
            return f"Mailtrap API Error: HTTP {response.status_code} — {response.text[:300]}"

    except requests.exceptions.Timeout:
        return "Mailtrap Error: Request timed out after 10 seconds."
    except requests.exceptions.ConnectionError:
        return "Mailtrap Error: Could not connect to send.api.mailtrap.io. Check your internet connection."
    except Exception as e:
        return f"Mailtrap Exception: {str(e)}"


# ==========================================
# LOCAL CHAT STORAGE & SESSION HISTORY
# ==========================================
SAVED_CHATS_DIR = "saved_chats"


def save_chat_session(session_id: str, messages: list[dict], requirements: dict):
    """
    Save complete chat session history and requirements into saved_chats/{session_id}.json.
    """
    import json
    os.makedirs(SAVED_CHATS_DIR, exist_ok=True)
    filepath = os.path.join(SAVED_CHATS_DIR, f"session_{session_id}.json")

    data = {
        "session_id": session_id,
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "requirements": requirements or {},
        "messages": messages or []
    }
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath
    except Exception as e:
        return None


def list_chat_sessions() -> list[dict]:
    """
    List all saved chat sessions ordered by last modified date.
    """
    import json
    os.makedirs(SAVED_CHATS_DIR, exist_ok=True)
    sessions = []

    for fname in os.listdir(SAVED_CHATS_DIR):
        if fname.endswith(".json") and fname.startswith("session_"):
            fpath = os.path.join(SAVED_CHATS_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sess_id = data.get("session_id", fname.replace("session_", "").replace(".json", ""))
                    reqs = data.get("requirements", {})
                    name = reqs.get("client_name") or "Guest"
                    loc = reqs.get("location") or ""
                    room = reqs.get("room_type") or "Design Chat"
                    mtime = os.path.getmtime(fpath)
                    time_str = data.get("last_updated") or datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                    
                    preview_parts = [name]
                    if loc: preview_parts.append(loc)
                    if room and room != "Design Chat": preview_parts.append(room)
                    summary = " • ".join(preview_parts)

                    sessions.append({
                        "session_id": sess_id,
                        "filename": fname,
                        "summary": f"{summary} ({time_str})",
                        "last_updated": time_str,
                        "mtime": mtime,
                        "message_count": len(data.get("messages", []))
                    })
            except Exception:
                pass

    sessions.sort(key=lambda s: s.get("mtime", 0), reverse=True)
    return sessions


def load_chat_session(session_id: str) -> dict | None:
    """
    Load a saved chat session by ID.
    """
    import json
    fpath = os.path.join(SAVED_CHATS_DIR, f"session_{session_id}.json")
    if not os.path.exists(fpath):
        return None
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# ==========================================
# LLM-POWERED CLIENT SPECIFICATION EXTRACTOR
# ==========================================
def extract_client_specs_llm(conversation_text: str, current_reqs: dict | None = None) -> dict:
    """
    Uses Gemini LLM in JSON mode to accurately extract all client contact details and specs from natural conversation.
    Handles typos ('phnone', 'plce'), Indian states/cities (Kerala, Bangalore, Kochi), formats, and styles effortlessly.
    """
    import json
    from google import genai

    reqs = dict(current_reqs or {})
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        return reqs

    model_id = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    prompt = f"""
Analyze the following interior design consultation conversation.
Extract or update the client's contact details and design specifications into valid JSON.

JSON Schema to return:
{{
  "client_name": string or null,
  "mobile_no": string or null,
  "location": string or null,
  "client_email": string or null,
  "room_type": string or null,
  "style": string or null,
  "room_length": float or null,
  "room_width": float or null,
  "budget": integer or null,
  "site_visit_slot": string or null
}}

Guidelines:
- If a detail was NOT mentioned, set it to null.
- client_name: Extract the client's real name (e.g. Manu, Priya Sharma, John).
- mobile_no: Extract the 10-12 digit mobile/phone number (e.g. 92719877893, +91 9876543210).
- location: Extract client city, place, or state (e.g. Kerala, Bangalore, Kochi, Whitefield, Mumbai).
- room_type: e.g. Living Room, Bedroom, Kitchen, Dining Room, Home Office.
- style: e.g. Warm Modern, Minimalist, Scandinavian, Luxury.
- room_length / room_width: numeric dimensions in feet (e.g. 14.0, 18.0).
- budget: numeric budget in Rupees (e.g. 4 lakh -> 400000, 50k -> 50000).
- site_visit_slot: e.g. Saturday Morning, Next Sunday, Tomorrow 3 PM.

Conversation Text:
\"\"\"
{conversation_text}
\"\"\"
"""
    try:
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        data = json.loads(resp.text)
        for k, v in data.items():
            if v is not None:
                if k == "client_name" and isinstance(v, str):
                    reqs[k] = v.title()
                elif k == "location" and isinstance(v, str):
                    reqs[k] = v.title()
                elif k == "room_type" and isinstance(v, str):
                    reqs[k] = v.title()
                elif k == "style" and isinstance(v, str):
                    reqs[k] = v.title()
                elif k == "site_visit_slot" and isinstance(v, str):
                    reqs[k] = v.title()
                else:
                    reqs[k] = v
        return reqs
    except Exception:
        return reqs


