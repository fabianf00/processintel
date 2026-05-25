from dataclasses import dataclass
from typing import Any

from app.graphs.visualization import BPMNGraph


@dataclass
class InductiveBPMNData:
    process_tree: Any
    filtered_events: set[str]
    filtered_appearance_freqs: dict[str, int]
    node_sizes: dict[str, tuple[float, float]]
    node_stats_map: dict[str, dict]


class BPMNConverter:

    @staticmethod
    def build_inductive_graph(data: InductiveBPMNData) -> BPMNGraph:
        """Create the BPMNGraph for an inductive miner."""
        if not data.filtered_events:
            return BPMNConverter._build_empty_graph(data)

        return BPMNGraph(
            data.process_tree,
            frequency=data.filtered_appearance_freqs,
            node_sizes=data.node_sizes,
            node_stats_map=data.node_stats_map,
        )

    @staticmethod
    def _build_empty_graph(data: InductiveBPMNData) -> BPMNGraph:
        graph = BPMNGraph(data.filtered_events)
        graph.add_start_node()
        graph.add_end_node()
        graph.add_edge("Start", "End", None)
        return graph
