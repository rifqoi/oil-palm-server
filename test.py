from app.core.config import settings
from app.ml_inference.yolo import OilPalmModel
from app.crud.crud_prediction import (
    static_map_url,
    read_image_from_url,
    convert_yolo_to_coco,
)
import numpy as np
import logging

print(settings.get_postgres_url())
url = static_map_url(-6.470459014959625, 107.02424991129193, 20, 640, 640)
print(url)
image = read_image_from_url(url)
print(image)

print(image.shape)

model = OilPalmModel("./model/yolov4_1_3_416_416_static.onnx")
box = model.predict(image)

coco_box = convert_yolo_to_coco(box, 640, 640)
print(box)
print()
print(coco_box)
# print(box)
# BoundingBox(x=0.3030061, y=0.110007465, width=0.40366134, height=0.22254899,confidence=0.978258, label='oilpalm')
