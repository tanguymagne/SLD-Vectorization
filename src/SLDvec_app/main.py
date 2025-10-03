import base64
import copy
import io
from pathlib import Path
from typing import List, Tuple

import networkx as nx
import numpy as np
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from numba import jit
from PIL import Image
from pydantic import BaseModel

from SLDvec.curve import Spline
from SLDvec.fitting import fit_all_curves
from SLDvec.ordering import ModelPredictor, get_predictor, get_stroke_order
from SLDvec.preprocessing import binarize_image, blur_image, load_image, potrace_vectorize
from SLDvec.skeleton import get_medial_axis
from SLDvec.utils.networkx import merge_branch
from SLDvec.utils.networkx.api import get_graph_data
from SLDvec.utils.svg import export_svg as export

app = FastAPI()

# Mount static files
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=current_dir / "templates")


class PreprocessParams(BaseModel):
    sigma: float
    thresh: float


class SelectedNodes(BaseModel):
    nodes: List[int]
    selectionType: str


class MultipleLines(BaseModel):
    state: bool


class SelectedIntersection(BaseModel):
    intersection: float


class AppState:
    image: np.array = None
    orig_image_shape: Tuple[int, int] = None
    scale_ratio: float = None
    blur_image: np.array = None
    binary_image: np.array = None
    binary_threshold: float = None
    base_medial_axis: nx.Graph = None
    simplified_medial_axis: nx.Graph = None
    full_graph: nx.Graph = None
    largest_component_graph: nx.Graph = None
    model: ModelPredictor = get_predictor()
    intersections_pos: np.array = None
    intersections_node: List[int] = None
    current_graph: nx.Graph = None
    bezier_splines: np.array = None


global app_state
app_state = AppState()


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    # Get the app state and data
    global app_state
    content = await file.read()

    # Load the image
    app_state.image, app_state.orig_image_shape, app_state.scale_ratio = load_image(
        io.BytesIO(content)
    )

    # Process image for frontend
    img = Image.fromarray((app_state.image * 255).astype(np.uint8))
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return JSONResponse(content=img_str)


@app.post("/preprocess")
async def update_params(p: PreprocessParams):
    # Get the app state and data
    global app_state

    # Preprocess the image
    app_state.blur_image = blur_image(app_state.image, p.sigma)
    app_state.binary_image, app_state.binary_threshold = binarize_image(
        app_state.blur_image, p.thresh if p.thresh <= 1.0 else None
    )

    # Process image for frontend
    blur_img = Image.fromarray((app_state.blur_image * 255).astype(np.uint8))
    buffered = io.BytesIO()
    blur_img.save(buffered, format="PNG")
    blur_img_str = base64.b64encode(buffered.getvalue()).decode()

    binary_img = Image.fromarray((app_state.binary_image * 255).astype(np.uint8))
    buffered = io.BytesIO()
    binary_img.save(buffered, format="PNG")
    binary_img_str = base64.b64encode(buffered.getvalue()).decode()

    return JSONResponse(
        {
            "blur_image": blur_img_str,
            "binary_image": binary_img_str,
            "thresh": app_state.binary_threshold,
        }
    )


@app.post("/graph")
async def create_graph(multiple_lines: MultipleLines):
    global app_state
    if app_state.binary_image is not None:
        curves = potrace_vectorize(app_state.binary_image)
        base_medial_axis, simplified_medial_axis = get_medial_axis(
            curves, multiple_lines=multiple_lines.state
        )

        app_state.base_medial_axis = nx.convert_node_labels_to_integers(base_medial_axis)
        app_state.simplified_medial_axis = nx.convert_node_labels_to_integers(
            simplified_medial_axis
        )

        graph_data_simplified = get_graph_data(app_state.simplified_medial_axis)
        graph_data_base = get_graph_data(app_state.base_medial_axis)

        control_points = [
            [np.array([b.P1[0], b.P2[0], b.P3[0], b.P4[0]]).tolist() for b in curve.beziers]
            for curve in curves
        ]

        app_state.full_graph = copy.deepcopy(app_state.simplified_medial_axis)
        app_state.largest_component_graph = app_state.full_graph.subgraph(
            max(nx.connected_components(app_state.full_graph), key=len)
        )

        return JSONResponse(
            content={
                "graph_data": graph_data_simplified,
                "base_graph_data": graph_data_base,
                "curves": control_points,
            }
        )


