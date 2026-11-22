"""
ui_dashboard.py - AI-GLAZE Commercial-Grade Frontend & Studio Platform
Lead: Member 2 (Teammate A: Frontend & Interactive UI Lead)
Project: AI-GLAZE - Intelligent Home Planning & Interior Platform (Indian Market Edition - INR ₹)
"Plan it. Design it. Source it. Budget it!"

Features:
  1. Commercial Glassmorphic Landing & Auth Portal (Sign In, Register, Quick Demo 1-Click Logins)
  2. Role-Based Workspace (Professional Architect vs Homeowner / DIY Renovator)
  3. Status Bar & User Session Manager (Welcome banner, role badge, city, sign-out)
  4. Sidebar Controls (Style Selector, INR ₹ Budget Slider ₹50k-₹6L, Dynamic Economy/Mid/Luxury Badge)
  5. Studio Tab 1: Spatial Design Studio (AI Vision Mode, Depth Heatmap, Canny Edges, HUD Telemetry,
                   Magic Wand Inpainting, YOLOv8 Furniture Detection & Spatial Pins, Save to Portfolio)
  6. Studio Tab 2: My Saved Portfolio (Persistent SQLite retrieval, analytics, project cards, deletion)
  7. Studio Tab 3: Contractor BoQ Document (Interactive HTML report preview, BoQ breakdown, 1-click download)
"""

import os
import io
import json
import time
from datetime import datetime
from PIL import Image
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Import local modules with defensive fallbacks
try:
    import auth_manager
    AUTH_AVAILABLE = True
except Exception as _auth_err:
    AUTH_AVAILABLE = False
    AUTH_ERR_MSG = str(_auth_err)

try:
    import vision_engine
    VISION_AVAILABLE = True
except Exception as _vis_err:
    VISION_AVAILABLE = False
    VISION_ERR_MSG = str(_vis_err)

try:
    import cost_engine
    COST_AVAILABLE = True
except Exception as _cost_err:
    COST_AVAILABLE = False
    COST_ERR_MSG = str(_cost_err)


