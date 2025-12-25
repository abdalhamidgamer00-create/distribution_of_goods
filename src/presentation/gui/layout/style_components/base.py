"""Base typography and layout styles."""

def get_base_styles() -> str:
    """Return CSS for layout and typography."""
    return """
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
    """
