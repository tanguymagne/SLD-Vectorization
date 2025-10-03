import networkx as nx
import numpy as np

from SLDvec import NUMBER_ADJACENT_NODE_TANGENT_COMPUTATION


def get_tangent(G: nx.Graph, node: int, node_dir: int) -> np.array:
    """Compute the tangent to the curve at a given node, in a given direction.
    The tangent is computed as the average of the difference between the positions of the nodes
    in the direction of the node_dir.

    Args:
        G (nx.Graph): The graph representing the curve to consider.
        node (int): The node for which to compute the tangent.
        node_dir (int): The node in the direction of which to compute the tangent.

    Returns:
        np.array: A 2D vector representing the tangent.
    """
    # Find a list of nodes starting from node in the direction of the node_dir
    node_branch = [node, node_dir]
    current = node_dir
    while G.degree[current] == 2 and len(node_branch) < NUMBER_ADJACENT_NODE_TANGENT_COMPUTATION:
        neighbors = list(G.neighbors(current))
        neighbors.remove(node_branch[-2])
        current = neighbors[0]
        node_branch.append(current)

    # Get the positions of all these nodes and computes the local tangent
    pos = np.array([G.nodes[n]["pos"] for n in node_branch])
    tangents = pos[1:] - pos[:-1]

    # Compute the tangent of the node of interest as the average of the local tangents, and
    # normalize the results. Note that this method emphasizes more the direction of the longest
    # segment.
    avg_tangent = np.mean(tangents, axis=0)
    norm_avg_tangent = avg_tangent / np.linalg.norm(avg_tangent)

    return norm_avg_tangent
