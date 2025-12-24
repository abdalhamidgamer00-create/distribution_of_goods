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
    from src.app.cli.executors.step_executor.step_executor_orchestrator import (
        execute_step, execute_step_with_dependencies
    )
    from src.app.cli.executors.step_executor.lookup import find_step_by_id
    
    setup_logging()
    
    args = sys.argv[1:]
    use_latest = "--latest" in args
    
    # CASE 1: Isolated step execution via --step flag
    if "--step" in args:
        try:
            step_idx = args.index("--step")
            step_id = args[step_idx + 1]
            step = find_step_by_id(step_id)
            if step:
                print(f"\n--- [CLI] Isolated Execution: {step.name} ({step_id}) ---")
                execute_step(step_id, use_latest_file=use_latest)
                return
            else:
                print(f"Error: Step {step_id} not found.")
                return
        except (IndexError, ValueError):
            print("Usage: python main.py --step <id> [--latest]")
            return

    # CASE 2: Positional step ID (Defaults to dependency-aware execution like the menu)
    positional_args = [a for a in args if not a.startswith("--")]
    if positional_args and positional_args[0].isdigit():
        step_id = positional_args[0]
        step = find_step_by_id(step_id)
        if step:
            # If explicit --step is not used, we assume interactive-like behavior (with deps)
            execute_step_with_dependencies(step_id, use_latest_file=use_latest)
            return

    # CASE 3: Execute all steps via --all flag
    if "--all" in args:
        from src.app.cli.executors.batch_executor import _run_steps_with_mode
        _run_steps_with_mode(use_latest)
        return

    # Default to interactive menu
    run_menu()


if __name__ == "__main__":
    if "--gui" in sys.argv:
        run_gui()
    else:
        run_cli()

