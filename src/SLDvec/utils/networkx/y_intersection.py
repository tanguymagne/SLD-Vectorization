from typing import Dict, Tuple

import networkx as nx
import numpy as np

from SLDvec.utils.networkx import get_tangent


def get_opposite_angle(G: nx.Graph, node: int) -> Dict[int, float]:
    # Check that the node has 3 neighbors, and find these neighbors
    neighbors = list(G.neighbors(node))
    if len(neighbors) != 3:
        raise ValueError(
            f"The node {node} should have 3 neighbors for it to be a Y intersection node."
        )

    # Compute all three outgoing tangents, and the angles they form with the x-axis (between 0 and
    # 2*pi)
    neighbors_tangent = np.array([get_tangent(G, node, n) for n in neighbors])
    angles = np.arctan2(neighbors_tangent[:, 1], neighbors_tangent[:, 0])
    angles[angles < 0] += 2 * np.pi

    # Sort the neighbors by increasing angles, convert the angles to degrees
    neighbor_order = np.argsort(angles)
    angles = np.degrees(angles[neighbor_order])
    order = np.array(neighbors)[neighbor_order]

    # Compute the angles between the neighbors
    opposite_angle = {
        order[0]: angles[2] - angles[1],
        order[1]: 360 - (angles[2] - angles[0]),
        order[2]: angles[1] - angles[0],
    }

    return opposite_angle


def get_Y_shape_informations(G: nx.Graph, node: int) -> Tuple[np.array, np.array]:
    """This function returns some informations about a Y intersection node in a graph.
    A Y intersection node is a node with 3 neighbors. The function returns the neighbors in the
    order they are encountered when turning around the node in the clockwise direction, and the
    angles between the neighbors.

    Args:
        G (nx.Graph): The graph to analyze.
        node (int): The degree 3 Y-shape node for which to find the shape information.

    Raises:
        ValueError: If the node does not have 3 neighbors.

    Returns:
        Tuple[np.array, np.array]: The neighbors in the order they are encountered when turning
            around the node in the clockwise direction, and the angles between the neighbors
            (in degrees).
    """
    # Check that the node has 3 neighbors, and find these neighbors
    neighbors = list(G.neighbors(node))
    if len(neighbors) != 3:
        raise ValueError(
            f"The node {node} should have 3 neighbors for it to be a Y intersection node."
        )

    # Compute all three outgoing tangents, and the angles they form with the x-axis (between 0 and
    # 2*pi)
    neighbors_tangent = np.array([get_tangent(G, node, n) for n in neighbors])
    angles = np.arctan2(neighbors_tangent[:, 1], neighbors_tangent[:, 0])
    angles[angles < 0] += 2 * np.pi

    # Sort the neighbors by increasing angles, convert the angles to degrees
    neighbor_order = np.argsort(angles)
    angles = np.degrees(angles[neighbor_order])
    order = np.array(neighbors)[neighbor_order]

    # Compute the angles between the neighbors
    angle01 = angles[1] - angles[0]
    angle12 = angles[2] - angles[1]
    angle20 = 360 - (angles[2] - angles[0])

    return order, np.array([angle01, angle12, angle20])


def get_Y_shape_angle_metric(G: nx.Graph, node: int) -> Tuple[float, float]:
    """Return the maximum angle of a Y intersection node and the difference between the two smallest
    angles.

    Args:
        G (nx.Graph): The graph to analyze.
        node (int): The degree 3 Y-shape node for which to find the angle metric.

    Raises:
        ValueError: If the node does not have 3 neighbors.

    Returns:
        Tuple[float, float]: The maximum angle of the Y intersection node, and the difference
            between the two smallest angles.
    """
    order, angles = get_Y_shape_informations(G, node)
    angle01, angle12, angle20 = angles[0], angles[1], angles[2]

    if angle01 > angle12 and angle01 > angle20:
        max_angle = abs(180 - angle01)
        diff_small_angle = abs(angle12 - angle20)
    elif angle12 > angle01 and angle12 > angle20:
        max_angle = abs(180 - angle12)
        diff_small_angle = abs(angle01 - angle20)
    else:
        max_angle = abs(180 - angle20)
        diff_small_angle = abs(angle01 - angle12)
    return max_angle, diff_small_angle


def find_Y_foot_direction(G: nx.Graph, node: int) -> int:
    """Given a graph and a degree 3 node, find the direction of the foot of the Y intersection.
    In practice, this function finds the node opposite to the smallest angle formed by the three
    branches.

    Args:
        G (nx.Graph): The graph to analyze.
        node (int): The degree 3 Y-shape node for which to find the direction of the foot.

    Raises:
        ValueError: If the node does not have 3 neighbors.

    Returns:
        int: The index of the node in the direction of the foot of the Y intersection.
    """
    order, angles = get_Y_shape_informations(G, node)
    angle01, angle12, angle20 = angles[0], angles[1], angles[2]

    # Output the node with the smallest opposite angle
    if angle01 < angle12 and angle01 < angle20:
        return order[2]
    elif angle12 < angle01 and angle12 < angle20:
        return order[0]
    else:
        return order[1]
