import copy
from typing import List

import networkx as nx
import numpy as np

from SLDvec.ordering.intersection import ModelPredictor, get_crop

from .travel import order_curve


def traverse_graph(
    G: nx.Graph,
    terminating_node: List[int],
    image: np.array,
    model: ModelPredictor,
    force_single_line: bool,
) -> List[List[int]]:
    """Order the node of a graph representing a line drawing.

    Args:
        G (nx.Graph): The graph representing the line drawing.
        terminating_node (List[int]): The list of terminating nodes.
        image (np.array): The image of the line drawing.
        model (ModelPredictor): The model used to predict the intersection type.
        force_single_line (bool): If True, tries to force the line to be a single line.

    Raises:
        NotImplementedError: _description_

    Returns:
        List[List[int]]: The list of ordered nodes. Each list in this list represents a stroke.
    """
    # Predict all intersections of degree 4
    for node in G.nodes():
        if G.degree(node) == 4:
            if "intersection_type" not in G.nodes[node]:
                crop = get_crop(G, image, node)
                intersection_type, confidence1, confidence2 = model(crop)
                G.nodes[node]["intersection_type"] = intersection_type
                G.nodes[node]["intersection_confidence_1"] = confidence1
                G.nodes[node]["intersection_confidence_2"] = confidence2

    # Order the nodes
    end_node = terminating_node.copy()
    ordered_node_lists = order_curve(G, end_node)

    # If we don't want to force the output to be made of a single line, we return the result
    if not force_single_line:
        return ordered_node_lists
    else:
        if len(ordered_node_lists) == 1:
            # If the graph is already a single line, we return it
            return ordered_node_lists
        else:
            # Otherwise, we try to force the output to be a single line

            # We get all degree 4 nodes that are common to multiple curves
            # Those nodes are the ones that can be switched to make the graph a single line

            degree_4_node_common_to_multiple_curves = []
            for node in G.nodes():
                if G.degree(node) == 4 and sum([node in curve for curve in ordered_node_lists]) > 1:
                    degree_4_node_common_to_multiple_curves.append(node)

            # The ones with confidence_1 == 1.0 are removed from the list, as they are already
            # correctly classified. The other ones are ordered by increasing confidence
            degree_4_node_common_to_multiple_curves = [
                n
                for n in degree_4_node_common_to_multiple_curves
                if G.nodes[n]["intersection_confidence_1"] < 1.0
                or G.nodes[n]["intersection_confidence_2"] < 0.9
            ]

            degree_4_node_common_to_multiple_curves = sorted(
                degree_4_node_common_to_multiple_curves,
                key=lambda x: [G.nodes[x]["intersection_confidence_2"]],
            )

            # The nodes are switched one by one, starting with the ones with the lowest confidence
            # until the graph is ordered in a single stroke, or all the nodes have been switched
            best_ordered_node_lists = copy.deepcopy(ordered_node_lists)
            best_stroke_number = len(best_ordered_node_lists)
            switch_back_node = []
            for node in degree_4_node_common_to_multiple_curves:
                if G.nodes[node]["intersection_type"] == "crossing":
                    G.nodes[node]["intersection_type"] = "tangent"
                else:
                    G.nodes[node]["intersection_type"] = "crossing"

                end_node = terminating_node.copy()
                ordered_node_lists = order_curve(G, end_node)
                switch_back_node.append(node)
                if len(ordered_node_lists) == 1:
                    return ordered_node_lists

                if len(ordered_node_lists) <= best_stroke_number:
                    best_stroke_number = len(ordered_node_lists)
                    best_ordered_node_lists = copy.deepcopy(ordered_node_lists)
                    switch_back_node = []

            # This nodes were not switched in the best result, so we switch them back
            for node in switch_back_node:
                if G.nodes[node]["intersection_type"] == "crossing":
                    G.nodes[node]["intersection_type"] = "tangent"
                else:
                    G.nodes[node]["intersection_type"] = "crossing"

            return best_ordered_node_lists
