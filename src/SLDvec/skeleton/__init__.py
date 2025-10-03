import networkx as nx

from .medial_axis import medial_axis_wrapper
from .simplification import merge_3_neighbords_node
from .vanishing_angle import vanishing_angle_wrapper


def get_medial_axis(curves, multiple_lines: bool = False):
    # Compute the Medial Axis
    G = medial_axis_wrapper(curves=curves)
    G_simplified = G.copy()

    # Compute the vanishing angle and filter the graph arccordingly
    G_simplified = vanishing_angle_wrapper(G_simplified, multiple_lines=multiple_lines)

    # Merge 3 neighbors node
    G_simplified = merge_3_neighbords_node(G_simplified)

    G_simplified = nx.convert_node_labels_to_integers(G_simplified)

    return G, G_simplified
