import streamlit as st

from app.mining_algorithms.inductive_mining_infrequent import InductiveMiningInfrequent
from app.ui.base_algorithm_ui.base_algorithm_controller import BaseAlgorithmController
from app.ui.inductive_miner_infrequent_ui.inductive_miner_infrequent_view import (
    InductiveMinerInfrequentView,
)


class InductiveMinerInfrequentController(BaseAlgorithmController):

    def __init__(
        self, views=None, mining_model_class=None, dataframe_transformations=None
    ):

        self.traces_threshold = None
        self.noise_threshold = 0.2
        self.use_petri_net = False

        if views is None:
            views = [InductiveMinerInfrequentView()]

        if mining_model_class is None:
            mining_model_class = InductiveMiningInfrequent
        super().__init__(views, mining_model_class, dataframe_transformations)

    def get_page_title(self) -> str:

        return "Inductive Mining Infrequent"

    def process_algorithm_parameters(self):

        super().process_algorithm_parameters()

        if "traces_threshold" not in st.session_state:
            st.session_state.traces_threshold = self.mining_model.get_traces_threshold()
        self.traces_threshold = st.session_state.traces_threshold

        if "noise_threshold" not in st.session_state:
            st.session_state.noise_threshold = self.noise_threshold
        self.noise_threshold = st.session_state.noise_threshold

        if "inductive_infrequent_use_petri_net" not in st.session_state:
            st.session_state.inductive_infrequent_use_petri_net = self.use_petri_net
        self.use_petri_net = st.session_state.inductive_infrequent_use_petri_net

    def perform_mining(self):

        super().perform_mining(
            traces_threshold=self.traces_threshold,
            use_petri_net=self.use_petri_net,
            noise_threshold=self.noise_threshold,
        )

    def have_parameters_changed(self) -> bool:

        return (
            super().have_parameters_changed()
            or self.mining_model.get_traces_threshold() != self.traces_threshold
            or getattr(self.mining_model, "noise_threshold", 0.2)
            != self.noise_threshold
            or getattr(self.mining_model, "use_petri_net", False) != self.use_petri_net
        )

    def get_sidebar_values(self) -> dict[str, tuple[int | float, int | float]]:

        sidebar_values = super().get_sidebar_values()
        sidebar_values.update(
            {
                "traces_threshold": (0.0, 1.0),
                "noise_threshold": (0.0, 1.0),
            }
        )

        return sidebar_values
