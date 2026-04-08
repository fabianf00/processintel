import unittest

from app.mining_algorithms.inductive_mining import InductiveMining
from tests.utils.process_tree_utils import isProcessTreeEqual


class TestInductiveMiner(unittest.TestCase):

    def test_inductive_mining_with_only_one_cut(self):
        log = {(1, 2, 3): 6}

        inductive_mining = InductiveMining(log)
        result = inductive_mining.inductive_mining(log)

        self.assertTrue(isProcessTreeEqual(result, ("seq", 1, 2, 3)))

    def test_inductive_miner_with_multiple_cuts(self):
        log = {
            (1, 2, 3, 4): 2,
            (1, 3, 2, 4): 5,
            (1, 2, 3, 5, 6, 2, 3, 4): 3,
            (1, 3, 2, 5, 6, 3, 2, 4): 1,
        }

        inductive_mining = InductiveMining(log)
        result = inductive_mining.inductive_mining(log)

        expected_tree = ("seq", 1, ("loop", ("par", 2, 3), ("seq", 5, 6)), 4)

        self.assertTrue(isProcessTreeEqual(result, expected_tree))

    def test_inductive_miner_fallthrough_with_empty_sublog(self):
        log = {(1, 2, 3): 2, (1, 3): 1, (): 1}

        inductive_mining = InductiveMining(log)
        result = inductive_mining.inductive_mining(log)

        expected_tree = ("xor", "tau", ("seq", 1, ("xor", "tau", 2), 3))

        self.assertTrue(isProcessTreeEqual(result, expected_tree))

    def test_fallthrough_with_one_event_more_than_once_in_trace(self):
        log = {(1,): 1, (1, 1, 1): 5, (1, 1): 1}

        inductive_mining = InductiveMining(log)
        result = inductive_mining.inductive_mining(log)

        self.assertTrue(isProcessTreeEqual(result, ("loop", 1, "tau")))

    def test_flower_model_fallthrough(self):
        log = {(1, 2, 3): 1, (2, 3, 1): 1}

        inductive_mining = InductiveMining(log)
        result = inductive_mining.inductive_mining(log)

        expected_tree = ("loop", "tau", 1, 2, 3)

        self.assertTrue(isProcessTreeEqual(result, expected_tree))

    def test_inductive_miner_with_test_csv(self):
        log = {
            ("a", "e"): 5,
            ("a", "b", "c", "e"): 10,
            ("a", "c", "b", "e"): 10,
            ("a", "b", "e"): 1,
            ("a", "c", "e"): 1,
            ("a", "d", "e"): 10,
            ("a", "d", "d", "e"): 2,
            ("a", "d", "d", "d", "e"): 1,
        }

        inductive_mining = InductiveMining(log)
        result = inductive_mining.inductive_mining(log)

        expected_tree = (
            "seq",
            "a",
            (
                "xor",
                "tau",
                (
                    "xor",
                    ("loop", "d", "tau"),
                    ("par", ("xor", "tau", "b"), ("xor", "tau", "c")),
                ),
            ),
            "e",
        )
        self.assertTrue(isProcessTreeEqual(result, expected_tree))


if __name__ == "__main__":
    unittest.main()
