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
    binary = binary.astype(int) * 255

    # Create a bitmap from the array
    bmp = potrace.Bitmap(binary)

    # Trace the bitmap to a path
    plist = bmp.trace()

    # Extract all the bezier control points from the path
    points = []
    for curve in plist:
        points.append([])
        points[-1].append([[curve.start_point.x, curve.start_point.y]])

        for segment in curve.segments:
            if segment.is_corner:
                points[-1][-1].append([segment.c.x, segment.c.y])
                points[-1][-1].append([segment.c.x, segment.c.y])
                points[-1][-1].append([segment.end_point.x, segment.end_point.y])
            else:
                points[-1][-1].append([segment.c1.x, segment.c1.y])
                points[-1][-1].append([segment.c2.x, segment.c2.y])
                points[-1][-1].append([segment.end_point.x, segment.end_point.y])

            points[-1].append([[segment.end_point.x, segment.end_point.y]])

        points[-1].pop(-1)

    # Remove empty curves
    points = [np.array(curve).astype(float) for curve in points if len(curve) > 0]

    # Convert the bezier curves to Spline objects
    curves = [Spline(bezier_curve) for bezier_curve in points if len(bezier_curve) > 0]
    return curves