# =====================================================================
# 1. PAGE CONFIGURATION & COMMERCIAL THEME CSS
# =====================================================================
st.set_page_config(
    page_title="AI-GLAZE | Intelligent Home Planning & Interior Platform",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Typography & Palette */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Commercial Hero Header Banner */
    .og-hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 45%, #1e3a8a 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 30px 36px;
        border-radius: 20px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.6);
        position: relative;
        overflow: hidden;
    }
    .og-hero-card::after {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.25) 0%, rgba(0,0,0,0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .og-hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: -0.7px;
        margin-bottom: 6px;
        background: linear-gradient(90deg, #ffffff 30%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .og-hero-subtitle {
        font-size: 1.15rem;
        font-weight: 500;
        color: #94a3b8;
        letter-spacing: 0.2px;
        margin-bottom: 14px;
    }
    .og-pill {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-right: 8px;
        margin-top: 6px;
        backdrop-filter: blur(8px);
    }

    /* User Profile Status Bar */
    .user-nav-bar {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 12px 20px;
        color: #f8fafc;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 22px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
    .user-meta-group {
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
    }
    .user-role-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .role-arch {
        background: #3b82f6;
        color: white;
    }
    .role-home {
        background: #10b981;
        color: white;
    }

    /* Spatial HUD Card */
    .hud-card {
        background: linear-gradient(145deg, #0b1120, #1e293b);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        color: #f8fafc;
        margin-top: 14px;
        margin-bottom: 18px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .hud-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #38bdf8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 14px;
    }
    .hud-stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 14px;
    }
    .hud-stat-box {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    .hud-stat-val {
        font-size: 1.35rem;
        font-weight: 700;
        color: #38bdf8;
        font-family: 'JetBrains Mono', monospace;
    }
    .hud-stat-lbl {
        font-size: 0.74rem;
        color: #94a3b8;
        text-transform: uppercase;
        margin-top: 4px;
    }

    /* Tier Badges (INR ₹) */
    .tier-badge-economy {
        background: #10b981;
        color: white;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
    }
    .tier-badge-mid {
        background: #0284c7;
        color: white;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
    }
    .tier-badge-luxury {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
    }

    /* Section Subheaders */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 14px;
        margin-bottom: 12px;
        border-left: 4px solid #38bdf8;
        padding-left: 10px;
    }

    /* Portfolio Card */
    .portfolio-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        transition: transform 0.15s ease;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# 2. SESSION STATE MANAGEMENT
# =====================================================================
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

# Fallback room presets in the repository
CANDIDATE_DEMOS = ["real_room.jpeg", "real_room.jpg", "test_room.jpg"]
RESOLVED_DEMO = None
for candidate in CANDIDATE_DEMOS:
    if os.path.exists(candidate):
        RESOLVED_DEMO = candidate
        break

if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = RESOLVED_DEMO

if "depth_heatmap_path" not in st.session_state:
    st.session_state.depth_heatmap_path = "depth_heatmap.png" if os.path.exists("depth_heatmap.png") else None

if "structural_edges_path" not in st.session_state:
    st.session_state.structural_edges_path = "structural_edges.png" if os.path.exists("structural_edges.png") else None

if "spatial_metrics" not in st.session_state:
    st.session_state.spatial_metrics = None

if "redesign_path" not in st.session_state:
    st.session_state.redesign_path = "redesign_output.png" if os.path.exists("redesign_output.png") else None

if "inpaint_path" not in st.session_state:
    st.session_state.inpaint_path = "inpaint_output.png" if os.path.exists("inpaint_output.png") else None

if "detected_objects" not in st.session_state:
    st.session_state.detected_objects = None

if "detected_objects_path" not in st.session_state:
    st.session_state.detected_objects_path = "detected_objects.png" if os.path.exists("detected_objects.png") else None


# =====================================================================
# 3. AUTHENTICATION PORTAL (WHEN NOT LOGGED IN)
# =====================================================================
if st.session_state.authenticated_user is None:
    # Commercial Hero Banner
    st.markdown("""
    <div class="og-hero-card">
        <div class="og-hero-title">🏡 AI-GLAZE: Intelligent Home Planning & Interior Platform</div>
        <div class="og-hero-subtitle">Plan it. Design it. Source it. Budget it! (Indian Architecture & Market Edition - INR ₹)</div>
        <div>
            <span class="og-pill">📐 Depth Anything V2</span>
            <span class="og-pill">🧱 Canny Structural Edges</span>
            <span class="og-pill">🪄 Magic Wand Inpainting</span>
            <span class="og-pill">📍 YOLOv8 Furniture Pins</span>
            <span class="og-pill">📊 Knapsack BoQ Optimizer</span>
            <span class="og-pill">🔒 SQLite Enterprise Auth</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    auth_col_main, auth_col_info = st.columns([1.15, 0.85], gap="large")

    with auth_col_main:
        st.markdown("### 🔐 Secure Workspace Portal")
        auth_tab_login, auth_tab_reg = st.tabs(["[ 🔐 Sign In to Workspace ]", "[ 📝 Register New Account ]"])

        # ------------ TAB 1: SIGN IN ------------
        with auth_tab_login:
            st.markdown("Enter your registered credentials or select a 1-click evaluation demo below.")
            with st.form("form_signin"):
                login_id = st.text_input("Username or Email Address:", placeholder="e.g. sanjana_arch or rahul_home")
                login_pwd = st.text_input("Password:", type="password", placeholder="Enter your password")
                signin_submit = st.form_submit_button("Sign In to Dashboard", type="primary", use_container_width=True)

                if signin_submit:
                    if not login_id or not login_pwd:
                        st.warning("Please provide both username/email and password.")
                    else:
                        user = auth_manager.authenticate_user(login_id, login_pwd)
                        if user:
                            st.session_state.authenticated_user = user
                            st.success(f"Welcome back, {user['full_name']}!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please verify your details or use the quick demo logins below.")

            st.markdown("---")
            st.markdown("##### ⚡ Quick 1-Click Evaluation Presets (College Review & Viva)")
            demo_c1, demo_c2 = st.columns(2)
            with demo_c1:
                if st.button("📐 Demo: Architect Mode\n(Ar. Sanjana Hoskote)", use_container_width=True):
                    demo_user = auth_manager.authenticate_user("sanjana_arch", "demo123")
                    if demo_user:
                        st.session_state.authenticated_user = demo_user
                        st.rerun()
            with demo_c2:
                if st.button("🏠 Demo: Homeowner Mode\n(Rahul Sharma)", use_container_width=True):
                    demo_user = auth_manager.authenticate_user("rahul_home", "demo123")
                    if demo_user:
                        st.session_state.authenticated_user = demo_user
                        st.rerun()

        # ------------ TAB 2: REGISTER ------------
        with auth_tab_reg:
            st.markdown("Create a new role-based account in our persistent SQLite database (`users.db`).")
            with st.form("form_register"):
                reg_name = st.text_input("Full Name:", placeholder="e.g. Priya Venkatesh")
                reg_user = st.text_input("Choose Username:", placeholder="e.g. priya_design")
                reg_mail = st.text_input("Email Address:", placeholder="e.g. priya@gmail.com")
                reg_pass = st.text_input("Password:", type="password", placeholder="Minimum 4 characters")
                reg_city = st.text_input("City:", value="Bangalore", placeholder="e.g. Bangalore, Mumbai, Delhi")
                
                reg_role = st.selectbox(
                    "Select Your Platform Role:",
                    options=[
                        "Professional Architect / Interior Designer",
                        "Homeowner / DIY Renovator"
                    ],
                    index=0
                )
                
                reg_submit = st.form_submit_button("Create Account & Enter Platform", type="primary", use_container_width=True)

                if reg_submit:
                    success, msg, new_user = auth_manager.register_user(
                        full_name=reg_name,
                        username=reg_user,
                        email=reg_mail,
                        password=reg_pass,
                        role=reg_role,
                        city=reg_city
                    )
                    if success:
                        st.session_state.authenticated_user = new_user
                        st.success(f"{msg} Logging you in...")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(msg)

    with auth_col_info:
        st.markdown("""
        ### 🌟 AI-GLAZE Core Capabilities
        
        **1. Depth Anything V2 Thermal Perception**
        - Traces 3D room volume and locks architectural structural boundaries.
        - Calculates floor and wall area metrics in real-time.
        
        **2. Showstopper #1: "The Magic Wand"**
        - Selective surface inpainting: swap only the flooring or walls without disturbing furniture or lighting.
        
        **3. Showstopper #4: YOLOv8 Furniture Pins**
        - Accurate bounding boxes with pin coordinates for catalog sourcing.
        
        **4. Indian Market BoQ & Knapsack Optimization (INR ₹)**
        - Real supplier pricing: Kajaria Tiles, Italian Carrara Marble, Asian Paints Royale, Action TESA wood.
        - Generates contractor-ready BoQ HTML reports.
        """)
        st.info("💡 **Tip for Reviewers:** Use the 1-Click Demo buttons on the left to immediately enter the studio as an Architect or Homeowner.")

    # Guard: Stop execution here so protected studio only renders when authenticated!
    st.stop()


# =====================================================================
# 4. LOGGED-IN STATUS BAR & USER CONTEXT
# =====================================================================
user = st.session_state.authenticated_user
is_architect = "Architect" in user.get("role", "")
role_class = "role-arch" if is_architect else "role-home"
role_emoji = "📐" if is_architect else "🏠"

bar_col_info, bar_col_btn = st.columns([4, 1])
with bar_col_info:
    st.markdown(f"""
    <div class="user-nav-bar">
        <div class="user-meta-group">
            <span style="font-size: 1.15rem; font-weight: 700;">👤 Welcome, {user['full_name']}</span>
            <span class="user-role-badge {role_class}">{role_emoji} {user['role']}</span>
            <span style="color: #94a3b8; font-size: 0.9rem;">📍 {user.get('city', 'Bangalore')}</span>
            <span style="color: #64748b; font-size: 0.82rem;">• Active Session: <code>users.db</code></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with bar_col_btn:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.authenticated_user = None
        st.toast("Signed out successfully.")
        st.rerun()


# =====================================================================
# 5. SIDEBAR CONFIGURATION (INDIAN MARKET EDITION - INR ₹)
# =====================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/interior.png", width=60)
    st.markdown("### 🎛️ Design & Budget Engine")
    st.caption("AI-GLAZE Indian Market Studio (INR ₹)")
    st.markdown("---")

    # 1. Interior Style Selector
    st.markdown("#### 🎨 Theme Aesthetic")
    style_options = [
        "Scandinavian Minimalist",
        "Modern Luxury",
        "Industrial Warm",
        "Traditional Heritage"
    ]
    style_descriptions = {
        "Scandinavian Minimalist": "Light oak timber, airy layouts, clean lines & natural sunlight.",
        "Modern Luxury": "Italian Carrara marble, brushed brass, cove lighting & velvet.",
        "Industrial Warm": "Exposed Bangalore wirecut brick, raw iron & warm Edison glows.",
        "Traditional Heritage": "Carved Burma teak wood, brass urlis & timeless royal warmth."
    }
    selected_style = st.selectbox(
        "Select Theme:",
        options=style_options,
        index=0,
        help="Controls the diffusion conditioning and generative color tones in vision_engine.py"
    )
    st.caption(f"ℹ️ *{style_descriptions[selected_style]}*")
    st.markdown("---")

    # 2. Budget Slider in Indian Rupees (₹)
    # Range ₹50,000 to ₹6,00,000, step ₹10,000, default ₹1,50,000
    st.markdown("#### 💰 Renovation Budget (INR ₹)")
    budget_inr = st.slider(
        "Budget Cap (₹):",
        min_value=50000,
        max_value=600000,
        value=150000,
        step=10000,
        format="₹%d",
        help="Defines the knapsack budget constraint in cost_engine.py"
    )

    # 3. Dynamic Tier Badge (< ₹1L Economy, ₹1L - ₹2.5L Mid-Range, > ₹2.5L Luxury)
    if budget_inr < 100000:
        tier_title = "Economy Tier"
        tier_class = "tier-badge-economy"
        tier_emoji = "🏷️"
        tier_badge_text = f"₹{budget_inr/100000:.2f}L • Economy"
        tier_desc = "Optimal for Kajaria vitrified tiles, washable emulsion & modular DIY elements."
    elif budget_inr <= 250000:
        tier_title = "Mid-Range Tier"
        tier_class = "tier-badge-mid"
        tier_emoji = "⚖️"
        tier_badge_text = f"₹{budget_inr/100000:.2f}L • Mid-Range"
        tier_desc = "Engineered oak planks, Asian Paints Royale Silk & designer upholstery."
    else:
        tier_title = "Luxury Premium Tier"
        tier_class = "tier-badge-luxury"
        tier_emoji = "✨"
        tier_badge_text = f"₹{budget_inr/100000:.2f}L • Luxury"
        tier_desc = "Italian Statuario marble, bespoke teak woodwork, Hafele hardware & smart lighting."

    st.markdown(f"""
    <div style="margin-top: 10px; margin-bottom: 6px;">
        <span class="{tier_class}">{tier_emoji} {tier_badge_text}</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"*{tier_desc}*")

    st.markdown("---")
    st.markdown("#### 🛠️ Module Telemetry")
    st.markdown(f"🟢 `auth_manager.py` (Active)")
    st.markdown(f"🟢 `vision_engine.py` ({'Ready' if VISION_AVAILABLE else 'Mock'})")
    st.markdown(f"🟢 `cost_engine.py` ({'Ready' if COST_AVAILABLE else 'Mock'})")


# =====================================================================
# 6. MAIN 3 STUDIO TABS
# =====================================================================
tab_design, tab_portfolio, tab_boq = st.tabs([
    "🛋️ Spatial Design Studio",
    "📁 My Saved Portfolio",
    "📄 Contractor BoQ Document"
])


# =====================================================================
# TAB 1: SPATIAL DESIGN STUDIO
# =====================================================================
with tab_design:
    st.markdown('<div class="section-title">Step 1: Room Photo Upload & Spatial Ingestion</div>', unsafe_allow_html=True)

    up_c1, up_c2 = st.columns([3, 1])
    with up_c1:
        uploaded_file = st.file_uploader(
            "📸 Upload Living Room / Bedroom Photo (JPG, PNG, JPEG):",
            type=["jpg", "jpeg", "png"],
            help="Upload your room photo to trigger automated depth calculation and object detection."
        )
    with up_c2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if RESOLVED_DEMO and st.button("🖼️ Use Demo Room Photo", use_container_width=True):
            st.session_state.current_image_path = RESOLVED_DEMO
            st.toast(f"Loaded preset room image: {RESOLVED_DEMO}", icon="✅")

    if uploaded_file is not None:
        save_temp_path = "uploaded_room_temp.jpg"
        with open(save_temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.current_image_path = save_temp_path
        st.toast("Room photo uploaded and ready for analysis!", icon="📸")

    current_img = st.session_state.current_image_path

    if not current_img or not os.path.exists(current_img):
        st.info("👋 Please upload a room photo above or click **'Use Demo Room Photo'** to launch the design studio.")
        st.stop()

    st.markdown("---")

    # -------------------------------------------------------------
    # SHOWSTOPPER #3: AI VISION MODE TOGGLE
    # -------------------------------------------------------------
    st.markdown('<div class="section-title">🔬 Showstopper #3: Spatial Depth & Structural Perception</div>', unsafe_allow_html=True)

    v_toggle_col, _ = st.columns([2, 1])
    with v_toggle_col:
        ai_vision_mode = st.toggle(
            "🔬 Enable AI Vision Mode (Depth Anything V2 + Canny Lineart)",
            value=False,
            help="Visualizes the thermal depth heatmap, structural invariants, and room dimension telemetry."
        )

    # Compute metrics if not cached
    if st.session_state.spatial_metrics is None and VISION_AVAILABLE:
        try:
            st.session_state.spatial_metrics = vision_engine.estimate_spatial_metrics(current_img)
        except Exception as e:
            st.warning(f"Spatial metrics calculation note: {e}")

    metrics = st.session_state.spatial_metrics or {
        "floor_area_sqft": 138.0,
        "wall_surface_area_sqft": 401.5,
        "estimated_length_ft": 12.0,
        "estimated_width_ft": 11.5,
        "detected_structural_openings": "2 Windows, 1 Doorway"
    }

    if not ai_vision_mode:
        img_c1, img_c2 = st.columns([2, 1])
        with img_c1:
            st.image(current_img, caption="Original Room Photo (Clean Perspective)", use_container_width=True)
        with img_c2:
            st.markdown("### 📷 Clean Perspective View")
            st.markdown("""
            You are viewing the pristine room photograph.
            
            👉 **Turn ON `[ 🔬 Enable AI Vision Mode ]`** above to unlock:
            - **Thermal Depth Heatmap** (Depth Anything V2 tensor: Blue = Floor, Red = Far Walls)
            - **Structural Canny Edges** (Locks architectural walls & beam geometry)
            - **Architectural HUD Telemetry** (Real-time calculated floor sq.ft & wall sq.ft)
            """)
            st.info("Tip: Architects use AI Vision Mode to verify structural load lines before initiating renovations.")
    else:
        # Generate depth and edges if missing
        if VISION_AVAILABLE:
            with st.spinner("Generating Depth Anything V2 tensors and Canny structural wireframes..."):
                if not st.session_state.depth_heatmap_path or not os.path.exists(st.session_state.depth_heatmap_path):
                    st.session_state.depth_heatmap_path = vision_engine.generate_depth_heatmap(current_img)
                if not st.session_state.structural_edges_path or not os.path.exists(st.session_state.structural_edges_path):
                    st.session_state.structural_edges_path = vision_engine.detect_structural_edges(current_img)

        c_v1, c_v2, c_v3 = st.columns(3)
        with c_v1:
            st.markdown("**1. Original Room Input**")
            st.image(current_img, use_container_width=True)
            st.caption("Pristine RGB perspective")

        with c_v2:
            st.markdown("**2. Thermal Depth Heatmap**")
            if st.session_state.depth_heatmap_path and os.path.exists(st.session_state.depth_heatmap_path):
                st.image(st.session_state.depth_heatmap_path, use_container_width=True)
                st.caption("🔵 Blue = Floor/Near | 🔴 Red = Distant Walls")
            else:
                st.warning("Depth map generating...")

        with c_v3:
            st.markdown("**3. Structural Canny Edges**")
            if st.session_state.structural_edges_path and os.path.exists(st.session_state.structural_edges_path):
                st.image(st.session_state.structural_edges_path, use_container_width=True)
                st.caption("Wall, beam & window frame geometry")
            else:
                st.warning("Structural edges generating...")

        # HUD Telemetry Card
        st.markdown(f"""
        <div class="hud-card">
            <div class="hud-header">📡 Architectural Telemetry HUD // Indian Standard Room Metrics</div>
            <div class="hud-stat-grid">
                <div class="hud-stat-box">
                    <div class="hud-stat-val">{metrics.get('floor_area_sqft', 138.0)}</div>
                    <div class="hud-stat-lbl">Floor Area (Sq.Ft)</div>
                </div>
                <div class="hud-stat-box">
                    <div class="hud-stat-val">{metrics.get('wall_surface_area_sqft', 401.5)}</div>
                    <div class="hud-stat-lbl">Wall Surface (Sq.Ft)</div>
                </div>
                <div class="hud-stat-box">
                    <div class="hud-stat-val">{metrics.get('estimated_length_ft', 12.0)} x {metrics.get('estimated_width_ft', 11.5)}</div>
                    <div class="hud-stat-lbl">Dimensions (L x W ft)</div>
                </div>
                <div class="hud-stat-box">
                    <div class="hud-stat-val" style="font-size: 1rem; padding-top: 4px;">{metrics.get('detected_structural_openings', '2 Windows, 1 Door')}</div>
                    <div class="hud-stat-lbl">Structural Openings</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------------------------------------------------------------
    # GENERATIVE REDESIGN & SHOWSTOPPER #1: MAGIC WAND INPAINTING
    # -------------------------------------------------------------
    st.markdown('<div class="section-title">🎨 Generative Redesign & Showstopper #1: Magic Wand Inpainting</div>', unsafe_allow_html=True)

    subtab_redesign, subtab_inpaint = st.tabs([
        "🪄 AI Interior Redesign (Full Room)",
        "✨ Showstopper #1: Selective Surface Inpainting (Material Swap)"
    ])

    with subtab_redesign:
        r_col1, r_col2 = st.columns([1, 1])
        with r_col1:
            st.markdown(f"#### Transform Room into **{selected_style}**")
            st.markdown(f"""
            - **Target Aesthetic:** `{selected_style}`
            - **Budget Cap:** `₹{budget_inr:,}` ({tier_title})
            - **Structural Geometry:** Canny boundary invariant locking active
            """)
            if st.button("🪄 Generate Interior Redesign", type="primary", use_container_width=True):
                if VISION_AVAILABLE:
                    with st.spinner(f"Synthesizing {selected_style} design with structural preservation..."):
                        out_redesign = vision_engine.generate_interior_redesign(current_img, style=selected_style)
                        st.session_state.redesign_path = out_redesign
                        st.success(f"Interior redesigned in '{selected_style}' style!")
                else:
                    st.error("`vision_engine.py` is not accessible.")

        with r_col2:
            if st.session_state.redesign_path and os.path.exists(st.session_state.redesign_path):
                st.image(st.session_state.redesign_path, caption=f"AI Generated: {selected_style}", use_container_width=True)
                with open(st.session_state.redesign_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Redesigned Render",
                        data=f.read(),
                        file_name=f"aiglaze_redesign_{selected_style.lower().replace(' ', '_')}.png",
                        mime="image/png"
                    )
            else:
                st.image(current_img, caption="Original Room (Awaiting Redesign Generation)", use_container_width=True)

    with subtab_inpaint:
        st.markdown("#### 🪄 'The Magic Wand' - Selective Surface Inpainting")
        st.caption("Swap materials on specific architectural surfaces without altering the rest of the room.")

        inp_c1, inp_c2 = st.columns([1, 1])
        with inp_c1:
            target_surface = st.selectbox(
                "1. Target Surface to Inpaint:",
                options=["floor", "wall"],
                format_func=lambda s: "🏢 Flooring Surface (Sub-floor / Tiles)" if s == "floor" else "🧱 Wall Facade (Vertical Surfaces)"
            )

            material_options_inr = [
                "Italian Carrara Marble",
                "Kajaria Vitrified Tile",
                "Action TESA Oak Wood",
                "Venetian Stucco Plaster",
                "Asian Paints Royale Silk"
            ]
            new_material = st.selectbox("2. Select Replacement Material:", options=material_options_inr, index=0)

            st.markdown(f"""
            **Inpainting Specifications:**
            - **Target Surface:** `{target_surface.upper()}`
            - **Material:** `{new_material}`
            - **Preservation:** Surrounding furniture, lighting & structural boundaries remain invariant.
            """)

            if st.button("🎨 Inpaint Surface", use_container_width=True, type="secondary"):
                if VISION_AVAILABLE:
                    with st.spinner(f"Inpainting {target_surface} with {new_material}..."):
                        out_inp = vision_engine.inpaint_surface_material(
                            current_img,
                            target_surface=target_surface,
                            new_material=new_material
                        )
                        st.session_state.inpaint_path = out_inp
                        st.success(f"Inpainted {target_surface} with {new_material}!")
                else:
                    st.error("`vision_engine.py` is not accessible.")

        with inp_c2:
            if st.session_state.inpaint_path and os.path.exists(st.session_state.inpaint_path):
                st.image(st.session_state.inpaint_path, caption=f"Inpainted: {new_material} on {target_surface.capitalize()}", use_container_width=True)
                with open(st.session_state.inpaint_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Inpainted Image",
                        data=f.read(),
                        file_name=f"aiglaze_inpainted_{target_surface}.png",
                        mime="image/png"
                    )
            else:
                st.image(current_img, caption="Original Room (Click 'Inpaint Surface' to render preview)", use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------
    # SHOWSTOPPER #4: YOLOV8 FURNITURE DETECTION & PINS
    # -------------------------------------------------------------
    st.markdown('<div class="section-title">📍 Showstopper #4: YOLOv8 Furniture Detection & Spatial Pins</div>', unsafe_allow_html=True)
    st.caption("Identifies room furniture and calculates interactive pin coordinates for catalog sourcing.")

    obj_btn_col, _ = st.columns([2, 1])
    with obj_btn_col:
        run_detect = st.button("📍 Detect Furniture Objects & Pins", use_container_width=True)

    if run_detect or (st.session_state.detected_objects is None and os.path.exists("detected_objects.png")):
        if VISION_AVAILABLE:
            with st.spinner("Running YOLOv8 neural network inference for furniture localization..."):
                items = vision_engine.detect_furniture_objects(current_img)
                st.session_state.detected_objects = items
                st.session_state.detected_objects_path = "detected_objects.png"

    det_c1, det_c2 = st.columns([1, 1])
    with det_c1:
        if st.session_state.detected_objects_path and os.path.exists(st.session_state.detected_objects_path):
            st.image(st.session_state.detected_objects_path, caption="YOLOv8 Detected Furniture & Interactive Spatial Pins", use_container_width=True)
        else:
            st.image(current_img, caption="Original Room", use_container_width=True)

    with det_c2:
        st.markdown("#### 📋 Detected Spatial Inventory")
        items = st.session_state.detected_objects
        if items and len(items) > 0:
            table_rows = []
            for i, obj in enumerate(items, 1):
                pin_x, pin_y = obj.get("pin", (0, 0))
                conf = obj.get("confidence", 0.0)
                box = obj.get("box", (0, 0, 0, 0))
                table_rows.append({
                    "Pin #": f"📍 {i}",
                    "Item": obj.get("label", "Unknown"),
                    "Confidence": f"{int(conf * 100)}%",
                    "Pin (X, Y)": f"({pin_x}, {pin_y})",
                    "Bounding Box": f"W:{box[2]}px, H:{box[3]}px",
                    "Catalog Action": "Ready for Sourcing"
                })
            df_items = pd.DataFrame(table_rows)
            st.dataframe(df_items, use_container_width=True, hide_index=True)
            st.success(f"🎯 Total **{len(items)}** furniture pieces localized with active pin coordinates.")
        else:
            sample_preview = pd.DataFrame([
                {"Pin #": "📍 1", "Item": "Couch", "Confidence": "93%", "Pin (X, Y)": "(480, 520)", "Catalog Action": "Ready for Sourcing"},
                {"Pin #": "📍 2", "Item": "Dining Table", "Confidence": "88%", "Pin (X, Y)": "(310, 410)", "Catalog Action": "Ready for Sourcing"},
                {"Pin #": "📍 3", "Item": "Flooring Surface", "Confidence": "99%", "Pin (X, Y)": "(640, 780)", "Catalog Action": "Inpainting Ready"},
            ])
            st.caption("Sample Inventory Structure:")
            st.dataframe(sample_preview, use_container_width=True, hide_index=True)

    st.markdown("---")

    # -------------------------------------------------------------
    # SAVE PROJECT TO PERSISTENT PORTFOLIO
    # -------------------------------------------------------------
    st.markdown('<div class="section-title">💾 Save Design to Portfolio</div>', unsafe_allow_html=True)
    st.caption("Persist this complete design configuration, telemetry metrics, and cost estimate to your personal portfolio.")

    save_c1, save_c2 = st.columns([2, 1])
    with save_c1:
        proj_name_input = st.text_input("Project Name / Title:", value=f"{selected_style} - {user.get('city', 'Bangalore')} Residence")
    with save_c2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("💾 Save Project to Portfolio", type="primary", use_container_width=True):
            # Calculate an estimated cost based on selected parameters
            rate = 280.0 if "marble" in new_material.lower() else (150.0 if "wood" in new_material.lower() else 65.0)
            est_cost = round((metrics.get("floor_area_sqft", 138.0) * rate * 1.10) + (metrics.get("wall_surface_area_sqft", 401.5) * 35.0) + 45000.0, 2)

            preview_path = st.session_state.redesign_path or st.session_state.inpaint_path or current_img

            project_record = {
                "project_name": proj_name_input,
                "style": selected_style,
                "target_surface": target_surface,
                "surface_material": new_material,
                "budget_inr": float(budget_inr),
                "estimated_cost_inr": est_cost,
                "floor_sqft": float(metrics.get("floor_area_sqft", 138.0)),
                "wall_sqft": float(metrics.get("wall_surface_area_sqft", 401.5)),
                "preview_image_path": preview_path,
                "detected_items_count": len(st.session_state.detected_objects or []),
                "metadata": {
                    "tier": tier_title,
                    "city": user.get("city", "Bangalore"),
                    "saved_by": user["full_name"],
                    "saved_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }

            proj_id = auth_manager.save_user_project(user["id"], project_record)
            st.success(f"🎉 Project '{proj_name_input}' successfully saved to SQLite portfolio (Project ID: #{proj_id})!")
            st.toast("Project saved to your portfolio!", icon="📁")


# =====================================================================
# TAB 2: MY SAVED PORTFOLIO
# =====================================================================
with tab_portfolio:
    st.markdown('<div class="section-title">📁 My Architectural Portfolio & Saved Works</div>', unsafe_allow_html=True)
    st.markdown(f"Projects saved under account: **{user['full_name']}** (`{user['role']}`) in `users.db`")

    saved_projects = auth_manager.get_user_projects(user["id"])

    # Portfolio Analytics Metrics
    m_p1, m_p2, m_p3, m_p4 = st.columns(4)
    total_projects = len(saved_projects)
    total_valuation = sum(p.get("estimated_cost_inr", 0.0) for p in saved_projects)
    avg_cost = total_valuation / total_projects if total_projects > 0 else 0.0

    with m_p1:
        st.metric("Total Saved Designs", f"{total_projects}")
    with m_p2:
        st.metric("Portfolio Value (INR)", f"₹{total_valuation:,.0f}")
    with m_p3:
        st.metric("Avg Project Cost", f"₹{avg_cost:,.0f}")
    with m_p4:
        st.metric("Logged Account", f"{user['username']}")

    st.markdown("---")

    if total_projects == 0:
        st.info("💡 You have not saved any design projects yet. Navigate to **'🛋️ Spatial Design Studio'** to generate a redesign and click **'💾 Save Project to Portfolio'**!")
    else:
        for p in saved_projects:
            with st.container():
                st.markdown(f"""
                <div class="portfolio-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h4 style="margin: 0; color: #1e3a8a;">📁 #{p['id']} - {p['project_name']}</h4>
                        <span style="color: #64748b; font-size: 0.82rem;">📅 {p['created_at']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                p_col_img, p_col_details, p_col_action = st.columns([1.2, 2.2, 0.8])
                with p_col_img:
                    preview_f = p.get("preview_image_path", "redesign_output.png")
                    if os.path.exists(preview_f):
                        st.image(preview_f, use_container_width=True)
                    else:
                        st.image(current_img, use_container_width=True)

                with p_col_details:
                    st.markdown(f"""
                    - **Interior Style:** `{p.get('style', 'Scandinavian Minimalist')}`
                    - **Material Inpainted:** `{p.get('surface_material', 'N/A')}` on `{p.get('target_surface', 'floor')}`
                    - **Budget Allocated:** `₹{p.get('budget_inr', 0.0):,}`
                    - **Estimated BoQ Cost:** **`₹{p.get('estimated_cost_inr', 0.0):,}`**
                    - **Spatial Dimensions:** Floor `{p.get('floor_sqft', 0.0)} sq.ft` | Walls `{p.get('wall_sqft', 0.0)} sq.ft`
                    - **Furniture Tracked:** `{p.get('detected_items_count', 0)} items with YOLOv8 pins`
                    """)

                with p_col_action:
                    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"del_{p['id']}", use_container_width=True):
                        auth_manager.delete_user_project(p['id'], user['id'])
                        st.toast(f"Deleted project #{p['id']}", icon="🗑️")
                        st.rerun()

            st.markdown("---")


# =====================================================================
# TAB 3: CONTRACTOR BOQ DOCUMENT
# =====================================================================
with tab_boq:
    st.markdown('<div class="section-title">📄 Contractor Specification & BoQ Report (Indian Market - INR ₹)</div>', unsafe_allow_html=True)
    st.caption("Official Bill of Quantities (BoQ) generated by cost_engine.py with itemized line items, wastage allowances, and contractor signatures.")

    boq_html_file = "contractor_boq_report.html"

    # Action Toolbar
    b_act1, b_act2, b_act3 = st.columns([1.5, 1.5, 2])
    with b_act1:
        regen_boq = st.button("🔄 Re-Generate BoQ Report", use_container_width=True, type="primary")

    if regen_boq or not os.path.exists(boq_html_file):
        if COST_AVAILABLE:
            with st.spinner("Executing cost_engine.py Knapsack optimization and generating contractor BoQ..."):
                try:
                    f_area = metrics.get("floor_area_sqft", 138.0)
                    w_area = metrics.get("wall_surface_area_sqft", 401.5)
                    f_rate = 280.0 if "marble" in new_material.lower() else (150.0 if "wood" in new_material.lower() else 65.0)
                    p_rate = 38.0
                    
                    boq_calc = cost_engine.generate_full_boq(
                        floor_sqft=f_area,
                        floor_rate=f_rate,
                        wall_sqft=w_area,
                        paint_rate=p_rate,
                        sofa_price=45000.0,
                        budget_cap=float(budget_inr)
                    )
                    cost_engine.export_boq_report(boq_calc, output_file=boq_html_file)
                    st.success("Fresh Contractor BoQ Report synthesized!")
                except Exception as e:
                    st.warning(f"Note on dynamic BoQ synthesis: {e}")

    # Executive Cost Breakdown Metrics
    boq_m1, boq_m2, boq_m3, boq_m4 = st.columns(4)
    sample_grand = round((metrics.get('floor_area_sqft', 138.0) * 175.0 * 1.10) + (metrics.get('wall_surface_area_sqft', 401.5) * 38.0 * 2) + 45000.0, 2)
    delta = budget_inr - sample_grand

    with boq_m1:
        st.metric("Flooring Estimate", f"₹{(metrics.get('floor_area_sqft', 138.0) * 175.0 * 1.10):,.0f}")
    with boq_m2:
        st.metric("Wall Treatment", f"₹{(metrics.get('wall_surface_area_sqft', 401.5) * 38.0 * 2):,.0f}")
    with boq_m3:
        st.metric("Grand Total (BoQ)", f"₹{sample_grand:,.0f}")
    with boq_m4:
        st.metric("Budget Delta", f"₹{abs(delta):,.0f}", delta=f"{'Within Budget' if delta >= 0 else 'Over Budget'}")

    st.markdown("---")

    # Embedded HTML Preview & Download
    if os.path.exists(boq_html_file):
        with open(boq_html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        with b_act2:
            st.download_button(
                "⬇️ Download BoQ Report (.HTML)",
                data=html_content,
                file_name="AI_GLAZE_Contractor_BoQ_Report.html",
                mime="text/html",
                use_container_width=True
            )

        st.markdown("#### 📑 Interactive Contractor Document Preview")
        components.html(html_content, height=750, scrolling=True)
    else:
        st.info("Click **'🔄 Re-Generate BoQ Report'** to synthesize the contractor report.")


# =====================================================================
# 7. PLATFORM FOOTER
# =====================================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 12px;">
    <strong>AI-GLAZE</strong> • Intelligent Home Planning & Interior Platform (Indian Market Edition - INR ₹)<br>
    Member 2: Frontend & Interactive UI Lead • Built with Streamlit, OpenCV, YOLOv8 & SQLite
</div>
""", unsafe_allow_html=True)
