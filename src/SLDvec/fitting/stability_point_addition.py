import numpy as np


def add_intermediate_points_begin(points: np.array) -> np.array:
    """Add intermediate points at the beginning of the curve (between first and second point).
    This is done to avoid large gap between the first and second point, which can lead to weird
    spline fitting (because the tangent at the first point is not well defined).

    Args:
        points (np.array): The list of points positions.

    Returns:
        np.array: The list of points positions with intermediate points added at the beginning.
    """
    first = points[0][None, :]
    last = points[1][None, :]

    ts = np.array([[0.0], [0.01], [1.0]])
    interpolated = ts * last + (1 - ts) * first
    return np.concatenate([interpolated, points[2:]])


def add_intermediate_points_end(points: np.array) -> np.array:
    """Add intermediate points at the end of the curve (between last and second to last point).
    This is done to avoid large gap between the last and second to last point, which can lead to
    weird spline fitting (because the tangent at the last point is not well defined).

    Args:
        points (np.array): The list of points positions.

    Returns:
        np.array: The list of points positions with intermediate points added at the end.
    """
    first = points[-2][None, :]
    last = points[-1][None, :]

    ts = np.array([[0.0], [0.99], [1.0]])
    interpolated = ts * last + (1 - ts) * first
    return np.concatenate([points[:-2], interpolated])


def add_random_noise_to_duplicate(points: np.array, noise: float = 1e-6, seed: int = 0) -> np.array:
    """Add random noise to the points that are duplicate.
    This is done to avoid numerical issue when fitting the curve, as the spline fitting algorithm
    does not like duplicate points.

    Args:
        points (np.array): The list of points positions.
        noise (float, optional): The amount of noise to add to duplicate node. Defaults to 1e-6.
        seed (int, optional): The seed for adding noise. Defaults to 0.

    Returns:
        np.array: The list of points positions with noise added to duplicate points.
    """
    np.random.seed(seed)
    for i in range(1, len(points) - 1):
        if np.all(points[i] == points[:i], axis=-1).any():
            points[i] += np.random.randn(2) * noise
    return points
