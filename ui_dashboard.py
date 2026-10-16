"""
ui_dashboard.py - AI-GLAZE Interactive Frontend Dashboard
Lead: Teammate A (Member 2: Frontend & Interactive UI Lead)
Project: AI-GLAZE - Intelligent Home Planning & Interior Platform
"Plan it. Design it. Source it. Budget it!"

This module implements the complete Streamlit dashboard providing:
  - Header & Brand styling
  - Sidebar Controls (Style Selector, Budget Slider, Dynamic Tier Badge)
  - Room Photo Upload & Demo Preset
  - Showstopper #3: AI Vision Mode (Thermal Depth Heatmap, Canny Edges, HUD Metrics Card)
  - Showstopper #1: Interior Redesign & Magic Wand Localized Inpainting (Material Swap)
  - Showstopper #4: YOLOv8 Furniture Detection & Interactive Spatial Pins
  - Master Vision Pipeline Runner
"""

import os
import io
import time
from PIL import Image
import pandas as pd
import streamlit as st

# Safe import of vision_engine written by Tech Lead (Member 1)
try:
    import vision_engine
    VISION_ENGINE_AVAILABLE = True
    VISION_ERROR_MSG = ""
except Exception as err:
    VISION_ENGINE_AVAILABLE = False
    VISION_ERROR_MSG = str(err)


