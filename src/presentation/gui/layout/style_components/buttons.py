"""Button design system styles."""

def get_button_styles() -> str:
    """Return CSS for the hierarchical button system."""
    return """
        /* 1. Global Base Style */
        .stButton>button {
            width: 100%;
            border-radius: 14px;
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            font-family: 'Tajawal', sans-serif;
            letter-spacing: 0.3px;
            overflow: hidden;
            position: relative;
        }

        /* 2. Dashboard Tiles (Home Page) - 'Apple-esque' Indigo Gradient */
        div:has(> button[key^="home_"]) .stButton > button,
        div:has(> button[key^="home_"]) .stButton > button p {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            font-weight: 700 !important;
            font-size: 1.6rem !important;
            padding: 1.8rem 0.5rem !important;
            box-shadow: 0 12px 24px rgba(79, 70, 229, 0.15);
            min-height: 130px;
        }

        /* 3. Tool Action Buttons (Professional Navy/Slate) */
        div:has(> button[key^="run_"]) .stButton > button,
        div:has(> button[key^="run_"]) .stButton > button p {
            background: #ffffff !important;
            color: #1e293b !important;
            border: 1.5px solid #e2e8f0 !important;
            font-weight: 600 !important;
            font-size: 1.15rem !important;
            padding: 1.2rem !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
            min-height: 85px;
        }
        
        div:has(> button[key^="run_"]) .stButton > button:hover {
            border-color: #4f46e5 !important;
            color: #4f46e5 !important;
            background: #f8fafc !important;
        }

        /* 4. Primary Command Buttons (Vibrant Emerald) */
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primary"] p {
            background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            padding: 1.2rem !important;
            box-shadow: 0 8px 16px rgba(16, 185, 129, 0.25);
            border: none !important;
        }

        /* 5. Utility Buttons (Minimalist Slate) */
        button[data-testid="stBaseButton-secondary"],
        button[data-testid="stBaseButton-secondary"] p {
            background: transparent !important;
            color: #64748b !important;
            border: 1px solid #cbd5e1 !important;
            font-weight: 500 !important;
            font-size: 0.95rem !important;
        }

        /* Interactive Elements */
        .stButton>button:active {
            transform: scale(0.96);
        }

        .stButton>button:hover {
            transform: translateY(-4px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.12) !important;
        }

        /* Specific hover for primary to make it 'pop' */
        button[data-testid="stBaseButton-primary"]:hover {
            filter: brightness(1.05);
            box-shadow: 0 12px 24px rgba(16, 185, 129, 0.35) !important;
        }
    """
