import os
import streamlit as st


def render_layout_svg(layout_data: dict) -> str:
    if not layout_data:
        return ""

    room_l = layout_data.get("room_length", 16)
    room_w = layout_data.get("room_width", 12)
    placements = layout_data.get("layout", [])

    svg_w, svg_h = 500, 380
    pad = 40
    draw_w = svg_w - (pad * 2)
    draw_h = svg_h - (pad * 2)

    # Build clean SVG without leading markdown indentation to prevent code-block rendering
    svg_parts = [
        f'<svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg" style="background:#12151B; border-radius:10px; border:1px solid rgba(216,195,165,0.2); max-width:100%;">',
        f'<rect x="{pad}" y="{pad}" width="{draw_w}" height="{draw_h}" fill="#191D26" stroke="#D8C3A5" stroke-width="4" rx="4"/>',
        f'<text x="{svg_w/2}" y="{pad - 12}" fill="#A0A5B1" font-size="12" font-weight="bold" text-anchor="middle">NORTH WALL (WINDOW)</text>',
        f'<text x="{svg_w/2}" y="{svg_h - pad + 24}" fill="#A0A5B1" font-size="12" font-weight="bold" text-anchor="middle">SOUTH WALL</text>',
        f'<text x="{pad - 12}" y="{svg_h/2}" fill="#A0A5B1" font-size="12" font-weight="bold" text-anchor="middle" transform="rotate(-90 {pad - 12} {svg_h/2})">WEST (DOOR)</text>',
        f'<text x="{svg_w - pad + 24}" y="{svg_h/2}" fill="#A0A5B1" font-size="12" font-weight="bold" text-anchor="middle" transform="rotate(90 {svg_w - pad + 24} {svg_h/2})">EAST</text>',
        f'<rect x="{svg_w/2 - 50}" y="{pad - 5}" width="100" height="6" fill="#87CEEB" rx="2"/>',
        f'<line x1="{pad-2}" y1="{pad + 40}" x2="{pad-2}" y2="{pad + 75}" stroke="#FFA07A" stroke-width="4"/>'
    ]

    box_coords = {
        "sofa": (svg_w/2 - 90, pad + 20, 180, 50, "#3B4A6B", "Main Sofa"),
        "coffee": (svg_w/2 - 50, pad + 95, 100, 40, "#7A5230", "Coffee Table"),
        "tv": (svg_w/2 - 75, svg_h - pad - 45, 150, 25, "#2C3540", "TV Unit"),
        "desk": (svg_w - pad - 110, pad + 25, 90, 45, "#4E5D52", "Study Desk"),
        "chair": (pad + 30, svg_h/2 - 25, 50, 50, "#6B4A5B", "Armchair")
    }

    placed_keys = set()
    for item in placements:
        fname = item.get("furniture", "").lower()
        key_found = None
        if "sofa" in fname or "couch" in fname:
            key_found = "sofa"
        elif "coffee" in fname or "center" in fname:
            key_found = "coffee"
        elif "tv" in fname or "media" in fname:
            key_found = "tv"

        if key_found and key_found not in placed_keys:
            placed_keys.add(key_found)
            x, y, w, h, col, label = box_coords[key_found]
            svg_parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="1.5" rx="6"/>')
            svg_parts.append(f'<text x="{x + w/2}" y="{y + h/2 + 4}" fill="#FFFFFF" font-size="11" font-weight="600" text-anchor="middle">{label}</text>')

    if not placed_keys:
        for k, (x, y, w, h, col, label) in box_coords.items():
            if k in ["sofa", "coffee", "tv"]:
                svg_parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" stroke="#FFFFFF" stroke-opacity="0.3" stroke-width="1.5" rx="6"/>')
                svg_parts.append(f'<text x="{x + w/2}" y="{y + h/2 + 4}" fill="#FFFFFF" font-size="11" font-weight="600" text-anchor="middle">{label}</text>')

    svg_parts.append(f'<text x="{svg_w/2}" y="{svg_h/2}" fill="rgba(255,255,255,0.12)" font-size="22" font-weight="bold" text-anchor="middle">{room_l} × {room_w} FT</text>')
    svg_parts.append('</svg>')

    return "".join(svg_parts)


