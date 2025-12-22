"""قسم المبيعات"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.app.gui.page_config import DEPARTMENTS
from src.app.gui.page_templates.department import render_department
render_department(DEPARTMENTS['sales'])
