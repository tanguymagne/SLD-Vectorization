import uuid
from typing import List

import networkx as nx
import numpy as np
from scipy.spatial import Voronoi

from SLDvec import SAMPLE_RATE_MEDIAL_AXIS_COMPUTATION
from SLDvec.curve import Spline
from SLDvec.skeleton.medial_axis_cpp.voronoi_pruning import medialAxis  # type: ignore


def medial_axis_wrapper(
    curves: List[Spline], sample_rate: float = SAMPLE_RATE_MEDIAL_AXIS_COMPUTATION
) -> nx.Graph:
    """Construct the medial axis of a set of curves.
    It uses the Voronoi diagram of the sample points to construct the medial axis.

    Args:
        curves (List[Spline]): The list of Spline objects representing the vectorized image.
            All splines together represent the outline of the shape to compute the medial axis.
        sample_rate (float, optional): The number of points to sample for each unit of length.
            Defaults to SAMPLE_RATE_MEDIAL_AXIS_COMPUTATION, set to 2 for images of size 1000x1000.

    Returns:
        nx.Graph: The medial axis of the shape.
    """
    # Sample points on the curve
    sample_points = [
        curve.eval_at_arc_length(np.linspace(0, 1, int(sample_rate * curve.length())))[::-1]
        for curve in curves
    ]

    # Compute the voronoi diagram of the sample points
    all_points = np.concatenate([v[:-1] for v in sample_points])
    voronoi = Voronoi(all_points)

    # Extract the medial axis from the voronoi diagram
    nodes, edges = medialAxis(
        points=voronoi.points,
        vertices=voronoi.vertices,
        ridge_points=voronoi.ridge_points,
        ridge_vertices=voronoi.ridge_vertices,
        sample=sample_points,
    )

    # Convert the medial axis to a networkx graph
    G = nx.Graph()
    for idx, n in nodes.items():
        G.add_node(idx, pos=np.array(n.pos), dist=n.dist, uuid=uuid.uuid4())
    for idx, e in edges.items():
        G.add_edge(e.node1, e.node2, object_angle=e.object_angle)
    G.graph["ghost"] = dict()

    return G
