import itertools

from graphs.visualization import PetriNetGraph
from graphs.petri_net import add_petri_net_to_graph


class InductiveGraphConverter:
    """
    Converts an inductive mining BPMN/process tree result into a Petri net graph.
    """
    def bpmn_to_petri_net(self, miner, process_tree, node_stats_map):
        toolkit = miner.petri_toolkit
        net, start_place, end_place = toolkit.create_base_net()
        place_counter = itertools.count()
        tau_counter = itertools.count()

        def new_place(prefix):
            place_id = f"p_im_{prefix}_{next(place_counter)}"
            toolkit.register_place(place_id)
            return place_id

        def new_tau(prefix):
            return f"tau_im_{prefix}_{next(tau_counter)}"

        def connect_places(source_place, target_place, prefix):
            # Connect two places by inserting a silent between
            tau_id = new_tau(prefix)
            toolkit.register_transition(tau_id, visible=False)
            toolkit.add_arc(source_place, tau_id)
            toolkit.add_arc(tau_id, target_place)

        def register_visible_transition(label):
            base = str(label)
            trans_id = base
            suffix = 1
            while trans_id in net["transitions"]:  # If multiple transitions have the same label -> append incrementing suffix
                suffix += 1
                trans_id = f"{base}__{suffix}"
            toolkit.register_transition(trans_id, visible=True, label=base)
            return trans_id

        def build_fragment(tree, entry_override=None, exit_override=None):
            if isinstance(tree, (str, int)):
                label = str(tree)
                # Create entry and exit places for the leaf
                entry = entry_override or new_place("leaf_in")
                exit_place = exit_override or new_place("leaf_out")
                if label == "tau":
                    trans_id = new_tau("silent")
                    toolkit.register_transition(trans_id, visible=False)
                else:
                    trans_id = register_visible_transition(label)
                toolkit.add_arc(entry, trans_id)
                toolkit.add_arc(trans_id, exit_place)
                return entry, exit_place

            if not isinstance(tree, tuple) or not tree:
                raise ValueError("Invalid process tree node")

            op = tree[0]
            children = tree[1:]

            if op == "seq":
                if not children:
                    raise ValueError("Rrequires at least one child")

                entry = None
                previous_exit = None

                for idx, child in enumerate(children):
                    # Reuse the previous fragment's exit as the next entry -> avoid extra silent transitions between steps
                    forced_entry = entry_override if idx == 0 else previous_exit
                    forced_exit = exit_override if idx == len(children) - 1 else None
                    child_entry, child_exit = build_fragment(child, forced_entry, forced_exit)
                    if entry is None:
                        entry = child_entry
                    previous_exit = child_exit
                return entry, previous_exit

            if op == "xor":
                entry = entry_override or new_place("xor_in")
                exit_place = exit_override or new_place("xor_out")
                join_id = new_tau("xor_join")
                toolkit.register_transition(join_id, visible=False)
                
                # XOR marker on the place where branches split/join
                toolkit.register_gateway(entry, "xor", "split")
                toolkit.register_gateway(exit_place, "xor", "join")

                for child in children:
                    child_entry, child_exit = build_fragment(child)
                    branch_id = new_tau("xor_branch")
                    toolkit.register_transition(branch_id, visible=False)
                    toolkit.add_arc(entry, branch_id)
                    toolkit.add_arc(branch_id, child_entry)
                    toolkit.add_arc(child_exit, join_id)
                toolkit.add_arc(join_id, exit_place)
                return entry, exit_place

            if op == "par":  # Parallel (AND)
                entry = entry_override or new_place("par_in")
                exit_place = exit_override or new_place("par_out")
                # Explicit split and join silent transitions.
                split_id = new_tau("par_split")
                join_id = new_tau("par_join")

                toolkit.register_transition(split_id, visible=False)
                toolkit.register_transition(join_id, visible=False)
                toolkit.add_arc(entry, split_id)
                toolkit.add_arc(join_id, exit_place)

                # Each parallel branch connects to split and join
                for child in children:
                    child_entry, child_exit = build_fragment(child)
                    # Mark first place of each AND branch
                    toolkit.register_gateway(child_entry, "and", "split")
                    toolkit.add_arc(split_id, child_entry)
                    toolkit.add_arc(child_exit, join_id)
                    # Mark last place before join
                    toolkit.register_gateway(child_exit, "and", "join")
                return entry, exit_place

            if op == "loop":
                if not children:
                    raise ValueError("Requires at least one child")
                entry = entry_override or new_place("loop_in")
                exit_place = exit_override or new_place("loop_out")

                # First child is loop body
                body_entry, body_exit = build_fragment(children[0], entry_override=entry)

                connect_places(body_exit, exit_place, "loop_exit")

                # If the redo branch is only tau, collapse it to one back edge instead of building a full silent fragment
                if len(children) == 2 and children[1] == "tau":
                    back_id = new_tau("loop_back")
                    toolkit.register_transition(back_id, visible=False)
                    toolkit.add_arc(body_exit, back_id)
                    toolkit.add_arc(back_id, body_entry)
                    return entry, exit_place

                # Remaining childs are redo/return branches
                for redo in children[1:]:
                    redo_entry, redo_exit = build_fragment(redo)
                    connect_places(body_exit, redo_entry, "loop_redo_in")
                    connect_places(redo_exit, body_entry, "loop_redo_back")
                return entry, exit_place

            raise ValueError(f"Unsupported process tree operator: {op}")

        # Build root fragment and connect it to global start and end places
        if process_tree:
            build_fragment(process_tree, entry_override=start_place, exit_override=end_place)
        else:
            # Empty model -> direct connection between start and end
            toolkit.add_arc(start_place, end_place)

        toolkit.finalize_net(net)
        miner.petri_net = net

        graph = PetriNetGraph()
        graph.add_start_node()
        graph.add_end_node()
        add_petri_net_to_graph(
            graph,
            net,
            miner.filtered_events,
            node_stats_map,
            miner.filtered_appearance_freqs,
            logger=miner.logger,
        )
        return graph
