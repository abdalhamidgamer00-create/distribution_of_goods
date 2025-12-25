"""Application styles."""

import streamlit as st


def apply_custom_styles() -> None:
    """Apply premium custom CSS styles."""
    styles = """
    <style>
        /* Main Layout & RTL */
        .main { 
            direction: rtl; 
            text-align: right; 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* Typography */
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Tajawal', sans-serif;
        }
        
        h1, h2, h3 { 
            text-align: right; 
            color: #1a2a6c;
            font-weight: 700;
        }

        /* =========================================================================
           BUTTON DESIGN SYSTEM
           ========================================================================= */

        /* 1. Global Base Style (Common for all buttons) */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        /* 2. Dashboard Tiles (Home Page - Big & Bold) */
        div:has(> button[key^="home_"]) .stButton > button,
        div:has(> button[key^="home_"]) .stButton > button p {
            background: linear-gradient(90deg, #1a2a6c 0%, #b21f1f 50%, #fdbb2d 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 1.8rem !important;
            padding: 1.2rem 0.5rem !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: none !important;
        }

        /* 3. Tool Action Buttons (Purchases Tools - Medium & Professional) */
        div:has(> button[key^="run_"]) .stButton > button,
        div:has(> button[key^="run_"]) .stButton > button p {
            background: #1a2a6c !important; /* Elegant Royal Blue */
            color: white !important;
            font-weight: 600 !important;
            font-size: 1.2rem !important;
            padding: 0.6rem !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(26, 42, 108, 0.3);
        }

        /* 4. Primary Command Buttons (e.g., Run All - Bold & Distinct) */
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primary"] p {
            background: linear-gradient(90deg, #ce2029 0%, #8b0000 100%) !important; /* Deep Red for main actions */
            color: white !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            border: none !important;
            padding: 0.8rem !important;
        }

        /* 5. Secondary / Utility Buttons (e.g., Back to Home - Subtle & Clean) */
        button[data-testid="stBaseButton-secondary"],
        button[data-testid="stBaseButton-secondary"] p {
            background: #f8f9fa !important;
            color: #1a2a6c !important;
            border: 1px solid #1a2a6c !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
        }

        /* Hover Effects */
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
            opacity: 0.95;
        }
        
        div:has(> button[key^="home_"]) .stButton > button:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
        }

        /* Specifically style the container for the tiles */
        div[data-testid="stVerticalBlock"] > div:has(button[key^="home_"]) {
            transition: all 0.3s ease;
        }

        /* Glassmorphism containers */
        div[data-testid="stVerticalBlock"] > div:has(div.stInfo) {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        /* Sidebar Polishing */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-left: 1px solid #eee;
        }
        
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: #1a2a6c;
            border-bottom: 2px solid #fdbb2d;
            padding-bottom: 5px;
            margin-top: 20px;
        }
    </style>
    """
    st.markdown(styles, unsafe_allow_html=True)
