from typing import List

import networkx as nx
import numpy as np

from .tangent import get_tangent


def find_T_foot_direction(node: int, G: nx.Graph) -> int:
    """Given a degree 3 node in a graph representing a T-shape intersection of a line drawing, find
    the direction of the foot of the T intersection.

    Args:
        node (int): The degree 3 T-shape node for which to find the direction of the foot.
        G (nx.Graph): The graph to analyze.

    Raises:
        ValueError: If the node does not have 3 neighbors.

    Returns:
        int: The index of the node in the direction of the foot of the T intersection.
    """

    # Find all the neighbors of the node and the tangent in their direction
    neighbors = list(G.neighbors(node))
    if len(neighbors) != 3:
        raise ValueError(f"The node {node} should have 3 neighbors.")

    tangents = {n: get_tangent(G, node, n) for n in neighbors}

    # Compute the cosine distance between all the tangents
    cosines = np.zeros([len(neighbors), len(neighbors)])
    for i, n1 in enumerate(neighbors):
        for j, n2 in enumerate(neighbors):
            cosines[i, j] = np.dot(tangents[n1], tangents[n2])

    # Find the neighbors that is the less aligned with the others (in opposite directions)
    idx = np.argmin(cosines)
    i, j = np.unravel_index(idx, cosines.shape)
    other = [x for x in range(3) if x not in [i, j]][0]

    return neighbors[other]


def find_T_bar_directions(node: int, G: nx.Graph) -> List[int]:
    """Given a degree 3 node in a graph representing a T-shape intersection of a line drawing, find
    the directions of the two bars of the T intersection.

    Args:
        node (int): The degree 3 T-shape node for which to find the directions of the bars.
        G (nx.Graph): The graph to analyze.

    Raises:
        ValueError: If the node does not have 3 neighbors.

    Returns:
        List[int]: The indices of the nodes in the direction of the bars of the T intersection.
    """
    # Find all the neighbors of the node and the tangent in their direction
    neighbors = list(G.neighbors(node))
    if len(neighbors) != 3:
        raise ValueError(f"The node {node} should have 3 neighbors.")

    tangents = {n: get_tangent(G, node, n) for n in neighbors}

    # Compute the cosine distance between all the tangents
    cosines = np.zeros([len(neighbors), len(neighbors)])
    for i, n1 in enumerate(neighbors):
        for j, n2 in enumerate(neighbors):
            cosines[i, j] = np.dot(tangents[n1], tangents[n2])

    # Find the two neighbors that are the most aligned (in opposite directions)
    idx = np.argmin(cosines)
    i, j = np.unravel_index(idx, cosines.shape)

    return [neighbors[i], neighbors[j]]
