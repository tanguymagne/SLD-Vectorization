from dataclasses import dataclass
from typing import List

import networkx as nx
import numpy as np

from SLDvec.utils.networkx.path import (
    get_path_from_degree_1_node_to_crossroad,
    get_path_to_crossroad_node,
)


@dataclass
class BranchInfo:
    """A small dataclass to store informations about a branch.

    Attributes:
        branch (List[int]): The branch itself (list of nodes).
        min_distance_along_branch (float): The minimum distance to the shape outline along
            the branch.
        endbranch_n_neighbors (int): The number of neighbors of the crossroad end-node.
    """

    branch: List[int]
    min_distance_along_branch: float
    endbranch_n_neighbors: int


def get_all_branches_info(G: nx.Graph, node: int) -> List[BranchInfo]:
    """Get informations about all branches going out of a node.
    A branch is a path from the specified node (usually a crossroad node) and a crossroad node.
    A crossroad node a node with a degree different from 2.

    Args:
        G (nx.Graph): The graph to analyze.
        node (int): The node to analyze.

    Returns:
        List[BranchInfo]: The informations about all branches.
    """
    branches_info = []
    for n in G.neighbors(node):
        branch = get_path_to_crossroad_node(G, node, n)
        endbranch_n_neighbors = G.degree(branch[-1])

        if branch[-1] == node:
            min_distance_along_branch = 0
        else:
            min_distance_along_branch = min(G.nodes[x]["dist"] for x in branch)

        branches_info.append(
            BranchInfo(
                branch=branch,
                min_distance_along_branch=min_distance_along_branch,
                endbranch_n_neighbors=endbranch_n_neighbors,
            )
        )
    return branches_info


def get_length(G: nx.Graph, branch: List[int]) -> float:
    """Compute the length of a branch in a graph.

    Args:
        G (nx.Graph): The graph.
        branch (List[int]): The branch to compute the length of.

    Returns:
        float: The length of the branch.
    """
    l = 0
    for i in range(len(branch) - 1):
        l += np.linalg.norm(G.nodes[branch[i]]["pos"] - G.nodes[branch[i + 1]]["pos"])
    return l


def annotate_crossroad_linked_to_single_neighbor_node(G: nx.Graph, ending_nodes: List[int]) -> None:
    """Add a flag to the crossroad linked to a single neighbor node.
    The flag is `is_direct_neighbor_single_neighbor_node`.
    Also add the direction to the single neighbor node in the attribute `direction_to_single`.

    Args:
        G (nx.Graph): The graph to annotate.
    """
    # For each ending points of degree 1, we find the nearest crossroad node and get its neighbor
    ending_nodes_crossroad_neighbor = [
        get_path_from_degree_1_node_to_crossroad(G, node)[-2]
        for node in ending_nodes
        if G.degree(node) == 1
    ]

    # For each degree 1 node, we find the path to the nearest crossroad node, and annotate the node
    nx.set_node_attributes(G, False, "is_direct_neighbor_single_neighbor_node")
    for node in G.nodes():
        if G.degree(node) == 1 and node not in ending_nodes:
            path = get_path_from_degree_1_node_to_crossroad(G, node)
            G.nodes[path[-1]]["is_direct_neighbor_single_neighbor_node"] = True
            if "direction_to_single" not in G.nodes[path[-1]]:
                G.nodes[path[-1]]["direction_to_single"] = path[-2]
            elif G.degree(path[-1]) == 3:
                # The crossroad is linked to multiple single neighbor node. The direction to go to
                # is the one that is not an ending node.
                if (
                    path[-2] in ending_nodes_crossroad_neighbor
                    and G.nodes[path[-1]]["direction_to_single"]
                    not in ending_nodes_crossroad_neighbor
                ):
                    # The current one is not an ending node, we should keep it
                    pass
                elif (
                    path[-2] not in ending_nodes_crossroad_neighbor
                    and G.nodes[path[-1]]["direction_to_single"] in ending_nodes_crossroad_neighbor
                ):
                    # The current one is an ending node, we should change to the new one
                    G.nodes[path[-1]]["direction_to_single"] = path[-2]
            else:
                pass
                # If the crossroad has more than 3 neighbors, the case is not tackled as
                # - the crossroad should not have more than 4 neighbors
                # - if the crossroad has 4 neighbors, we use the result of the intersection
                #   prediction to decide which direction to take
