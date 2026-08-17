import os
import re
import uuid
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modular UI package
from ui.styles import apply_custom_css, render_brand_header
from ui.components import render_chat_history, render_quick_suggestions
from ui.sidebar import render_sidebar

# Import Agno Team builder & storage/extraction tools
from agent.root_agent import build_stelar_team
from tools.storage_tools import (
    verify_email_deliverability,
    update_consultation_excel,
    save_chat_session,
    load_chat_session,
    extract_client_specs_llm
)

# Streamlit Page Setup
st.set_page_config(page_title="Stelar Interiors — AI Interior Design Consultant", page_icon="✨", layout="wide")
apply_custom_css()

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Welcome to **Stelar Interiors** 👋\n\nI am your lead design concierge. How may I assist you with your space today?"
    }]

if "requirements" not in st.session_state:
    st.session_state.requirements = {
        "client_name": None, "mobile_no": None, "location": None, "client_email": None,
        "site_visit_slot": None, "room_type": None, "room_length": None, "room_width": None,
        "unit": "feet", "style": None, "budget": None
    }


def build_conversation_context() -> str:
    """
    Build a conversation context string from the last N messages.
    This gives the Team leader full awareness of the ongoing conversation.
    """
    recent = st.session_state.messages[-12:]  # last 12 turns for context
    lines = []
    for msg in recent:
        role_label = "CLIENT" if msg["role"] == "user" else "CONCIERGE"
        lines.append(f"{role_label}: {msg['content']}")
    return "\n".join(lines)


# Render UI Shell
render_sidebar()
render_brand_header()
render_chat_history()

# Quick Suggestions & Input Controls
chip_input = render_quick_suggestions()

# Prompt Resend / Edit feature
with st.expander("✏️ Edit / Resend Previous Prompt", expanded=False):
    last_user_prompt = ""
    for m in reversed(st.session_state.messages):
        if m["role"] == "user":
            last_user_prompt = m["content"]
            break
    edited_prompt = st.text_input("Modify your previous query and resend:", value=last_user_prompt, key="resend_input")
    resend_clicked = st.button("🔄 Resend Updated Prompt", key="resend_btn")

user_input = st.chat_input("Ask Stelar Interiors design concierge...")
prompt = chip_input or (edited_prompt if resend_clicked and edited_prompt else user_input)

# Pure Agno Team Turn Execution
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    api_key = os.getenv("GEMINI_API_KEY")
    turn_data = {}  # Structured tool data for rich UI rendering

    # Build full conversation context
    context = build_conversation_context()

    # 1. LLM-Powered Client Specifications & Contact Details Extractor
    try:
        updated_reqs = extract_client_specs_llm(context, st.session_state.requirements)
        st.session_state.requirements.update(updated_reqs)
    except Exception:
        pass

    if api_key and api_key != "your_gemini_api_key_here":
        try:
            with st.spinner("✨ Stelar Concierge is coordinating with team..."):
                # Build and run the multi-agent team
                team = build_stelar_team()
                team_output = team.run(context)
                assistant_content = team_output.content

                if not assistant_content or not assistant_content.strip():
                    assistant_content = "I would be delighted to assist you further! Would you like to explore color palettes, calculate a 2D floor plan, or schedule a complimentary site visit?"

                # Extract which member was delegated to and call tools for structured UI data
                delegated_members = set()
                if team_output.tools:
                    for tool_exec in team_output.tools:
                        if tool_exec.tool_name == "delegate_task_to_member":
                            member_id = (tool_exec.tool_args or {}).get("member_id", "").lower()
                            delegated_members.add(member_id)

                reqs = st.session_state.requirements
                style_val = reqs.get("style") or "Warm Modern"
                room_val = reqs.get("room_type") or "Living Room"

                # DesignAdvisor was called → get palette + materials as structured dicts
                if "designadvisor" in delegated_members:
                    from tools.design_tools import generate_palette
                    from tools.web_tools import fetch_materials, web_search
                    turn_data["palette"] = generate_palette(style=style_val, room_type=room_val)
                    turn_data["materials"] = fetch_materials(style=style_val)
                    turn_data["web_results"] = web_search(f"{style_val} {room_val} interior design")

                # LayoutAgent was called → get layout as structured dict
                if "layoutagent" in delegated_members:
                    from tools.design_tools import calculate_layout
                    l_val = reqs.get("room_length") or 16.0
                    w_val = reqs.get("room_width") or 12.0
                    turn_data["layout"] = calculate_layout(room_length=l_val, room_width=w_val)

                # ResearchAgent was called → get web results as structured list
                if "researchagent" in delegated_members:
                    from tools.web_tools import web_search
                    turn_data["web_results"] = web_search(f"{style_val} {room_val} interior design inspiration")

                # BriefCoordinator was called → handle saving/dispatching brief
                if "briefcoordinator" in delegated_members:
                    from tools.storage_tools import save_consultation, send_email_consultation
                    dim_display = f"{reqs['room_length']} x {reqs['room_width']} ft" if (reqs.get('room_length') and reqs.get('room_width')) else 'Not specified'
                    budget_display = f"₹{reqs['budget']:,}" if reqs.get('budget') else 'Not specified'
                    client_ident = reqs.get("client_name") or reqs.get("location") or st.session_state.session_id
                    
                    brief_lines = [
                        "====================================================",
                        "                STELAR INTERIORS",
                        "             AI DESIGN CONSULTATION",
                        "====================================================",
                        f"SESSION ID: {st.session_state.session_id}",
                        f"Client Name: {reqs.get('client_name') or 'Not specified'}",
                        f"Mobile Number: {reqs.get('mobile_no') or 'Not specified'}",
                        f"Location / City: {reqs.get('location') or 'Not specified'}",
                        f"Room Type: {reqs.get('room_type') or 'Not specified'}",
                        f"Design Style: {reqs.get('style') or 'Not specified'}",
                        f"Dimensions: {dim_display}",
                        f"Budget: {budget_display}",
                        f"Site Visit Slot: {reqs.get('site_visit_slot') or 'Not specified'}",
                        f"Client Email: {reqs.get('client_email') or 'Not specified'}",
                        "===================================================="
                    ]
                    brief_text = "\n".join(brief_lines)
                    fpath = save_consultation(brief_text, client_identifier=client_ident)
                    turn_data["saved_file"] = fpath
                    target_email = reqs.get("client_email") or os.getenv("MAILTRAP_RECEIVER_EMAIL", "")
                    if target_email:
                        email_res = send_email_consultation(target_email, brief_text, filename=os.path.basename(fpath))
                        turn_data["email_status"] = email_res

        except Exception as e:
            assistant_content = "Thank you for your interest! Our design team is ready to assist. Would you like to explore palettes or schedule a complimentary site visit?"
    else:
        assistant_content = "Welcome to Stelar Interiors! Please configure `GEMINI_API_KEY` in `.env` to activate the multi-agent design concierge."

    assistant_msg = {
        "role": "assistant",
        "content": assistant_content
    }
    assistant_msg.update(turn_data)

    # 2. Persist to Excel leads database on every message
    try:
        update_consultation_excel(
            session_id=st.session_state.session_id,
            requirements=st.session_state.requirements,
            latest_message=prompt,
            assistant_response=assistant_content
        )
    except Exception:
        pass

    st.session_state.messages.append(assistant_msg)

    # 3. Persist local chat session to saved_chats/{session_id}.json
    try:
        save_chat_session(
            session_id=st.session_state.session_id,
            messages=st.session_state.messages,
            requirements=st.session_state.requirements
        )
    except Exception:
        pass

    st.rerun()
