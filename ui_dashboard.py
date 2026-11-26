"""
ui_dashboard.py - AI-GLAZE Interactive Frontend Dashboard with Full Authentication
Lead: Teammate A (Member 2: Frontend & Interactive UI Lead)
Project: AI-GLAZE - Intelligent Home Planning & Interior Platform
"Plan it. Design it. Source it. Budget it!"

Features:
  - OG Authentication Portal: Login, Registration, and Role-Based Access (Homeowner vs. Architect)
  - 1-Click Demo Logins for immediate examiner/guide demonstration
  - Header & Brand styling with User Profile Bar
  - Sidebar Controls (Style Selector, Indian Rupee Budget Slider, Dynamic Tier Badge)
  - Room Photo Upload & Demo Preset
  - Showstopper #3: AI Vision Mode (Thermal Depth Heatmap, Canny Edges, HUD Metrics Card)
  - Showstopper #1: Interior Redesign & Magic Wand Localized Inpainting (Material Swap)
  - Showstopper #4: YOLOv8 Furniture Detection & Interactive Spatial Pins
  - Master Vision Pipeline Runner
  - Saved Projects Portfolio (Persistent SQLite storage)
"""

import os
import io
import time
from PIL import Image
import pandas as pd
import streamlit as st

# Directory Anchor for absolute asset resolution regardless of launch cwd
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resolve_path(rel_path):
    if not rel_path:
        return None
    if os.path.isabs(rel_path):
        return rel_path
    abs_p = os.path.join(BASE_DIR, rel_path)
    return abs_p if os.path.exists(abs_p) else os.path.join(BASE_DIR, rel_path)

# Safe import of vision_engine written by Tech Lead (Member 1)
try:
    import vision_engine
    import importlib
    importlib.reload(vision_engine)
    VISION_ENGINE_AVAILABLE = True
    VISION_ERROR_MSG = ""
except Exception as err:
    VISION_ENGINE_AVAILABLE = False
    VISION_ERROR_MSG = str(err)

# Safe import of auth_manager
try:
    import auth_manager
    AUTH_AVAILABLE = True
except Exception as err:
    AUTH_AVAILABLE = False

# Safe import of Pillars 4 & 6 (cost_engine & reasoning_engine)
try:
    import cost_engine
    import reasoning_engine
    import importlib as _importlib
    _importlib.reload(cost_engine)
    _importlib.reload(reasoning_engine)
    COST_ENGINE_AVAILABLE = True
    COST_ERROR_MSG = ""
except Exception as err:
    COST_ENGINE_AVAILABLE = False
    COST_ERROR_MSG = str(err)


