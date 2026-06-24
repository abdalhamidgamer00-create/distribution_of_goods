"""Streamlit page path bootstrap.

Every Streamlit multi-page page file needs the project root on
``sys.path`` so that ``src.*`` imports resolve.  Import this module
at the top of each page file instead of duplicating the boilerplate::

    import src.presentation.gui.page_setup  # noqa: F401  -- path bootstrap
"""

import os
import sys

_project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
