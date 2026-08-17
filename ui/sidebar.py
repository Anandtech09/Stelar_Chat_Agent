import os
import uuid
import streamlit as st
from scheduler import run_daily_mailtrap_dispatch
from tools.storage_tools import list_chat_sessions, load_chat_session


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding-bottom: 12px; border-bottom: 1px solid rgba(216,195,165,0.2);">
            <h3 style="color: #D8C3A5; letter-spacing: 0.1em; margin:0;">STELAR INTERIORS</h3>
            <p style="color: #8A8F9E; font-size: 0.8rem; margin: 4px 0 0 0;">AI DESIGN CONSULTANT</p>
        </div>
        """, unsafe_allow_html=True)

        # 1. Start New Consultation Button
        if st.button("➕ Start New Chat", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Welcome to **Stelar Interiors** 👋\n\nI am your lead design concierge. How may I assist you with your space today?"
                }
            ]
            st.session_state.requirements = {
                "client_name": None, "mobile_no": None, "location": None, "client_email": None,
                "site_visit_slot": None, "room_type": None, "room_length": None, "room_width": None,
                "unit": "feet", "style": None, "budget": None
            }
            st.session_state.palette = None
            st.session_state.materials = []
            st.session_state.layout = None
            st.session_state.web_results = []
            st.session_state.saved_file = None
            st.session_state.email_status = None
            st.rerun()

        # 2. Live Client Specs Section
        st.write("")
        st.markdown("<h4 style='color:#E6E8EC; margin-bottom:8px;'>LIVE CLIENT SPECS</h4>", unsafe_allow_html=True)

        reqs = st.session_state.requirements
        name_str = reqs.get("client_name") or "Not specified"
        mobile_str = reqs.get("mobile_no") or "Not specified"
        loc_str = reqs.get("location") or "Not specified"
        room_str = reqs.get("room_type") or "Not specified"
        style_str = reqs.get("style") or "Not specified"
        dim_str = f"{reqs['room_length']} × {reqs['room_width']} ft" if (reqs.get("room_length") and reqs.get("room_width")) else "Not specified"
        budget_str = f"₹{reqs['budget']:,}" if reqs.get("budget") else "Not specified"
        visit_slot = reqs.get("site_visit_slot") or "Not specified"
        email_str = reqs.get("client_email") or "Not specified"

        st.markdown(f"""
        <div class="sidebar-section">
            <div class="status-item"><span style="color:#A0A5B1;">Session ID</span><span style="color:#D8C3A5; font-weight:600;">{st.session_state.session_id}</span></div>
            <div class="status-item"><span style="color:#A0A5B1;">👤 Client Name</span><span style="color:#D8C3A5; font-weight:600;">{name_str}</span></div>
            <div class="status-item"><span style="color:#A0A5B1;">📱 Mobile No</span><span style="color:{'#55E6A5' if mobile_str != 'Not specified' else '#D8C3A5'}; font-weight:600;">{mobile_str}</span></div>
            <div class="status-item"><span style="color:#A0A5B1;">📍 Location / City</span><span style="color:#D8C3A5; font-weight:600;">{loc_str}</span></div>
            <div class="status-item"><span style="color:#A0A5B1;">Room Type</span><span style="color:#D8C3A5; font-weight:600;">{room_str}</span></div>
            <div class="status-item"><span style="color:#A0A5B1;">Design Style</span><span style="color:#D8C3A5; font-weight:600;">{style_str}</span></div>
            <div class="status-item"><span style="color:#A0A5B1;">Dimensions</span><span style="color:#D8C3A5; font-weight:600;">{dim_str}</span></div>
            <div class="status-item"><span style="color:#A0A5B1;">Budget</span><span style="color:#D8C3A5; font-weight:600;">{budget_str}</span></div>
            <div class="status-item"><span style="color:#A0A5B1;">Site Visit Slot</span><span style="color:#D8C3A5; font-size:0.8rem; font-weight:600;">{visit_slot}</span></div>
            <div class="status-item" style="border-bottom:none;"><span style="color:#A0A5B1;">Email (Optional)</span><span style="color:#D8C3A5; font-size:0.8rem;">{email_str}</span></div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Past Chat Sessions Section (Local Storage)
        st.markdown("<h4 style='color:#E6E8EC; margin-bottom:8px;'>📜 PAST CHAT SESSIONS</h4>", unsafe_allow_html=True)
        saved_sessions = list_chat_sessions()
        if saved_sessions:
            options = {s["session_id"]: s["summary"] for s in saved_sessions}
            current_id = st.session_state.session_id
            default_idx = 0
            if current_id in options:
                default_idx = list(options.keys()).index(current_id)

            selected_sess = st.selectbox(
                "Select previous chat session:",
                options=list(options.keys()),
                index=default_idx,
                format_func=lambda x: options[x],
                key="session_selector",
                label_visibility="collapsed"
            )
            if selected_sess != st.session_state.session_id:
                if st.button("📂 Open Selected Chat", use_container_width=True):
                    loaded = load_chat_session(selected_sess)
                    if loaded:
                        st.session_state.session_id = loaded.get("session_id", selected_sess)
                        st.session_state.messages = loaded.get("messages", [])
                        st.session_state.requirements = loaded.get("requirements", {})
                        st.rerun()
        else:
            st.markdown("<div style='font-size:0.75rem; color:#8A8F9E; margin-bottom:10px;'>No previous local chat sessions found.</div>", unsafe_allow_html=True)

        # 4. Excel Leads Database Section
        st.markdown("<h4 style='color:#E6E8EC; margin-bottom:8px;'>📊 EXCEL LEADS DATABASE</h4>", unsafe_allow_html=True)
        excel_path = os.path.join("saved_excels", "stelar_client_leads.xlsx")
        excel_exists = os.path.exists(excel_path)
        st.markdown(f"""
        <div class="sidebar-section">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#A0A5B1; font-size:0.82rem;">Live Excel Sync:</span>
                <span style="color:{'#55E6A5' if excel_exists else '#FFB86C'}; font-weight:600; font-size:0.82rem;">
                    {'● Synced' if excel_exists else '○ Waiting for turns'}
                </span>
            </div>
            <div style="font-size:0.75rem; color:#8A8F9E; margin-top:4px;">
                Appends lead requirements & chat transcript on every message turn.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if excel_exists:
            try:
                with open(excel_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Leads Excel (.xlsx)",
                        data=f.read(),
                        file_name="stelar_client_leads.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception:
                pass

        # 5. Standalone Dispatcher Section
        st.markdown("<h4 style='color:#E6E8EC; margin-bottom:8px;'>STANDALONE DISPATCHER</h4>", unsafe_allow_html=True)
        schedule_time = os.getenv("EMAIL_SCHEDULE_TIME", "14:00")
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="mailtrap-badge">📫 Daily Dispatch @ {schedule_time} PM</div>
        </div>
        """, unsafe_allow_html=True)