def render_chat_history():
    for msg in st.session_state.messages:
        role = msg["role"]
        avatar_icon = "👤" if role == "user" else "✨"

        with st.chat_message(role, avatar=avatar_icon):
            st.markdown(msg["content"])

            if "palette" in msg and msg["palette"]:
                pal = msg["palette"]
                st.markdown(f"#### 🎨 Color Palette: {pal.get('name', 'Custom Palette')}")
                st.write(pal.get("description", ""))
                cols = st.columns(len(pal.get("colors", [])))
                for idx, c in enumerate(pal.get("colors", [])):
                    with cols[idx]:
                        st.markdown(f"""
                        <div style="background-color:{c['hex']}; height:65px; border-radius:8px; border:1px solid rgba(255,255,255,0.2);"></div>
                        <div style="font-size:0.8rem; font-weight:600; margin-top:4px; text-align:center;">{c['name']}</div>
                        <div style="font-size:0.75rem; color:#A0A5B1; text-align:center;">{c['hex']}</div>
                        <div style="font-size:0.7rem; color:#D8C3A5; text-align:center;">{c['role']}</div>
                        """, unsafe_allow_html=True)

            if "materials" in msg and msg["materials"]:
                st.markdown("#### 🪵 Scraped Material Recommendations")
                m_cols = st.columns(2)
                for idx, mat in enumerate(msg["materials"]):
                    with m_cols[idx % 2]:
                        st.markdown(f"""
                        <div class="material-card">
                            <div class="material-name">✨ {mat['name']} ({mat['category']})</div>
                            <div class="material-meta">Texture: <i>{mat['texture']}</i> | Application: {mat['application']}</div>
                            <div class="material-source">Source: {mat['source']}</div>
                        </div>
                        """, unsafe_allow_html=True)

            if "layout" in msg and msg["layout"]:
                lay = msg["layout"]
                st.markdown(f"#### 📐 2D Spatial Layout Plan ({lay.get('room_length', 16)} × {lay.get('room_width', 12)} ft)")
                st.markdown(render_layout_svg(lay), unsafe_allow_html=True)
                with st.expander("View Furniture Placement Specs", expanded=False):
                    for item in lay.get("layout", []):
                        st.write(f"• **{item['furniture']}** ({item.get('dimensions','')}): placed at *{item['position']}*")
                    for note in lay.get("notes", []):
                        st.info(f"💡 {note}")

            if "web_results" in msg and msg["web_results"]:
                st.markdown("#### 🖼️ Live Web Design Inspiration")
                insp_cols = st.columns(2)
                for idx, res in enumerate(msg["web_results"]):
                    with insp_cols[idx % 2]:
                        img_url = res.get("image_url", "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=600")
                        st.markdown(f"""
                        <div class="inspiration-card">
                            <img src="{img_url}" style="width:100%; height:140px; object-fit:cover; border-radius:6px; margin-bottom:8px;" />
                            <div class="inspiration-title">{res.get('title','Design Inspiration')}</div>
                            <div class="inspiration-snippet">{res.get('snippet','')}</div>
                            <a class="inspiration-link" href="{res.get('url','#')}" target="_blank">View Source ↗ ({res.get('source','Web')})</a>
                        </div>
                        """, unsafe_allow_html=True)

            # Compact, elegant icon badges for Save and Email status (Green = Success, Red = Failed)
            status_badges = []
            if "saved_file" in msg and msg["saved_file"]:
                fname = os.path.basename(msg["saved_file"])
                status_badges.append(f'<span style="background:rgba(85,230,165,0.12); border:1px solid #55E6A5; color:#55E6A5; padding:3px 10px; border-radius:14px; font-size:0.75rem; font-weight:600;">💾 🟢 Brief Saved ({fname})</span>')

            if "email_status" in msg and msg["email_status"]:
                estatus = str(msg["email_status"])
                is_success = "success" in estatus.lower() or "dispatched" in estatus.lower()
                badge_bg = "rgba(85,230,165,0.12)" if is_success else "rgba(255,107,107,0.12)"
                badge_border = "#55E6A5" if is_success else "#FF6B6B"
                badge_color = "#55E6A5" if is_success else "#FF8E8E"
                badge_dot = "🟢" if is_success else "🔴"
                status_label = "Email Sent" if is_success else "Email Error / Offline"
                status_badges.append(f'<span style="background:{badge_bg}; border:1px solid {badge_border}; color:{badge_color}; padding:3px 10px; border-radius:14px; font-size:0.75rem; font-weight:600;">📫 {badge_dot} {status_label}</span>')

            if status_badges:
                st.markdown(f'<div style="display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;">{"".join(status_badges)}</div>', unsafe_allow_html=True)


def render_quick_suggestions():
    st.markdown("<div style='font-size:0.8rem; color:#8A8F9E; margin-top:10px;'>QUICK SUGGESTIONS:</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    chip_prompt = None
    with c1:
        if st.button("🛋️ Living Room", use_container_width=True):
            chip_prompt = "I want to design a modern living room, 12 by 16 feet."
    with c2:
        if st.button("✨ Warm Modern", use_container_width=True):
            chip_prompt = "Suggest a warm modern style with ₹3 lakh budget."
    with c3:
        if st.button("🎨 Colors & Materials", use_container_width=True):
            chip_prompt = "Suggest a color palette and scrape matching materials from the web."
    with c4:
        if st.button("📐 2D Layout", use_container_width=True):
            chip_prompt = "Calculate layout for sofa, coffee table, and TV unit."
    with c5:
        if st.button("🏡 Site Visit Booking", use_container_width=True):
            chip_prompt = "I would like to book a complimentary in-person site visit consultation slot for next Saturday."
    return chip_prompt
