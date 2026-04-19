"""Main project entry point"""

import sys
import os

from src.shared.utility.logging_utils import setup_logging


def run_gui():
    """تشغيل واجهة Streamlit"""
    import subprocess
    app_path = os.path.join("src", "presentation", "gui", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])


def run_cli():
    """تشغيل واجهة سطر الأوامر"""
    from src.presentation.cli.menu import run_menu
    from src.presentation.cli.executors.step_executor.step_executor_orchestrator import (
        execute_step, execute_step_with_dependencies
    )
    from src.presentation.cli.executors.step_executor.lookup import find_step_by_id
    from src.domain.models.config import InventoryConfig
    
    setup_logging()
    
    args = sys.argv[1:]
    use_latest = "--latest" in args
    
    # Parse Coverage Config
    def get_arg_val(flag, default):
        try:
            idx = args.index(flag)
            return int(args[idx + 1])
        except (ValueError, IndexError):
            return default

    config = InventoryConfig(
        need_days=get_arg_val("--need", 20),
        surplus_days=get_arg_val("--surplus", 60),
        shortage_days=get_arg_val("--shortage", 30)
    )
    
    # CASE 1: Isolated step execution via --step flag
    if "--step" in args:
        try:
            step_idx = args.index("--step")
            step_id = args[step_idx + 1]
            step = find_step_by_id(step_id)
            if step:
                print(f"\n--- [CLI] Isolated Execution: {step.name} ({step_id}) ---")
                execute_step(step_id, use_latest_file=use_latest, config=config)
                return
            else:
                print(f"Error: Step {step_id} not found.")
                return
        except (IndexError, ValueError):
            print("Usage: python main.py --step <id> [--latest] [--need <d>] [--surplus <d>] [--shortage <d>]")
            return

    # CASE 2: Positional step ID
    positional_args = [a for a in args if not a.startswith("--")]
    if positional_args and positional_args[0].isdigit():
        step_id = positional_args[0]
        step = find_step_by_id(step_id)
        if step:
            execute_step_with_dependencies(step_id, use_latest_file=use_latest, config=config)
            return

    # CASE 3: Execute all steps via --all flag
    if "--all" in args:
        from src.presentation.cli.executors.batch_executor import _run_steps_with_mode
        _run_steps_with_mode(use_latest, config=config)
        return

    # Default to interactive menu
    run_menu()


if __name__ == "__main__":
    if "--gui" in sys.argv:
        run_gui()
    else:
        run_cli()

