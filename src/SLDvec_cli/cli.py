from pathlib import Path
from typing import Optional

import typer
import uvicorn
from typing_extensions import Annotated

from SLDvec import run as run_image
from SLDvec.ordering import get_predictor

app = typer.Typer(
    help="A vectorization command line tool for single line drawing.", add_completion=True
)


@app.command(help="Run the vectorization method on a single file.")
def run(
    image_path: Annotated[Path, typer.Argument(help="Path to the input image.")],
    output_path: Annotated[
        Optional[Path], typer.Option(help="Path to the output SVG file.")
    ] = None,
    thresh: Annotated[Optional[float], typer.Option(help="Manually set the threshold.")] = None,
    multiple_lines: Annotated[
        bool, typer.Option(help="If the input drawing contains multiple lines.")
    ] = False,
) -> None:
    if output_path is None:
        output_path = image_path.with_suffix(".svg")

    intersection_predictor = get_predictor()
    run_image(
        image_path=image_path,
        output_path=output_path,
        intersection_predictor=intersection_predictor,
        thresh=thresh,
        multiple_lines=multiple_lines,
    )


@app.command(help="Run the vectorization method on a folder containing multiple images.")
def run_folder(
    dir: Annotated[Path, typer.Argument(help="Path to the folder containing the input images.")],
    output_dir: Annotated[Optional[Path], typer.Option(help="Path to the output folder.")] = None,
    thresh: Annotated[Optional[float], typer.Option(help="Manually set the threshold.")] = None,
    multiple_lines: Annotated[
        bool, typer.Option(help="If the input drawing contains multiple lines.")
    ] = False,
):
    intersection_predictor = get_predictor()

    if output_dir is None:
        output_dir = dir / "output"
        output_dir.mkdir(exist_ok=True)

    for image_path in dir.glob("*.png"):
        output_path = output_dir / image_path.with_suffix(".svg").name
        run_image(
            image_path=image_path,
            output_path=output_path,
            intersection_predictor=intersection_predictor,
            thresh=thresh,
            multiple_lines=multiple_lines,
        )

    for image_path in dir.glob("*.jpg"):
        output_path = output_dir / image_path.with_suffix(".svg").name
        run_image(
            image_path=image_path,
            output_path=output_path,
            intersection_predictor=intersection_predictor,
            thresh=thresh,
            multiple_lines=multiple_lines,
        )


@app.command(help="Launch the GUI for the vectorization method.")
def gui(
    port: Annotated[int, typer.Option(help="Port to run the server on")] = 5000,
    host: Annotated[str, typer.Option(help="Host to run the server on")] = "127.0.0.1",
    reload: Annotated[bool, typer.Option(help="Enable auto-reload on code changes")] = True,
):
    """Launch the web-based GUI interface"""
    # Assuming your FastAPI app is in a module named 'webapp'
    uvicorn.run("SLDvec_app.main:app", host=host, port=port, reload=reload, log_level="info")
