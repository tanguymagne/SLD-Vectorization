import networkx as nx


def get_all_branches(G_orig: nx.Graph) -> list:
    """Create a list where each entry corresponf to a node and contains the index of the branch
    that the node belongs to.
    If the node is a junction or a degree 1 node, the index is -1.

    Args:
        G_orig (nx.Graph): The graph to extract the branches from.

    Returns:
        list: The list of branches index.
    """
    G = G_orig.copy()

    # Remove all nodes with degree more than 2 from the graph
    to_remove = []
    for node in G.nodes:
        if G.degree(node) > 2:
            to_remove.append(node)
    G.remove_nodes_from(to_remove)

    # Loop over all connected components and get the branches
    branches = []
    for component in nx.connected_components(G):
        component = G.subgraph(component)
        branches.append(list(component.nodes))

    branch_idx = [-1] * len(G_orig.nodes)
    for i, branch in enumerate(branches):
        for node in branch:
            branch_idx[node] = i
    return branch_idx


def get_graph_data(G: nx.Graph) -> dict:
    """Create a dictionary containing the nodes, edges and branches of a graph.
    These are all the informations necessary to draw the graph.
    They can be sent as a JSON object to the frontend.

    Args:
        G (nx.Graph): The graph to extract the data from.

    Raises:
        Exception: If a node has no position.

    Returns:
        dict: The dictionary containing the nodes, edges and branches of the graph.
    """
    G_data = {
        "nodes": [],
        "edges": [{"source": u, "target": v} for u, v in G.edges],
        "branch_idx": get_all_branches(G),
    }
    for i, node in enumerate(G.nodes):
        try:
            G_data["nodes"].append(
                {"id": node, "x": G.nodes[node]["pos"][0], "y": G.nodes[node]["pos"][1]}
            )
        except Exception:
            raise Exception(f"Node {node} has no position {G.nodes[node]}")
    return G_data
