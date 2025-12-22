"""صفحة ملفات التحويل"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.app.gui.page_templates.branch_browser import render_transfers_browser
render_transfers_browser('ملفات التحويل', '📤',
    os.path.join("data", "output", "transfers", "csv"),
    os.path.join("data", "output", "transfers", "excel"), 7, 'selected_source_branch', 'transfers')