# =====================================================================
# 1. STREAMLIT PAGE CONFIGURATION & CUSTOM STYLING
# =====================================================================
st.set_page_config(
    page_title="AI-GLAZE | Intelligent Home Planning & Interior Architecture",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Luxury Glassmorphism & High-End Architecture Studio UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Deep Luxury Architectural Canvas */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: #F1F5F9;
    }

    h1, h2, h3, h4, .brand-title, .main-header-title {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Ambient Architectural Grid & Mesh Background */
    .stApp {
        background: 
            radial-gradient(circle at 12% 18%, rgba(99, 102, 241, 0.18) 0%, transparent 45%),
            radial-gradient(circle at 88% 82%, rgba(14, 165, 233, 0.15) 0%, transparent 45%),
            radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.10) 0%, transparent 60%),
            linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            #080C15 !important;
        background-size: 100% 100%, 100% 100%, 100% 100%, 36px 36px, 36px 36px, 100% 100% !important;
    }

    /* Luxury Studio Navigation Header */
    .studio-header {
        background: rgba(15, 23, 42, 0.78);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 20px 48px -15px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.18);
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
    }

    .studio-brand-group {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .brand-icon-box {
        width: 56px;
        height: 56px;
        border-radius: 16px;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #ec4899 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.85rem;
        box-shadow: 0 8px 26px rgba(124, 58, 237, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .brand-title {
        font-size: 2.15rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.1;
    }

    .brand-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 4px 10px;
        border-radius: 12px;
        background: linear-gradient(135deg, #06B6D4, #3B82F6);
        color: white;
        margin-left: 8px;
        vertical-align: middle;
        -webkit-text-fill-color: white;
        white-space: nowrap !important;
        display: inline-block;
    }

    .brand-tagline {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 4px;
        font-weight: 400;
    }

    .studio-meta-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
    }

    .meta-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #CBD5E1;
        backdrop-filter: blur(10px);
        transition: all 0.2s ease;
    }
    .meta-pill:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(99, 102, 241, 0.4);
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 10px #10B981;
        animation: pulseAnimation 2s infinite;
    }

    @keyframes pulseAnimation {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }

    /* Auth Portal Main Header Card */
    .main-header-card {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        backdrop-filter: blur(28px);
        -webkit-backdrop-filter: blur(28px);
        box-shadow: 0 24px 60px -15px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        margin-bottom: 28px;
    }

    .main-header-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #FFFFFF 20%, #A5B4FC 60%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }

    .main-header-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        max-width: 680px;
        margin: 0 auto 16px auto;
        line-height: 1.5;
        font-weight: 400;
    }

    .tag-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #C7D2FE;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 4px;
        backdrop-filter: blur(10px);
        transition: all 0.25s ease;
    }
    .tag-pill:hover {
        background: rgba(99, 102, 241, 0.25);
        border-color: rgba(99, 102, 241, 0.6);
        transform: translateY(-1px);
        color: #FFFFFF;
    }

    /* Floating Logged-in User Profile Bar */
    .user-profile-bar {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 12px 24px;
        margin-bottom: 20px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 28px -8px rgba(0, 0, 0, 0.45);
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.68);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.35);
        box-shadow: 0 20px 44px -10px rgba(99, 102, 241, 0.22);
    }

    /* Section Subheaders */
    .section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 14px;
        margin-bottom: 12px;
        color: #F8FAFC;
        display: flex;
        align-items: center;
        gap: 12px;
        border-left: 4px solid #6366F1;
        padding-left: 14px;
        letter-spacing: -0.01em;
    }

    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        color: #FFFFFF;
        font-size: 0.88rem;
        font-weight: 800;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }

    /* Primary CTA Buttons Overrides */
    div.stButton > button[kind="primary"], div.stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #d946ef 100%) !important;
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        letter-spacing: 0.3px !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        box-shadow: 0 6px 22px rgba(124, 58, 237, 0.45) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(124, 58, 237, 0.65) !important;
        color: #FFFFFF !important;
    }

    /* Secondary Buttons */
    div.stButton > button[kind="secondary"], div.stButton > button[data-testid="baseButton-secondary"] {
        background: rgba(30, 41, 59, 0.65) !important;
        color: #E2E8F0 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="secondary"]:hover, div.stButton > button[data-testid="baseButton-secondary"]:hover {
        background: rgba(51, 65, 85, 0.85) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3) !important;
    }

    /* Streamlit Forms Reskinning */
    [data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 20px !important;
        padding: 26px !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 20px 48px rgba(0, 0, 0, 0.45) !important;
    }

    /* Input Fields & Select Boxes */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 12px !important;
        color: #F8FAFC !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-baseweb="input"]:focus-within > div, div[data-baseweb="select"]:focus-within > div {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3) !important;
    }

    /* File Uploader Luxury Dropzone */
    section[data-testid="stFileUploadDropzone"] {
        background: rgba(15, 23, 42, 0.55) !important;
        border: 2px dashed rgba(99, 102, 241, 0.4) !important;
        border-radius: 16px !important;
        padding: 28px !important;
        transition: all 0.25s ease !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #38BDF8 !important;
        background: rgba(99, 102, 241, 0.1) !important;
    }

    /* Slider Thumb and Glow Track */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #38BDF8 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.8) !important;
        border: 2px solid #FFFFFF !important;
    }

    /* Tabs Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(15, 23, 42, 0.85);
        padding: 8px 10px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 26px;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        color: #94A3B8;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.4), rgba(124, 58, 237, 0.4)) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(124, 58, 237, 0.55) !important;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.3) !important;
    }

    /* Material Swatch Preview Card */
    .material-swatch-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 16px;
        padding: 18px 22px;
        margin-top: 10px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
        transition: all 0.25s ease;
    }
    .material-swatch-card:hover {
        border-color: rgba(99, 102, 241, 0.45);
        transform: translateY(-2px);
        box-shadow: 0 14px 32px rgba(99, 102, 241, 0.2);
    }
    .material-icon-bubble {
        width: 50px;
        height: 50px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.7rem;
        flex-shrink: 0;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .material-details-title {
        font-weight: 700;
        font-size: 1.02rem;
        color: #F8FAFC;
    }
    .material-details-price {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.95rem;
        color: #38BDF8;
    }
    .material-details-desc {
        font-size: 0.82rem;
        color: #94A3B8;
        margin-top: 3px;
        line-height: 1.4;
    }

    /* HUD Metrics Card */
    .hud-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 18px;
        padding: 24px;
        color: #f8fafc;
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.12);
        margin-top: 14px;
        margin-bottom: 18px;
    }
    .hud-header {
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #38bdf8;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .hud-stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
    }
    .hud-stat-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 12px;
        text-align: center;
        transition: all 0.2s ease;
    }
    .hud-stat-box:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(56, 189, 248, 0.3);
    }
    .hud-stat-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.45rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .hud-stat-lbl {
        font-size: 0.72rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
        font-weight: 600;
    }

    /* Tier Badges */
    .tier-badge-budget {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 6px 16px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
    }
    .tier-badge-mid {
        background: linear-gradient(135deg, #0284c7, #38bdf8);
        color: white;
        padding: 6px 16px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
    }
    .tier-badge-luxury {
        background: linear-gradient(135deg, #d97706, #fbbf24);
        color: #0f172a;
        padding: 6px 16px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 0.95rem;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# 2. AUTHENTICATION & SESSION STATE MANAGEMENT
# =====================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

# If not authenticated, display the Luxury Authentication Suite
if not st.session_state.logged_in:
    # Luxury Branded Welcome Header
    st.markdown("""
    <div class="main-header-card" style="text-align: center; padding: 40px 24px;">
        <div style="display: flex; justify-content: center; margin-bottom: 14px;">
            <div class="brand-icon-box" style="width: 70px; height: 70px; font-size: 2.3rem;">🏡</div>
        </div>
        <div class="main-header-title">AI-GLAZE <span class="brand-badge" style="font-size: 0.85rem; padding: 4px 12px;">PRO STUDIO</span></div>
        <div class="main-header-subtitle">Autonomous Spatial Perception, Generative Interior Architecture & Real Material Intelligence</div>
        <div style="margin-top: 14px;">
            <span class="tag-pill">📐 Geometry-Preserved Redesign</span>
            <span class="tag-pill">💰 Indian Market BoQ (INR ₹)</span>
            <span class="tag-pill">🛒 Real Sourcing & Supplier Links</span>
            <span class="tag-pill">🏛️ Architect & Homeowner Portals</span>
            <span class="tag-pill">⚡ Offline-Capable Neural Pipeline</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 2.2, 1])

    with auth_col2:
        auth_tab_login, auth_tab_reg = st.tabs(["🔐 Sign In to Workspace", "📝 Register New Account"])

        # TAB 1: SIGN IN
        with auth_tab_login:
            st.markdown('<div class="section-title">🔐 Welcome Back</div>', unsafe_allow_html=True)
            st.caption("Sign in to access your spatial design workspace, neural pipelines, and saved project portfolios.")

            with st.form("login_form"):
                login_user = st.text_input("Username or Email", placeholder="e.g. sanjana or architect@aiglaze.com")
                login_pwd = st.text_input("Password", type="password", placeholder="••••••••")
                login_submitted = st.form_submit_button("Sign In to Studio Dashboard", type="primary", use_container_width=True)

            if login_submitted:
                if AUTH_AVAILABLE:
                    success, msg, user_data = auth_manager.authenticate_user(login_user, login_pwd)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = user_data
                        st.success(f"Welcome back, {user_data['full_name']}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Authentication module not loaded.")

            st.markdown("---")
            st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 0.88rem; font-weight: 600;'>⚡ One-Click Reviewer Access for Faculty & Reviewers:</p>", unsafe_allow_html=True)
            
            demo_col_a, demo_col_b = st.columns(2)
            with demo_col_a:
                if st.button("📐 Demo: Architect Portal", use_container_width=True):
                    if AUTH_AVAILABLE:
                        _, _, user_data = auth_manager.authenticate_user("architect_demo", "demo123")
                        st.session_state.logged_in = True
                        st.session_state.user = user_data
                        st.rerun()
            with demo_col_b:
                if st.button("🏠 Demo: Homeowner Portal", use_container_width=True):
                    if AUTH_AVAILABLE:
                        _, _, user_data = auth_manager.authenticate_user("homeowner_demo", "demo123")
                        st.session_state.logged_in = True
                        st.session_state.user = user_data
                        st.rerun()

        # TAB 2: REGISTER
        with auth_tab_reg:
            st.markdown('<div class="section-title">📝 Create Studio Account</div>', unsafe_allow_html=True)
            st.caption("Join licensed architects and homeowners planning intelligent spaces.")

            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Ar. Sanjana Hoskote")
                reg_col_a, reg_col_b = st.columns(2)
                with reg_col_a:
                    reg_user = st.text_input("Username", placeholder="e.g. sanjana_arch")
                with reg_col_b:
                    reg_email = st.text_input("Email Address", placeholder="e.g. sanjana@example.com")
                
                reg_col_c, reg_col_d = st.columns(2)
                with reg_col_c:
                    reg_role = st.selectbox("Professional Role:", ["Professional Architect", "Homeowner", "Interior Designer", "Contractor"])
                with reg_col_d:
                    reg_city = st.text_input("City", value="Bangalore")

                reg_pwd = st.text_input("Password", type="password", placeholder="••••••••")
                reg_pwd_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")

                reg_submitted = st.form_submit_button("Create Account & Launch Workspace", type="primary", use_container_width=True)

            if reg_submitted:
                if reg_pwd != reg_pwd_confirm:
                    st.error("Passwords do not match!")
                elif len(reg_pwd) < 4:
                    st.error("Password must be at least 4 characters.")
                elif AUTH_AVAILABLE:
                    success, msg, user_data = auth_manager.register_user(
                        username=reg_user, email=reg_email, password=reg_pwd,
                        full_name=reg_name, role=reg_role, city=reg_city
                    )
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = user_data
                        st.success("Account created successfully! Launching dashboard...")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(msg)

    # Stop rendering the protected dashboard until authenticated
    st.stop()


# =====================================================================
# 3. LOGGED-IN USER SESSION & NAVIGATION BAR
# =====================================================================
user = st.session_state.user or {
    "full_name": "Ar. Sanjana Hoskote", "role": "Professional Architect", "city": "Bangalore", "id": 1
}

# User Status Header Bar (Luxury Floating Dock)
st.markdown(f"""
<div class="user-profile-bar">
    <div style="display: flex; align-items: center; gap: 14px;">
        <div style="width: 40px; height: 40px; border-radius: 12px; background: linear-gradient(135deg, #6366F1, #8B5CF6); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.45); border: 1px solid rgba(255, 255, 255, 0.2);">👤</div>
        <div>
            <div style="font-weight: 700; font-size: 1.02rem; color: #F8FAFC;">
                {user['full_name']} &nbsp;
                <span style="font-size: 0.74rem; font-weight: 600; padding: 3px 10px; border-radius: 20px; background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.35);">
                    🏷️ {user['role']}
                </span>
            </div>
            <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 2px;">
                📍 {user.get('city', 'Bangalore')} • Department of AI & ML, MVJCE
            </div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <span class="meta-pill"><span class="pulse-dot"></span> Studio Online</span>
        <span class="meta-pill">v2.4 Pro</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Preset demo images if present (resolved against BASE_DIR without duplicates)
DEMO_IMAGE_CANDIDATES = []
for fname in ["real_room.jpeg", "test_room.jpg"]:
    resolved_candidate = resolve_path(fname)
    if os.path.exists(resolved_candidate) and resolved_candidate not in DEMO_IMAGE_CANDIDATES:
        DEMO_IMAGE_CANDIDATES.append(resolved_candidate)

DEFAULT_IMAGE = DEMO_IMAGE_CANDIDATES[0] if DEMO_IMAGE_CANDIDATES else None

if "current_image_path" not in st.session_state or not st.session_state.current_image_path:
    st.session_state.current_image_path = DEFAULT_IMAGE

if "depth_heatmap_path" not in st.session_state:
    d_cand = resolve_path("depth_heatmap.png")
    st.session_state.depth_heatmap_path = d_cand if os.path.exists(d_cand) else None

if "structural_edges_path" not in st.session_state:
    e_cand = resolve_path("structural_edges.png")
    st.session_state.structural_edges_path = e_cand if os.path.exists(e_cand) else None

if "spatial_metrics" not in st.session_state:
    st.session_state.spatial_metrics = None

if "redesign_path" not in st.session_state:
    r_cand = resolve_path("redesign_output.png")
    st.session_state.redesign_path = r_cand if os.path.exists(r_cand) else None

if "inpaint_path" not in st.session_state:
    i_cand = resolve_path("inpaint_output.png")
    st.session_state.inpaint_path = i_cand if os.path.exists(i_cand) else None

if "detected_objects" not in st.session_state:
    st.session_state.detected_objects = None

if "detected_objects_path" not in st.session_state:
    do_cand = resolve_path("detected_objects.png")
    st.session_state.detected_objects_path = do_cand if os.path.exists(do_cand) else None

if "active_preview_mode" not in st.session_state:
    st.session_state.active_preview_mode = "✨ Style Redesign"

if "last_action_msg" not in st.session_state:
    st.session_state.last_action_msg = None


# =====================================================================
# 4. SIDEBAR CONTROLS & INDIAN RUPEE (₹) BUDGET
# =====================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/interior.png", width=64)
    st.markdown("### 🎛️ Design Configuration")
    st.caption(f"Active Profile: **{user['full_name']}** ({user['role']})")

    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    st.markdown("---")
    
    # 1. Interior Style Selector
    st.markdown("#### 🎨 Interior Style")
    style_options = [
        "Scandinavian Minimalist",
        "Modern Luxury",
        "Industrial Warm",
        "Traditional Heritage"
    ]
    style_descriptions = {
        "Scandinavian Minimalist": "Light oak, airy spaces, clean lines & natural sunlight.",
        "Modern Luxury": "Polished marble, brass accents, ambient lighting & sleek velvet.",
        "Industrial Warm": "Exposed brick, iron finishes, warm Edison glows & reclaimed wood.",
        "Traditional Heritage": "Intricate craftsmanship, rich teak wood & timeless royal warmth."
    }
    
    selected_style = st.selectbox(
        "Select Theme Aesthetic:",
        options=style_options,
        index=0,
        help="Defines the tone mapping and generative diffusion prompt in vision_engine.py"
    )
    st.caption(f"_{style_descriptions[selected_style]}_")

    st.markdown("---")

    # 2. Budget Allocation Slider (Indian Rupees ₹)
    st.markdown("#### 💰 Budget Constraint (INR ₹)")
    budget_inr = st.slider(
        "Target Renovation Cap (₹):",
        min_value=50000,
        max_value=600000,
        value=150000,
        step=10000,
        help="Used by the Knapsack Optimizer to swap luxury materials for budget-friendly alternatives."
    )
    
    # Dynamic Tier Evaluation (Indian market benchmarks)
    if budget_inr < 100000:
        tier_label = "Economy / Budget Tier"
        tier_class = "tier-badge-budget"
        tier_desc = "Vitrified tiles (₹65/sq.ft), acrylic emulsion & modular fabric furniture."
    elif budget_inr <= 250000:
        tier_label = "Mid-Range / Premium Tier"
        tier_class = "tier-badge-mid"
        tier_desc = "Engineered wood (₹175/sq.ft), Asian Paints Royale & solid teak accents."
    else:
        tier_label = "Luxury Contemporary Tier"
        tier_class = "tier-badge-luxury"
        tier_desc = "Italian Carrara Marble (₹380/sq.ft), velvet textures & custom chandeliers."

    st.markdown(f'<div class="{tier_class}">{tier_label}</div>', unsafe_allow_html=True)
    st.caption(tier_desc)

    st.markdown("---")
    
    # Ceiling Height Calibration
    ceiling_height = st.slider("Ceiling Height Calibration (Feet):", 8.0, 14.0, 9.5, 0.5)


# =====================================================================
# 5. MAIN HEADER CARD & PLATFORM TABS
# =====================================================================
st.markdown("""
<div class="studio-header">
    <div class="studio-brand-group">
        <div class="brand-icon-box">🏡</div>
        <div>
            <div class="brand-title">AI-GLAZE <span class="brand-badge">PRO ARCHITECTURE</span></div>
            <div class="brand-tagline">Autonomous Spatial Perception, Generative Interior Architecture & Real Material Intelligence</div>
        </div>
    </div>
    <div class="studio-meta-badges">
        <div class="meta-pill"><span class="pulse-dot"></span> Neural Vision Mode Active</div>
        <div class="meta-pill">🇮🇳 Indian Market (INR ₹)</div>
        <div class="meta-pill">🏛️ VTU / MVJCE Capstone</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs (Including My Saved Portfolio!)
tab_workspace, tab_portfolio, tab_contractor_report = st.tabs([
    "🛋️ Spatial Design Studio", 
    "📁 My Saved Portfolio", 
    "📄 Contractor BoQ Document"
])


# =====================================================================
# TAB 2: MY SAVED PORTFOLIO (PERSISTENT SQLITE STORAGE)
# =====================================================================
with tab_portfolio:
    st.markdown('<div class="section-title">📁 Client Design Portfolio & Project History</div>', unsafe_allow_html=True)
    st.caption(f"Stored projects in local SQLite database (`users.db`) for **{user['full_name']}**.")

    if AUTH_AVAILABLE:
        user_projects = auth_manager.get_user_projects(user["id"])
        if user_projects and len(user_projects) > 0:
            for p in user_projects:
                with st.expander(f"📌 {p['project_name']} ({p['style']}) - Saved on {p['created_at'][:10]}", expanded=False):
                    col_p1, col_p2 = st.columns([1, 2])
                    with col_p1:
                        if p.get("image_path") and os.path.exists(p["image_path"]):
                            st.image(p["image_path"], caption="Design Concept", use_container_width=True)
                        else:
                            st.info("Render file path: " + str(p.get("image_path", "N/A")))
                    with col_p2:
                        st.markdown(f"**Room Floor Area:** `{p.get('floor_sqft', 0)} sq.ft` &nbsp;|&nbsp; **Wall Area:** `{p.get('wall_sqft', 0)} sq.ft`")
                        st.markdown(f"**Target Budget Cap:** `₹{p.get('budget', 0):,.2f}`")
                        st.markdown(f"**Estimated Grand Total:** `₹{p.get('grand_total', 0):,.2f}`")
                        st.caption("Full specification stored in SQLite `projects` table.")
        else:
            st.info("No saved projects in your portfolio yet. Run a design in the 'Spatial Design Studio' and click 'Save to Portfolio'!")
    else:
        st.warning("Database module offline.")


# =====================================================================
# TAB 3: CONTRACTOR BOQ DOCUMENT PREVIEW & DOWNLOAD
# =====================================================================
with tab_contractor_report:
    st.markdown('<div class="section-title">📄 Contractor Specification Sheet, 18% GST BoQ & Architectural Reasoning</div>', unsafe_allow_html=True)
    st.caption("Connects generated floorplan / scanned room areas to Indian construction & finishing costs (INR + 18% GST), engineering rationale, and smart budget trade-offs.")

    report_path = resolve_path("contractor_boq_report.html")

    if COST_ENGINE_AVAILABLE:
        default_city = user.get("city", "Bangalore") or "Bangalore"
        city_choices = ["Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad"]
        city_idx = city_choices.index(default_city) if default_city in city_choices else 0

        with st.expander("📐 Floorplan & Material Parameters (Pillars 4 & 6)", expanded=True):
            cfg_c1, cfg_c2, cfg_c3, cfg_c4 = st.columns(4)
            area_source = cfg_c1.selectbox(
                "Area Source:",
                ["Generated Floorplan (30×40 Plot / Carpet)", "Scanned Room (AI Vision Metrics)"],
                key="boq_area_source"
            )
            boq_city = cfg_c2.selectbox("City (Climate Context):", city_choices, index=city_idx, key="boq_city")
            boq_scope = cfg_c3.selectbox("Work Scope:", ["renovation", "full_construction"], key="boq_scope")

            if area_source.startswith("Generated Floorplan"):
                plot_w = cfg_c4.number_input("Plot Width (ft)", min_value=15.0, value=30.0, step=5.0, key="boq_plot_w")
                dim_c1, dim_c2, dim_c3 = st.columns(3)
                plot_l = dim_c1.number_input("Plot Length (ft)", min_value=20.0, value=40.0, step=5.0, key="boq_plot_l")
                suggested_carpet = round(plot_w * plot_l * 0.66, 1)
                carpet_sqft = dim_c2.number_input("Floorplan Carpet Area (sq.ft)", min_value=100.0, value=suggested_carpet, step=10.0, key="boq_carpet_sqft")
                boq_budget_cap = dim_c3.number_input("Floorplan Budget Ceiling (₹)", min_value=50000.0, value=1200000.0, step=25000.0, key="boq_budget_cap")
            else:
                metrics_src = st.session_state.spatial_metrics or {
                    "floor_area_sqft": 140.3,
                    "wall_surface_area_sqft": 405.3
                }
                carpet_sqft = float(metrics_src.get("floor_area_sqft", 140.3))
                cfg_c4.metric("Scanned Floor Area", f"{carpet_sqft:,.1f} sq.ft")
                boq_budget_cap = float(budget_inr)

            mat_c1, mat_c2, mat_c3, mat_c4 = st.columns(4)
            floor_tiers = [m["tier"] for m in cost_engine.MATERIAL_CATALOGUE["flooring"]]
            paint_tiers = [m["tier"] for m in cost_engine.MATERIAL_CATALOGUE["painting"]]
            furn_tiers = [m["tier"] for m in cost_engine.MATERIAL_CATALOGUE["furniture"]]
            sel_floor_tier = mat_c1.selectbox("Flooring Tier:", floor_tiers, index=0, key="boq_floor_tier")
            sel_paint_tier = mat_c2.selectbox("Wall Finish Tier:", paint_tiers, index=1, key="boq_paint_tier")
            sel_furn_tier = mat_c3.selectbox("Joinery Tier:", furn_tiers, index=2, key="boq_furn_tier")
            mat_c4.write("")
            if mat_c4.button("🔄 Reset BoQ to Selected Specs", use_container_width=True):
                st.session_state.pop("boq_override_data", None)
                st.session_state.pop("boq_applied_cuts", None)
                st.rerun()

        if area_source.startswith("Generated Floorplan"):
            base_boq = cost_engine.generate_floorplan_boq(
                carpet_area_sqft=carpet_sqft,
                plot_width_ft=plot_w,
                plot_length_ft=plot_l,
                scope=boq_scope,
                flooring_tier=sel_floor_tier,
                painting_tier=sel_paint_tier,
                furniture_tier=sel_furn_tier,
                budget_cap=boq_budget_cap,
                city=boq_city,
                gst_pct=0.18,
                include_reasoning=True,
            )
        else:
            f_spec = cost_engine._find_catalogue_tier("flooring", sel_floor_tier)
            p_spec = cost_engine._find_catalogue_tier("painting", sel_paint_tier)
            fn_spec = cost_engine._find_catalogue_tier("furniture", sel_furn_tier)
            metrics_src = st.session_state.spatial_metrics or {
                "floor_area_sqft": 140.3,
                "wall_surface_area_sqft": 405.3
            }
            billable_floor = round(float(metrics_src["floor_area_sqft"]) * 1.10, 2)
            net_wall = float(metrics_src["wall_surface_area_sqft"])
            base_boq = cost_engine.generate_full_boq(
                floor_sqft=billable_floor,
                floor_rate=f_spec["rate_per_sqft"],
                wall_sqft=net_wall,
                paint_rate=p_spec["rate_per_sqft"],
                furniture_price=round(85000.0 * fn_spec["multiplier"], 2),
                budget_cap=boq_budget_cap,
                room_name=f"Scanned Space ({selected_style})",
                selected_specs={
                    "flooring": f_spec["name"],
                    "painting": p_spec["name"],
                    "furniture": fn_spec["name"],
                },
                gst_pct=0.18,
                carpet_area_sqft=float(metrics_src["floor_area_sqft"]),
                city=boq_city,
            )

        active_boq = st.session_state.get("boq_override_data", base_boq)
        reasoning_notes = reasoning_engine.generate_boq_reasoning_notes(active_boq, city=boq_city)
        active_boq["reasoning_notes"] = reasoning_notes
        st.session_state["active_boq"] = active_boq

        fin = active_boq["financial_summary"]
        dims = active_boq["dimensions"]

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Carpet Area", f"{dims.get('carpet_area_sqft', 0):,.1f} sq.ft")
        k2.metric("Pre-GST Subtotal", f"₹{fin.get('pre_gst_total', 0):,.0f}")
        k3.metric(f"GST ({fin.get('gst_percentage', 18):.0f}%)", f"₹{fin.get('gst_amount', 0):,.0f}")
        k4.metric("Grand Total (Incl. GST)", f"₹{fin.get('grand_total', 0):,.0f}")
        delta_txt = (
            f"₹{fin.get('delta', 0):,.0f} under cap"
            if fin.get("is_within_budget", True)
            else f"-₹{fin.get('delta', 0):,.0f} over cap"
        )
        k5.metric("Budget Status", fin.get("status", "Analyzed"), delta_txt)

        st.dataframe(
            pd.DataFrame([
                {
                    "Item ID": it["id"],
                    "Category": it["category"],
                    "Specification": it["description"],
                    "Qty": f"{it['quantity']:,.1f} {it['unit']}",
                    "Unit Rate (₹)": f"₹{it['unit_rate']:,.2f}",
                    "Subtotal (₹)": f"₹{it['subtotal']:,.2f}",
                }
                for it in active_boq["line_items"]
            ]),
            use_container_width=True,
            hide_index=True,
        )

        # Architectural & Material Reasoning Notes
        st.markdown("### 🧠 Material Intelligence & Architectural Reasoning Notes")
        st.info(reasoning_notes["executive_summary"])
        for note in reasoning_notes["material_notes"]:
            with st.expander(f"{note['category']}: {note['material_name']} (Durability {note['durability_score']}/100)", expanded=True):
                st.markdown(f"**Why Chosen:** {note['why_chosen']}")
                st.markdown(f"**Climate Fit ({reasoning_notes['city']}):** {note['climate_fit']}")
                st.caption(f"**Cost Comparison:** {note['cost_comparison']} • **Standard:** {note['is_code']}")

        # Budget Trade-Off Advisor
        st.markdown("### 💡 Budget Trade-Off Advisor")
        adv_c1, adv_c2 = st.columns([2, 1])
        advisor_query = adv_c1.text_input("Ask Budget Advisor:", value="How can I cut ₹25,000?", key="boq_advisor_prompt")
        advisor_target = adv_c2.number_input("Or Target Cut (₹):", min_value=0.0, value=25000.0, step=5000.0, key="boq_advisor_inr")

        btn_c1, btn_c2 = st.columns(2)
        run_adv = btn_c1.button("🔍 Analyze Budget Cuts", use_container_width=True)
        apply_adv = btn_c2.button("✅ Apply Suggested Cuts to BoQ", type="primary", use_container_width=True)

        if run_adv:
            qa = reasoning_engine.answer_budget_question(advisor_query, active_boq, city=boq_city)
            advice = qa["details"] if qa["intent"] == "budget_cut" else reasoning_engine.suggest_budget_cuts(active_boq, advisor_target, city=boq_city)
            st.session_state["boq_last_advice"] = advice
        else:
            advice = st.session_state.get("boq_last_advice") or reasoning_engine.suggest_budget_cuts(active_boq, advisor_target, city=boq_city)

        if advice.get("recommendations"):
            st.success(advice["client_explanation"])
            if apply_adv:
                st.session_state["boq_override_data"] = advice["updated_boq"]
                st.session_state["boq_applied_cuts"] = advice
                st.session_state["boq_last_advice"] = advice
                st.rerun()
        else:
            st.warning(advice["client_explanation"])

        # Export updated HTML report with reasoning notes & 18% GST
        cost_engine.export_boq_report(
            active_boq,
            output_file=report_path,
            reasoning_notes=reasoning_notes,
            budget_cuts=st.session_state.get("boq_applied_cuts") or advice,
        )

    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        col_rep1, col_rep2 = st.columns([3, 1])
        with col_rep1:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 12px 18px; margin-bottom: 14px;">
                <span style="color: #34D399; font-weight: 700;">✅ Certified BoQ Specification Document</span> &nbsp;|&nbsp; 
                <span style="color: #CBD5E1; font-size: 0.88rem;">18% GST &amp; Architectural Reasoning Notes Included</span>
            </div>
            """, unsafe_allow_html=True)
        with col_rep2:
            st.download_button(
                "⬇️ Download Official BoQ Report (HTML)",
                data=html_content,
                file_name="AI_GLAZE_Contractor_BoQ_Report.html",
                mime="text/html",
                type="primary",
                use_container_width=True
            )

        st.components.v1.html(html_content, height=700, scrolling=True)
    else:
        st.info("Contractor report is generating. Run the design pipeline to view the full document.")


# =====================================================================
# TAB 1: SPATIAL DESIGN STUDIO (MAIN INTERACTION)
# =====================================================================
with tab_workspace:
    # -------------------------------------------------------------
    # 5.1 Image Intake
    # -------------------------------------------------------------
    st.markdown('<div class="section-title"><span class="step-badge">1</span> Room Imagery Intake & Spatial Preprocessing</div>', unsafe_allow_html=True)
    
    col_upload, col_preset = st.columns([2, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload Room Photograph (JPG, PNG, JPEG)", 
            type=["jpg", "png", "jpeg"],
            help="High-resolution monocular room photo taken from eye level"
        )
        if uploaded_file is not None:
            uploaded_save_path = resolve_path("uploaded_room_temp.jpg")
            img_bytes = uploaded_file.read()
            with open(uploaded_save_path, "wb") as f:
                f.write(img_bytes)
            st.session_state.current_image_path = uploaded_save_path
    
    with col_preset:
        st.markdown("**Quick Preset Spaces:**")
        preset_labels = {
            "real_room.jpeg": "🛋️ Scandinavian Lounge",
            "test_room.jpg": "🏡 Modern Living Room"
        }
        for idx, resolved_p in enumerate(DEMO_IMAGE_CANDIDATES):
            base_fname = os.path.basename(resolved_p)
            btn_lbl = preset_labels.get(base_fname, f"🛋️ Preset Space ({base_fname})")
            if st.button(btn_lbl, key=f"btn_preset_{idx}", use_container_width=True):
                st.session_state.current_image_path = resolved_p
                st.rerun()

    current_img = st.session_state.current_image_path
    if not current_img or not os.path.exists(current_img):
        st.warning("Please upload a room photograph or select a preset demo above to continue.")
        st.stop()

    st.markdown("---")

    # -------------------------------------------------------------
    # 5.2 Showstopper #3: AI Vision Mode Toggle
    # -------------------------------------------------------------
    st.markdown('<div class="section-title"><span class="step-badge">2</span> Spatial Perception & Neural Vision HUD</div>', unsafe_allow_html=True)
    
    vision_toggle_col, _ = st.columns([2, 2])
    with vision_toggle_col:
        ai_vision_mode = st.toggle(
            "🔬 Enable AI Vision Mode (Expose CV Brain)", 
            value=False,
            help="Toggles between normal photography and internal computer vision neural heatmaps + structural edge lines."
        )

    if ai_vision_mode:
        st.info("💡 **AI Vision Mode Active:** Displaying Metric Depth Anything V2 thermal map and Canny structural edge locking.")
        
        vis_col1, vis_col2, vis_col3 = st.columns(3)
        
        with vis_col1:
            st.image(current_img, caption="Input Room Photo", use_container_width=True)
        
        with vis_col2:
            if st.session_state.depth_heatmap_path and os.path.exists(st.session_state.depth_heatmap_path):
                st.image(st.session_state.depth_heatmap_path, caption="Depth Anything V2 Heatmap (Blue=Near, Red=Far)", use_container_width=True)
            elif VISION_ENGINE_AVAILABLE:
                with st.spinner("Generating Depth Heatmap..."):
                    d_path = vision_engine.generate_depth_heatmap(current_img)
                    st.session_state.depth_heatmap_path = d_path
                    st.image(d_path, caption="Depth Anything V2 Heatmap", use_container_width=True)
        
        with vis_col3:
            if st.session_state.structural_edges_path and os.path.exists(st.session_state.structural_edges_path):
                st.image(st.session_state.structural_edges_path, caption="Canny Structural Wireframe (Locked Edges)", use_container_width=True)
            elif VISION_ENGINE_AVAILABLE:
                with st.spinner("Tracing Structural Edges..."):
                    e_path = vision_engine.detect_structural_edges(current_img)
                    st.session_state.structural_edges_path = e_path
                    st.image(e_path, caption="Canny Structural Wireframe", use_container_width=True)

        # HUD Spatial Metrics
        if st.session_state.spatial_metrics is None and VISION_ENGINE_AVAILABLE:
            st.session_state.spatial_metrics = vision_engine.estimate_spatial_metrics(current_img, ceiling_height)

        metrics = st.session_state.spatial_metrics or {
            "floor_area_sqft": 140.3, "wall_surface_area_sqft": 405.3,
            "estimated_length_ft": 12.2, "estimated_width_ft": 11.5,
            "detected_structural_openings": "2 Windows, 1 Doorway"
        }

        st.markdown(f"""
        <div class="hud-card">
            <div class="hud-header">📐 Spatial Dimension & Boundary HUD</div>
            <div class="hud-stat-grid">
                <div class="hud-stat-box">
                    <div class="hud-stat-val">{metrics['floor_area_sqft']}</div>
                    <div class="hud-stat-lbl">Floor Area (Sq.Ft)</div>
                </div>
                <div class="hud-stat-box">
                    <div class="hud-stat-val">{metrics['wall_surface_area_sqft']}</div>
                    <div class="hud-stat-lbl">Wall Surface (Sq.Ft)</div>
                </div>
                <div class="hud-stat-box">
                    <div class="hud-stat-val">{metrics['estimated_length_ft']}' × {metrics['estimated_width_ft']}'</div>
                    <div class="hud-stat-lbl">Est. L × W</div>
                </div>
                <div class="hud-stat-box">
                    <div class="hud-stat-val">Locked</div>
                    <div class="hud-stat-lbl">{metrics['detected_structural_openings']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.image(current_img, caption="Input Room Photo (Flip 'AI Vision Mode' toggle above to reveal depth & edge maps)", use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------
    # 5.3 Showstopper #1: Redesign & Inpainting
    # -------------------------------------------------------------
    st.markdown('<div class="section-title"><span class="step-badge">3</span> Architecture-Conditioned Redesign & Magic Wand Inpainting</div>', unsafe_allow_html=True)
    st.caption("ControlNet locks the room geometry while localized inpainting swaps target surface materials on demand.")

    redesign_col_controls, redesign_col_view = st.columns([1, 1])

    with redesign_col_controls:
        st.markdown("#### Full Theme Synthesis")
        st.write(f"Target Aesthetic: **{selected_style}**")
        if st.button("🪄 Generate Interior Redesign", type="primary", use_container_width=True):
            if VISION_ENGINE_AVAILABLE:
                with st.spinner(f"Synthesizing {selected_style} design with geometric invariance..."):
                    r_path = vision_engine.generate_interior_redesign(current_img, style=selected_style)
                    st.session_state.redesign_path = r_path
                    st.session_state.active_preview_mode = "✨ Style Redesign"
                    st.session_state.last_action_msg = f"✨ Synthesized '{selected_style}' redesign!"
                    st.rerun()

        st.markdown("---")
        st.markdown("#### 🪄 Magic Wand: Selective Surface Inpainting")
        target_surface = st.selectbox("Target Surface to Modify:", ["floor", "wall"])
        new_material = st.selectbox("Swap Material To (Indian Catalog):", [
            "Italian Carrara Marble",
            "Kajaria Double-Charged Vitrified Tile",
            "Action TESA Engineered Oak Wood",
            "Asian Paints Royale Velvet Texture"
        ])

        material_specs = {
            "Italian Carrara Marble": ("🏛️", "Italian Carrara Marble", "₹380 / sq.ft", "Polished luxury pearl-white surface with organic grey-blue veining."),
            "Kajaria Double-Charged Vitrified Tile": ("🧱", "Kajaria Vitrified Tiles", "₹75 / sq.ft", "High-gloss porcelain finish with laser-cut 2mm grout grid."),
            "Action TESA Engineered Oak Wood": ("🪵", "Action TESA Oak Wood", "₹175 / sq.ft", "Warm golden-honey oak planks with micro-beveled seams."),
            "Asian Paints Royale Velvet Texture": ("🎨", "Asian Paints Royale Velvet", "₹28 / sq.ft", "Luxury velvet sheen with low-VOC Teflon surface protection.")
        }
        m_icon, m_title, m_price, m_desc = material_specs.get(new_material, ("✨", new_material, "Catalog Rate", "Verified Indian supplier SKU."))
        st.markdown(f"""
        <div class="material-swatch-card">
            <div class="material-icon-bubble">{m_icon}</div>
            <div>
                <div class="material-details-title">{m_title} &nbsp;<span class="material-details-price">{m_price}</span></div>
                <div class="material-details-desc">{m_desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("✨ Inpaint Surface Only", use_container_width=True):
            if VISION_ENGINE_AVAILABLE:
                with st.spinner(f"Inpainting {target_surface} with {new_material}..."):
                    inp_path = vision_engine.inpaint_surface_material(
                        current_img, target_surface=target_surface, new_material=new_material
                    )
                    st.session_state.inpaint_path = inp_path
                    st.session_state.active_preview_mode = "🪄 Localized Inpaint"
                    st.session_state.last_action_msg = f"🪄 Inpainted {target_surface.capitalize()} with '{new_material}'!"
                    st.rerun()

    with redesign_col_view:
        if st.session_state.last_action_msg:
            st.success(st.session_state.last_action_msg)
            
        preview_modes = ["✨ Style Redesign", "🪄 Localized Inpaint", "🔄 Before vs After Side-by-Side"]
        curr_mode = st.session_state.active_preview_mode
        curr_idx = preview_modes.index(curr_mode) if curr_mode in preview_modes else 0
        
        chosen_view = st.radio(
            "Live Output View:",
            preview_modes,
            index=curr_idx,
            horizontal=True
        )
        st.session_state.active_preview_mode = chosen_view

        if chosen_view == "✨ Style Redesign":
            if st.session_state.redesign_path and os.path.exists(st.session_state.redesign_path):
                img_obj = Image.open(st.session_state.redesign_path)
                st.image(img_obj, caption=f"Redesigned ({selected_style})", use_container_width=True)
            else:
                st.image(Image.open(current_img), caption="Original Room Preview", use_container_width=True)
                
        elif chosen_view == "🪄 Localized Inpaint":
            if st.session_state.inpaint_path and os.path.exists(st.session_state.inpaint_path):
                img_obj = Image.open(st.session_state.inpaint_path)
                st.image(img_obj, caption=f"Inpainted: {new_material} on {target_surface.capitalize()}", use_container_width=True)
            else:
                st.image(Image.open(current_img), caption="Original Room Preview (Click 'Inpaint Surface Only' to generate)", use_container_width=True)
                
        elif chosen_view == "🔄 Before vs After Side-by-Side":
            b_col, a_col = st.columns(2)
            with b_col:
                st.image(Image.open(current_img), caption="Before: Original Room", use_container_width=True)
            with a_col:
                if st.session_state.inpaint_path and os.path.exists(st.session_state.inpaint_path) and curr_mode == "🪄 Localized Inpaint":
                    st.image(Image.open(st.session_state.inpaint_path), caption=f"After: Inpainted ({new_material})", use_container_width=True)
                elif st.session_state.redesign_path and os.path.exists(st.session_state.redesign_path):
                    st.image(Image.open(st.session_state.redesign_path), caption=f"After: Redesigned ({selected_style})", use_container_width=True)
                elif st.session_state.inpaint_path and os.path.exists(st.session_state.inpaint_path):
                    st.image(Image.open(st.session_state.inpaint_path), caption=f"After: Inpainted ({new_material})", use_container_width=True)
                else:
                    st.info("Click 'Generate Redesign' or 'Inpaint Surface' to see comparison.")

    st.markdown("---")

    # -------------------------------------------------------------
    # 5.4 Showstopper #4: YOLOv8 Furniture Detection & Pins
    # -------------------------------------------------------------
    st.markdown('<div class="section-title"><span class="step-badge">4</span> YOLOv8 Furniture Localization & Spatial Pins</div>', unsafe_allow_html=True)
    
    if st.button("📍 Detect Furniture Objects & Interactive Pins", use_container_width=True):
        if VISION_ENGINE_AVAILABLE:
            with st.spinner("Running YOLOv8 neural network inference for furniture localization..."):
                items = vision_engine.detect_furniture_objects(current_img)
                st.session_state.detected_objects = items
                st.session_state.detected_objects_path = resolve_path("detected_objects.png")
                st.rerun()

    det_col_img, det_col_table = st.columns([1, 1])
    with det_col_img:
        if st.session_state.detected_objects_path and os.path.exists(st.session_state.detected_objects_path):
            st.image(Image.open(st.session_state.detected_objects_path), caption="YOLOv8 Localized Furniture & Interactive Pins", use_container_width=True)
        else:
            st.image(Image.open(current_img), caption="Original Room", use_container_width=True)
    
    with det_col_table:
        st.markdown("#### 📋 Detected Spatial Inventory")
        items = st.session_state.detected_objects
        if items and len(items) > 0:
            table_rows = []
            for i, obj in enumerate(items, 1):
                pin_x, pin_y = obj.get("pin", (0, 0))
                conf = obj.get("confidence", 0.0)
                table_rows.append({
                    "Pin": f"📍 {i}",
                    "Item": obj.get("label", "Unknown"),
                    "Confidence": f"{int(conf * 100)}%",
                    "Pin Coordinates": f"({pin_x}, {pin_y})",
                    "Status": "Sourced via Kajaria / Urban Ladder"
                })
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Click 'Detect Furniture Objects' above to run YOLOv8 on this space.")

    st.markdown("---")

    # -------------------------------------------------------------
    # 5.5 Portfolio Save Action
    # -------------------------------------------------------------
    st.markdown('<div class="section-title"><span class="step-badge">5</span> Save Project to Persistent Portfolio</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card" style="padding: 22px 24px; margin-top: 10px;">
        <div style="font-weight: 700; color: #F8FAFC; font-size: 1.05rem; margin-bottom: 4px;">
            💼 Store Session in Architect & Client Portfolio
        </div>
        <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 16px;">
            Saves high-resolution synthesis renders, localized inpaint maps, YOLO inventory, and BoQ calculations to your SQLite project history.
        </div>
    </div>
    """, unsafe_allow_html=True)

    save_col_name, save_col_btn = st.columns([3, 1])
    with save_col_name:
        save_p_name = st.text_input("Project Name:", value=f"Living Room Design - {selected_style}")
    with save_col_btn:
        st.write("") # spacing
        st.write("")
        if st.button("💾 Save to Portfolio", type="primary", use_container_width=True):
            if AUTH_AVAILABLE:
                saved_boq = st.session_state.get("active_boq") or {}
                saved_fin = saved_boq.get("financial_summary", {})
                saved_dims = saved_boq.get("dimensions", {})
                pid = auth_manager.save_user_project(
                    user_id=user["id"],
                    project_name=save_p_name,
                    style=selected_style,
                    budget=float(saved_fin.get("budget_cap", budget_inr)),
                    grand_total=float(saved_fin.get("grand_total", 119342.20)),
                    floor_sqft=float(saved_dims.get("floor_sqft", 140.3)),
                    wall_sqft=float(saved_dims.get("wall_sqft", 405.3)),
                    boq_data=saved_boq or {"status": "Within Budget"},
                    image_path=st.session_state.redesign_path or current_img
                )
                st.success(f"Project '{save_p_name}' successfully saved to SQLite database (Project ID: #{pid})!")
            else:
                st.error("Database connection unavailable.")


# =====================================================================
# 6. FOOTER
# =====================================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 16px;">
    <strong>AI-GLAZE</strong> • College Capstone Project • MVJ College of Engineering • Indian Market Edition (INR ₹)
</div>
""", unsafe_allow_html=True)
