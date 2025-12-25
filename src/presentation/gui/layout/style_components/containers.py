"""Container and glassmorphism styles."""

def get_container_styles() -> str:
    """Return CSS for containers and glassmorphism."""
    return """
        /* Glassmorphism containers */
        div[data-testid="stVerticalBlock"] > div:has(div.stInfo) {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        /* Specific container for tool grid spacing */
        div[data-testid="stVerticalBlock"] > div:has(button[key^="run_"]) {
            margin-bottom: 20px;
        }

        /* Style for the dashboard tile vertical block */
        div[data-testid="stVerticalBlock"] > div:has(button[key^="home_"]) {
            transition: all 0.3s ease;
        }
    """