@app.post("/update_graph")
async def update_graph(selected_nodes: SelectedNodes):
    """This function is called when the user wants to merge a branch or split a node that was
    created by merging several nodes.
    """
    global app_state

    # If the selected node is a branch, merge it, and keeps track of merged nodes
    if selected_nodes.selectionType == "branch":
        to_merge = set()
        core_node = set()
        for node, selected in enumerate(selected_nodes.nodes):
            if selected:
                to_merge.add(node)
                to_merge.update(app_state.simplified_medial_axis.neighbors(node))
                core_node.add(node)
        ending_nodes = to_merge - core_node
        if len(to_merge) > 0 and len(ending_nodes) > 1:
            _ = merge_branch(app_state.simplified_medial_axis, list(to_merge))
        elif len(ending_nodes) == 1:
            # In that case simply remove all the core nodes (the branch is a dead-end)
            app_state.simplified_medial_axis.remove_nodes_from(core_node)

    # If the selected node is a single node, we split it if it was created by merging several nodes
    elif selected_nodes.selectionType == "node":
        assert sum(selected_nodes.nodes) == 1, "Only one node should be selected in that case"
        # Remove this node
        for node, selected in enumerate(selected_nodes.nodes):
            if selected:
                merged_from_nodes = app_state.simplified_medial_axis.nodes[node]["merged_from"]
                app_state.simplified_medial_axis.remove_node(node)
                break

        # Rename the nodes by their uuid and add previously merged nodes back
        app_state.simplified_medial_axis = nx.relabel_nodes(
            G=app_state.simplified_medial_axis,
            mapping={
                old_node: app_state.simplified_medial_axis.nodes[old_node]["uuid"]
                for old_node in app_state.simplified_medial_axis.nodes
            },
        )
        app_state.simplified_medial_axis.add_nodes_from(
            [node["uuid"], node] for node in merged_from_nodes["nodes"]
        )

        # Add the edges back
        edges = []
        for edge in merged_from_nodes["edges"]:
            edge = list(edge)
            while edge[0] not in app_state.simplified_medial_axis.nodes:
                edge[0] = app_state.simplified_medial_axis.graph["ghost"][edge[0]]
                while isinstance(edge[0], dict):
                    edge[0] = edge[0][edge[1]]
            while edge[1] not in app_state.simplified_medial_axis.nodes:
                edge[1] = app_state.simplified_medial_axis.graph["ghost"][edge[1]]
                while isinstance(edge[1], dict):
                    edge[1] = edge[1][edge[0]]
            edges.append(edge)

        app_state.simplified_medial_axis.add_edges_from(edges)

    app_state.simplified_medial_axis = nx.convert_node_labels_to_integers(
        app_state.simplified_medial_axis
    )

    app_state.simplified_medial_axis.graph.pop("terminating_node", None)

    graph_data_simplified = get_graph_data(app_state.simplified_medial_axis)

    app_state.full_graph = copy.deepcopy(app_state.simplified_medial_axis)
    app_state.largest_component_graph = app_state.full_graph.subgraph(
        max(nx.connected_components(app_state.full_graph), key=len)
    )

    return JSONResponse(content={"graph_data": graph_data_simplified})


@jit(nopython=True)
def create_triangle_strip_coor(points, derivative):
    normal = np.zeros_like(derivative)
    normal[:, 0] = -derivative[:, 1]
    normal[:, 1] = derivative[:, 0]
    normal_norm = np.sqrt(normal[:, 0] ** 2 + normal[:, 1] ** 2)
    normal /= normal_norm[:, None]

    points1 = points + normal
    points2 = points - normal

    all_points = np.zeros((len(points) * 4))
    for i in range(len(points)):
        all_points[4 * i + 0] = points1[i][0]
        all_points[4 * i + 1] = points1[i][1]
        all_points[4 * i + 2] = points2[i][0]
        all_points[4 * i + 3] = points2[i][1]
    return all_points


