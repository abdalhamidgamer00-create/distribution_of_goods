"""صفحة النقص"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.app.gui.page_templates.simple_browser import render_simple_browser
render_simple_browser('النقص في المنتجات', '⚠️',
    os.path.join("data", "output", "shortage", "csv"),
    os.path.join("data", "output", "shortage", "excel"), 10, 'shortage', show_branch=False)
