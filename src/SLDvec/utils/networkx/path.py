from typing import List

import networkx as nx


def get_path_from_degree_1_node_to_crossroad(G: nx.Graph, node: int) -> List[int]:
    """Find the path from a node with a single neighbor to the closest crossroad node (node with 3
    or more neighbors).
    If there the path is a loop, the function will return the loop.
    If the path is a simple line without crossroads, the function will return the line.

    Args:
        G (nx.Graph): The graph to analyze.
        node (int): The node with only one neighbor to start from.

    Raises:
        ValueError: If the original node has more than one neighbor.

    Returns:
        List[int]: A list of nodes from the single neighbor node to the crossroad.
    """
    # Check that the node has only one neighbor
    neighbors = list(G.neighbors(node))
    if len(neighbors) != 1:
        raise ValueError(f"The node {node} should have only one neighbor.")

    # Initialize the path to the crossroad with the node and its neighbor
    original_node = node
    path_to_crossroad = [node]
    node = neighbors[0]
    path_to_crossroad.append(node)

    # Follow the path until a crossroad is found or the path is a loop
    neighbors = list(G.neighbors(node))
    while len(neighbors) == 2 and node != original_node:
        for n in neighbors:
            if n not in path_to_crossroad:
                path_to_crossroad.append(n)
                node = n
                neighbors = list(G.neighbors(n))
                break

    return path_to_crossroad


def get_path_to_crossroad_node(G: nx.Graph, node: int, direction: int) -> List[int]:
    """Find the path between a given node and the closest crossroad node, in a given node direction.
    A crossroad is a node with 3 or more neighbors, or a dead end.

    Args:
        G (nx.Graph): The graph to analyze.
        node (int): The starting node.
        direction (int): The direction node, it should be a node adjacent to the starting node.

    Raises:
        ValueError: If the direction node is not a neighbor of the starting node.

    Returns:
        List[int]: A list of nodes from the starting node to the non-route node.
    """
    # Check that the direction node is a neighbor of the starting node
    if direction not in G.neighbors(node):
        raise ValueError(f"The node {direction} should be a neighbor of the node {node}.")

    # Initialize the path to the non-route node with the node and the direction node
    path_to_crossroad = [node, direction]

    # Follow the path until a crossroad node is found or the path is a loop
    neighbors = list(G.neighbors(direction))
    while len(neighbors) == 2:
        for n in neighbors:
            if n not in path_to_crossroad:
                path_to_crossroad.append(n)
                neighbors = list(G.neighbors(n))
                break

        if len(path_to_crossroad) > 1 and any([n == path_to_crossroad[0] for n in neighbors]):
            # Avoid infinite loop in the case the path is a loop
            path_to_crossroad.append(path_to_crossroad[0])
            break
    return path_to_crossroad
