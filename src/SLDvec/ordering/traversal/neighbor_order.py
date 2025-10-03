import networkx as nx
import numpy as np

from SLDvec.utils.networkx import get_tangent


class ClockwiseNeighborCycle:
    """This class is used to cycle around the neighbors of a node in a clockwise manner.
    For degree 4 nodes, it also computes the pairs of tangent neighbors."""

    def __init__(self, node, G):
        self.node = node
        self._order_neighbors(G)

    def _order_neighbors(self, G):
        """Order the neighbors of the node in a clockwise manner."""
        # Get the neighbors of the node
        neighbors = list(G.neighbors(self.node))

        # Compute the vectors from the node to the neighbors
        neighbors_pos = [G.nodes[n]["pos"] for n in neighbors]
        vector_to_neighbors = np.array(neighbors_pos) - G.nodes[self.node]["pos"]
        vector_to_neighbors = (
            vector_to_neighbors / np.linalg.norm(vector_to_neighbors, axis=1)[:, None]
        )

        # Compute the angles of the vectors to the x-axis between 0 and 2pi
        angles = np.arctan2(vector_to_neighbors[:, 1], vector_to_neighbors[:, 0])
        angles[angles < 0] += 2 * np.pi

        # Order the neighbors by increasing angles
        order = np.argsort(angles)
        self.order = np.array(neighbors)[order]
        self.angles = np.degrees(angles[order])

        # For degree 4 nodes, compute the pairs of tangent neighbors
        if len(list(G.neighbors(self.node))) == 4:
            self._get_tangent_pairs(G)

    def _get_tangent_pairs(self, G):
        """If the node has a degree of 4, compute the pairs of tangent neighbors.
        Those are the the consecutive pairs of neighbors which are the most continuous.
        """
        # There are two possible pairs of non-crossing neighbors. We want to find the most
        # continuous one, i.e. the one with the smallest angle between the two branches.
        pairs_options = [[[0, 1], [2, 3]], [[0, 3], [1, 2]]]
        angle_measure = [0, 0]
        for i, pairs in enumerate(pairs_options):
            for idx1, idx2 in pairs:
                # Compute the angle between the two branches
                tangent1 = get_tangent(G, self.node, self.order[idx1])
                tangent2 = get_tangent(G, self.node, self.order[idx2])

                angle_idx1 = np.arctan2(tangent1[1], tangent1[0])
                angle_idx2 = np.arctan2(tangent2[1], tangent2[0])

                angle_diff = abs(angle_idx1 - angle_idx2)
                if angle_diff > np.pi:
                    angle_diff = 2 * np.pi - angle_diff

                angle_measure[i] += np.degrees(angle_diff)

        # Choose the pair with the smallest angle between the two branches
        if angle_measure[0] > angle_measure[1]:
            self.tangent_order = {
                self.order[pairs_options[0][0][0]]: self.order[pairs_options[0][0][1]],
                self.order[pairs_options[0][0][1]]: self.order[pairs_options[0][0][0]],
                self.order[pairs_options[0][1][0]]: self.order[pairs_options[0][1][1]],
                self.order[pairs_options[0][1][1]]: self.order[pairs_options[0][1][0]],
            }
        else:
            self.tangent_order = {
                self.order[pairs_options[1][0][0]]: self.order[pairs_options[1][0][1]],
                self.order[pairs_options[1][0][1]]: self.order[pairs_options[1][0][0]],
                self.order[pairs_options[1][1][0]]: self.order[pairs_options[1][1][1]],
                self.order[pairs_options[1][1][1]]: self.order[pairs_options[1][1][0]],
            }

    def next(self, node):
        """Return the next neighbor of the node in the clockwise order."""
        for i, neighbor in enumerate(self.order):
            if neighbor == node:
                return self.order[(i + 1) % len(self.order)]
        return None

    def previous(self, node):
        """Return the previous neighbor of the node in the clockwise order."""
        for i, neighbor in enumerate(self.order):
            if neighbor == node:
                return self.order[(i - 1) % len(self.order)]
        return None


def get_next_node(current_node: int, previous_node: int, G: nx.Graph) -> int:
    """Given a degree 4 node, the previous travelled node and the corresponding graph, return the
    next node to travel to.

    Args:
        current_node (int): The degree 4 node for which to find the next node.
        previous_node (int): The previous node travelled to (a neighbor of the degree 4 node).
        G (_type_): The graph to traverse.

    Raises:
        ValueError: _description_

    Returns:
        int: The next node to travel to.
    """

    if G.nodes[current_node]["intersection_type"] == "crossing":
        neighbor_cycle = G.nodes[current_node]["neighbor_cycle"]
        next_node = neighbor_cycle.next(previous_node)
        crossing = neighbor_cycle.next(next_node)
        return crossing
    else:
        neighbor_cycle = G.nodes[current_node]["neighbor_cycle"]
        next_node = neighbor_cycle.tangent_order[previous_node]
        return next_node
