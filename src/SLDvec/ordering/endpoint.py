from collections import defaultdict
from typing import List

import networkx as nx
import numpy as np

from SLDvec.utils.networkx import (
    get_opposite_angle,
    get_path_from_degree_1_node_to_crossroad,
    get_path_to_crossroad_node,
    get_Y_shape_angle_metric,
)


def get_degree_3_node_infos(G: nx.Graph, degree_3_nodes: List[int]) -> dict:
    """Return the angles informations of a list of degree 3 nodes.
    It returns 180 - maximum angle and the difference between the two smallest angles.

    Args:
        G (nx.Graph): The graph representing the single line drawing.
        degree_3_nodes (List[int]): The list of degree 3 nodes.

    Returns:
        dict: A dictionary containing the angle informations of the degree 3 nodes.
    """
    # We first check the nodes with a degree of 3
    degree_3_node_info = {}
    for node in degree_3_nodes:
        max_angle, small_angle_diff = get_Y_shape_angle_metric(G, node)
        degree_3_node_info[node] = [max_angle, small_angle_diff]
    return degree_3_node_info


def complete_terminating_nodes(terminating: List[int], degree_3_node_info: dict) -> List[int]:
    """Complete a set of terminating nodes to have an even number of them.
    If there is an odd number of terminating nodes, a degree 3 node is added to the list.
    Otherwise, the list is returned as is.

    Args:
        terminating (List[int]): The list of terminating nodes.
        degree_3_node_info (dict): The dictionary containing the angle informations of the degree 3
            nodes.

    Returns:
        List[int]: The completed list of terminating nodes.
    """
    if len(terminating) % 2 == 0:
        return terminating

    # There is an odd number of terminating nodes, a degree 3 node is added to the list
    # The degree 3 node with the smallest angle and difference below 60 degrees and that is not
    # already in the list of terminating node is added if its minimum angle is below 30.
    min_angle = np.inf
    min_node = None
    for node, (angle, diff) in degree_3_node_info.items():
        if angle < min_angle and angle < 30 and diff < 60 and node not in terminating:
            min_angle = angle
            min_node = node
    if min_node is not None:
        terminating.append(min_node)
        return terminating

    # There is atill an odd number of terminating nodes, a degree 3 node is added to the list
    # The degree 3 node with the smallest angle and that is not already in the list of terminating
    # node is added.
    min_angle = np.inf
    min_node = None
    for node, (angle, diff) in degree_3_node_info.items():
        if angle < min_angle and node not in terminating:
            min_angle = angle
            min_node = node
    if min_node is not None:
        terminating.append(min_node)
        return terminating

    # NOTE: this shouldn't happen, it is there to avoid errors and always return
    # If it happens it means that no degree 3 node can be added to the list of terminating nodes so
    # there is an odd degree of odd degree nodes in the graph.
    return terminating


def find_terminating_node(G: nx.Graph, force_single_line: bool) -> List[int]:
    """Find all the terminating nodes in a graph of a single line drawing.
    If force_single_line is True, non node of degree 3 are added, except if there is an off number
    of terminating nodes then exactly one degree 3 node is added, the more T-shape like
    intersection.
    If force_single_line is False, all T-shape like degree 3 nodes are added to the list of
    terminating nodes.

    Args:
        G (nx.Graph): The graph representing the single line drawing.
        force_single_line (bool): Whether to force the output to contain a single stroke.

    Returns:
        List[int]: The list of terminating nodes.
    """
    # Find the degree 1 and 3 nodes
    degree_1_nodes = []
    degree_3_nodes = []
    for node in G.nodes():
        if G.degree(node) % 2 == 1:
            if G.degree(node) == 1:
                degree_1_nodes.append(node)
            elif G.degree(node) == 3:
                degree_3_nodes.append(node)

    # For node with degree 3, get infos about the angles
    degree_3_node_info = get_degree_3_node_infos(G, degree_3_nodes)

    # Find the terminating nodes
    terminating = []

    # We first check the nodes with a degree of 1
    odd_degree_close_to_degree_1_node = defaultdict(list)
    for node in degree_1_nodes:
        branch_to_crossroad = get_path_from_degree_1_node_to_crossroad(G, node)
        closest_crossroad = branch_to_crossroad[-1]
        if G.degree(closest_crossroad) % 2 == 0 or closest_crossroad in degree_1_nodes:
            # If the node has degree 1, it is terminating
            # - if the adjacent crossroad has an even degree
            # - if the closest crossroad node (node of degree different than 2) is a degree 1 node
            #       (line without crossroad)
            terminating.append(node)
        elif G.degree(closest_crossroad) % 2 == 1:
            # If the adjacent crossroad has an odd degree, we need to keep track of the crossroad
            odd_degree_close_to_degree_1_node[closest_crossroad].append(
                {"degree_1_node": node, "corresponding_crossroad_neighbor": branch_to_crossroad[-2]}
            )

    # We then check the crossroads with odd degree and connected to 2 or more degree 1 nodes
    for crossroad, degree_1s in odd_degree_close_to_degree_1_node.items():
        if len(degree_1s) == 2:
            # 2 degree 1 nodes are connected to the same crossroad. The one with the smallest
            # opposite angle is added to the list of terminating nodes
            opposite_angle = get_opposite_angle(G, crossroad)
            if (
                opposite_angle[degree_1s[0]["corresponding_crossroad_neighbor"]]
                > opposite_angle[degree_1s[1]["corresponding_crossroad_neighbor"]]
            ):
                terminating.append(degree_1s[0]["degree_1_node"])
            else:
                terminating.append(degree_1s[1]["degree_1_node"])
        if len(degree_1s) == 3:
            # This case basically means that we have a crossroad with 3 single neighbor nodes
            # connected to it. So the entire graph is a star graph, we simply need to add two ending
            # nodes from these single neighbor nodes
            opposite_angle = get_opposite_angle(G, crossroad)
            min_angle_node = min(opposite_angle, key=opposite_angle.get)
            for degree_1 in degree_1s:
                if degree_1["corresponding_crossroad_neighbor"] != min_angle_node:
                    terminating.append(degree_1["degree_1_node"])

    # Finally, we add all the degree 3 nodes not connected to a degree 1 node
    for node in degree_3_nodes:
        connected_to_degree_1 = False
        for neighbor in G.neighbors(node):
            branch_to_crossroad = get_path_to_crossroad_node(G, node=node, direction=neighbor)
            if G.degree(branch_to_crossroad[-1]) == 1:
                connected_to_degree_1 = True
                break
        if not connected_to_degree_1 and node not in terminating:
            terminating.append(node)

    if force_single_line:
        return complete_terminating_nodes(terminating, degree_3_node_info)

    # For multiple line drawing, we also check for T-shape like degree 3 nodes
    for node, (max_angle, small_angle_diff) in degree_3_node_info.items():
        if max_angle < 30 and small_angle_diff < 60:
            if node not in terminating:
                terminating = [node] + terminating
            # Degree 1 node linked to this node are also terminating
            for neighbor in G.neighbors(node):
                path = get_path_to_crossroad_node(G, node=node, direction=neighbor)
                if G.degree(path[-1]) == 1 and path[-1] not in terminating:
                    terminating.append(path[-1])

    return complete_terminating_nodes(terminating, degree_3_node_info)
