"""صفحة التحويلات المنفصلة"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.app.gui.page_templates.branch_browser import render_separate_browser
render_separate_browser('التحويلات المنفصلة', '📂',
    os.path.join("data", "output", "combined_transfers", "separate", "csv"),
    os.path.join("data", "output", "combined_transfers", "separate", "excel"), 11, 'sep_selected_source', 'sep')
