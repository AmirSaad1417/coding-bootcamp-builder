"""Root entry point for cloud deployments (Hugging Face Spaces, Streamlit Cloud)."""
import sys
from pathlib import Path

# Add project root to Python module search path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Execute main Streamlit app in src/app.py
import runpy
runpy.run_path(str(PROJECT_ROOT / "src" / "app.py"), run_name="__main__")
