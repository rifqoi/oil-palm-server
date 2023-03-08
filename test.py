from app.core.config import settings
from app.ml_inference.yolo import OilPalmModel
from app.crud.crud_prediction import (
    static_map_url,
    read_image_from_url,
    convert_yolo_to_coco,
)

from app.mercator.mercator_projection import G_LatLng, G_Point, MercatorProjection
import numpy as np
import cv2
import logging

proj = MercatorProjection()
latlng2 = {"lat": -6.47484745212241, "lng": 107.03319672664993}

latlng = G_LatLng(latlng2["lat"], latlng2["lng"])
point = proj.fromLatLngToPoint(latlng)
print(point.__dict__)

# point = G_Point(204.11262099249075, 132.6140866762166)
# lat = proj.fromPointToLatLng(point)
# print(lat.__dict__)


# def draw_bounding_box(img, boxes):
#     img = np.array(img)
#     for box in boxes[0]:
#         width = img.shape[1]
#         height = img.shape[0]
#         x = int(box[0] * width)
#         y = int(box[1] * height)
#         x2 = int(box[2] * width)
#         y2 = int(box[3] * height)
#         w = x2 - x
#         h = y2 - y
#         confidence = box[4]
#         print(f"x {x} y {y}")
#         print("w", w, "h", h)
#         print()
#         label = box[5]
#         img = cv2.rectangle(img, (x, y, w, h), (0, 102, 255), 2)
#         img = cv2.rectangle(img, (x, y - 20), (x + w, y), (0, 102, 255), -1)
#         img = cv2.putText(
#             img,
#             "{}: {:.3f}".format(label, confidence),
#             (x, y - 5),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.6,
#             (255, 255, 255),
#             1,
#         )
#     return img


# print(settings.get_postgres_url())
# url, url_raw = static_map_url(-6.470459014959625, 107.02424991129193, 20, 640, 640)
# print(url)
# image = read_image_from_url(url)
# print(image)

# print(image.shape)

# model = OilPalmModel("./model/yolov4_1_3_416_416_static.onnx")
# box = model.predict(image)

# bbox_img = draw_bounding_box(image, box)

# cv2.imwrite("test.png", bbox_img)

# print(box)
# # coco_box = convert_yolo_to_coco(box, 640, 640)
# # print(box)
# # print()
# # print(coco_box)
# # print(box)
# # BoundingBox(x=0.3030061, y=0.110007465, width=0.40366134, height=0.22254899,confidence=0.978258, label='oilpalm')
