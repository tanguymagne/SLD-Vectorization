from typing import List

import networkx as nx
import numpy as np

from .endpoint import find_terminating_node
from .intersection import ModelPredictor, get_predictor
from .traversal import traverse_graph

__all__ = ["get_predictor"]


def get_stroke_order(
    G: nx.Graph, image: np.array, model: ModelPredictor, force_single_line: bool = False
) -> List[List[int]]:
    """Obtain the list of ordered nodes representing the strokes of a line drawing.

    Args:
        G (nx.Graph): The graph representing the line drawing.
        image (np.array): The image of the line drawing.
        model (ModelPredictor): The model used to predict the intersection type.
        force_single_line (bool, optional): Wheter to force the output to contain a single stroke.
            Defaults to False.

    Returns:
        List[List[int]]: The list of stroke, represented as a list of node indices.
    """
    if "terminating_node" not in G.graph:
        terminating_node = find_terminating_node(G, force_single_line)
        G.graph["terminating_node"] = terminating_node
    else:
        terminating_node = G.graph["terminating_node"]

    node_lists = traverse_graph(G, terminating_node, image, model, force_single_line)
    return node_lists, terminating_node
