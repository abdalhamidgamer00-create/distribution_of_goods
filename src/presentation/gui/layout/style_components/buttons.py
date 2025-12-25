"""Button design system styles."""

def get_button_styles() -> str:
    """Return CSS for the hierarchical button system."""
    return """
        /* 1. Global Base Style */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            border: none !important;
            color: white !important;
            font-family: 'Tajawal', sans-serif;
            letter-spacing: 0.5px;
        }

        /* 2. Dashboard Tiles (Home Page) - The 'WOW' entry */
        div:has(> button[key^="home_"]) .stButton > button,
        div:has(> button[key^="home_"]) .stButton > button p {
            background: linear-gradient(135deg, #1a2a6c 0%, #b21f1f 50%, #fdbb2d 100%) !important;
            font-weight: 700 !important;
            font-size: 1.8rem !important;
            padding: 1.5rem 0.5rem !important;
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
            min-height: 120px;
        }

        /* 3. Tool Action Buttons (Indigo/Blue Cards) */
        div:has(> button[key^="run_"]) .stButton > button,
        div:has(> button[key^="run_"]) .stButton > button p {
            background: linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%) !important;
            font-weight: 600 !important;
            font-size: 1.25rem !important;
            padding: 1.2rem !important;
            box-shadow: 0 6px 15px rgba(0, 210, 255, 0.2);
            min-height: 90px;
            border-bottom: 3px solid rgba(0,0,0,0.1) !important;
        }

        /* 4. Primary Command Buttons (Vibrant Crimson) */
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primary"] p {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%) !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            padding: 1rem !important;
            box-shadow: 0 8px 15px rgba(235, 51, 73, 0.3);
            text-transform: uppercase;
        }

        /* 5. Utility Buttons (Glass-like with Blue Glow) */
        button[data-testid="stBaseButton-secondary"],
        button[data-testid="stBaseButton-secondary"] p {
            background: rgba(26, 42, 108, 0.05) !important;
            color: #1a2a6c !important;
            border: 2px solid #1a2a6c !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }

        /* Hover states */
        .stButton>button:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2) !important;
            filter: brightness(1.1);
        }
        
        div:has(> button[key^="home_"]) .stButton > button:hover {
            transform: translateY(-8px) scale(1.03);
        }
    """
