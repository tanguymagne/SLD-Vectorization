from typing import List

import networkx as nx
import numpy as np
from numba import jit
from numba.typed import List as nbList

from SLDvec.utils.networkx import get_path_from_degree_1_node_to_crossroad


@jit(nopython=True)
def filter(main_list, to_remove):
    return [
        x
        for i, x in enumerate(main_list)
        if (x not in to_remove or i == 0 or i == len(main_list) - 1)
    ]


def filter_points(G: nx.Graph, terminating_node: List[int], node_list: List[int]):
    """Filter some points in order to have a better set of points to fit a curve on.
    The function removes the following points:
    - The points that are too close to a crossing node, that is for all neighbors of a crossing
        node, create a circle of radius equal to the distance to border of the shape and remove all
        the points that are inside the circle.
    - The points that are between a non ending single neighbor node and a crossing node.

    Also split the path at the single neighbor node that are non ending.

    Args:
        G (nx.Graph): The graph corresping to the line drawing.
        terminating_node (List[int]): The list of terminating nodes.
        node_list (List[int]): The list of node representing one stroke, ordered.

    Returns:
        List[List[int]]: The list of node representing one stroke, ordered, filtered and split when
            needed.
    """
    # Remove the points that are too close to a crossing node
    # Also remove the nodes that are between a non ending single neighbor node and a crossing node
    all_node_pos = np.array([G.nodes[n]["pos"] for n in G.nodes()])
    all_node = list(G.nodes())

    # Get the nodes to remove and the ones where we need to split the curve at
    to_remove = set()
    split_at = []
    for node in node_list:
        if G.degree[node] > 2:
            # Remove points that are too close to a neighbor of a crossroad node
            for n in G.neighbors(node):
                dist = G.nodes[n]["dist"] if "dist" in G.nodes[n] else 0

                # First find all the nodes that are close enough, that is the node inside the square
                infinite_norm = np.max(np.abs(all_node_pos - G.nodes[n]["pos"][None, :]), axis=1)
                close_enough = np.where(infinite_norm < dist)[0]

                # Then find the nodes that are inside the circle
                l2_norm = np.linalg.norm(
                    all_node_pos[close_enough] - G.nodes[n]["pos"][None, :], axis=1
                )
                close = close_enough[l2_norm < dist]

                to_remove.update([all_node[idx] for idx in close])

        if G.degree[node] == 1 and node not in terminating_node:
            # Remove points that are between a non ending single neighbor node and a crossing node
            # Also split the path at the single neighbor node
            branch_to_remove = get_path_from_degree_1_node_to_crossroad(G, node)[1:]
            to_remove.update(branch_to_remove)

            split_at.append(node)

    # Keep the nodes at intersection only if the intersection is crossing
    for node in node_list:
        if G.degree[node] == 4 and G.nodes[node]["intersection_type"] == "tangent":
            to_remove.add(node)
    # Keep the node where we need to split the curve at
    for node in split_at:
        if node in to_remove:
            to_remove.discard(node)

    # Remove the nodes from the list
    if len(to_remove) == 0:
        node_list_filtered_ = node_list
    else:
        to_remove_list_nb = nbList(to_remove)
        node_list_nb = nbList(node_list)
        node_list_filtered_ = filter(node_list_nb, to_remove_list_nb)

    # Split the path at the degree 1 node
    node_list_filtered_split = []
    i = 0
    while i < len(node_list_filtered_):
        if node_list_filtered_[i] in split_at:
            new_split_to_add = node_list_filtered_[: i + 1]
            if len(new_split_to_add) > 4:
                node_list_filtered_split.append(new_split_to_add)
            node_list_filtered_ = node_list_filtered_[i:]
            i = 0
        i += 1
    if len(node_list_filtered_) > 4:
        node_list_filtered_split.append(node_list_filtered_)

    return node_list_filtered_split
