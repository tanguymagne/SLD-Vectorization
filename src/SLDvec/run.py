import sys
import threading
import time
from itertools import cycle
from pathlib import Path
from typing import Optional

import networkx as nx

from SLDvec.fitting import fit_all_curves
from SLDvec.ordering import ModelPredictor, get_stroke_order
from SLDvec.preprocessing import binarize_image, load_image, potrace_vectorize
from SLDvec.skeleton import get_medial_axis
from SLDvec.utils.svg import export_svg as export


class LoadingIndicator:
    def __init__(self):
        self.spinner = cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        self.running = False
        self.current_status = ""

    def update_status(self, status: str):
        """Update the current status message."""
        self.current_status = status

    def animate(self):
        """Animate the spinner while running is True."""
        while self.running:
            sys.stdout.write("\r" + next(self.spinner) + " " + self.current_status)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r\033[K")  # Clear the line when done

    def start(self, initial_status: str = ""):
        """Start the loading animation."""
        self.running = True
        self.current_status = initial_status
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def stop(self):
        """Stop the loading animation."""
        self.running = False
        self.thread.join()
        sys.stdout.flush()

    def complete(self, status: str):
        """Complete the loading animation and print a final status message."""
        self.stop()
        print(status)


def run(
    image_path: Path,
    output_path: Path,
    intersection_predictor: ModelPredictor,
    thresh: Optional[float] = None,
    multiple_lines: bool = False,
):
    """Run the method on a single image. Save the result as an SVG file.

    Args:
        image_path (Path): Path to the input image.
        output_path (Path): Path to the output SVG file.
        intersection_predictor (ModelPredictor): The model to use for intersection classification.
        thresh (Optional[float], optional): To set the threshold. Defaults to None.
        multiple_lines (bool, optional): Wheter the input image contains multiple lines. Defaults
            to False.
    """
    loading = LoadingIndicator()
    print(f"⏳ Vectorizing : {image_path}")

    try:
        # Load the image
        loading.start("Loading image...")
        image, orig_image_shape, scale_ratio = load_image(image_path)
        # Preprocess the image
        binary_image, threshold = binarize_image(image, thresh=thresh)
        loading.stop()

        # Get the medial axis
        loading.start("Computing the medial axis...")
        curves = potrace_vectorize(binary_image)
        _, simplified_medial_axis = get_medial_axis(curves, multiple_lines=multiple_lines)
        loading.stop()

        # Order the graph
        loading.start("Ordering the graph...")
        if not multiple_lines:
            simplified_medial_axis = simplified_medial_axis.subgraph(
                max(nx.connected_components(simplified_medial_axis), key=len)
            )
        node_lists, terminating_node = get_stroke_order(
            G=simplified_medial_axis,
            image=image,
            model=intersection_predictor,
            force_single_line=not multiple_lines,
        )
        loading.stop()

        # Fit each curve
        loading.start("Fitting the curves...")
        splines = fit_all_curves(
            simplified_medial_axis, terminating_node=terminating_node, node_lists=node_lists
        )
        loading.stop()

        # Export the SVG
        loading.start("Exporting the SVG...")
        dwg = export(orig_image_shape, scale_ratio, splines, output_path)
        dwg.save()
        loading.complete("\tSuccessfully vectorized the line drawing.")

        print(f"\033[F \033[F✅ Successfully vectorized: {image_path}")

    except Exception as e:
        loading.complete(f"\tAn error occurred: {e}")
        raise