# =====================================================================
# 1. STREAMLIT PAGE CONFIGURATION & CUSTOM STYLING
# =====================================================================
st.set_page_config(
    page_title="AI-GLAZE | Intelligent Home Planning & Interior Platform",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Glassmorphism & Clean Typography
st.markdown("""
<style>
    /* Global Card & Container Styling */
    .main-header-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 24px 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
    }
    .main-header-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    .main-header-subtitle {
        font-size: 1.15rem;
        font-weight: 400;
        opacity: 0.95;
        letter-spacing: 0.3px;
    }
    .tag-pill {
        display: inline-block;
        background: rgba(255, 255, 255, 0.22);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 8px;
        margin-top: 10px;
        backdrop-filter: blur(4px);
    }
    
    /* HUD Metrics Card */
    .hud-card {
        background: linear-gradient(145deg, #0f172a, #1e293b);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        color: #f8fafc;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        margin-top: 12px;
        margin-bottom: 16px;
    }
    .hud-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #38bdf8;
        display: flex;
        align-items: center;
        margin-bottom: 14px;
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
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    .hud-stat-val {
        font-size: 1.35rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .hud-stat-lbl {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        margin-top: 4px;
    }

    /* Tier Badges */
    .tier-badge-budget {
        background-color: #10b981;
        color: white;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        text-align: center;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
    }
    .tier-badge-mid {
        background-color: #0284c7;
        color: white;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        text-align: center;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
    }
    .tier-badge-luxury {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        text-align: center;
        box-shadow: 0 4px 10px rgba(245, 158, 11, 0.4);
    }

    /* Section Subheaders */
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 12px;
        color: inherit;
        border-left: 4px solid #3b82f6;
        padding-left: 10px;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# 2. SESSION STATE INITIALIZATION
# =====================================================================
# Preset demo images if present
DEMO_IMAGE_CANDIDATES = ["real_room.jpeg", "test_room.jpg", "test_room.jpeg"]
DEFAULT_IMAGE = None
for candidate in DEMO_IMAGE_CANDIDATES:
    if os.path.exists(candidate):
        DEFAULT_IMAGE = candidate
        break

if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = DEFAULT_IMAGE

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
# 3. SIDEBAR CONTROLS & DYNAMIC BUDGET TIER BADGE
# =====================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/interior.png", width=64)
    st.markdown("### 🎛️ Design Configuration")
    st.markdown("Customize your spatial parameters and budget allocation below.")

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
    st.caption(f"ℹ️ *{style_descriptions[selected_style]}*")

    st.markdown("---")

    # 2. Budget Slider ($1,000 to $15,000, step $500)
    st.markdown("#### 💰 Budget Allocation")
    budget_value = st.slider(
        "Target Renovation Budget ($):",
        min_value=1000,
        max_value=15000,
        value=5500,
        step=500,
        format="$%d",
        help="Select your target room renovation expenditure."
    )

    # 3. Dynamic Tier Badge
    # (< $3000 -> Budget, < $8000 -> Mid-Range, otherwise -> Luxury)
    if budget_value < 3000:
        tier_title = "Budget Friendly"
        tier_class = "tier-badge-budget"
        tier_emoji = "🏷️"
        tier_desc = "Optimal for DIY essentials, surface touch-ups & cost-effective flooring."
    elif budget_value < 8000:
        tier_title = "Mid-Range Balanced"
        tier_class = "tier-badge-mid"
        tier_emoji = "⚖️"
        tier_desc = "Balanced designer materials, engineered hardwood & premium upholstery."
    else:
        tier_title = "Luxury Premium"
        tier_class = "tier-badge-luxury"
        tier_emoji = "✨"
        tier_desc = "Italian marble, bespoke furniture, smart lighting & custom craftsmanship."

    st.markdown(f"""
    <div style="margin-top: 10px; margin-bottom: 8px;">
        <span class="{tier_class}">{tier_emoji} {tier_title}</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"*{tier_desc}*")

    st.markdown("---")
    
    # Team Info & Module Status
    st.markdown("#### 👥 Team AI-GLAZE")
    st.markdown("**Member 2:** Frontend & Interactive UI Lead")
    st.markdown("**Member 1:** CV & Generative AI Lead (`vision_engine.py`)")
    
    if VISION_ENGINE_AVAILABLE:
        st.success("🟢 `vision_engine.py` Connected")
    else:
        st.error("🔴 `vision_engine.py` Error")
        st.caption(f"Error details: {VISION_ERROR_MSG}")


# =====================================================================
# 4. HEADER & BRAND SECTION
# =====================================================================
st.markdown("""
<div class="main-header-card">
    <div class="main-header-title">🏡 AI-GLAZE: Intelligent Home Planning & Interior Platform</div>
    <div class="main-header-subtitle">Plan it. Design it. Source it. Budget it!</div>
    <div>
        <span class="tag-pill">🚀 Computer Vision V2</span>
        <span class="tag-pill">📐 Spatial Estimation</span>
        <span class="tag-pill">🎨 Surface Inpainting</span>
        <span class="tag-pill">📍 YOLOv8 Object Pins</span>
        <span class="tag-pill">💎 Multi-Tier Budgeting</span>
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================================
# 5. ROOM PHOTO UPLOAD & PRESET MANAGEMENT
# =====================================================================
upload_col, preset_col = st.columns([3, 1])

with upload_col:
    uploaded_file = st.file_uploader(
        "📸 Step 1: Upload Your Room Photo (JPG, PNG, JPEG):",
        type=["jpg", "jpeg", "png"],
        help="Upload a photo of your living room, lounge, or bedroom to begin spatial analysis"
    )

with preset_col:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if DEFAULT_IMAGE and st.button("🖼️ Use Demo Photo", use_container_width=True):
        st.session_state.current_image_path = DEFAULT_IMAGE
        st.toast(f"Loaded demo image: {DEFAULT_IMAGE}", icon="✅")

# Save uploaded image locally so vision_engine cv2 readers can process it
if uploaded_file is not None:
    temp_save_path = "uploaded_room_temp.jpg"
    with open(temp_save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.session_state.current_image_path = temp_save_path
    st.toast("Room photo uploaded and ready for analysis!", icon="📸")

current_img = st.session_state.current_image_path

if not current_img or not os.path.exists(current_img):
    st.info("👋 Welcome! Please upload a room photo above or click **'Use Demo Photo'** to inspect AI-GLAZE in action.")
    st.stop()


# =====================================================================
# 6. SHOWSTOPPER #3: "AI VISION MODE" TOGGLE & HUD CARDS
# =====================================================================
st.markdown('<div class="section-title">🔬 Showstopper #3: Spatial Depth & Structural Perception</div>', unsafe_allow_html=True)

vision_mode_col1, vision_mode_col2 = st.columns([2, 1])
with vision_mode_col1:
    ai_vision_mode = st.toggle(
        "🔬 Enable AI Vision Mode",
        value=False,
        help="Activates thermal depth estimation, Canny edge detection, and real-time room dimension HUD"
    )

# Compute metrics if not already cached
if st.session_state.spatial_metrics is None and VISION_ENGINE_AVAILABLE:
    try:
        st.session_state.spatial_metrics = vision_engine.estimate_spatial_metrics(current_img)
    except Exception as e:
        st.warning(f"Spatial metrics calculation deferred: {e}")

# When AI Vision Mode is OFF: show clean uploaded room photo
if not ai_vision_mode:
    col_img, col_info = st.columns([2, 1])
    with col_img:
        st.image(current_img, caption="Clean Input Room Photo", use_container_width=True)
    with col_info:
        st.markdown("### 📷 Standard Camera View")
        st.markdown("""
        You are viewing the unannotated room photograph.
        
        👉 **Turn ON `[ 🔬 Enable AI Vision Mode ]`** above to unlock:
        - **Thermal Depth Heatmap** (Depth Anything V2 spatial perception)
        - **Structural Canny Edge Geometry** (Locks architectural walls & windows)
        - **Informational HUD Card** (Real-time calculated floor & wall surface sq.ft)
        """)
        st.info("Tip: Interior designers use AI Vision Mode to ensure that structural walls are never altered during generative redesign.")

# When AI Vision Mode is ON: show Depth Heatmap, Structural Canny Edges & HUD Card
else:
    # Ensure Depth & Edges are generated
    if VISION_ENGINE_AVAILABLE:
        with st.spinner("Processing computer vision depth and edge tensors..."):
            if not st.session_state.depth_heatmap_path or not os.path.exists(st.session_state.depth_heatmap_path):
                st.session_state.depth_heatmap_path = vision_engine.generate_depth_heatmap(current_img)
            if not st.session_state.structural_edges_path or not os.path.exists(st.session_state.structural_edges_path):
                st.session_state.structural_edges_path = vision_engine.detect_structural_edges(current_img)

    # 3-column visual spatial breakdown
    v_col1, v_col2, v_col3 = st.columns(3)
    
    with v_col1:
        st.markdown("**1. Original Room Input**")
        st.image(current_img, use_container_width=True)
        st.caption("Pristine RGB perspective")

    with v_col2:
        st.markdown("**2. Thermal Depth Heatmap**")
        if st.session_state.depth_heatmap_path and os.path.exists(st.session_state.depth_heatmap_path):
            st.image(st.session_state.depth_heatmap_path, use_container_width=True)
            st.caption("🔵 Blue = Foreground/Floor | 🔴 Red = Distant Walls")
        else:
            st.warning("Depth heatmap not generated yet.")

    with v_col3:
        st.markdown("**3. Structural Canny Edges**")
        if st.session_state.structural_edges_path and os.path.exists(st.session_state.structural_edges_path):
            st.image(st.session_state.structural_edges_path, use_container_width=True)
            st.caption("Architectural boundary & beam invariant lineart")
        else:
            st.warning("Structural edges not generated yet.")

    # Informational HUD Card displaying estimated Room Dimensions
    metrics = st.session_state.spatial_metrics or {
        "floor_area_sqft": 138.0,
        "wall_surface_area_sqft": 401.5,
        "estimated_length_ft": 12.0,
        "estimated_width_ft": 11.5,
        "detected_structural_openings": "2 Windows, 1 Doorway"
    }

    st.markdown(f"""
    <div class="hud-card">
        <div class="hud-header">
            <span>📡 Spatial Perception HUD // Automated Architectural Telemetry</span>
        </div>
        <div class="hud-stat-grid">
            <div class="hud-stat-box">
                <div class="hud-stat-val">{metrics.get('floor_area_sqft', 'N/A')}</div>
                <div class="hud-stat-lbl">Floor Area (Sq.Ft)</div>
            </div>
            <div class="hud-stat-box">
                <div class="hud-stat-val">{metrics.get('wall_surface_area_sqft', 'N/A')}</div>
                <div class="hud-stat-lbl">Wall Surface (Sq.Ft)</div>
            </div>
            <div class="hud-stat-box">
                <div class="hud-stat-val">{metrics.get('estimated_length_ft', '12.0')} x {metrics.get('estimated_width_ft', '11.5')}</div>
                <div class="hud-stat-lbl">Dimensions (L x W ft)</div>
            </div>
            <div class="hud-stat-box">
                <div class="hud-stat-val" style="font-size: 1.05rem; padding-top: 5px;">{metrics.get('detected_structural_openings', '2 Windows, 1 Door')}</div>
                <div class="hud-stat-lbl">Structural Openings</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# =====================================================================
# 7. REDESIGN & SHOWSTOPPER #1: MAGIC WAND INPAINTING
# =====================================================================
st.markdown('<div class="section-title">🎨 Generative Redesign & Showstopper #1: "The Magic Wand"</div>', unsafe_allow_html=True)

tab_redesign, tab_inpaint = st.tabs([
    "🪄 AI Interior Redesign (Full Room)", 
    "✨ Showstopper #1: Selective Surface Inpainting (Material Swap)"
])

# ----------------- TAB 1: INTERIOR REDESIGN -----------------
with tab_redesign:
    r_col1, r_col2 = st.columns([1, 1])
    
    with r_col1:
        st.markdown(f"#### Transform Room into **{selected_style}**")
        st.markdown(f"""
        - **Target Aesthetic:** {selected_style}
        - **Budget Tier:** {tier_title} (${budget_value:,})
        - **Geometry Protection:** Structural Canny edge locking active
        """)
        
        redesign_clicked = st.button("🪄 Generate Interior Redesign", use_container_width=True, type="primary")
        if redesign_clicked:
            if VISION_ENGINE_AVAILABLE:
                with st.spinner(f"Synthesizing {selected_style} interior design with architectural conditioning..."):
                    out_path = vision_engine.generate_interior_redesign(current_img, style=selected_style)
                    st.session_state.redesign_path = out_path
                    st.success(f"Interior redesigned successfully in '{selected_style}' style!")
            else:
                st.error("`vision_engine.py` is not accessible.")

    with r_col2:
        if st.session_state.redesign_path and os.path.exists(st.session_state.redesign_path):
            st.image(st.session_state.redesign_path, caption=f"AI-Generated {selected_style} Room", use_container_width=True)
            with open(st.session_state.redesign_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Redesigned Render",
                    data=f.read(),
                    file_name=f"ai_glaze_redesign_{selected_style.lower().replace(' ', '_')}.png",
                    mime="image/png"
                )
        else:
            st.image(current_img, caption="Original Room (Awaiting Redesign Generation)", use_container_width=True)


# ----------------- TAB 2: SHOWSTOPPER #1 INPAINTING -----------------
with tab_inpaint:
    st.markdown("#### 🪄 'The Magic Wand' - Selective Surface Inpainting")
    st.caption("Swap materials on specific architectural surfaces without altering the surrounding room.")
    
    inp_col_ctrl, inp_col_view = st.columns([1, 1])
    
    with inp_col_ctrl:
        target_surface = st.selectbox(
            "1. Select Target Surface:",
            options=["floor", "wall"],
            format_func=lambda s: "🏢 Flooring Surface (Sub-floor / Tiles)" if s == "floor" else "🧱 Wall Facade (Vertical Surfaces)",
            help="Defines the spatial mask region in vision_engine.py"
        )
        
        material_options = [
            "Italian Beige Marble",
            "Oak Wood",
            "Vitrified Tile"
        ]
        new_material = st.selectbox(
            "2. Select Replacement Material:",
            options=material_options,
            index=0,
            help="Applies texture synthesis specifically onto the masked region"
        )
        
        st.markdown(f"""
        **Material Specifications:**
        - **Target:** `{target_surface.upper()}`
        - **Texture Applied:** `{new_material}`
        - **Preservation:** Surrounding furniture, lighting & boundaries remain invariant.
        """)
        
        inpaint_btn = st.button("🎨 Inpaint Surface", use_container_width=True, type="secondary")
        if inpaint_btn:
            if VISION_ENGINE_AVAILABLE:
                with st.spinner(f"Inpainting {target_surface} with {new_material}..."):
                    out_inp = vision_engine.inpaint_surface_material(
                        current_img,
                        target_surface=target_surface,
                        new_material=new_material
                    )
                    st.session_state.inpaint_path = out_inp
                    st.success(f"Successfully inpainted {target_surface} with {new_material}!")
            else:
                st.error("`vision_engine.py` is not accessible.")

    with inp_col_view:
        if st.session_state.inpaint_path and os.path.exists(st.session_state.inpaint_path):
            st.image(st.session_state.inpaint_path, caption=f"Inpainted: {new_material} on {target_surface.capitalize()}", use_container_width=True)
            with open(st.session_state.inpaint_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Inpainted Surface Image",
                    data=f.read(),
                    file_name=f"ai_glaze_inpainted_{target_surface}.png",
                    mime="image/png"
                )
        else:
            st.image(current_img, caption="Original Room (Click 'Inpaint Surface' to render preview)", use_container_width=True)

st.markdown("---")


# =====================================================================
# 8. SHOWSTOPPER #4: DETECTED OBJECTS & INTERACTIVE PINS
# =====================================================================
st.markdown('<div class="section-title">📍 Showstopper #4: YOLOv8 Furniture Detection & Spatial Pins</div>', unsafe_allow_html=True)
st.caption("Real AI object detection tags furniture items and marks interactive pin coordinates for catalog sourcing.")

obj_col_action, obj_col_summary = st.columns([2, 1])

with obj_col_action:
    detect_clicked = st.button("📍 Detect Furniture Objects & Pins", use_container_width=True)

if detect_clicked or (st.session_state.detected_objects is None and os.path.exists("detected_objects.png")):
    if VISION_ENGINE_AVAILABLE:
        with st.spinner("Running YOLOv8 neural network inference for furniture localization..."):
            items = vision_engine.detect_furniture_objects(current_img)
            st.session_state.detected_objects = items
            st.session_state.detected_objects_path = "detected_objects.png"

# Display Detected Objects View
det_img_col, det_table_col = st.columns([1, 1])

with det_img_col:
    if st.session_state.detected_objects_path and os.path.exists(st.session_state.detected_objects_path):
        st.image(st.session_state.detected_objects_path, caption="YOLOv8 Detected Furniture & Interactive Spatial Pins", use_container_width=True)
    else:
        st.image(current_img, caption="Original Room", use_container_width=True)

with det_table_col:
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
        
        # Display as styled dataframe
        df_items = pd.DataFrame(table_rows)
        st.dataframe(df_items, use_container_width=True, hide_index=True)
        
        st.success(f"🎯 Total **{len(items)}** furniture pieces localized with active pin coordinates.")
    else:
        st.info("Click **'📍 Detect Furniture Objects & Pins'** to run the YOLOv8 vision detector.")
        # Provide sample preview fallback if not yet run
        sample_preview = pd.DataFrame([
            {"Pin #": "📍 1", "Item": "Couch", "Confidence": "91%", "Pin (X, Y)": "(480, 520)", "Catalog Action": "Ready for Sourcing"},
            {"Pin #": "📍 2", "Item": "Dining Table", "Confidence": "85%", "Pin (X, Y)": "(310, 410)", "Catalog Action": "Ready for Sourcing"},
            {"Pin #": "📍 3", "Item": "Flooring Surface", "Confidence": "99%", "Pin (X, Y)": "(640, 780)", "Catalog Action": "Inpainting Ready"},
        ])
        st.caption("Sample Inventory Structure:")
        st.dataframe(sample_preview, use_container_width=True, hide_index=True)

st.markdown("---")


# =====================================================================
# 9. MASTER VISION PIPELINE RUNNER (THE ONE-CALL DEMO BUTTON)
# =====================================================================
st.markdown('<div class="section-title">🚀 Master Pipeline: Full 1-Click Vision Execution</div>', unsafe_allow_html=True)
st.caption("Executes depth heatmapping, edge extraction, spatial dimensioning, style redesign, inpainting, and object detection in a unified sequence.")

if st.button("⚡ Run Full AI-GLAZE Vision Pipeline", type="primary", use_container_width=True):
    if VISION_ENGINE_AVAILABLE:
        with st.status("Executing complete AI-GLAZE Vision Suite...", expanded=True) as status:
            st.write("1️⃣ Generating thermal depth heatmap...")
            st.session_state.depth_heatmap_path = vision_engine.generate_depth_heatmap(current_img)
            
            st.write("2️⃣ Tracing architectural Canny structural edges...")
            st.session_state.structural_edges_path = vision_engine.detect_structural_edges(current_img)
            
            st.write("3️⃣ Calculating spatial dimensions & surface area...")
            st.session_state.spatial_metrics = vision_engine.estimate_spatial_metrics(current_img)
            
            st.write(f"4️⃣ Generating interior redesign ({selected_style})...")
            st.session_state.redesign_path = vision_engine.generate_interior_redesign(current_img, style=selected_style)
            
            st.write(f"5️⃣ Inpainting surface ({target_surface} -> {new_material})...")
            st.session_state.inpaint_path = vision_engine.inpaint_surface_material(
                current_img, target_surface=target_surface, new_material=new_material
            )
            
            st.write("6️⃣ Running YOLOv8 furniture detection & pin coordinate assignment...")
            st.session_state.detected_objects = vision_engine.detect_furniture_objects(current_img)
            st.session_state.detected_objects_path = "detected_objects.png"
            
            status.update(label="🎉 All 6 Vision Pipelines Completed Successfully!", state="complete", expanded=False)
            st.rerun()
    else:
        st.error("`vision_engine.py` is not accessible.")


# =====================================================================
# 10. FOOTER
# =====================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 12px;">
    <strong>AI-GLAZE</strong> • College Capstone Project • Frontend & Interactive UI Dashboard • Built with Streamlit & OpenCV
</div>
""", unsafe_allow_html=True)
