"""Button design system styles."""

def get_button_styles() -> str:
    """Return CSS for the hierarchical button system."""
    return """
        /* 1. Global Base Style - Modern & Slick */
        .stButton>button {
            width: 100%;
            border-radius: 16px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            border: none !important;
            color: white !important;
            font-family: 'Tajawal', sans-serif;
            letter-spacing: 0.5px;
            font-weight: 700 !important;
        }

        /* 2. Dashboard Tiles (Home Page) - Deep Glass Gradient */
        div:has(> button[key^="home_"]) .stButton > button,
        div:has(> button[key^="home_"]) .stButton > button p {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e3c72 100%) !important;
            font-size: 1.8rem !important;
            padding: 2rem 0.5rem !important;
            box-shadow: 0 10px 30px rgba(30, 60, 114, 0.3);
            min-height: 140px;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        /* 3. Tool Action Buttons (Vibrant Emerald/Teal Tiles) */
        div:has(> button[key^="run_"]) .stButton > button,
        div:has(> button[key^="run_"]) .stButton > button p {
            background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important;
            font-size: 1.3rem !important;
            padding: 1.5rem !important;
            box-shadow: 0 8px 20px rgba(0, 176, 155, 0.25);
            min-height: 100px;
            border-radius: 20px !important;
        }

        /* 4. Primary Command Buttons (Lustrous Ruby Red) */
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primary"] p {
            background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%) !important;
            font-size: 1.25rem !important;
            padding: 1.2rem !important;
            box-shadow: 0 12px 25px rgba(238, 9, 121, 0.3);
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }

        /* 5. Utility Buttons (Premium White Glass) */
        button[data-testid="stBaseButton-secondary"],
        button[data-testid="stBaseButton-secondary"] p {
            background: rgba(255, 255, 255, 0.9) !important;
            color: #1e3c72 !important;
            border: 2px solid #1e3c72 !important;
            font-size: 1.1rem !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }

        /* Interactive Animations */
        .stButton>button:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.25) !important;
            filter: brightness(1.1);
        }

        .stButton>button:active {
            transform: translateY(2px) scale(0.98);
        }
        
        /* Specific glow for tools */
        div:has(> button[key^="run_"]) .stButton > button:hover {
            box-shadow: 0 15px 35px rgba(0, 176, 155, 0.45) !important;
        }
    """
