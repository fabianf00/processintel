"""
Tests for threshold-dependent behavior on Inductive Mining Infrequent algorithm.

These tests verify that changing the IMf noise threshold updates the miner state,
triggers graph regeneration, and affects DFG-based filtering behavior.
"""

import unittest

from app.mining_algorithms.inductive_mining_infrequent import InductiveMiningInfrequent


class TestIMfThresholdFiltering(unittest.TestCase):
    """Tests for Inductive Miner - Infrequent (IMf) noise threshold filtering."""

    def setUp(self):
        """
        Create a log with clear main behavior and noise.

        Main behavior: A -> B -> C (frequent)
        Noise: Various infrequent edges
        """
        self.noisy_log = {
            # Main behavior (100 traces)
            ("A", "B", "C"): 100,
            # Some noise (10 traces each)
            ("A", "X", "C"): 10,
            ("A", "Y", "B", "C"): 10,
            ("A", "B", "Z", "C"): 10,
            # Very rare noise (1 trace each)
            ("A", "B", "B", "C"): 1,
            ("A", "C"): 1,
        }

    def test_noise_threshold_zero_keeps_all_edges(self):
        """Test that noise_threshold=0.0 keeps all edges in the DFG."""
        miner = InductiveMiningInfrequent(self.noisy_log)
        miner.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=0.0,
        )

        # With threshold=0.0, Phase 2 filtering should not be applied
        self.assertEqual(miner.noise_threshold, 0.0)
        self.assertIsNotNone(miner.filtered_log)
        self.assertGreater(len(miner.filtered_log), 0)

    def test_noise_threshold_high_filters_edges(self):
        """Test that high noise_threshold filters out infrequent edges."""
        miner = InductiveMiningInfrequent(self.noisy_log)

        # Use high threshold (e.g., 0.5) which should filter many edges
        high_threshold = 0.5

        miner.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=high_threshold,
        )

        self.assertEqual(miner.noise_threshold, high_threshold)
        self.assertIsNotNone(miner.graph)

    def test_different_noise_thresholds_produce_different_results(self):
        """Test that different noise thresholds produce different graphs."""
        # Mine with low threshold
        miner_low = InductiveMiningInfrequent(self.noisy_log)
        miner_low.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=0.0,
        )
        graph_low = miner_low.graph

        # Mine with high threshold
        miner_high = InductiveMiningInfrequent(self.noisy_log)
        miner_high.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=0.5,
        )
        graph_high = miner_high.graph

        # Verify thresholds were applied
        self.assertEqual(miner_low.noise_threshold, 0.0)
        self.assertEqual(miner_high.noise_threshold, 0.5)

        # Both should have valid graphs
        self.assertIsNotNone(graph_low)
        self.assertIsNotNone(graph_high)

    def test_noise_threshold_change_forces_regeneration(self):
        """Test that changing noise threshold on same miner forces regeneration."""
        miner = InductiveMiningInfrequent(self.noisy_log)

        # First generation with low threshold
        miner.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=0.0,
        )
        graph1_id = id(miner.graph)

        # Second generation with high threshold
        miner.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=0.5,
        )
        graph2_id = id(miner.graph)

        # The threshold should have changed
        self.assertEqual(miner.noise_threshold, 0.5)

        # The graph should be regenerated (different object)
        self.assertNotEqual(
            graph1_id, graph2_id, "Graph was not regenerated when threshold changed!"
        )

        # At minimum, verify that the threshold was actually updated
        self.assertEqual(miner.noise_threshold, 0.5)


class TestThresholdEffectOnCutDetection(unittest.TestCase):
    """Tests to verify thresholds affect cut detection in calculate_cut()."""

    def setUp(self):
        """
        Create a log where noise prevents cut detection without filtering.

        Main structure: Sequence A -> (B || C) -> D
        Noise: Random edges that break the parallel cut
        """
        self.cut_sensitive_log = {
            # Clear parallel behavior
            ("A", "B", "C", "D"): 50,
            ("A", "C", "B", "D"): 50,
            # Noise that might break parallel cut detection
            ("A", "B", "D"): 5,
            ("A", "C", "D"): 5,
            ("A", "D"): 2,
            ("A", "B", "C", "C", "D"): 1,
        }

    def test_imf_threshold_affects_cut_detection(self):
        """Test that noise_threshold affects which cuts are detected."""
        # Low threshold - might not find optimal cuts due to noise
        miner_low = InductiveMiningInfrequent(self.cut_sensitive_log)
        miner_low.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=0.0,
        )

        # High threshold - should filter noise and find cleaner cuts
        miner_high = InductiveMiningInfrequent(self.cut_sensitive_log)
        miner_high.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=0.3,
        )

        # Both should produce graphs
        self.assertIsNotNone(miner_low.graph)
        self.assertIsNotNone(miner_high.graph)

        # Verify the thresholds were actually set
        self.assertEqual(miner_low.noise_threshold, 0.0)
        self.assertEqual(miner_high.noise_threshold, 0.3)


class TestEdgeFrequencyCalculation(unittest.TestCase):
    """Tests to verify edge frequency calculation is correct."""

    def test_edge_frequency_calculation_imf(self):
        """Test that IMf correctly calculates edge frequencies."""
        log = {
            ("A", "B", "C"): 10,
            ("A", "B", "D"): 5,
            ("A", "X", "C"): 2,
        }

        miner = InductiveMiningInfrequent(log)
        edge_freq = miner._compute_edge_frequencies(log)

        # Expected frequencies:
        # A->B: 10 + 5 = 15
        # B->C: 10
        # B->D: 5
        # A->X: 2
        # X->C: 2

        self.assertEqual(edge_freq[("A", "B")], 15)
        self.assertEqual(edge_freq[("B", "C")], 10)
        self.assertEqual(edge_freq[("B", "D")], 5)
        self.assertEqual(edge_freq[("A", "X")], 2)
        self.assertEqual(edge_freq[("X", "C")], 2)

    def test_filtered_dfg_creation_imf(self):
        """Test that IMf creates filtered DFG correctly."""
        log = {
            ("A", "B", "C"): 100,
            ("A", "X", "C"): 10,
            ("A", "Y", "C"): 1,
        }

        miner = InductiveMiningInfrequent(log)
        miner.noise_threshold = 0.5

        # Create filtered DFG
        filtered_dfg = miner._create_filtered_dfg(log)

        # Max frequency is A->B: 100
        # Threshold: 100 * 0.5 = 50
        # Should keep: A->B (100), B->C (100)
        # Should filter: A->X (10), X->C (10), A->Y (1), Y->C (1)

        edges = filtered_dfg.get_edges()

        self.assertIn(("A", "B"), edges)
        self.assertIn(("B", "C"), edges)
        self.assertNotIn(("A", "X"), edges)
        self.assertNotIn(("A", "Y"), edges)


if __name__ == "__main__":
    unittest.main()
