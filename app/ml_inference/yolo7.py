from typing import List
import cv2
import time
import requests
import random
import numpy as np
import onnxruntime as ort
from PIL import Image
from pathlib import Path
from collections import OrderedDict, namedtuple

from app.ml_inference.types import BoundingBox


class OilPalmModelYoloV7:
    def __init__(
        self,
        onnx_path="model/yolo7.onnx",
        threshold=0.4,
        iou_threshold=0.4,
        input_size=(640, 640),
    ):
        """
        Parameters:
        ----------
        onnx_path: str
                Path onnx weights
        input_size: tuple
                Input Image Size
        """

        self.class_names = ["oilpalm"]
        self.input_size = input_size
        self.onnx_path = onnx_path
        self.threshold = threshold
        self.nms_threshold = 0 if iou_threshold - 0.1 < 0 else iou_threshold - 0.1

        self.__get_ort_session()

    def __get_ort_session(self):
        if ort.get_device() == "CPU":
            self.ort_session = ort.InferenceSession(
                self.onnx_path, providers=["CPUExecutionProvider"]
            )
        else:
            self.ort_session = ort.InferenceSession(
                self.onnx_path, providers=["CPUExecutionProvider"]
            )

    def letterbox(
        self,
        im,
        new_shape=(640, 640),
        color=(114, 114, 114),
        auto=True,
        scaleup=True,
        stride=32,
    ):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(
            im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
        )  # add border
        return im, r, (dw, dh)

    def __preprocessing_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        image, ratio, dwdh = self.letterbox(img, auto=False)
        image = image.transpose((2, 0, 1))
        image = np.expand_dims(image, 0)
        image = np.ascontiguousarray(image)
        im = image.astype(np.float32)
        im /= 255

        return im, ratio, dwdh

    def predict(self, img, threshold=None, iou_threshold=None) -> List[BoundingBox]:
        if threshold is None:
            threshold = self.threshold
        if iou_threshold is None:
            iou_threshold = self.nms_threshold
        img, ratio, dwdh = self.__preprocessing_image(img)
        outname = [i.name for i in self.ort_session.get_outputs()]

        inname = [i.name for i in self.ort_session.get_inputs()]

        inp = {inname[0]: img}
        input_onnx = self.ort_session.get_inputs()[0].name
        outputs = self.ort_session.run(outname, inp)[0]

        ori_images = [img.copy()]

        bboxes: List[BoundingBox] = []
        for i, (batch_id, x0, y0, x1, y1, cls_id, score) in enumerate(outputs):
            print(f"yolo7 x0={x0} y0={y0} x1={x1} y1={y1}")
            score = round(float(score), 3)
            name = "oilpalm"

            x = x0 / 640
            y = y0 / 640

            x1 = x1 / 640
            y1 = y1 / 640

            bbox_model = BoundingBox()

            # Convert npfloat to native flaot
            bbox_model.x = x
            bbox_model.y = y
            bbox_model.width = x1
            bbox_model.height = y1
            bbox_model.confidence = score
            bbox_model.label = name

            bboxes.append(bbox_model)

        return bboxes
