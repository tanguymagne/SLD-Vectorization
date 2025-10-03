from importlib import resources


def get_asset_path(asset_name: str) -> str:
    """Get the full path to an asset file."""
    with resources.path("SLDvec.assets", asset_name) as path:
        return str(path)


SAMPLE_RATE_MEDIAL_AXIS_COMPUTATION = 2
VANISHING_ANGLE_THRESHOLD_SINGLE = 0.95  # Correspond to an angle of 0.95 * 90 = 85.5 degrees
VANISHING_ANGLE_THRESHOLD_MULTIPLE = 0.90  # Correspond to an angle of 0.90 * 90 = 81 degrees
NUMBER_ADJACENT_NODE_TANGENT_COMPUTATION = SAMPLE_RATE_MEDIAL_AXIS_COMPUTATION * 10


MODEL_PATH = get_asset_path("model.pth")
MODEL_NAME = "resnet50"
MODEL_NUM_CLASSES = 2
MODEL_PREDICTIONS_N_AUGMENTATIONS = 16

CURVE_FITTING_ERROR_CONSTANT = 1 / 1000
