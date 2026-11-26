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

# Safe import of Pillar 1 (layout_generator - Space Planning & Vastu CAD Engine)
try:
    import layout_generator
    import importlib as _layout_importlib
    _layout_importlib.reload(layout_generator)
    LAYOUT_AVAILABLE = True
    LAYOUT_ERROR_MSG = ""
except Exception as err:
    LAYOUT_AVAILABLE = False
    LAYOUT_ERROR_MSG = str(err)

# =====================================================================

# 1. STREAMLIT PAGE CONFIGURATION & CUSTOM STYLING

# =====================================================================

st.set_page_config(

    page_title="AI-GLAZE | Intelligent Home Planning & Interior Architecture",

    page_icon="🏡",

    layout="wide",

    initial_sidebar_state="expanded"

)

# Custom CSS for Editorial Luxury Architectural Studio (Havenly / Aura Studios / DreamHome Aesthetic)
st.markdown("""

<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Warm Architectural Canvas */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #FAF8F5 !important;
        color: #1C1917 !important;
    }

    /* Editorial Serif Headings */
    h1, h2, h3, .hero-headline, .brand-title, .main-header-title, .collection-title {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #1C1917 !important;
        letter-spacing: -0.02em;
    }

    /* Subheadings and Eyebrows */
    .eyebrow-tag {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #B45309;
        margin-bottom: 8px;
        display: inline-block;
    }

    /* Studio Header Navigation Bar */
    .studio-header {
        background: #FFFFFF;
        border: 1px solid rgba(28, 25, 23, 0.08);
        border-radius: 20px;
        padding: 20px 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px -10px rgba(28, 25, 23, 0.05);
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
        width: 52px;
        height: 52px;
        border-radius: 16px;
        background: linear-gradient(135deg, #1C1917 0%, #292524 100%);
        color: #FBF9F5;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        box-shadow: 0 6px 18px rgba(28, 25, 23, 0.15);
        border: 1px solid rgba(28, 25, 23, 0.1);
    }

    .brand-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1C1917 !important;
        margin: 0;
        line-height: 1.1;
    }

    .brand-badge {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.70rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        padding: 4px 12px;
        border-radius: 20px;
        background: #F5EFEB;
        color: #854D0E;
        border: 1px solid rgba(133, 77, 14, 0.2);
        margin-left: 10px;
        vertical-align: middle;
        white-space: nowrap !important;
        display: inline-block;
    }

    .brand-tagline {
        font-size: 0.92rem;
        color: #78716C;
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
        background: #F5F2EB;
        border: 1px solid rgba(28, 25, 23, 0.08);
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #44403C;
        transition: all 0.2s ease;
    }
    .meta-pill:hover {
        background: #EFECE6;
        border-color: rgba(28, 25, 23, 0.15);
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #15803D;
        box-shadow: 0 0 8px rgba(21, 128, 61, 0.5);
        animation: pulseAnimation 2s infinite;
    }

    @keyframes pulseAnimation {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }

    /* Editorial Hero Section (Havenly / Aura Studios) */
    .editorial-hero {
        background: #FFFFFF;
        border: 1px solid rgba(28, 25, 23, 0.08);
        border-radius: 28px;
        padding: 40px 48px;
        margin-bottom: 28px;
        box-shadow: 0 16px 40px -15px rgba(28, 25, 23, 0.06);
    }

    .hero-headline {
        font-size: 2.85rem;
        font-weight: 700;
        line-height: 1.18;
        color: #1C1917;
        margin-top: 6px;
        margin-bottom: 14px;
    }
    .hero-headline i {
        font-family: 'Playfair Display', Georgia, serif;
        font-style: italic;
        color: #B45309;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #57534E;
        max-width: 650px;
        margin-bottom: 24px;
    }

    /* Floating Architectural Filter Dock */
    .hero-filter-dock {
        background: #FAF8F5;
        border: 1px solid rgba(28, 25, 23, 0.1);
        border-radius: 20px;
        padding: 14px 22px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 16px;
        box-shadow: 0 6px 20px -8px rgba(28, 25, 23, 0.06);
        margin-top: 20px;
    }

    .filter-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .filter-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #78716C;
        font-weight: 600;
    }
    .filter-value {
        font-size: 0.90rem;
        font-weight: 700;
        color: #1C1917;
    }

    /* Arched Image Container (from Aura Studios & Havenly) */
    .arched-image-card {
        border-radius: 120px 120px 24px 24px;
        overflow: hidden;
        border: 1px solid rgba(28, 25, 23, 0.08);
        box-shadow: 0 20px 40px -15px rgba(28, 25, 23, 0.12);
        height: 100%;
        min-height: 340px;
        background-size: cover;
        background-position: center;
    }

    /* Trust & Provenance Strip (from DreamHome) */
    .trust-strip {
        background: #F5F2EB;
        border: 1px solid rgba(28, 25, 23, 0.06);
        border-radius: 16px;
        padding: 14px 24px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-around;
        gap: 12px;
        margin-top: 20px;
    }
    .trust-strip-item {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #44403C;
    }

    /* Aura Studios Curated Collection Cards */
    .collection-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 20px 0 28px 0;
    }
    .collection-card {
        border-radius: 20px;
        padding: 24px 20px;
        color: #FFFFFF;
        box-shadow: 0 10px 24px -8px rgba(0, 0, 0, 0.12);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .collection-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 32px -10px rgba(0, 0, 0, 0.2);
    }
    .collection-card-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .collection-card-rate {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        opacity: 0.9;
        font-weight: 600;
    }
    .collection-card-desc {
        font-size: 0.78rem;
        opacity: 0.8;
        margin-top: 8px;
        line-height: 1.4;
    }

    /* Auth Portal Main Header Card */
    .main-header-card {
        background: #FFFFFF;
        border: 1px solid rgba(28, 25, 23, 0.08);
        border-radius: 24px;
        box-shadow: 0 20px 48px -15px rgba(28, 25, 23, 0.08);
        margin-bottom: 28px;
    }
    .main-header-title {
        font-size: 3rem;
        font-weight: 700;
        color: #1C1917 !important;
        margin-bottom: 6px;
    }
    .main-header-subtitle {
        font-size: 1.05rem;
        color: #78716C;
        max-width: 680px;
        margin: 0 auto 16px auto;
        line-height: 1.5;
    }

    .tag-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #F5F2EB;
        border: 1px solid rgba(28, 25, 23, 0.08);
        color: #44403C;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 4px;
        transition: all 0.2s ease;
    }
    .tag-pill:hover {
        background: #EFECE6;
        color: #1C1917;
        transform: translateY(-1px);
    }

    /* Floating Logged-in User Profile Bar */
    .user-profile-bar {
        background: #FFFFFF;
        border: 1px solid rgba(28, 25, 23, 0.08);
        border-radius: 16px;
        padding: 12px 24px;
        margin-bottom: 20px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        box-shadow: 0 6px 18px -6px rgba(28, 25, 23, 0.05);
    }

    /* Studio Glass Cards (Warm Alabaster) */
    .glass-card {
        background: #FFFFFF;
        border: 1px solid rgba(28, 25, 23, 0.08);
        border-radius: 20px;
        padding: 26px;
        box-shadow: 0 10px 30px -10px rgba(28, 25, 23, 0.05);
        margin-bottom: 20px;
        transition: all 0.25s ease;
    }
    .glass-card:hover {
        border-color: rgba(180, 83, 9, 0.3);
        box-shadow: 0 14px 36px -10px rgba(28, 25, 23, 0.08);
    }

    /* Section Subheaders */
    .section-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.45rem;
        font-weight: 700;
        margin-top: 14px;
        margin-bottom: 12px;
        color: #1C1917;
        display: flex;
        align-items: center;
        gap: 12px;
        border-left: 4px solid #B45309;
        padding-left: 14px;
        letter-spacing: -0.01em;
    }

    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 10px;
        background: #1C1917;
        color: #FFFFFF;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.88rem;
        font-weight: 800;
        box-shadow: 0 4px 10px rgba(28, 25, 23, 0.2);
    }

    /* Primary CTA Buttons (Warm Charcoal & Terracotta Hover) */
    div.stButton > button[kind="primary"], div.stButton > button[data-testid="baseButton-primary"] {
        background: #1C1917 !important;
        color: #FAF8F5 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
        border: 1px solid #1C1917 !important;
        border-radius: 9999px !important;
        padding: 12px 28px !important;
        box-shadow: 0 6px 18px rgba(28, 25, 23, 0.15) !important;
        transition: all 0.25s ease !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="baseButton-primary"]:hover {
        background: #B45309 !important;
        border-color: #B45309 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 24px rgba(180, 83, 9, 0.25) !important;
    }

    /* Secondary Buttons */
    div.stButton > button[kind="secondary"], div.stButton > button[data-testid="baseButton-secondary"] {
        background: #FFFFFF !important;
        color: #1C1917 !important;
        border: 1px solid rgba(28, 25, 23, 0.15) !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="secondary"]:hover, div.stButton > button[data-testid="baseButton-secondary"]:hover {
        background: #F5F2EB !important;
        border-color: rgba(28, 25, 23, 0.3) !important;
        color: #1C1917 !important;
        transform: translateY(-1px) !important;
    }

    /* Streamlit Forms */
    [data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid rgba(28, 25, 23, 0.08) !important;
        border-radius: 20px !important;
        padding: 26px !important;
        box-shadow: 0 12px 32px rgba(28, 25, 23, 0.05) !important;
    }

    /* Input Fields & Select Boxes */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #FAF8F5 !important;
        border: 1px solid rgba(28, 25, 23, 0.14) !important;
        border-radius: 12px !important;
        color: #1C1917 !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-baseweb="input"]:focus-within > div, div[data-baseweb="select"]:focus-within > div {
        border-color: #B45309 !important;
        box-shadow: 0 0 0 3px rgba(180, 83, 9, 0.15) !important;
    }

    /* File Uploader Luxury Dropzone */
    section[data-testid="stFileUploadDropzone"] {
        background: #FAF8F5 !important;
        border: 2px dashed rgba(28, 25, 23, 0.2) !important;
        border-radius: 16px !important;
        padding: 28px !important;
        transition: all 0.25s ease !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #B45309 !important;
        background: #F5EFEB !important;
    }

    /* Tabs Overrides (Warm Minimalist Segmented Pill) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #F5F2EB;
        padding: 6px 8px;
        border-radius: 9999px;
        border: 1px solid rgba(28, 25, 23, 0.08);
        display: inline-flex;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9999px;
        padding: 9px 24px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 600;
        font-size: 0.90rem;
        color: #78716C;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: #1C1917 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(28, 25, 23, 0.15) !important;
    }

    /* Material Swatch Preview Card */
    .material-swatch-card {
        background: #FFFFFF;
        border: 1px solid rgba(28, 25, 23, 0.1);
        border-radius: 16px;
        padding: 18px 22px;
        margin-top: 10px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 4px 16px rgba(28, 25, 23, 0.04);
        transition: all 0.25s ease;
    }
    .material-swatch-card:hover {
        border-color: #B45309;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(28, 25, 23, 0.08);
    }
    .material-icon-bubble {
        width: 50px;
        height: 50px;
        border-radius: 14px;
        background: #FAF8F5;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.7rem;
        flex-shrink: 0;
        border: 1px solid rgba(28, 25, 23, 0.08);
    }
    .material-details-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-weight: 700;
        font-size: 1.05rem;
        color: #1C1917;
    }
    .material-details-price {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.92rem;
        color: #9A3412;
    }
    .material-details-desc {
        font-size: 0.82rem;
        color: #78716C;
        margin-top: 3px;
        line-height: 1.4;
    }

    /* HUD Metrics Card */
    .hud-card {
        background: #FFFFFF;
        border: 1px solid rgba(28, 25, 23, 0.1);
        border-radius: 18px;
        padding: 24px;
        color: #1C1917;
        box-shadow: 0 10px 28px rgba(28, 25, 23, 0.05);
        margin-top: 14px;
        margin-bottom: 18px;
    }
    .hud-header {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.12rem;
        font-weight: 700;
        color: #1C1917;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
    }
    .hud-stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
    }
    .hud-stat-box {
        background: #FAF8F5;
        border: 1px solid rgba(28, 25, 23, 0.08);
        border-radius: 14px;
        padding: 16px 12px;
        text-align: center;
        transition: all 0.2s ease;
    }
    .hud-stat-box:hover {
        background: #F5F2EB;
        border-color: #B45309;
    }
    .hud-stat-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.45rem;
        font-weight: 700;
        color: #1C1917;
    }
    .hud-stat-lbl {
        font-size: 0.72rem;
        color: #78716C;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
        font-weight: 600;
    }

    /* Tier Badges */
    .tier-badge-budget {
        background: #ECFDF5;
        border: 1px solid #10B981;
        color: #065F46;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.90rem;
        display: inline-block;
    }
    .tier-badge-mid {
        background: #EFF6FF;
        border: 1px solid #3B82F6;
        color: #1E40AF;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.90rem;
        display: inline-block;
    }
    .tier-badge-luxury {
        background: #FEF3C7;
        border: 1px solid #F59E0B;
        color: #92400E;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.90rem;
        display: inline-block;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F5F2EB !important;
        border-right: 1px solid rgba(28, 25, 23, 0.08) !important;
    }

    /* Universal High-Contrast Legibility Overrides */
    p, span, label, div, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] span {
        color: #1C1917 !important;
    }

    /* Form labels & widget titles */
    [data-testid="stWidgetLabel"] label, 
    [data-testid="stWidgetLabel"] p, 
    [data-testid="stWidgetLabel"] span {
        color: #1C1917 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    /* Captions & descriptions */
    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, .stCaption p {
        color: #57534E !important;
        font-weight: 500 !important;
        font-size: 0.84rem !important;
    }

    /* Sidebar High Contrast */
    section[data-testid="stSidebar"] {
        background-color: #F5F2EB !important;
        border-right: 1px solid rgba(28, 25, 23, 0.12) !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] div {
        color: #1C1917 !important;
    }
    section[data-testid="stSidebar"] .stCaption, 
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #57534E !important;
        font-weight: 500 !important;
    }

    /* Tabs Styling: High Contrast Pill Bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: #EFECE6 !important;
        padding: 6px 10px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(28, 25, 23, 0.12) !important;
        display: inline-flex !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9999px !important;
        padding: 10px 22px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: #57534E !important;
        background-color: transparent !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"] p, 
    .stTabs [data-baseweb="tab"] span, 
    .stTabs [data-baseweb="tab"] div {
        color: #57534E !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1C1917 !important;
        border-radius: 9999px !important;
        box-shadow: 0 4px 14px rgba(28, 25, 23, 0.2) !important;
    }
    .stTabs [aria-selected="true"] p, 
    .stTabs [aria-selected="true"] span, 
    .stTabs [aria-selected="true"] div {
        color: #FAF8F5 !important;
        font-weight: 700 !important;
    }

    /* Slider Thumb & Track */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #B45309 !important;
        box-shadow: 0 0 10px rgba(180, 83, 9, 0.5) !important;
        border: 2px solid #FFFFFF !important;
    }
    div[data-baseweb="slider"] [data-testid="stSliderTickBar"] {
        background-color: #D6D3D1 !important;
    }
    div[data-baseweb="slider"] div[data-testid="stThumbValue"] {
        color: #B45309 !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Selectbox & Dropdown menus */
    div[data-baseweb="select"] span {
        color: #1C1917 !important;
        font-weight: 600 !important;
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

            st.markdown("<p style='text-align: center; color: #78716C; font-size: 0.88rem; font-weight: 600;'>⚡ One-Click Reviewer Access for Faculty & Reviewers:</p>", unsafe_allow_html=True)

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
<div style="width: 40px; height: 40px; border-radius: 12px; background: #1C1917; color: #FAF8F5; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 0 4px 12px rgba(28, 25, 23, 0.15);">👤</div>
<div>
<div style="font-weight: 700; font-size: 1.02rem; color: #1C1917;">
{user['full_name']} &nbsp;
<span style="font-size: 0.74rem; font-weight: 600; padding: 3px 10px; border-radius: 20px; background: #F5EFEB; color: #854D0E; border: 1px solid rgba(133, 77, 14, 0.2);">
🏷️ {user['role']}
</span>
</div>
<div style="font-size: 0.8rem; color: #57534E; margin-top: 2px;">
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

# Pillar 1 (Plot-to-Floorplan Generator) session states
if "floorplan_data" not in st.session_state:
    st.session_state.floorplan_data = None

if "floorplan_image_path" not in st.session_state:
    fp_cand = resolve_path("floorplan_output.png")
    st.session_state.floorplan_image_path = fp_cand if os.path.exists(fp_cand) else None

if "fp_plot_w" not in st.session_state:
    st.session_state.fp_plot_w = 30.0

if "fp_plot_l" not in st.session_state:
    st.session_state.fp_plot_l = 40.0

if "fp_facing" not in st.session_state:
    st.session_state.fp_facing = "North"

if "fp_typology" not in st.session_state:
    st.session_state.fp_typology = "2BHK" 

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
<div class="brand-title">AI-GLAZE <span class="brand-badge">ATELIER ARCHITECTURE</span></div>
<div class="brand-tagline">Autonomous Spatial Perception, Generative Interior Architecture & Real Material Intelligence</div>
</div>
</div>
<div class="studio-meta-badges">
<div class="meta-pill"><span class="pulse-dot"></span> Studio Online</div>
<div class="meta-pill">🇮🇳 Indian Market (INR ₹)</div>
<div class="meta-pill">🏛️ VTU / MVJCE Capstone</div>
</div>
</div>

<div class="editorial-hero">
<div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 32px;">
<div style="flex: 1 1 480px; max-width: 620px;">
<div class="eyebrow-tag">✨ AUTONOMOUS ARCHITECTURAL SYNTHESIS</div>
<h1 class="hero-headline">Artful Living, <i>Reimagined</i> by Neural Intelligence.</h1>
<p class="hero-subtitle">
Transforming monocular room photos and vacant plots into geometry-locked architectural blueprints, photorealistic generative redesigns, and certified Indian contractor BoQ schedules.
</p>
<div class="hero-filter-dock">
<div class="filter-item">
<span class="filter-label">🎨 Aesthetic Theme</span>
<span class="filter-value">Scandinavian Minimalist</span>
</div>
<div style="height: 28px; width: 1px; background: rgba(28, 25, 23, 0.12);"></div>
<div class="filter-item">
<span class="filter-label">💰 Renovation Budget</span>
<span class="filter-value">₹1,50,000 (Tier-1 Market)</span>
</div>
<div style="height: 28px; width: 1px; background: rgba(28, 25, 23, 0.12);"></div>
<div class="filter-item">
<span class="filter-label">🏛️ Surface Target</span>
<span class="filter-value">Italian Marble / Kajaria</span>
</div>
</div>
</div>
<div style="flex: 1 1 320px; max-width: 420px;">
<div class="arched-image-card" style="background-image: url('https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80'); min-height: 320px; display: flex; align-items: flex-end; padding: 20px;">
<div style="background: rgba(255, 255, 255, 0.94); backdrop-filter: blur(8px); border-radius: 14px; padding: 12px 18px; width: 100%; box-shadow: 0 4px 14px rgba(28,25,23,0.08);">
<div style="font-family: 'Playfair Display', Georgia, serif; font-weight: 700; font-size: 0.95rem; color: #1C1917;">The Modern Villa Atelier</div>
<div style="font-size: 0.78rem; color: #78716C;">Geometry-Locked 3D Architectural Synthesis</div>
</div>
</div>
</div>
</div>
<div class="trust-strip">
<div class="trust-strip-item">🏛️ <strong>MVJCE Department of AI & ML</strong></div>
<div style="color: #D6D3D1;">•</div>
<div class="trust-strip-item">📐 <strong>ControlNet Geometry Locking</strong></div>
<div style="color: #D6D3D1;">•</div>
<div class="trust-strip-item">💰 <strong>100% Indian Market BoQ (INR ₹)</strong></div>
<div style="color: #D6D3D1;">•</div>
<div class="trust-strip-item">⚡ <strong>Sub-Second Local Tensor Engine</strong></div>
<div style="color: #D6D3D1;">•</div>
<div class="trust-strip-item">⭐ <strong>4.9 Architect Rating</strong></div>
</div>
</div>

<div style="margin-top: 10px; margin-bottom: 24px;">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px;">
<h3 style="font-family: 'Playfair Display', serif; font-size: 1.45rem; font-weight: 700; margin: 0; color: #1C1917;">Curated Architectural Materials & Finishes</h3>
<span style="font-size: 0.82rem; color: #78716C; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Verified Indian Supplier SKUs</span>
</div>
<div class="collection-grid">
<div class="collection-card" style="background: linear-gradient(145deg, #1E2238 0%, #2A3152 100%);">
<div style="font-size: 1.8rem; margin-bottom: 8px;">🏛️</div>
<div class="collection-card-title">Carrara Marble</div>
<div class="collection-card-rate">₹380 / sq.ft</div>
<div class="collection-card-desc">Italian pearl-white luxury slab with organic veining.</div>
</div>
<div class="collection-card" style="background: linear-gradient(145deg, #B25E43 0%, #D47A5D 100%);">
<div style="font-size: 1.8rem; margin-bottom: 8px;">🧱</div>
<div class="collection-card-title">Kajaria Vitrified</div>
<div class="collection-card-rate">₹75 / sq.ft</div>
<div class="collection-card-desc">High-gloss porcelain 1200×600mm laser-cut tiles.</div>
</div>
<div class="collection-card" style="background: linear-gradient(145deg, #C28E46 0%, #D9A862 100%);">
<div style="font-size: 1.8rem; margin-bottom: 8px;">🪵</div>
<div class="collection-card-title">Action TESA Oak</div>
<div class="collection-card-rate">₹175 / sq.ft</div>
<div class="collection-card-desc">Engineered warm honey-golden oak planks.</div>
</div>
<div class="collection-card" style="background: linear-gradient(145deg, #2D3A30 0%, #3D4E42 100%);">
<div style="font-size: 1.8rem; margin-bottom: 8px;">🎨</div>
<div class="collection-card-title">Royale Velvet</div>
<div class="collection-card-rate">₹28 / sq.ft</div>
<div class="collection-card-desc">Asian Paints washable luxury velvet sheen emulsion.</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs (Including My Saved Portfolio!)

tab_floorplan, tab_workspace, tab_portfolio, tab_contractor_report = st.tabs([
    "📐 Plot-to-Floorplan (Pillar 1)",
    "🛋️ Spatial Design Studio", 
    "📁 My Saved Portfolio", 
    "📄 Contractor BoQ Document"
])

# =====================================================================
# TAB 1: CLIENT-DRIVEN PLOT-TO-FLOORPLAN & VASTU CAD BLUEPRINT (PILLAR 1)
# =====================================================================
with tab_floorplan:
    st.markdown('<div class="section-title"><span class="step-badge">Pillar 1</span> Client-Driven Plot-to-Floorplan Generator & Vastu CAD Engine</div>', unsafe_allow_html=True)
    st.caption("Enter empty plot dimensions, road orientation, and client room wishlist to generate a municipal-compliant, Vastu-optimized 2D architectural blueprint with real dimensions & door swings.")

    if not LAYOUT_AVAILABLE:
        st.error(f"⚠️ Floorplan engine not loaded: {LAYOUT_ERROR_MSG}")
    else:
        # Standard Indian Plot Size Presets (Quick-select chips)
        st.markdown("**⚡ Quick Indian Standard Plot Presets:**")
        preset_c1, preset_c2, preset_c3, preset_c4 = st.columns(4)
        if preset_c1.button("📐 30 × 40 ft (1,200 sq.ft)", use_container_width=True, key="preset_30x40"):
            st.session_state.fp_plot_w = 30.0
            st.session_state.fp_plot_l = 40.0
            st.rerun()
        if preset_c2.button("📐 30 × 50 ft (1,500 sq.ft)", use_container_width=True, key="preset_30x50"):
            st.session_state.fp_plot_w = 30.0
            st.session_state.fp_plot_l = 50.0
            st.rerun()
        if preset_c3.button("📐 40 × 60 ft (2,400 sq.ft)", use_container_width=True, key="preset_40x60"):
            st.session_state.fp_plot_w = 40.0
            st.session_state.fp_plot_l = 60.0
            st.rerun()
        if preset_c4.button("📐 50 × 80 ft (4,000 sq.ft)", use_container_width=True, key="preset_50x80"):
            st.session_state.fp_plot_w = 50.0
            st.session_state.fp_plot_l = 80.0
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        col_fp_input, col_fp_output = st.columns([1, 1.25], gap="large")

        with col_fp_input:
            st.markdown("#### 🏡 1. Plot Dimensions & Road Orientation")
            
            c_w, c_l = st.columns(2)
            cur_w = float(st.session_state.get("fp_plot_w", 30.0))
            cur_l = float(st.session_state.get("fp_plot_l", 40.0))
            
            plot_w_input = c_w.slider("Plot Width (feet):", min_value=20.0, max_value=100.0, value=cur_w, step=1.0, key="slider_fp_w")
            plot_l_input = c_l.slider("Plot Length (feet):", min_value=25.0, max_value=120.0, value=cur_l, step=1.0, key="slider_fp_l")
            
            facing_options = ["North", "East", "South", "West"]
            cur_facing = st.session_state.get("fp_facing", "North")
            facing_idx = facing_options.index(cur_facing) if cur_facing in facing_options else 0
            road_facing_input = st.selectbox("Road Facing (Main Access):", facing_options, index=facing_idx, help="Determines front municipal setback and main entrance positioning.", key="select_fp_facing")

            st.markdown("#### 🛋️ 2. Custom Room Wishlist")
            
            c_typo, c_beds = st.columns(2)
            typo_options = ["1BHK", "2BHK", "3BHK", "4BHK"]
            cur_typo = st.session_state.get("fp_typology", "2BHK")
            typo_idx = typo_options.index(cur_typo) if cur_typo in typo_options else 1
            typology_input = c_typo.selectbox("Typology:", typo_options, index=typo_idx, key="select_fp_typo")
            
            def_beds = {"1BHK": 1, "2BHK": 2, "3BHK": 3, "4BHK": 4}.get(typology_input, 2)
            beds_input = c_beds.slider("Number of Bedrooms:", min_value=1, max_value=4, value=def_beds, key="slider_fp_beds")

            c_baths, c_theme = st.columns(2)
            baths_input = c_baths.slider("Number of Bathrooms:", min_value=1, max_value=4, value=max(1, min(beds_input, 3)), key="slider_fp_baths")
            theme_choice = c_theme.selectbox("CAD Visual Theme:", ["Architectural Blueprint (Classic Blue)", "Modern Clean (Light Minimal)", "Dark Tech (Cyber CAD)"], key="select_fp_theme")

            theme_map = {
                "Architectural Blueprint (Classic Blue)": "blueprint",
                "Modern Clean (Light Minimal)": "light",
                "Dark Tech (Cyber CAD)": "dark"
            }
            selected_theme = theme_map[theme_choice]

            st.markdown("**Add-on Spaces:**")
            col_add1, col_add2, col_add3 = st.columns(3)
            has_pooja = col_add1.checkbox("Pooja Room (NE)", value=True, help="Vastu Ishanya quadrant holy room")
            has_parking = col_add2.checkbox("Car Parking", value=True, help="Front portico / vehicle bay")
            has_balcony = col_add3.checkbox("Balcony", value=True, help="Verandah / sitout area")

            with st.expander("🏛️ Municipal Setback Parameters (BBMP / NBC Standards)", expanded=False):
                st.caption("Standard Indian building bylaws automatically applied to calculate net buildable plinth envelope.")
                sb_c1, sb_c2, sb_c3 = st.columns(3)
                front_sb = sb_c1.number_input("Front Setback (ft)", min_value=1.0, max_value=15.0, value=4.0, step=0.5)
                rear_sb = sb_c2.number_input("Rear Setback (ft)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
                side_sb = sb_c3.number_input("Side Setbacks (ft)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Generate 2D CAD Blueprint & Vastu Plan", type="primary", use_container_width=True, key="btn_generate_blueprint"):
                with st.spinner("📐 Calculating municipal setbacks, running Vastu optimization & rendering high-res CAD blueprint..."):
                    try:
                        fp_result = layout_generator.plan_room_layout(
                            plot_width=plot_w_input,
                            plot_length=plot_l_input,
                            road_facing=road_facing_input,
                            typology=typology_input,
                            num_bedrooms=beds_input,
                            num_bathrooms=baths_input,
                            has_pooja=has_pooja,
                            has_parking=has_parking,
                            has_balcony=has_balcony
                        )
                        blueprint_out = resolve_path("floorplan_output.png")
                        layout_generator.render_cad_blueprint(fp_result, output_path=blueprint_out, style_theme=selected_theme)
                        
                        st.session_state.floorplan_data = fp_result
                        st.session_state.floorplan_image_path = blueprint_out
                        st.session_state.fp_plot_w = plot_w_input
                        st.session_state.fp_plot_l = plot_l_input
                        st.session_state.fp_facing = road_facing_input
                        st.session_state.fp_typology = typology_input
                        st.success("✅ 2D CAD Blueprint and Vastu space plan generated successfully!")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"❌ Error during layout generation: {str(exc)}")

        with col_fp_output:
            fp_data = st.session_state.get("floorplan_data")
            fp_img_path = st.session_state.get("floorplan_image_path")

            if fp_data and fp_img_path and os.path.exists(fp_img_path):
                # Telemetry Metric Cards
                m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                m_c1.metric("Plot Area", f"{fp_data['plot_area_sqft']:,.0f} sq.ft")
                m_c2.metric("Plinth Built-up", f"{fp_data['buildable_area_sqft']:,.0f} sq.ft")
                m_c3.metric("Carpet Area", f"{fp_data['carpet_area_sqft']:,.0f} sq.ft")
                vastu_sc = fp_data['vastu_score']
                vastu_badge = f"{vastu_sc}%" + (" 🌟 Excellent" if vastu_sc >= 90 else " ✅ Compliant")
                m_c4.metric("Vastu Score", vastu_badge)

                # Blueprint Image Display
                st.image(fp_img_path, caption=f"AI-GLAZE Architectural CAD Blueprint — {fp_data['typology']} ({int(fp_data['plot_width'])}' × {int(fp_data['plot_length'])}')", use_container_width=True)

                # Action row: Download & Save to Portfolio
                act_c1, act_c2 = st.columns(2)
                with open(fp_img_path, "rb") as bf:
                    blueprint_bytes = bf.read()
                act_c1.download_button(
                    "📥 Download Blueprint (High-Res PNG)",
                    data=blueprint_bytes,
                    file_name=f"AIGLAZE_Floorplan_{int(fp_data['plot_width'])}x{int(fp_data['plot_length'])}_{fp_data['typology']}.png",
                    mime="image/png",
                    use_container_width=True,
                    key="btn_dl_fp"
                )

                if act_c2.button("💾 Save Blueprint to Portfolio", use_container_width=True, key="btn_save_fp"):
                    if AUTH_AVAILABLE:
                        proj_name = f"{fp_data['typology']} Vastu Plan ({int(fp_data['plot_width'])}×{int(fp_data['plot_length'])} ft)"
                        save_res = auth_manager.save_user_project(
                            user_id=user["id"],
                            project_name=proj_name,
                            style=f"Vastu {fp_data['vastu_score']}% Compliant",
                            budget=float(st.session_state.get("target_budget", 500000.0)),
                            floor_sqft=float(fp_data["carpet_area_sqft"]),
                            wall_sqft=float(fp_data["buildable_area_sqft"] * 2.8),
                            grand_total=float(fp_data["carpet_area_sqft"] * 1850.0),
                            image_path=fp_img_path,
                            metadata={"plot_width": fp_data["plot_width"], "plot_length": fp_data["plot_length"], "facing": fp_data["road_facing"], "typology": fp_data["typology"]}
                        )
                        if save_res.get("success"):
                            st.success("✅ Saved to client portfolio database!")
                        else:
                            st.error("Failed to save: " + str(save_res.get("error")))
                    else:
                        st.warning("Database unavailable.")

                # Vastu Shastra Compliance Breakdown
                with st.expander("🧭 Vastu Shastra Spatial Compliance Audit", expanded=True):
                    st.markdown(f"**Overall Vastu Score:** `{vastu_sc}%` (Weighted by Quadrant Energy & Direction)")
                    st.caption("Traditional Indian Vedic architecture guidelines mapped to cardinal quadrants:")
                    vastu_points = [
                        "🛡️ **Master Bedroom in Southwest (SW - Nairutya):** High stability, earth element, optimal master suite positioning.",
                        "🔥 **Kitchen in Southeast (SE - Agneya):** Lord Agni (Fire) direction, natural morning sunlight and ventilation.",
                        "✨ **Pooja Room in Northeast (NE - Ishanya):** Maximum positive cosmic energy and serene morning prayer orientation.",
                        "🛋️ **Living Room & Foyer in Northeast / North (Ishanya / Kuber):** Welcome wealth, open welcoming circulation.",
                        "💨 **Second Bedroom & Toilets in Northwest (NW - Vayavya):** Air element, ideal for guests and plumbing exhaust."
                    ]
                    for vp in vastu_points:
                        st.markdown(f"- {vp}")

                # Room Schedule & Dimensional Breakdown
                with st.expander("📐 Room Schedule & Dimensional Breakdown", expanded=False):
                    room_rows = []
                    for rm in fp_data.get("rooms", []):
                        room_rows.append({
                            "Room Name": rm["name"],
                            "Quadrant": rm.get("quadrant", "Core"),
                            "Width (ft)": f"{rm['width']:.1f}'",
                            "Length (ft)": f"{rm['length']:.1f}'",
                            "Carpet Area (sq.ft)": f"{rm['area_sqft']:.1f}",
                            "Vastu Zone": rm.get("vastu_zone", "Auspicious")
                        })
                    st.dataframe(room_rows, use_container_width=True)
            else:
                st.info("👈 Select your plot size, road facing, and room wishlist on the left, then click **'Generate 2D CAD Blueprint & Vastu Plan'** to generate the architectural blueprint.")
                default_demo = resolve_path("sample_floorplan.png")
                if os.path.exists(default_demo):
                    st.image(default_demo, caption="AI-GLAZE Sample 30×40 ft 2BHK Vastu Blueprint Preview", use_container_width=True)

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

<span style="color: #57534E; font-size: 0.88rem;">18% GST &amp; Architectural Reasoning Notes Included</span>

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

<div style="font-weight: 700; color: #1C1917; font-size: 1.05rem; margin-bottom: 4px;">

💼 Store Session in Architect & Client Portfolio

</div>

<div style="font-size: 0.85rem; color: #78716C; margin-bottom: 16px;">

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


<div style="text-align: center; color: #78716C; font-size: 0.85rem; padding: 16px;">

<strong>AI-GLAZE</strong> • College Capstone Project • MVJ College of Engineering • Indian Market Edition (INR ₹)

</div>

""", unsafe_allow_html=True)
