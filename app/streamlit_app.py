import os
import streamlit as st
import tempfile


from app.config import algorithm_routes
from app.ui.algorithm_explanation_ui.algorithm_explanation_controller import (
    AlgorithmExplanationController,
)
from app.ui.column_selection_ui.column_selection_controller import (
    ColumnSelectionController,
)
from app.ui.export_ui.export_controller import ExportController
from app.ui.home_ui.home_controller import HomeController

st.set_page_config(
    page_title="Process Mining Tool",
    page_icon=":bar_chart:",
    layout="wide",
)

APP_TMP_ROOT = os.path.join(tempfile.gettempdir(), "pm-insight")
os.makedirs(APP_TMP_ROOT, exist_ok=True)

if "session_tmp_dir" not in st.session_state:
    st.session_state.session_tmp_dir = tempfile.mkdtemp(
        dir=APP_TMP_ROOT, prefix="session_"
    )

if "page" not in st.session_state:
    st.session_state.page = "Home"

if st.session_state.page == "Home":
    HomeController().start()
elif st.session_state.page == "Algorithm":
    algorithm_routes[st.session_state.algorithm]().start()
elif st.session_state.page == "ColumnSelection":
    ColumnSelectionController().start()
elif st.session_state.page == "Export":
    ExportController().start()
elif st.session_state.page == "Documentation":
    AlgorithmExplanationController().start()
