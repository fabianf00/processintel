from typing import List, Set, cast
from app.graphs.cuts import exclusive_cut, parallel_cut, sequence_cut, loop_cut
from app.graphs.dfg import DFG
from app.logger import get_logger
from app.logs.splits import (
    exclusive_split,
    parallel_split,
    sequence_split,
    loop_split,
)
from app.logs.splits_imf import (
    exclusive_split_imf,
    is_empty_trace_frequent,
    parallel_split_imf,
    is_single_activity_frequent,
    loop_split_imf,
    sequence_split_imf,
)
from app.mining_algorithms.inductive_mining import InductiveMining


class InductiveMiningInfrequent(InductiveMining):

    def __init__(self, log):

        super().__init__(log)
        self.logger = get_logger("InductiveMiningInfrequent")

        self.noise_threshold: float = 0.2
        self._last_noise_threshold: float = -1.0
        self._use_imf_filters: bool = False
        self.logger.info(
            "Initialized IMf (Inductive Miner - Infrequent) with paper-based algorithm"
        )

    def generate_graph(
        self,
        spm_threshold: float,
        node_freq_threshold_normalized: float,
        node_freq_threshold_absolute: int,
        traces_threshold: float = 0.0,
        use_petri_net: bool = False,
        noise_threshold: float = 0.2,
    ):

        self.noise_threshold = max(0.0, min(1.0, noise_threshold))

        return super().generate_graph(
            spm_threshold,
            node_freq_threshold_normalized,
            node_freq_threshold_absolute,
            traces_threshold,
            use_petri_net,
        )

    def inductive_mining(self, log):
        return self._inductive_mining_imf(log)

    def _inductive_mining_imf(self, log):
        if not log:
            return "tau"

        self._use_imf_filters = False

        tree = self._base_cases_imf(log)
        if tree:
            return tree

        if tuple() not in log:
            result = self._try_cuts_standard(log)
            if result:
                operator, sublogs = result
                return (
                    operator,
                    *[self._inductive_mining_imf(sublog) for sublog in sublogs],
                )

        self.logger.debug("Phase 1 failed - applying IMf filters")
        self._use_imf_filters = True

        if tuple() in log:
            return self._handle_empty_trace_imf(log)

        if self.noise_threshold > 0.0:
            if result := self._try_cuts_filtered(log):
                operator, sublogs = result
                self.logger.debug(
                    f"Phase 2 SUCCESS: {operator} cut found with filtering"
                )
                return (
                    operator,
                    *[self._inductive_mining_imf(sublog) for sublog in sublogs],
                )

        return self._fallthrough_imf(log)

    def _base_cases_imf(self, log):
        if not log:
            return "tau"

        if len(log) == 1:
            trace = list(log.keys())[0]

            # Empty trace
            if len(trace) == 0:
                return "tau"

            # Single activity in single trace
            if len(trace) == 1:
                return trace[0]

        # Check for single-activity log (may have multiple traces)
        log_alphabet = self.get_log_alphabet(log)

        if len(log_alphabet) == 1:
            activity = list(log_alphabet)[0]

            # IMPORTANT: If empty traces exist, this is NOT a base case!
            # The empty traces need to be handled via XOR(tau, activity)
            # This is done in _handle_empty_trace_imf, not here
            if tuple() in log:
                return None  # Let the main algorithm handle empty traces

            # Apply IMf filter: check if single activity is appropriate
            if self._use_imf_filters:
                if is_single_activity_frequent(log, self.noise_threshold):
                    self.logger.debug(
                        f"Base case (IMf filter): single activity '{activity}'"
                    )
                    return activity
                else:
                    # Average occurrences too high - need loop model
                    self.logger.debug(
                        f"Base case (IMf filter): '{activity}' needs loop (avg > threshold)"
                    )
                    return None
            else:
                # Check if activity only occurs once per trace
                all_single = all(
                    trace.count(activity) == 1 for trace in log.keys() if trace
                )
                if all_single:
                    return activity

        return None
        # return self.base_cases(log)

    def _handle_empty_trace_imf(self, log):

        if tuple() not in log:
            return None

        if self._use_imf_filters and self.noise_threshold > 0.0:
            if is_empty_trace_frequent(log, self.noise_threshold):
                # Empty trace is frequent - model with XOR(tau, ...)
                self.logger.debug("Empty trace is frequent - using XOR(tau, ...)")
                log_without_empty = {k: v for k, v in log.items() if k != tuple()}
                return ("xor", "tau", self._inductive_mining_imf(log_without_empty))
            else:
                # Empty trace is infrequent - filter it out
                self.logger.debug(
                    "Empty trace is infrequent - filtering and continuing"
                )
                log_without_empty = {k: v for k, v in log.items() if k != tuple()}
                return self._inductive_mining_imf(log_without_empty)
        else:
            # Standard handling (no filter)
            log_without_empty = {k: v for k, v in log.items() if k != tuple()}
            return ("xor", "tau", self._inductive_mining_imf(log_without_empty))

    def _try_cuts_standard(self, log):

        if not log:
            return None

        try:
            dfg = DFG(log)

            # XOR
            if partitions := exclusive_cut(dfg):
                if len(partitions) > 1:
                    sublogs = exclusive_split(log, cast(List[Set[str]], partitions))
                    if self._validate_split(sublogs):
                        return ("xor", sublogs)

            if partitions := sequence_cut(dfg):
                if len(partitions) > 1:
                    sublogs = sequence_split(log, cast(List[Set[str]], partitions))
                    if self._validate_split(sublogs):
                        return ("seq", sublogs)

            if partitions := parallel_cut(dfg):
                if len(partitions) > 1:
                    sublogs = parallel_split(log, cast(List[Set[str]], partitions))
                    if self._validate_split(sublogs):
                        return ("par", sublogs)

            if partitions := loop_cut(dfg):
                if len(partitions) > 1:
                    sublogs = loop_split(log, cast(List[Set[str]], partitions))
                    if self._validate_split(sublogs):
                        return ("loop", sublogs)

        except Exception as e:
            self.logger.error(f"Error in standard cut detection: {e}")

        return None

    def _try_cuts_filtered(self, log):
        self.logger.debug("ENTERED _try_cuts_filtered")
        if not log:
            return None

        try:
            # Create filtered DFG
            filtered_dfg = self._create_filtered_dfg(log)

            if not filtered_dfg.get_nodes():
                self.logger.debug("Filtered DFG has no nodes")
                return None

            # Try cuts with IMf log splitting
            if partitions := exclusive_cut(filtered_dfg):
                if len(partitions) > 1:
                    # Use IMf filtered splitting
                    sublogs = exclusive_split_imf(log, cast(List[Set[str]], partitions))
                    if self._validate_split(sublogs):
                        return ("xor", sublogs)

            if partitions := sequence_cut(filtered_dfg):
                if len(partitions) > 1:
                    # Use IMf filtered splitting (optimal split)
                    sublogs = sequence_split_imf(log, cast(List[Set[str]], partitions))
                    if self._validate_split(sublogs):
                        return ("seq", sublogs)

            if partitions := parallel_cut(filtered_dfg):
                if len(partitions) > 1:
                    # Parallel: no filtering needed
                    sublogs = parallel_split_imf(log, cast(List[Set[str]], partitions))
                    if self._validate_split(sublogs):
                        return ("par", sublogs)

            if partitions := loop_cut(filtered_dfg):
                if len(partitions) > 1:
                    # Use IMf filtered splitting (empty traces for invalid starts/ends)
                    sublogs = loop_split_imf(log, cast(List[Set[str]], partitions))
                    if self._validate_split(sublogs):
                        return ("loop", sublogs)

        except Exception as e:
            self.logger.error(f"Error in filtered cut detection: {e}")

        return None

    def _validate_split(self, splits):

        if not splits or len(splits) < 2:
            return False

        for split in splits:
            for trace in split:
                if trace:  # not emtpy tuple
                    return True

        return False

    def _fallthrough_imf(self, log):
        log_alphabet = self.get_log_alphabet(log)
        # Handle empty trace
        if tuple() in log:
            if self._use_imf_filters:
                return self._handle_empty_trace_imf(log)
            else:
                log_without_empty = {k: v for k, v in log.items() if k != tuple()}
                return ("xor", "tau", self._inductive_mining_imf(log_without_empty))

        # Single activity with repetition -> loop
        if len(log_alphabet) == 1:
            activity = list(log_alphabet)[0]
            # Check if activity repeats in traces
            has_repetition = any(
                trace.count(activity) > 1 for trace in log.keys() if trace
            )
            if has_repetition:
                return ("loop", activity, "tau")
            else:
                return activity

        # Filter infrequent activities from flower model if IMf filters enabled
        if self._use_imf_filters and self.noise_threshold > 0.0:
            # Compute activity frequencies
            activity_freq: dict[str, int] = {}
            for trace, freq in log.items():
                for activity in trace:
                    activity_freq[activity] = activity_freq.get(activity, 0) + freq

            if activity_freq:
                max_freq = max(activity_freq.values())
                cutoff = max_freq * self.noise_threshold

                # Keep only frequent activities
                frequent_activities = {
                    act for act, freq in activity_freq.items() if freq >= cutoff
                }

                if frequent_activities and len(frequent_activities) < len(log_alphabet):
                    self.logger.debug(
                        f"IMf fallthrough: filtering {len(log_alphabet) - len(frequent_activities)} "
                        f"infrequent activities from flower model"
                    )
                    log_alphabet = frequent_activities

        # Flower model
        if len(log_alphabet) == 1:
            return ("loop", list(log_alphabet)[0], "tau")

        return ("loop", "tau", *sorted(log_alphabet))

    def _create_filtered_dfg(self, log) -> DFG:
        self.logger.debug("ENTERED _create_filtered_dfg")

        if not log:
            return DFG()

        # Compute edge frequencies
        edge_freq = self._compute_edge_frequencies(log)

        if not edge_freq:
            return DFG()

        # Calculate threshold
        max_freq = max(edge_freq.values())
        threshold = max_freq * self.noise_threshold

        self.logger.debug(f"Edge filtering: max={max_freq}, threshold={threshold:.2f}")

        # Identify frequent edges and connected nodes
        frequent_edges = []
        connected_nodes: Set[str] = set()

        for (src, tgt), freq in edge_freq.items():
            if freq >= threshold:
                frequent_edges.append((src, tgt))
                connected_nodes.add(src)
                connected_nodes.add(tgt)

        # Create filtered DFG
        filtered_dfg = DFG()

        # Add connected nodes
        for node in connected_nodes:
            filtered_dfg.add_node(node)

        # Add frequent edges
        for src, tgt in frequent_edges:
            filtered_dfg.add_edge(src, tgt)

        # Preserve start/end information
        self._preserve_start_end_nodes(filtered_dfg, log)

        self.logger.debug(
            f"Filtered DFG: {len(connected_nodes)} nodes, {len(frequent_edges)} edges "
            f"(filtered {len(edge_freq) - len(frequent_edges)} edges)"
        )

        return filtered_dfg

    def _compute_edge_frequencies(self, log) -> dict[tuple[str, str], int]:

        edge_freq: dict[tuple[str, str], int] = {}

        for trace, freq in log.items():
            if len(trace) < 2:
                continue

            for i in range(len(trace) - 1):
                edge = (trace[i], trace[i + 1])
                edge_freq[edge] = edge_freq.get(edge, 0) + freq

        return edge_freq

    def _preserve_start_end_nodes(self, dfg: DFG, log: dict[tuple[str, ...], int]):

        try:
            if hasattr(dfg, "start_nodes") and hasattr(dfg, "end_nodes"):
                start_nodes = {trace[0] for trace in log.keys() if trace}
                end_nodes = {trace[-1] for trace in log.keys() if trace}

                # Only include nodes that are in the DFG
                dfg_nodes = set(dfg.get_nodes())
                dfg.start_nodes = start_nodes & dfg_nodes  # type: ignore
                dfg.end_nodes = end_nodes & dfg_nodes  # type: ignore

        except Exception as e:
            self.logger.debug(f"Could not preserve start/end nodes: {e}")
