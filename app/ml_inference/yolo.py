from typing import List, Union
from pydantic import BaseModel

import cv2
import numpy as np
from numpy.core.numeric import argwhere
import onnxruntime as ort


class BoundingBox(BaseModel):
    # type: ignore
    x: float = None
    y: float = None
    width: float = None
    height: float = None
    confidence: float = None
    label: str = None

    # For mercator projection
    x_center: float = None
    y_center: float = None


class OilPalmModel:
    def __init__(
        self,
        onnx_path="model/yolov4_1_3_416_416_static.onnx",
        threshold=0.4,
        iou_threshold=0.4,
        input_size=(416, 416),
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

    def __preprocessing_img(self, img):
        w, h = img.shape[:2]
        if w > self.input_size[0] or h > self.input_size[1]:
            img = cv2.resize(img, self.input_size, interpolation=cv2.INTER_AREA)

        img = cv2.resize(img, self.input_size, interpolation=cv2.INTER_LINEAR)
        # convert to rgb
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.transpose(img, (2, 0, 1)).astype(np.float32)
        img = np.expand_dims(img, axis=0)
        img /= 255.0
        return img

    def __nmsbbox(self, bbox, max_confidence, iou_threshold, min_mode=True):
        x1 = bbox[:, 0]
        y1 = bbox[:, 1]
        x2 = bbox[:, 2]
        y2 = bbox[:, 3]
        areas = (x2 - x1) * (y2 - y1)
        order = max_confidence.argsort()[::-1]
        keep = []
        while order.size > 0:
            idx_self = order[0]
            idx_other = order[1:]
            keep.append(idx_self)
            xx1 = np.maximum(x1[idx_self], x1[idx_other])
            yy1 = np.maximum(y1[idx_self], y1[idx_other])
            xx2 = np.minimum(x2[idx_self], x2[idx_other])
            yy2 = np.minimum(y2[idx_self], y2[idx_other])
            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h
            if min_mode:
                over = inter / np.minimum(areas[order[0]], areas[order[1:]])
            else:
                over = inter / (areas[order[0]] + areas[order[1:]] - inter)
            inds = np.where(over <= iou_threshold)[0]
            order = order[inds + 1]

        return np.array(keep)

    def __postprocessing_onnx(self, output_onnx, threshold, iou_threshold):
        box_array = output_onnx[0]
        confs = output_onnx[1]
        num_classes = confs.shape[2]
        box_array = box_array[:, :, 0]
        max_conf = np.max(confs, axis=2)
        max_id = np.argmax(confs, axis=2)
        bboxes_batch = []
        for i in range(box_array.shape[0]):
            argwhere = max_conf[i] > threshold

            l_box_array = box_array[i, argwhere, :]
            l_max_conf = max_conf[i, argwhere]
            l_max_id = max_id[i, argwhere]
            bboxes = []
            for j in range(num_classes):
                cls_argwhere = l_max_id == j
                ll_box_array = l_box_array[cls_argwhere, :]
                ll_max_conf = l_max_conf[cls_argwhere]
                ll_max_id = l_max_id[cls_argwhere]
                keep = self.__nmsbbox(ll_box_array, ll_max_conf, iou_threshold)
                if keep.size > 0:
                    ll_box_array = ll_box_array[keep, :]
                    ll_max_conf = ll_max_conf[keep]
                    ll_max_id = ll_max_id[keep]
                    for k in range(ll_box_array.shape[0]):
                        bboxes.append(
                            [
                                ll_box_array[k, 0],
                                ll_box_array[k, 1],
                                ll_box_array[k, 2],
                                ll_box_array[k, 3],
                                ll_max_conf[k],
                                self.class_names[ll_max_id[k]],
                                ll_max_id[k],
                            ]
                        )
            bboxes_batch.append(bboxes)

        return bboxes_batch

    def predict(self, img, threshold=None, iou_threshold=None) -> List[BoundingBox]:
        if threshold is None:
            threshold = self.threshold
        if iou_threshold is None:
            iou_threshold = self.nms_threshold
        img = self.__preprocessing_img(img)
        input_onnx = self.ort_session.get_inputs()[0].name
        output_onnx = self.ort_session.run(None, {input_onnx: img})
        postprocess_onnx = self.__postprocessing_onnx(
            output_onnx, threshold, iou_threshold
        )
        pp_output_onnx: List[List[Union[np.float32, np.float64]]] = postprocess_onnx[0]

        bboxes: List[BoundingBox] = []
        for box in pp_output_onnx:
            bbox_model = BoundingBox()

            # Convert npfloat to native flaot
            bbox_model.x = box[0].item()
            bbox_model.y = box[1].item()
            bbox_model.width = box[2].item()
            bbox_model.height = box[3].item()
            bbox_model.confidence = box[4].item()
            bbox_model.label = box[5]

            bboxes.append(bbox_model)

        return bboxes
