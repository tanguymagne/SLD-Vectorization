from typing import List

import networkx as nx
import numpy as np

from SLDvec.utils.networkx import (
    annotate_crossroad_linked_to_single_neighbor_node,
    find_T_bar_directions,
    find_T_foot_direction,
)

from .neighbor_order import ClockwiseNeighborCycle, get_next_node


def travel_graph_starting_from(G: nx.Graph, start_from: int, end_nodes: List[int]) -> List[int]:
    # Initialize the list of nodes to visit with the starting node
    travel_node_list = []
    travel_node_list.append(start_from)
    G.nodes[start_from]["visited"] = True

    # Depending on the number of neighbors of the starting node, the second node to visit needs to
    # be chosen carefully
    if len(list(G.neighbors(start_from))) == 3:
        # If the start node has 3 neighbors, it is a T-shaped node, the next node is in the
        # direction of the foot of the T
        next_node = find_T_foot_direction(start_from, G)
        travel_node_list.append(next_node)
        G.nodes[next_node]["visited"] = True
        G.nodes[start_from]["visited_neighbor"] = set([next_node])
    elif len(list(G.neighbors(start_from))) == 2:
        # If the start node has 2 neighbors, it is either a loop component, or actually not the
        # beginning of a stroke. Either way, the next node is the first not already visited neighbor
        neighbors = list(G.neighbors(start_from))
        for n in neighbors:
            if not G.nodes[n]["visited"]:
                travel_node_list.append(n)
                G.nodes[n]["visited"] = True
                break

    # Travel the graph until an end node is reached (or an error occurs)
    terminate = False
    while not terminate:
        current_node = travel_node_list[-1]
        current_neighbors = list(G.neighbors(current_node))

        if len(current_neighbors) == 1:
            if current_node in end_nodes:
                terminate = True
                break

            next_node = current_neighbors[0]

            travel_node_list.append(next_node)
            G.nodes[next_node]["visited"] = True

        elif len(current_neighbors) == 2:
            if current_node in end_nodes:
                # The curve is a loop
                terminate = True
                break

            # One of the neighbor is the previous node, the other is the next node
            # If it's not the case, return the current list
            if travel_node_list[-2] not in current_neighbors:
                # NOTE: this shouldn't happen, it is there to avoid errors and always return
                return travel_node_list
            else:
                current_neighbors.remove(travel_node_list[-2])
                next_node = current_neighbors[0]

            travel_node_list.append(next_node)
            G.nodes[next_node]["visited"] = True

        elif len(current_neighbors) == 3:
            if "direction_to_single" in G.nodes[current_node]:
                # If the "direction_to_single" attribute is present, the node is traversed twice.
                if G.nodes[current_node]["visited_neighbor"] == set():
                    previous_node = travel_node_list[-2]
                    G.nodes[current_node]["visited_neighbor"].add(previous_node)

                    next_node = G.nodes[current_node]["direction_to_single"]
                    G.nodes[current_node]["visited_neighbor"].add(next_node)
                else:
                    for v in G.nodes[current_node]["visited_neighbor"]:
                        current_neighbors.remove(v)

                    if len(current_neighbors) != 1:
                        # NOTE: this shouldn't happen, it is there to avoid errors and always return
                        return travel_node_list
                    next_node = current_neighbors[0]
                    G.nodes[current_node]["visited_neighbor"].add(next_node)
            else:
                # Otherwise the node is not traversed twice and is thus en ending node.
                previous_node = travel_node_list[-2]
                G.nodes[current_node]["visited_neighbor"].add(previous_node)

                best_continous_tangent = find_T_bar_directions(current_node, G)
                try:
                    best_continous_tangent.remove(previous_node)
                    next_node = best_continous_tangent[0]
                except ValueError:
                    terminate = True
                    break

                G.nodes[current_node]["visited_neighbor"].add(next_node)

            travel_node_list.append(next_node)
            G.nodes[next_node]["visited"] = True

        elif len(current_neighbors) == 4:
            previous_node = travel_node_list[-2]
            next_node = get_next_node(current_node, previous_node, G)

            if next_node in G.nodes[current_node]["visited_neighbor"]:
                # NOTE: this shouldn't happen, it is there to avoid errors and always return
                return travel_node_list

            G.nodes[current_node]["visited_neighbor"].add(previous_node)
            G.nodes[current_node]["visited_neighbor"].add(next_node)

            travel_node_list.append(next_node)
            G.nodes[next_node]["visited"] = True

        elif len(current_neighbors) % 2 == 0:
            # If the node has an even number of neighbors, we always cross the node
            next_node = travel_node_list[-2]
            neighbor_cycle = G.nodes[current_node]["neighbor_cycle"]
            for _ in range(len(current_neighbors) // 2):
                next_node = neighbor_cycle.next(next_node)

            travel_node_list.append(next_node)
            G.nodes[next_node]["visited"] = True

        else:
            # If the node has an odd number of neighbors higher than 3, we stop the traversal
            return travel_node_list

    return travel_node_list


def sample_new_starting_degree_2_node(G: nx.Graph) -> int:
    """Given a graph, select an unvisited degree 2 node as a new starting point for the traversal..

    Args:
        G (nx.Graph): The input graph.

    Returns:
        int: The index of the selected node.
    """
    possible_sample = [n for n in G.nodes if G.degree(n) == 2 and not G.nodes[n]["visited"]]

    all_node_pos = np.array([G.nodes[n]["pos"] for n in G.nodes()])
    impossible_sample = set()
    for node in G.nodes:
        if G.degree(node) > 2:
            for n in G.neighbors(node):
                if "dist" in G.nodes[n]:
                    dist = G.nodes[n]["dist"]
                else:
                    print(f"Node {n} has no dist, continue")
                    continue
                # First find all the nodes that are close enough, that is the node inside the square
                infinite_norm = np.max(np.abs(all_node_pos - G.nodes[n]["pos"][None, :]), axis=1)
                close_enough = np.where(infinite_norm < dist)[0]

                # Then remove the nodes that are inside the circle
                l2_norm = np.linalg.norm(
                    all_node_pos[close_enough] - G.nodes[n]["pos"][None, :], axis=1
                )
                close = close_enough[l2_norm < dist]
                impossible_sample.update(close)

    for sample in impossible_sample:
        while sample in possible_sample:
            possible_sample.remove(sample)

    return possible_sample[0]


def order_curve(G: nx.Graph, end_node: List[int]) -> List[List[int]]:
    """Travel the graph and order the nodes until all nodes have been visited.

    Args:
        G (nx.Graph): The graph to traverse.
        end_node (List[int]): The list of detected end nodes.

    Returns:
        List[List[int]]: A list containing all ordered strokes. An ordered stroke is a list of
            ordered nodes.
    """
    # Initialize attributes of the nodes
    for node in G.nodes():
        if G.degree(node) > 2:
            G.nodes[node]["visited_neighbor"] = set()
            G.nodes[node].pop("direction_to_single", None)
            G.nodes[node].pop("is_direct_neighbor_single_neighbor_node", None)
        if G.degree(node) > 2 and G.degree(node) % 2 == 0:
            G.nodes[node]["neighbor_cycle"] = ClockwiseNeighborCycle(node, G)
    annotate_crossroad_linked_to_single_neighbor_node(G, end_node)
    nx.set_node_attributes(G, False, "visited")

    # Travel the graph starting from the detected end nodes
    node_lists = []
    while len(end_node) > 1:
        start_from = end_node.pop(0)
        node_lists.append(travel_graph_starting_from(G, start_from, end_node))
        if node_lists[-1][-1] in end_node:
            end_node.remove(node_lists[-1][-1])

        visited_nodes = np.array(list(nx.get_node_attributes(G, "visited", default=False).values()))
        # print(f"Number of visited nodes: {np.sum(visited_nodes)} / {len(G.nodes)}")

    # While all nodes have not been visited, start from a random node
    visited_nodes = np.array(list(nx.get_node_attributes(G, "visited", default=False).values()))
    while visited_nodes.sum() != len(G.nodes):
        # Select a node that has not been visited yet, and travel starting from it
        start_from = sample_new_starting_degree_2_node(G)
        end_node.append(start_from)
        G.nodes[start_from]["visited"] = True
        node_lists.append(travel_graph_starting_from(G, start_from, end_node))

        if node_lists[-1][-1] == start_from:
            # There is a loop
            end_node.remove(start_from)
        else:
            # No loop, travel again from the same starting node but in the other direction
            if node_lists[-1][-1] in end_node:
                end_node.remove(node_lists[-1][-1])
            new = travel_graph_starting_from(G, start_from, end_node)[::-1][:-1]
            node_lists[-1] = new + node_lists[-1]

            if new[0] in end_node:
                end_node.remove(new[0])

        visited_nodes = np.array(list(nx.get_node_attributes(G, "visited", default=False).values()))
        # print(f"Number of visited nodes: {np.sum(visited_nodes)} / {len(G.nodes)}")
    return node_lists