def sample_vectorization_for_triangle_strip(bezier, im_size, n_points=1000):
    bezierCurve = Spline(bezier, n=100)

    curve_length = bezierCurve.length() / im_size
    n_points = max(int(n_points * curve_length), 20)

    points = bezierCurve.eval_at_arc_length(np.linspace(0, 1, n_points))
    derivative = bezierCurve.eval_prime_at_arc_length(np.linspace(0, 1, n_points))

    return create_triangle_strip_coor(points, derivative)


@app.post("/vectorize")
async def get_vectorize(multiple_lines: MultipleLines):
    global app_state

    # If the drawing contains a single line, we select the largest component of the graph to remove
    # noise
    if not multiple_lines.state:
        app_state.current_graph = app_state.largest_component_graph
    else:
        app_state.current_graph = app_state.full_graph

    # Get the stroke order and fit the bezier curves
    app_state.current_graph.graph.pop("terminating_node", None)
    node_lists, terminating_node = get_stroke_order(
        app_state.current_graph,
        app_state.image,
        app_state.model,
        force_single_line=not multiple_lines.state,
    )
    app_state.bezier_splines = fit_all_curves(app_state.current_graph, terminating_node, node_lists)

    # Find the intersections
    intersections_pos = []
    app_state.intersections_node = []
    for node in app_state.current_graph.nodes():
        if app_state.current_graph.degree[node] > 3:
            intersections_pos.append(app_state.current_graph.nodes[node]["pos"])
            app_state.intersections_node.append(node)

    app_state.intersections_pos = np.array(intersections_pos)

    # Sample the bezier splines
    all_points = [
        sample_vectorization_for_triangle_strip(
            bezier_spline, max(app_state.orig_image_shape)
        ).tolist()  # change this base on length
        for bezier_spline in app_state.bezier_splines
    ]

    return JSONResponse(
        {"intersections_pos": app_state.intersections_pos.tolist(), "vectorize_points": all_points}
    )


@app.post("/update_vectorize")
async def update_vectorize(intersection_change: SelectedIntersection):
    global app_state

    # Change the intersection type of the selected intersection in the correct component
    node_change = app_state.intersections_node[int(intersection_change.intersection)]
    current_mode = app_state.current_graph.nodes[node_change]["intersection_type"]
    if current_mode == "crossing":
        app_state.current_graph.nodes[node_change]["intersection_type"] = "tangent"
    elif current_mode == "tangent":
        app_state.current_graph.nodes[node_change]["intersection_type"] = "crossing"

    # Recompute the vectorization
    node_lists, terminating_node = get_stroke_order(
        app_state.current_graph, app_state.image, app_state.model, force_single_line=False
    )
    app_state.bezier_splines = fit_all_curves(app_state.current_graph, terminating_node, node_lists)

    # Resample the bezier splines
    all_points = [
        sample_vectorization_for_triangle_strip(
            bezier_spline, max(app_state.orig_image_shape)
        ).tolist()  # change this base on length
        for bezier_spline in app_state.bezier_splines
    ]

    return JSONResponse(
        {"intersections_pos": app_state.intersections_pos.tolist(), "vectorize_points": all_points}
    )


@app.get("/export_svg")
async def export_svg():
    global app_state

    dwg = export(
        app_state.orig_image_shape,
        app_state.scale_ratio,
        copy.deepcopy(app_state.bezier_splines),
        "test.svg",
    )

    svg_string = dwg.tostring()
    return Response(content=svg_string, media_type="image/svg+xml")


if __name__ == "__main__":
    import uvicorn

    # Otherwise run with: uvicorn app.main:app --reload from the terminal
    uvicorn.run("main:app", port=5000, log_level="info", reload=True)
