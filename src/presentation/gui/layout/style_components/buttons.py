"""Button design system styles."""

def get_button_styles() -> str:
    """Return CSS for the hierarchical button system."""
    return """
        /* 1. Global Base Style - Pure & Clean */
        .stButton button {
            width: 100% !important;
            border-radius: 12px !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            text-align: center !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            border: none !important;
            color: white !important;
            font-family: 'Tajawal', sans-serif !important;
            letter-spacing: 0.5px !important;
            font-weight: 700 !important;
            text-decoration: none !important;
        }

        /* CRITICAL: Prevent 'Box in Box' effect by stripping all P styles */
        .stButton button p, 
        .stButton button div,
        .stButton button span {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            font-size: inherit !important;
            font-weight: inherit !important;
            color: inherit !important;
        }

        /* 2. Dashboard Tiles (Home Page) - Deep Premium Navy */
        div[data-testid="column"]:has(button[key^="home_"]) button {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1a2a6c 100%) !important;
            font-size: 1.8rem !important;
            padding: 2.5rem 1rem !important;
            box-shadow: 0 10px 25px rgba(30, 60, 114, 0.3) !important;
            min-height: 150px !important;
        }

        /* 3. Tool Action Buttons (Vibrant Emerald/Teal Tiles) */
        div[data-testid="column"]:has(button[key^="run_"]) button {
            background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important;
            font-size: 1.4rem !important;
            padding: 1.8rem !important;
            box-shadow: 0 8px 20px rgba(0, 176, 155, 0.25) !important;
            min-height: 120px !important;
            border-radius: 15px !important;
        }

        /* 4. Primary Command Buttons (Golden Sunset Glow) */
        button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #f09819 0%, #edde5d 100%) !important;
            color: #1a2a6c !important;
            font-size: 1.3rem !important;
            padding: 1.2rem !important;
            box-shadow: 0 10px 20px rgba(240, 152, 25, 0.2) !important;
        }

        /* 5. Utility & Back Buttons (Clean Minimal Glass) */
        button[data-testid="stBaseButton-secondary"] {
            background: rgba(255, 255, 255, 0.95) !important;
            color: #1a2a6c !important;
            border: 2px solid #1a2a6c !important;
            font-size: 1.1rem !important;
            padding: 0.8rem !important;
        }

        /* Interactivity & Hover Effects */
        .stButton button:hover {
            transform: translateY(-8px) !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2) !important;
            filter: brightness(1.1) !important;
        }

        /* Specific extra pop for Home Tiles */
        div[data-testid="column"]:has(button[key^="home_"]) button:hover {
            transform: translateY(-12px) scale(1.03) !important;
            box-shadow: 0 25px 50px rgba(30, 60, 114, 0.4) !important;
        }

        /* Active click effect */
        .stButton button:active {
            transform: translateY(2px) scale(0.98) !important;
        }
    """
