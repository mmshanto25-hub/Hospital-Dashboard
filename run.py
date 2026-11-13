"""
run.py
PyCharm & IDE One-Click Launcher for MediCore Health Dashboard.

Right-click this file in PyCharm and click "Run 'run'" (or press Shift + F10)
to automatically launch the Streamlit dashboard in your web browser.
"""

import sys
from pathlib import Path
from streamlit.web import cli as stcli

if __name__ == "__main__":
    app_file = str(Path(__file__).resolve().parent / "app.py")
    sys.argv = ["streamlit", "run", app_file] + sys.argv[1:]
    sys.exit(stcli.main())
