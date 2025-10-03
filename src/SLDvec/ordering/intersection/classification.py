from typing import Tuple, Union

import numpy as np
import timm
import torch
from PIL import Image
from scipy.special import softmax
from torchvision.transforms import v2

from SLDvec import MODEL_NAME, MODEL_NUM_CLASSES, MODEL_PATH, MODEL_PREDICTIONS_N_AUGMENTATIONS


def get_predictor() -> timm.models:
    """Load the model with pretrained weight.

    Returns:
        timm.models: The loaded model.
    """
    model = timm.create_model(MODEL_NAME, num_classes=MODEL_NUM_CLASSES)
    state_dict = torch.load(MODEL_PATH, weights_only=True)
    model.load_state_dict(state_dict["model_state_dict"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    transform_config = timm.data.resolve_data_config(model.pretrained_cfg, model=model)
    transform = timm.data.create_transform(**transform_config)

    return ModelPredictor(model, transform, device)


def convert_img_to_PIL(image: np.array) -> Image:
    """Convert an image given a np.array to a PIL image.
    The output image will be a RGB image, with 3 channels.

    Args:
        image (np.array): The input image.

    Returns:
        Image: The PIL image.
    """
    # Get the correct shape
    if len(image.shape) == 2:
        image = np.repeat(image[:, :, None], 3, axis=2)
    elif len(image.shape) == 3 and image.shape[2] == 1:
        image = np.repeat(image, 3, axis=2)
    elif len(image.shape) == 3 and image.shape[2] == 4:
        image = image[:, :, :3]

    # Convert to PIL image
    if image.dtype == np.uint8:
        image = Image.fromarray(image)
    else:
        if image.max() <= 1:
            image = (image * 255).astype(np.uint8)
        image = Image.fromarray(image)

    return image


class ModelPredictor:
    def __init__(self, model, transform, device):
        self.model = model
        self.transform = transform
        self.device = device
        self.index_to_class = {0: "crossing", 1: "tangent"}
        self.augmentation_transform = v2.Compose(
            [
                v2.RandomHorizontalFlip(p=0.5),
                v2.RandomVerticalFlip(p=0.5),
                v2.RandomRotation(degrees=90, fill=[2.2489, 2.4286, 2.6400]),
                v2.RandomResizedCrop(size=224, scale=(0.8, 1.0), ratio=(0.90, 1.1), antialias=True),
            ]
        )

    def __call__(self, image: Union[np.array, Image.Image]) -> Tuple[str, float, float]:
        """Predict the type of intersection of an image.
        This functions also returns 2 confidence metrics:
        - confidence1 represents the ratio of the most frequent prediction
        - confidence2 represents the average confidence (when looking at the softmax distribution
            of the output) of the most frequent prediction.

        Args:
            image (Union[np.array, Image]): The image to predict the intersection type of.

        Returns:
            Tuple(str, float, float): The predicted intersection type and the 2 confidence metrics.
        """
        if isinstance(image, np.ndarray):
            image = convert_img_to_PIL(image)

        # Create copies of the image with different augmentations, and predict the intersection type
        image = self.transform(image)
        augmented_image = [
            self.augmentation_transform(image) for _ in range(MODEL_PREDICTIONS_N_AUGMENTATIONS)
        ]
        image = torch.stack([image] + augmented_image)
        image = image.to(self.device)
        with torch.no_grad():
            output = self.model(image)

        # Aggregate the predictions, by taking the most frequent prediction
        preds = torch.argmax(output, dim=1).cpu().numpy()
        pred = np.percentile(preds, 50)
        label = self.index_to_class[pred]

        # Compute the confidence of the prediction
        # confidence1 represents the ratio of the most frequent prediction
        # confidence2 represents the average confidence (when looking at the softmax distribution
        # of the output) of the most frequent prediction
        confidence1 = sum(preds == pred) / len(preds)
        confidences = softmax(output.cpu().numpy(), axis=1)
        confidence2 = confidences[:, int(pred)].mean()
        return label, confidence1, confidence2
