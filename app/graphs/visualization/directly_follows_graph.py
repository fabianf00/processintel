import numpy as np

from app.graphs.visualization.base_graph import BaseGraph


class DirectlyFollowsGraph(BaseGraph):
    """
    Graph representation for directly-follows style visualizations.
    """

    def __init__(self, rankdir: str = "TB") -> None:
        """Initialize a DirectlyFollowsGraph."""
        super().__init__(rankdir=rankdir)

    def add_event(
        self,
        title: str,
        spm: float,
        normalized_frequency: float,
        absolute_frequency: int | None,
        size: tuple[float, float] | None = None,
        shape: str = "box",
        style: str | None = None,
        fillcolor: str = "#FDFFF5",
        label: str | None = None,
        **event_data,
    ) -> None:
        """Add an event to the graph."""
        event_data["SPM value"] = spm
        if absolute_frequency is not None:
            event_data["Frequency *(absolute)*"] = absolute_frequency
        if normalized_frequency is not None:
            event_data["Frequency *(normalized)*"] = normalized_frequency

        freq_label = "" if absolute_frequency is None else absolute_frequency
        final_label = label or f'<{title}<br/><font color="red">{freq_label}</font>>'
        width, height = size if size else (1.5, 0.5)
        node_style = style or ("rounded, filled" if shape == "box" else "filled")

        super().add_node(
            id=title,
            label=final_label,
            data=event_data,
            width=str(width),
            height=str(height),
            shape=shape,
            style=node_style,
            fillcolor=fillcolor,
        )

    def add_empty_circle(self, circle_id: str) -> None:
        """Add an empty circle node to the graph.

        Parameters
        ----------
        circle_id : str
            ID for the circle node
        """
        super().add_node(
            id=circle_id,
            label=" ",
            shape="circle",
            style="filled",
            fillcolor="#E1E1E1",
        )

    def create_edge(
        self,
        source: str,
        destination: str,
        size: float = 1.0,
        normalized_frequency: float | None = None,
        absolute_frequency: int | None = None,
        dependency_score: float | None = None,
        color: str = "black",
        correlation: float | None = None,
        significance: float | None = None,
        average: bool = False,
        **edge_data,
    ) -> None:
        """Create an edge between two nodes with optional metrics."""
        prefix = "Average " if average or color == "red" else ""

        if absolute_frequency is not None:
            edge_data[f"{prefix}Frequency *(absolute)*"] = absolute_frequency
        if normalized_frequency is not None:
            edge_data[f"{prefix}Frequency *(normalized)*"] = normalized_frequency
        if dependency_score is not None:
            edge_data["Dependency score"] = round(dependency_score, 3)
        if significance is not None:
            edge_data[f"{prefix}Binary Significance"] = round(significance, 2)
        if correlation is not None:
            edge_data[f"{prefix}Correlation"] = round(correlation, 2)

        super().add_edge(
            source,
            destination,
            weight=absolute_frequency,
            penwidth=str(size),
            color=color,
            data=edge_data or None,
        )

    def add_cluster(
        self,
        cluster_name: str,
        significance: int | float,
        size: tuple[float, float],
        merged_nodes: list[dict[str, str | int | float]],
        **cluster_data: dict[str, str | int | float],
    ) -> None:
        """Add a cluster node used by the fuzzy miner."""
        abs_freqs = [node.get("abs_freq", 0) for node in merged_nodes]
        avg_abs_freq = round(float(np.mean(abs_freqs))) if abs_freqs else 0
        cluster_data["Average Frequency *(normalized)*/Average Unary Significance"] = (
            significance
        )
        cluster_data["Average Frequency *(absolute)*"] = avg_abs_freq
        cluster_data["Nodes"] = merged_nodes
        width, height = size
        label = f"<{cluster_name}<br/>{len(merged_nodes)} Elements<br/><font color='red'>~{avg_abs_freq}</font>>"
        super().add_node(
            id=cluster_name,
            label=label,
            data=cluster_data,
            shape="octagon",
            style="filled",
            fillcolor="#6495ED",
            width=str(width),
            height=str(height),
        )

    def node_to_string(self, id: str) -> tuple[str, str]:
        """Return string representation; include cluster details when present."""
        node = self.get_node(id)
        data = node.get_data() or {}
        if data.get("Nodes"):
            description = ""
            avg_norm = data.get(
                "Average Frequency *(normalized)*/Average Unary Significance", 0.0
            )
            avg_abs = data.get("Average Frequency *(absolute)*", 0)
            description += f"\n**Average Frequency *(absolute)*:** {avg_abs}"
            description += f"\n**Average Frequency *(normalized)*/Average Unary Significance:** {float(avg_norm):.2f}"
            description += "\n\n**Clustered Nodes:**"
            for merged in data.get("Nodes", []):
                spm = merged.get("spm")
                norm_freq = merged.get("norm_freq")
                spm_str = (
                    f"{float(spm):.2f}" if isinstance(spm, (float, int)) else str(spm)
                )
                norm_freq_str = (
                    f"{float(norm_freq):.2f}"
                    if isinstance(norm_freq, (float, int))
                    else str(norm_freq)
                )
                description += f"\n **{merged.get('id')}**:\n"
                description += f"- SPM value: {spm_str}\n"
                description += f"- Frequency *(absolute)*: {merged.get('abs_freq')}\n"
                description += (
                    f"- Frequency *(normalized)*/Unary Significance: {norm_freq_str}\n"
                )

            return node.get_id(), description

        return super().node_to_string(id)
