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

        /* Premium Card/Button Style */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            border: none;
            background: linear-gradient(90deg, #1a2a6c 0%, #b21f1f 50%, #fdbb2d 100%);
            color: white;
            font-weight: 600;
            padding: 0.6rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            color: white;
            opacity: 0.9;
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
