import networkx as nx

from SLDvec import VANISHING_ANGLE_THRESHOLD_MULTIPLE, VANISHING_ANGLE_THRESHOLD_SINGLE
from SLDvec.skeleton.vanishing_angle_cpp.vanishing_angle import vanishingAngle  # type: ignore


def vanishing_angle_wrapper(G: nx.Graph, multiple_lines: bool) -> nx.Graph:
    """Compute the vanishing angles of the edges of a graph based on [1] and filter the edges based
    on a threshold.
    The threshold is set to VANISHING_ANGLE_THRESHOLD_SINGLE (0.95 or 85.5 degree) if multiple_line
    is False, and VANISHING_ANGLE_THRESHOLD_MULTIPLE (0.90 or 81 degree) otherwise.

    [1] Rong, P., & Ju, T. (2023). Variational Pruning of Medial Axes of Planar Shapes. https://doi.org/10.1111/cgf.14902

    Args:
        G (nx.Graph): The graph to compute the vanishing angles and filter the edges.
        multiple_line (bool): Wheter to use the single line threshold or the multiple line
            threshold.
    Returns:
        nx.Graph: The filtered graph, with the edges removed if their vanishing angle is below
            the threshold.
    """
    # Rename the nodes to ordered integers
    G = nx.convert_node_labels_to_integers(G)

    # Extract the nodes, edges and angles of the graph
    points = []
    for i in G.nodes:
        points.append(G.nodes[i]["pos"])

    edge_ids = []
    angles = []
    for edge in G.edges(data=True):
        edge_ids.append([edge[0], edge[1]])
        angles.append(edge[2]["object_angle"])

    # Compute the vanishing angles
    VA_tresholds = vanishingAngle(points, edge_ids, angles)

    ### Remove edges with vanishing angle below a threshold
    vanishing_angle_threshold = (
        VANISHING_ANGLE_THRESHOLD_SINGLE
        if not multiple_lines
        else VANISHING_ANGLE_THRESHOLD_MULTIPLE
    )
    edges_to_remove = []
    for i, edge in enumerate(G.edges(data=True)):
        edge[2]["vanishing_angle"] = VA_tresholds[i]
        if edge[2]["vanishing_angle"] < vanishing_angle_threshold:
            edges_to_remove.append((edge[0], edge[1]))

    for edge_0, edge_1 in edges_to_remove:
        G.remove_edge(edge_0, edge_1)

    # Remove nodes with degree 0 (isolated nodes)
    degree_0_nodes = [n for n in G.nodes if G.degree(n) == 0]
    G.remove_nodes_from(degree_0_nodes)

    return G
