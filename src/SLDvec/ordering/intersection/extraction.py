import networkx as nx
import numpy as np

from SLDvec.utils.networkx import get_path_to_crossroad_node


def get_all_non_adjacent_node(G: nx.Graph, crossroad_node: int) -> np.array:
    """Given a graph and a crossroad node in the graph, return all the nodes that are not adjacent
    to the crossroad node, that is the nodes that are not connected to the crossroad node through a
    chain of degree 2 nodes.

    Args:
        G (nx.Graph): The input graph.
        crossroad_node (int): The crossroad node in the graph.

    Returns:
        np.array: The position of all the non-adjacent nodes.
    """
    neighbors = list(G.neighbors(crossroad_node))
    adjacent_nodes = [get_path_to_crossroad_node(G, crossroad_node, n) for n in neighbors]
    adjacent_nodes = [x for sublist in adjacent_nodes for x in sublist]
    non_adjacent_nodes = []
    for node in G.nodes():
        if node not in adjacent_nodes and node != crossroad_node:
            non_adjacent_nodes.append(node)
    return np.array(non_adjacent_nodes)


def get_distance(G: nx.Graph, crossroad_node: int) -> float:
    """Given a graph and a crossroad node in the graph, return the Manhattan distance to the closest
    node that is not adjacent to the crossroad node.
    If there are no non-adjacent nodes, return the Manhattan distance to the farthest node in the
    graph.

    Args:
        G (nx.Graph): The input graph.
        crossroad_node (int): The crossroad node in the graph.

    Returns:
        float: The Manhattan distance from the crossroad node to the closest non-adjacent node.
    """
    non_adjacent_nodes = get_all_non_adjacent_node(G, crossroad_node)
    non_adjacent_pos = np.array([G.nodes[node]["pos"] for node in non_adjacent_nodes])
    pos = G.nodes[crossroad_node]["pos"]
    if len(non_adjacent_pos) > 0:
        distance = np.max(np.abs(non_adjacent_pos - pos), axis=1)  # Manhattan distance
        # distance = np.linalg.norm(non_adjacent_pos - pos, axis=1)  # Euclidean distance
        return np.min(distance)
    else:
        all_nodes_pos = np.array([G.nodes[n]["pos"] for n in G.nodes()])
        distance = np.max(np.abs(all_nodes_pos - pos), axis=1)
        return np.max(distance)


def get_crop(G: nx.Graph, image: np.array, node: int) -> np.array:
    """Given a graph, an image and a node in the graph, return the crop of the image centered on the
    node and with a size proportional to the distance to the closest non-adjacent node.

    Args:
        G (nx.Graph): The input graph.
        image (np.array): The input image.
        node (int): The node in the graph.

    Returns:
        np.array: The crop of the image centered on the node.
    """
    pos = G.nodes[node]["pos"].astype(int)
    min_distance = int(get_distance(G, node) * 0.9)
    x_min, y_min = pos - min_distance
    x_max, y_max = pos + min_distance
    x_min = np.clip(x_min, 0, image.shape[1])
    x_max = np.clip(x_max, 0, image.shape[1])
    y_min = np.clip(y_min, 0, image.shape[0])
    y_max = np.clip(y_max, 0, image.shape[0])
    crop = image[y_min:y_max, x_min:x_max]

    return crop
