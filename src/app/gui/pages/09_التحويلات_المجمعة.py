"""صفحة التحويلات المجمعة"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.app.gui.page_templates.branch_browser import render_merged_browser
render_merged_browser('التحويلات المجمعة', '📋',
    os.path.join("data", "output", "combined_transfers", "merged", "csv"),
    os.path.join("data", "output", "combined_transfers", "merged", "excel"), 11, 'merged_selected_branch', 'merged')
