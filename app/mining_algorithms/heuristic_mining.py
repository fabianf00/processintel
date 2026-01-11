import numpy as np

from app.converters.dfg_converter import DFGConverter, HeuristicDFGData
from app.logger import get_logger
from app.mining_algorithms.base_mining import BaseMining


class HeuristicMining(BaseMining):
    def __init__(self, log):
        super().__init__(log)
        self.logger = get_logger("HeuristicMining")

        self.dependency_matrix = {}
        self.graph_converter = DFGConverter()

        # Graph modifiers
        self.dependency_threshold = 0.5
        self.min_edge_thickness = 2

    def generate_graph(
        self,
        spm_threshold,
        node_freq_threshold_normalized,
        node_freq_threshold_absolute,
        edge_freq_threshold_normalized,
        edge_freq_threshold_absolute,
        dependency_threshold,
    ):
        self.start_nodes = self._get_start_nodes()
        self.end_nodes = self._get_end_nodes()

        self.spm_threshold = spm_threshold
        self.node_freq_threshold_normalized = node_freq_threshold_normalized
        self.node_freq_threshold_absolute = node_freq_threshold_absolute
        self.edge_freq_threshold_normalized = edge_freq_threshold_normalized
        self.edge_freq_threshold_absolute = edge_freq_threshold_absolute
        self.dependency_threshold = dependency_threshold

        self.recalculate_model_filters()
        self.dependency_matrix = self.__create_dependency_matrix()

        dependency_graph = self.__create_dependency_graph(dependency_threshold)

        node_stats_map = {stat["node"]: stat for stat in self.get_node_statistics()}

        if not self.filtered_events:
            self.graph = self.graph_converter.build_empty_graph(rankdir="TB")
            return

        node_sizes = {
            node: self.calculate_node_size(node) for node in self.filtered_events
        }
        edge_stats = self.get_edge_statistics()
        edge_stats_map = {(edge["source"], edge["target"]): edge for edge in edge_stats}

        data = HeuristicDFGData(
            dependency_graph=dependency_graph,
            dependency_matrix=self.dependency_matrix,
            filtered_events=list(self.filtered_events),
            filtered_appearance_freqs=self.filtered_appearance_freqs,
            node_sizes=node_sizes,
            start_nodes=set(self.start_nodes),
            end_nodes=set(self.end_nodes),
            node_stats_map=node_stats_map,
            edge_stats_map=edge_stats_map,
            min_edge_thickness=self.min_edge_thickness,
            edge_scale_factor=self.get_edge_scale_factor,
            get_sources=self.__get_sources_from_dependency_graph,
            get_sinks=self.__get_sinks_from_dependency_graph,
        )

        self.graph, self.start_nodes, self.end_nodes = (
            self.graph_converter.build_heuristic_graph(data)
        )

    def get_threshold(self):
        return self.dependency_threshold

    def __create_dependency_matrix(self):
        dependency_matrix = np.zeros(self.filtered_succession_matrix.shape)
        np.fill_diagonal(dependency_matrix, 1.0)

        non_diagonal_indices = np.where(dependency_matrix == 0)
        diagonal_indices = np.diag_indices(dependency_matrix.shape[0])

        dependency_matrix[diagonal_indices] = self.filtered_succession_matrix[
            diagonal_indices
        ] / (self.filtered_succession_matrix[diagonal_indices] + 1)

        x, y = non_diagonal_indices

        dependency_matrix[x, y] = (
            self.filtered_succession_matrix[x, y]
            - self.filtered_succession_matrix[y, x]
        ) / (
            self.filtered_succession_matrix[x, y]
            + self.filtered_succession_matrix[y, x]
            + 1
        )
        return dependency_matrix

    def __create_dependency_graph(self, dependency_threshold):
        dependency_graph = np.zeros(self.dependency_matrix.shape)

        filter_matrix = (self.filtered_succession_matrix > 0) & (
            self.dependency_matrix >= dependency_threshold
        )

        for i, j in zip(*np.where(filter_matrix)):
            if self.filter_edge(self.filtered_events[i], self.filtered_events[j]):
                dependency_graph[i, j] = 1.0

        return dependency_graph

    def __get_sources_from_dependency_graph(self, dependency_graph):
        indices = self.__get_all_axis_with_all_zero(dependency_graph, axis=0)
        return set([self.filtered_events[i] for i in indices])

    def __get_sinks_from_dependency_graph(self, dependency_graph):
        indices = self.__get_all_axis_with_all_zero(dependency_graph, axis=1)
        return set([self.filtered_events[i] for i in indices])

    def __get_all_axis_with_all_zero(self, dependency_graph, axis=0):
        filter_matrix = dependency_graph == 0
        # edges from and to the same node are not considered
        np.fill_diagonal(filter_matrix, True)
        return np.where(filter_matrix.all(axis=axis))[0]
