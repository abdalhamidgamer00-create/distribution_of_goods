"""Main project entry point"""

import sys
import os

from src.shared.utils.logging_utils import setup_logging


def run_gui():
    """تشغيل واجهة Streamlit"""
    import subprocess
    app_path = os.path.join("src", "app", "gui", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])


def run_cli():
    """تشغيل واجهة سطر الأوامر"""
    from src.app.cli.menu import run_menu
    setup_logging()
    run_menu()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        run_gui()
    else:
        run_cli()

