"""Streamlit entry point. Start with: streamlit run main.py."""

from pathlib import Path
import runpy


runpy.run_path(str(Path(__file__).with_name("app.py")))