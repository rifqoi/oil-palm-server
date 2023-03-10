from app.core.config import settings
from app.ml_inference.yolo4 import OilPalmModel
from app.crud.crud_prediction import (
    static_map_url,
    read_image_from_url,
    convert_yolo_to_coco,
)

from app.mercator.mercator_projection import G_LatLng, G_Point, MercatorProjection
import numpy as np
import cv2
import logging

# proj = MercatorProjection()
# latlng2 = {"lat": -6.47484745212241, "lng": 107.03319672664993}

# latlng = G_LatLng(latlng2["lat"], latlng2["lng"])
# point = proj.fromLatLngToPoint(latlng)
# print(point.__dict__)

# point = G_Point(204.11262099249075, 132.6140866762166)
# lat = proj.fromPointToLatLng(point)
# print(lat.__dict__)


def draw_bounding_box(img, boxes):
    img = np.array(img)
    for box in boxes[0]:
        width = img.shape[1]
        height = img.shape[0]
        x = int(box[0] * width)
        y = int(box[1] * height)
        x2 = int(box[2] * width)
        y2 = int(box[3] * height)
        w = x2 - x
        h = y2 - y
        confidence = box[4]
        print(f"x {x} y {y}")
        print("w", w, "h", h)
        print()
        label = box[5]
        img = cv2.rectangle(img, (x, y, w, h), (0, 102, 255), 2)
        img = cv2.rectangle(img, (x, y - 20), (x + w, y), (0, 102, 255), -1)
        img = cv2.putText(
            img,
            "{}: {:.3f}".format(label, confidence),
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )
    return img


# print(settings.get_postgres_url())
-6.471460, 107.024628
url, url_raw = static_map_url(-6.471460, 107.024628, 20, 640, 640)
print(url)
image = read_image_from_url(url)
# print(image)

# print(image.shape)

model = OilPalmModel("./model/yolov4_1_3_416_416_static.onnx")
box = model.predict(image)
print("yolo4", len(box))

# bbox_img = draw_bounding_box(image, box)

# cv2.imwrite("yolo4", bbox_img)

# print(box)
# coco_box = convert_yolo_to_coco(box, 640, 640)
# print(box)
# print()
# print(coco_box)
# print(box)
# BoundingBox(x=0.3030061, y=0.110007465, width=0.40366134, height=0.22254899,confidence=0.978258, label='oilpalm')

import cv2
import time
import requests
import random
import numpy as np
import onnxruntime as ort
from PIL import Image
from pathlib import Path
from collections import OrderedDict, namedtuple

cuda = False
providers = (
    ["CUDAExecutionProvider", "CPUExecutionProvider"]
    if cuda
    else ["CPUExecutionProvider"]
)

w = "/home/rifqoi/Downloads/docs/best2.onnx"
session = ort.InferenceSession(w, providers=providers)


def letterbox(
    im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32
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


names = ["oilpalm"]
colors = {
    name: [random.randint(0, 255) for _ in range(3)] for i, name in enumerate(names)
}

img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

image = img.copy()
image, ratio, dwdh = letterbox(image, auto=False)
image = image.transpose((2, 0, 1))
image = np.expand_dims(image, 0)
image = np.ascontiguousarray(image)

im = image.astype(np.float32)
im /= 255
im.shape

outname = [i.name for i in session.get_outputs()]

inname = [i.name for i in session.get_inputs()]

inp = {inname[0]: im}

outputs = session.run(outname, inp)[0]
print("yolo7", len(outputs))

ori_images = [img.copy()]

for i, (batch_id, x0, y0, x1, y1, cls_id, score) in enumerate(outputs):
    image = ori_images[int(batch_id)]
    box = np.array([x0, y0, x1, y1])
    box -= np.array(dwdh * 2)
    box /= ratio
    box = box.round().astype(np.int32).tolist()
    cls_id = int(cls_id)
    score = round(float(score), 3)
    name = names[cls_id]
    color = colors[name]
    name += " " + str(score)
    cv2.rectangle(image, box[:2], box[2:], color, 2)
    cv2.putText(
        image,
        name,
        (box[0], box[1] - 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        [225, 255, 255],
        thickness=2,
    )

cv2.imwrite("yolo7.png", (ori_images[0]))
