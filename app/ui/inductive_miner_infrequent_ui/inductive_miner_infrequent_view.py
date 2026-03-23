import streamlit as st

from app.components.number_input_slider import number_input_slider
from app.ui.base_algorithm_ui.base_algorithm_view import BaseAlgorithmView


class InductiveMinerInfrequentView(BaseAlgorithmView):

    def render_log_filter_extensions(
        self, sidebar_values: dict[str, tuple[int | float, int | float]]
    ) -> None:

        number_input_slider(
            label="Traces Threshold",
            min_value=sidebar_values["traces_threshold"][0],
            max_value=sidebar_values["traces_threshold"][1],
            key="traces_threshold",
            help="""Minimum frequency threshold for traces. Traces below this threshold will be filtered out.""",
        )

        st.toggle(
            "Petri-Net Visualization",
            key="inductive_infrequent_use_petri_net",
            value=st.session_state.get("inductive_infrequent_use_petri_net", False),
            help="Switch between classic and petri-net visualization.",
        )

        st.write("### Noise Filtering")

        number_input_slider(
            label="Noise Threshold",
            min_value=sidebar_values["noise_threshold"][0],
            max_value=sidebar_values["noise_threshold"][1],
            key="noise_threshold",
            help="""Determines which directly-follows relations are considered noise and filtered out.
            Relations with frequency < threshold × max_relation_frequency will be ignored.""",
        )
        with st.expander("Guidance"):
            st.markdown(
                """
                        - [0.0]: No noise filtering 
                        - [0.1-0.2]: Light noise filtering 
                        - [0.2-0.4]: Moderate noise filtering
                        - [above 0.5]: Aggressive noise filtering """
            )
