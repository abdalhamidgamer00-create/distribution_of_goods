"""صفحة الحسابات."""
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
))

from src.presentation.gui.page_templates.department import render_department
from src.presentation.gui.page_config import DEPARTMENTS

render_department(DEPARTMENTS['accounting'])
