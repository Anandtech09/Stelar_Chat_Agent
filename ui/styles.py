import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        .stApp {
            background-color: #0F1115;
            color: #E6E8EC;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .brand-header {
            text-align: center;
            padding: 1.5rem 0 1rem 0;
            background: linear-gradient(180deg, rgba(216,195,165,0.08) 0%, rgba(15,17,21,0) 100%);
            border-bottom: 1px solid rgba(216,195,165,0.15);
            margin-bottom: 1.5rem;
        }
        .brand-title {
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            color: #D8C3A5;
            margin: 0;
            text-transform: uppercase;
        }
        .brand-subtitle {
            font-size: 0.95rem;
            color: #A0A5B1;
            letter-spacing: 0.08em;
            margin-top: 0.4rem;
            font-style: italic;
        }
        .thought-box {
            background: #141822;
            border-left: 3px solid #D8C3A5;
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 12px;
            font-size: 0.85rem;
            color: #B0B7C6;
            font-style: italic;
        }
        .mailtrap-badge {
            display: inline-block;
            background: rgba(255, 107, 107, 0.15);
            border: 1px solid #FF6B6B;
            color: #FF8E8E;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 12px;
            margin-bottom: 10px;
        }
        .material-card {
            background: #191D27;
            border: 1px solid rgba(216,195,165,0.15);
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 8px;
        }
        .material-name {
            font-weight: 600;
            color: #E8D5BC;
            font-size: 0.9rem;
        }
        .material-meta {
            font-size: 0.78rem;
            color: #9096A4;
        }
        .material-source {
            font-size: 0.72rem;
            color: #D8C3A5;
            font-weight: 500;
        }
        .inspiration-card {
            background: #1C2029;
            border-left: 4px solid #D8C3A5;
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 10px;
        }
        .inspiration-title {
            font-weight: 600;
            color: #E8D5BC;
            margin-bottom: 4px;
        }
        .inspiration-snippet {
            font-size: 0.85rem;
            color: #B0B5C0;
        }
        .inspiration-link {
            font-size: 0.8rem;
            color: #D8C3A5;
            text-decoration: underline;
        }
        .sidebar-section {
            background: #14171E;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.2rem;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px dashed rgba(255,255,255,0.05);
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)


def render_brand_header():
    st.markdown("""
    <div class="brand-header">
        <div class="brand-title">STELAR INTERIORS</div>
        <div style="letter-spacing: 0.2em; font-size: 0.75rem; color:#D8C3A5; margin-top:2px;">AGNO MULTI-AGENT DESIGN TEAM</div>
        <div class="brand-subtitle">"Let's turn your ideas into a beautiful space."</div>
    </div>
    """, unsafe_allow_html=True)
