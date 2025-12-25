"""Container and glassmorphism styles."""

def get_container_styles() -> str:
    """Return CSS for containers and glassmorphism."""
    return """
        /* Glassmorphism containers */
        div[data-testid="stVerticalBlock"] > div:has(div.stInfo) {
            background: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(12px) !important;
            border-radius: 18px !important;
            padding: 1.5rem !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.07) !important;
        }

        /* Metrics cards enhancement */
        div[data-testid="stMetric"] {
            background: white !important;
            padding: 1rem !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
            border: 1px solid #f0f2f6 !important;
        }

        /* Specific container for tool grid spacing */
        div[data-testid="stVerticalBlock"] > div:has(button[key^="run_"]) {
            margin-bottom: 25px !important;
            padding: 5px !important;
        }

        /* Style for the dashboard tile vertical block */
        div[data-testid="stVerticalBlock"] > div:has(button[key^="home_"]) {
            transition: all 0.4s ease !important;
        }

        /* Divider styling */
        hr {
            margin: 2rem 0 !important;
            border: 0 !important;
            height: 1px !important;
            background-image: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.1), rgba(0,0,0,0)) !important;
        }
    """
