"""
app.py
Main entry point for MediCore Health: Hospital Management & Staffing Analytics Dashboard.
Directs users into the primary Executive Hospital Overview page.
"""

import sys
from pathlib import Path
from streamlit.runtime import exists

# If executed directly via standard Python (e.g. PyCharm 'Run' button), launch via Streamlit CLI
if __name__ == "__main__" and not exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", __file__] + sys.argv[1:]
    sys.exit(stcli.main())

# Streamlit application execution
import streamlit as st

st.set_page_config(
    page_title="MediCore Health | Hospital Overview",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    st.switch_page("pages/1_Hospital_Overview.py")
except Exception:
    import importlib
    overview_module = importlib.import_module("pages.1_Hospital_Overview")
    overview_module.main()
