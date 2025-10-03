from typing import Optional, Tuple

import numpy as np
from skimage import io
from skimage.filters import gaussian, threshold_li
from skimage.transform import rescale


def load_image(image_path: str, max_size: int = 1000) -> Tuple[np.array, Tuple[int, int], float]:
    """Load an image and rescale it if it is too large.

    Args:
        image_path (str): The path to the image.
        max_size (int, optional): The maximum size of the image. Defaults to 1000.

    Returns:
        Tuple[np.array, Tuple[int, int], float]: The rescaled image, the original shape of the
            image, and the scale factor.
    """
    image = io.imread(image_path, as_gray=True)
    if max(image.shape) > max_size:
        scale = max_size / max(image.shape)
        rescale_image = rescale(image, scale, anti_aliasing=True)
    else:
        rescale_image = image
        scale = 1
    return rescale_image, image.shape, scale


def blur_image(image: np.array, sigma: float = 1) -> np.array:
    """Blur an image using a Gaussian filter.

    Args:
        image (np.array): The input image to blur.
        sigma (float, optional): The Gaussian filter kernel size. Defaults to 1.

    Returns:
        np.array: The blurred image.
    """
    return gaussian(image, sigma=sigma)


def binarize_image(image: np.array, thresh: Optional[float] = None) -> Tuple[float, np.array]:
    """Binarizes an image.

    Args:
        image (np.array): The input image to binarize.
        thresh (Optional[float], optional): The threshold to use for binarization. If None, Li's
            method is used to find the threshold. Defaults to None.

    Returns:
        Tuple[float, np.array]: The binarized image and the threshold value.
    """
    if thresh is None:
        thresh = threshold_li(image)
        # Note, other method have been tested, such as threshold_isodata, threshold_mean,
        # threshold_minimum, threshold_otsu, threshold_triangle, threshold_yen
        # Otsu thresholding still pretty good, but Li seems to be the best
    binary = image > thresh
    return binary.astype(int), thresh
