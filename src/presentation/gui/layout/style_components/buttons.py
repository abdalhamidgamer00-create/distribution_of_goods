"""Button design system styles."""

def get_button_styles() -> str:
    """Return CSS for the hierarchical button system."""
    return """
        /* 1. Global Base Style - Pure & Clean */
        .stButton {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }

        .stButton>button {
            width: 100%;
            border-radius: 12px;
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
            outline: none !important;
        }

        /* 2. Dashboard Tiles (Home Page) - Strong Deep Gradient */
        div:has(> button[key^="home_"]) button,
        div:has(> button[key^="home_"]) button p {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1a2a6c 100%) !important;
            font-size: 1.8rem !important;
            padding: 2.5rem 1rem !important;
            box-shadow: 0 10px 25px rgba(30, 60, 114, 0.3);
            min-height: 150px;
        }

        /* 3. Tool Action Buttons (Vibrant Emerald Tiles) */
        div:has(> button[key^="run_"]) button,
        div:has(> button[key^="run_"]) button p {
            background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important;
            font-size: 1.4rem !important;
            padding: 1.5rem !important;
            box-shadow: 0 8px 20px rgba(0, 176, 155, 0.25);
            min-height: 110px;
            border-radius: 15px !important;
        }

        /* 4. Primary Command Buttons (Warm Sunset Gradient) */
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primary"] p {
            background: linear-gradient(135deg, #f09819 0%, #edde5d 100%) !important; /* Golden Orange */
            color: #1e3c72 !important;
            font-size: 1.3rem !important;
            padding: 1.2rem !important;
            box-shadow: 0 10px 20px rgba(240, 152, 25, 0.2);
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
