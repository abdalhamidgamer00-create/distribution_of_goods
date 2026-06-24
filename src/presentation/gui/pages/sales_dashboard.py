import src.presentation.gui.page_setup  # noqa: F401  -- path bootstrap

from src.presentation.gui.page_templates.department import render_department
from src.presentation.gui.page_config import DEPARTMENTS

render_department(DEPARTMENTS['sales'])
