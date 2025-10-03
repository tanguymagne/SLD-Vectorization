from pathlib import Path
from typing import Tuple

import numpy as np
import svgwrite


def export_svg(
    orig_image_shape: Tuple[int, int], scale_ratio: float, bezier_splines: np.array, save_path: Path
):
    """Export a list of bezier splines to an SVG file.

    Args:
        orig_image_shape (Tuple[int, int]): The shape of the original image.
        scale_ratio (float): The ratio by which the bezier splines were scaled.
        bezier_splines (np.array): The list of bezier splines to export, as a list of lists of 4
            pairs (x-y coordinates).
        save_path (Path): The path to the SVG file to save.
    """
    dwg = svgwrite.Drawing(
        save_path, profile="tiny", size=(orig_image_shape[1], orig_image_shape[0])
    )

    for i in range(len(bezier_splines)):
        bezier_splines[i] /= scale_ratio

        beziers = bezier_splines[i]

        path = dwg.path()
        path.push("M", *beziers[0][0])  # Move to the beginning of the curve
        for bezier in beziers:
            path.push("C", bezier[1], bezier[2], bezier[3])  # Cubic Bezier

        if (beziers[0][0] == beziers[-1][-1]).all():
            path.push("Z")  # Close the path

        # Set style attributes and add the path to the drawing
        path.update(
            {
                "stroke": "black",
                "stroke-width": 2,
                "fill": "none",
                "stroke-linecap": "round",
                "stroke-linejoin": "round",
            }
        )
        dwg.add(path)

    return dwg
