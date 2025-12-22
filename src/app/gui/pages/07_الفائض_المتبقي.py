"""صفحة الفائض المتبقي"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.app.gui.page_templates.simple_browser import render_simple_browser
render_simple_browser('الفائض المتبقي', '📦', 
    os.path.join("data", "output", "remaining_surplus", "csv"),
    os.path.join("data", "output", "remaining_surplus", "excel"), 9, 'surplus')
