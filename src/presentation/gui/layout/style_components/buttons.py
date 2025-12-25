"""Button design system styles."""

def get_button_styles() -> str:
    """Return CSS for the hierarchical button system."""
    return """
        /* 1. Global Base Style */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            border: none !important;
        }

        /* 2. Dashboard Tiles (Home Page) */
        div:has(> button[key^="home_"]) .stButton > button,
        div:has(> button[key^="home_"]) .stButton > button p {
            background: linear-gradient(90deg, #1a2a6c 0%, #b21f1f 50%, #fdbb2d 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 1.8rem !important;
            padding: 1.2rem 0.5rem !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        /* 3. Tool Action Buttons (Medium & Professional) */
        div:has(> button[key^="run_"]) .stButton > button,
        div:has(> button[key^="run_"]) .stButton > button p {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            padding: 1rem 0.8rem !important;
            box-shadow: 0 4px 10px rgba(30, 60, 114, 0.2);
            min-height: 80px;
        }

        /* 4. Primary Command Buttons (e.g., Run All) */
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primary"] p {
            background: linear-gradient(90deg, #8b0000 0%, #600000 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            padding: 0.8rem !important;
        }

        /* 5. Utility Buttons (e.g., Back to Home) */
        button[data-testid="stBaseButton-secondary"],
        button[data-testid="stBaseButton-secondary"] p {
            background: white !important;
            color: #1a2a6c !important;
            border: 1.5px solid #1a2a6c !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }

        /* Hover Effects */
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
        }
        
        div:has(> button[key^="home_"]) .stButton > button:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
        }
    """
