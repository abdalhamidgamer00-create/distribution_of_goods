"""صفحة التسويق."""
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
))

from src.app.gui.page_templates.department import render_department
from src.app.gui.page_config import DEPARTMENTS

render_department(DEPARTMENTS['marketing'])
