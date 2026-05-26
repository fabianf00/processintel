import unittest

from app.converters.bpmn_converter import BPMNConverter, InductiveBPMNData


class BPMNConverterTest(unittest.TestCase):
    def setUp(self):
        self.bpmn_converter = BPMNConverter()

    def test_build_inductive_graph_with_empty_filtered_events(self):
        """Test that empty filtered events create a Start to End BPMN graph."""
        empty_data = InductiveBPMNData(
            process_tree=None,
            filtered_events=set(),
            filtered_appearance_freqs={},
            node_sizes={},
            node_stats_map={},
        )
        graph = self.bpmn_converter.build_inductive_graph(empty_data)

        self.assertTrue(graph.contains_node("Start"))
        self.assertTrue(graph.contains_node("End"))
        self.assertTrue(graph.contains_edge("Start", "End"))


if __name__ == "__main__":
    unittest.main()
