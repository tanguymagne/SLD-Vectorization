from typing import List

import networkx as nx
import numpy as np

from .filter import filter_points
from .fit import fit_curve


def fit_all_curves(
    G: nx.Graph, terminating_node: List[int], node_lists: List[List[int]]
) -> np.array:
    """Fit bezier curves to all the ordered stroke of a line drawing.

    Args:
        G (nx.Graph): The graph representing the line drawing.
        terminating_node (List[int]): The list of detected terminating nodes.
        node_lists (List[List[int]]): The list of ordered nodes representing the strokes.

    Returns:
        np.array: The list of bezier curves representing the strokes.
    """
    # Filter and split the strokes
    node_lists_filtered_split = [
        filter_points(G, terminating_node, node_list) for node_list in node_lists
    ]
    node_lists_filtered_split = [x for x in node_lists_filtered_split if x != [[]] and x != []]

    # Get the position of the nodes
    all_ordered_points = []
    for node_list_filtered_split in node_lists_filtered_split:
        all_ordered_points.append(
            [
                np.array([G.nodes[node]["pos"] for node in split])
                for split in node_list_filtered_split
            ]
        )

    # Fit the curves
    bezier_spline = [fit_curve(all_ordered_point) for all_ordered_point in all_ordered_points]

    return bezier_spline
