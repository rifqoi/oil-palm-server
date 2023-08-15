from dataclasses import dataclass

from pathlib import Path
from typing import List, cast

from PIL import Image as ImageModule
from PIL import ImageOps
from PIL.Image import Image, Resampling
import cv2

import numpy
from numpy import float32, float64, int32, int64
from numpy.typing import NDArray
import onnxruntime

from app.ml_inference.types import BoundingBox


@dataclass
class ImageTensor:
    original_size: tuple[int, int]
    scale_size: tuple[int, int]
    data: numpy.ndarray


def compute_iou(box: NDArray[int32], boxes: NDArray[int32]) -> NDArray[float64]:
    # Compute xmin, ymin, xmax, ymax for both boxes
    xmin = numpy.minimum(box[0], boxes[:, 0])
    ymin = numpy.minimum(box[1], boxes[:, 1])
    xmax = numpy.maximum(box[0] + box[2], boxes[:, 0] + boxes[:, 2])
    ymax = numpy.maximum(box[1] + box[3], boxes[:, 1] + boxes[:, 3])

    # Compute intersection area
    intersection_area = numpy.maximum(0, xmax - xmin) * numpy.maximum(0, ymax - ymin)

    # Compute union area
    box_area = box[2] * box[3]
    boxes_area = boxes[:, 2] * boxes[:, 3]
    union_area = box_area + boxes_area - intersection_area

    # Compute IoU
    iou = intersection_area / union_area

    return iou


def nms(
    boxes: NDArray[int32], scores: NDArray[float32], iou_threshold: float
) -> list[int64]:
    # Sort by score
    sorted_indices = numpy.argsort(scores)[::-1]

    keep_boxes = []
    while sorted_indices.size > 0:
        # Pick the last box
        box_id = sorted_indices[0]
        keep_boxes.append(box_id)

        # Compute IoU of the picked box with the rest
        ious = compute_iou(boxes[box_id, :], boxes[sorted_indices[1:], :])

        # Remove boxes with IoU over the threshold
        keep_indices = numpy.where(ious < iou_threshold)[0]

        # print(keep_indices.shape, sorted_indices.shape)
        sorted_indices = sorted_indices[keep_indices + 1]

    return keep_boxes


def image_to_tensor(img: Image, model):
    _, _, width, height = model.get_inputs()[0].shape

    img = ImageOps.exif_transpose(img)
    original_size = img.size

    img = ImageOps.contain(img, (width, height), Resampling.BILINEAR)
    scale_size = img.size

    img = ImageOps.pad(
        img, (width, height), Resampling.BILINEAR, (114, 114, 114), (0, 0)
    )
    data = numpy.array(img)

    data = data / 255.0
    data = data.transpose(2, 0, 1)
    print("sini4?")
    tensor = data[numpy.newaxis, :, :, :].astype(numpy.float32)

    return ImageTensor(original_size, scale_size, tensor)


class Predictor:
    def __init__(
        self,
        path="model/yolov8.onnx",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.7,
    ) -> None:
        self.model = onnxruntime.InferenceSession(
            path, providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )
        self.__names = ["oilpalm"]
        self.__conf_threshold = conf_threshold
        self.__iou_threshold = iou_threshold
        self.input_width = 640
        self.input_height = 640

    def prepare_input(self, image):
        self.img_height, self.img_width = image.shape[:2]

        input_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Resize input image
        input_img = cv2.resize(input_img, (self.input_width, self.input_height))

        # Scale input pixel values to 0 to 1
        input_img = input_img / 255.0
        input_img = input_img.transpose(2, 0, 1)
        input_tensor = input_img[numpy.newaxis, :, :, :].astype(numpy.float32)

        return input_tensor

    def predict(self, img: Image | Path | str) -> List[BoundingBox]:
        # if isinstance(img, str):
        #     img = Path(img)
        # if isinstance(img, Path):
        #     img = ImageModule.open(img)
        # if not isinstance(img, Image):
        #     raise ValueError("img must be an PIL Image, Path or string")

        tensor = image_to_tensor(img, self.model)
        results = cast(
            List[numpy.ndarray], self.model.run(None, {"images": tensor.data})
        )
        predictions = numpy.squeeze(results[0]).T

        scores = numpy.max(predictions[:, 4:], axis=1)
        keep = scores > self.__conf_threshold
        predictions = predictions[keep, :]
        scores = scores[keep]
        class_ids = numpy.argmax(predictions[:, 4:], axis=1)

        boxes = predictions[:, :4]
        # Make x0, y0 left upper corner instead of box center
        boxes[:, 0:2] -= boxes[:, 2:4] / 2
        boxes /= numpy.array(
            [*tensor.scale_size, *tensor.scale_size], dtype=numpy.float32
        )
        boxes *= numpy.array([*tensor.original_size, *tensor.original_size])
        boxes = boxes.astype(numpy.int32)

        keep = nms(boxes, scores, self.__iou_threshold)
        bboxes: List[BoundingBox] = []
        for bbox, label in zip(boxes[keep], class_ids[keep]):
            bbox = BoundingBox(
                x=bbox[0].item(),
                y=bbox[1].item(),
                width=bbox[2].item(),
                height=bbox[3].item(),
                label=self.__names[label],
            )
            print(bbox)
            bboxes.append(bbox)

        return bboxes
