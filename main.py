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
    from src.app.cli.executors import execute_step, execute_all_steps
    from src.app.cli.executors.step_executor.execution import execute_single_step
    from src.app.cli.executors.step_executor.lookup import find_step_by_id
    
    setup_logging()
    
    # Check for CLI arguments
    if "--step" in sys.argv:
        try:
            step_idx = sys.argv.index("--step")
            step_id = sys.argv[step_idx + 1]
            use_latest = "--latest" in sys.argv
            
            step = find_step_by_id(step_id)
            if step:
                print(f"\n--- [CLI] Executing Step {step_id}: {step.name} ---")
                execute_single_step(step, use_latest_file=use_latest)
            else:
                print(f"Error: Step {step_id} not found.")
        except (IndexError, ValueError):
            print("Usage: python main.py --step <id> [--latest]")
    elif "--all" in sys.argv:
        use_latest = "--latest" in sys.argv
        from src.app.cli.executors.batch_executor import _run_steps_with_mode
        _run_steps_with_mode(use_latest)
    else:
        run_menu()


if __name__ == "__main__":
    if "--gui" in sys.argv:
        run_gui()
    else:
        run_cli()

