from typing import List

import numpy as np
import potrace

from SLDvec.curve import Spline


def potrace_vectorize(binary_image: np.array) -> List[Spline]:
    """Vectorize a binary image using potrace.

    Args:
        binary_image (np.array): The binary image to vectorize.

    Returns:
        List[Spline]: The list of Spline objects representing the vectorized image.
    """
    # Revert the binary image
    binary = binary_image.copy()
    binary = 1 - binary.astype(int)

    # Create a bitmap from the array
    bmp = potrace.Bitmap(binary)

    # Trace the bitmap to a path
    path = bmp.trace()

    # Extract all the bezier control points from the path
    points = []
    for curve in path.curves:
        points.append([])
        points[-1].append([curve.start_point])

        for segment in curve:
            if segment.is_corner:
                points[-1][-1].append(segment.c)
                points[-1][-1].append(segment.c)
                points[-1][-1].append(segment.end_point)
            else:
                points[-1][-1].append(segment.c1)
                points[-1][-1].append(segment.c2)
                points[-1][-1].append(segment.end_point)

            points[-1].append([segment.end_point])

        points[-1].pop(-1)

    # Remove empty curves
    points = [np.array(curve) for curve in points if len(curve) > 0]

    # Convert the bezier curves to Spline objects
    curves = [Spline(bezier_curve) for bezier_curve in points if len(bezier_curve) > 0]
    return curves
