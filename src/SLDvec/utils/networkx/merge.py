import uuid
from typing import List

import networkx as nx
import numpy as np


def merge_branch(G: nx.Graph, nodes: List[int]) -> int:
    """Creates a new node and merges the nodes in the list of nodes into it.
    The position of the new node is the mean of the positions of the nodes in the list nodes,
    projected back onto the set of original nodes.
    The nodes to merge should be connected to each other, and form a branch, meaning that they form
    a path graph.

    Args:
        G (nx.Graph): A graph with nodes index being integers. Each node should have a "pos"
            attribute, that contains the position of the node in a 2D space (list of two floats).
        nodes (List[int]): The indexes of the nodes to merge.

    Returns:
        int: The index of the new node.
    """
    # Find the position of the new node. If there are only 2 nodes, the new node is at the middle.
    # If more than 2 nodes are being merged, we want to insert the new node at the middle of the
    # branch (length wise)
    new_pos = np.mean([G.nodes[i]["pos"] for i in nodes], axis=0)
    if len(nodes) > 2:
        # Find the two end nodes of the branch
        ending_node = []
        for node in nodes:
            neighbors = list(G.neighbors(node))
            if not all([neigh in nodes for neigh in neighbors]):
                ending_node.append(node)
        if len(ending_node) != 2:
            raise ValueError("The nodes to merge should form a branch.")

        # Order the nodes from the first ending node to the second ending node
        order_node = [ending_node[0]]
        while order_node[-1] != ending_node[1]:
            current = order_node[-1]
            neighbors = list(G.neighbors(current))
            for neigh in neighbors:
                if neigh in nodes and neigh not in order_node:
                    order_node.append(neigh)
                    break

        # Find the node at the middle of the branch
        dist_left = 0
        dist_right = 0
        left = 0
        right = len(order_node) - 1
        while left < right:
            if dist_left < dist_right:
                dist_left += np.linalg.norm(
                    G.nodes[order_node[left]]["pos"] - G.nodes[order_node[left + 1]]["pos"]
                )
                left += 1
            else:
                dist_right += np.linalg.norm(
                    G.nodes[order_node[right]]["pos"] - G.nodes[order_node[right - 1]]["pos"]
                )
                right -= 1

        new_pos = G.nodes[order_node[left]]["pos"]

    # Create the new node and add it to the graph
    new_node_idx = max(G.nodes) + 1
    G.add_node(new_node_idx, pos=new_pos, uuid=uuid.uuid4())

    # Add attribute to the new node, edges and attributes to the graph, remove the old nodes
    G.nodes[new_node_idx]["merged_from"] = dict(nodes=[], edges=set())
    G.graph["ghost"][G.nodes[new_node_idx]["uuid"]] = {}
    for node in nodes:
        neighbors = list(G.neighbors(node))

        # Add the edges to the new node
        for neigh in neighbors:
            # Only add edges to nodes that are not being merged (avoid self loops)
            if neigh not in nodes:
                G.add_edge(new_node_idx, neigh)

        # Keep track of the nodes and edges that were merged to create the new node
        for neigh in neighbors:
            G.nodes[new_node_idx]["merged_from"]["edges"].add(
                frozenset([G.nodes[node]["uuid"], G.nodes[neigh]["uuid"]])
            )
            if neigh not in nodes:
                G.graph["ghost"][G.nodes[new_node_idx]["uuid"]][G.nodes[neigh]["uuid"]] = G.nodes[
                    node
                ]["uuid"]

        G.nodes[new_node_idx]["merged_from"]["nodes"].append(G.nodes[node])
        G.graph["ghost"][G.nodes[node]["uuid"]] = G.nodes[new_node_idx]["uuid"]
        G.remove_node(node)

    return new_node_idx
