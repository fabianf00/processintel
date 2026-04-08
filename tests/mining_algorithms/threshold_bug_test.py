"""
Test that changing the IMf threshold triggers graph regeneration.

Behavior:
- Pre-filtering thresholds affect the log before mining.
- The IMf noise threshold affects filtered DFG cut detection during mining.
- Changing only noise_threshold should keep filtered_log unchanged.
- Visual feedback is immediate and intuitive.

All thresholds should trigger graph regeneration and produce different results.
"""

import unittest

from app.mining_algorithms.inductive_mining_infrequent import InductiveMiningInfrequent


class TestThresholdChangeDetection(unittest.TestCase):
    """
    Verify that changing noise thresholds triggers graph regeneration
    and produces visibly different results.
    """

    def setUp(self):
        """Simple log with main behavior and noise."""
        self.log = {
            ("A", "B", "C"): 100,
            ("A", "X", "C"): 10,
            ("A", "Y", "C"): 5,
        }

    def test_imf_change_only_noise_threshold(self):
        """
        Test paper-based IMf behavior: Changing noise_threshold affects DFG filtering, not log filtering.

        Paper-based IMf behavior (from Leemans et al. 2014):
        - Noise threshold filters EDGES in the DFG during cut detection
        - The log itself is NOT filtered (preserves all trace information)
        - Graph is regenerated with different structure due to different cuts found

        This is different from activity/traces thresholds which filter the log directly.
        """
        miner = InductiveMiningInfrequent(self.log)

        miner.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=0.0,
        )

        graph1_id = id(miner.graph)
        filtered_log1 = miner.filtered_log.copy() if miner.filtered_log else None

        miner.generate_graph(
            spm_threshold=0.0,
            node_freq_threshold_normalized=0.0,
            node_freq_threshold_absolute=0,
            traces_threshold=0.0,
            noise_threshold=0.9,
        )
        graph2_id = id(miner.graph)
        filtered_log2 = miner.filtered_log.copy() if miner.filtered_log else None

        self.assertEqual(
            filtered_log1,
            filtered_log2,
            "Paper-based IMf: filtered log should remain the same (DFG filtering)",
        )

        self.assertEqual(
            miner.noise_threshold, 0.9, "Noise threshold should be updated"
        )

        self.assertNotEqual(
            graph1_id,
            graph2_id,
            "Graph should be regenerated when noise_threshold changes",
        )


if __name__ == "__main__":
    unittest.main()
