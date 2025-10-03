from typing import List

import numpy as np
from scipy.interpolate import splprep

from SLDvec import CURVE_FITTING_ERROR_CONSTANT

from .b_spline_to_bezier import b_spline_to_bezier_series
from .stability_point_addition import (
    add_intermediate_points_begin,
    add_intermediate_points_end,
    add_random_noise_to_duplicate,
)


def fit_curve(lists_ordered_points: List[np.array]) -> np.array:
    """Fit a series of Bezier curves on a list of ordered points.
    The input is a list of array. Each array is a list of points that are ordered, and for which
    a series of bezier curves should be fitted.

    """

    # First, some points are added to the beginning and end of the curve and some random noise is
    # added to the duplicate points to avoid weird spline fitting.
    for i in range(len(lists_ordered_points) - 1):
        lists_ordered_points[i] = add_intermediate_points_end(lists_ordered_points[i])
    for i in range(1, len(lists_ordered_points)):
        lists_ordered_points[i] = add_intermediate_points_begin(lists_ordered_points[i])
    for i in range(len(lists_ordered_points)):
        lists_ordered_points[i] = add_random_noise_to_duplicate(lists_ordered_points[i])

    # Create weights for each of the nodes in the list of ordered points. Set all weights to 1.
    # The weights of added points is set to 0.1.
    weights = [np.ones(ordered_points.shape[0]) for ordered_points in lists_ordered_points]
    for i in range(len(lists_ordered_points) - 1):
        weights[i][-2] = 0.1
    for i in range(1, len(lists_ordered_points)):
        weights[i][1] = 0.1

    # Check if the curve is periodic
    periodic = (lists_ordered_points[0][0] == lists_ordered_points[-1][-1]).all()

    # Fit the splines
    # The splines are fitted periodically only if the curve contains a single segment and is
    # periodic, otherwise the curve is fitted non-periodically, and ajusted later if needed.
    fit_per = periodic if len(lists_ordered_points) == 1 else False
    fitted_splines = [
        splprep(
            lists_ordered_points[i].T,
            w=weights[i],
            k=3,
            # s=max(np.sum(weights[i]) * CURVE_FITTING_ERROR_CONSTANT, 20) / 20,  # For tight fitting
            s=max(np.sum(weights[i]) * CURVE_FITTING_ERROR_CONSTANT, 20),  # For smoother curves
            per=fit_per,
        )
        for i in range(len(lists_ordered_points))
    ]

    # Convert the splines to bezier curves
    beziers = [np.array(b_spline_to_bezier_series(tck, per=fit_per)) for tck, u in fitted_splines]
    beziers = np.concatenate(beziers)

    # If the curve is periodic, but has more than one segment, we adjust the first and last
    # segments to make sure they are connected G1 continuously
    if periodic:
        avg_endpoint = (beziers[-1][-1] + beziers[0][0]) / 2

        tangent_1 = beziers[0][1] - beziers[0][0]
        tangent_2 = beziers[-1][-1] - beziers[-1][-2]

        length_tangent_1 = np.linalg.norm(tangent_1)
        length_tangent_2 = np.linalg.norm(tangent_2)

        normalized_tangent_1 = tangent_1 / (length_tangent_1 + 1e-6)
        normalized_tangent_2 = tangent_2 / (length_tangent_2 + 1e-6)

        avg_tangent = (normalized_tangent_1 + normalized_tangent_2) / 2
        normalized_avg_tangent = avg_tangent / np.linalg.norm(avg_tangent)

        beziers[0][0] = avg_endpoint
        beziers[0][1] = avg_endpoint + normalized_avg_tangent * length_tangent_1
        beziers[-1][-1] = avg_endpoint
        beziers[-1][-2] = avg_endpoint - normalized_avg_tangent * length_tangent_2

    return beziers
