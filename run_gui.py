"""تشغيل واجهة Streamlit مباشرة"""

import subprocess
import sys
import os

if __name__ == "__main__":
    app_path = os.path.join("src", "app", "gui", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

