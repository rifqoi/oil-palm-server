import io
from typing import Tuple

from PIL import Image

import numpy as np
from pydantic import BaseModel
import requests
from app.mercator.mercator_projection import MercatorProjection, G_Point, G_LatLng
from app.core.config import settings


class LatLng(BaseModel):
    lat: float
    lng: float


class BoundsLatLng(BaseModel):
    nw: LatLng = None
    se: LatLng = None


# Create a class for operations on a Google Static Map image
class GoogleStaticMap:
    # Initialize class object with
    def __init__(self, mapWidth=640, mapHeight=640):
        # Set the dimensions of Google Static Map image
        self.map_width = mapWidth
        self.map_height = mapHeight

    def read_image_from_url(self, url: str) -> np.ndarray:
        response = requests.get(url=url)
        img = Image.open(io.BytesIO(response.content))

        arr = np.asarray(img)
        return arr

    def static_map_url(
        self,
        lat: float,
        long: float,
        zoom: int,
    ) -> Tuple[str, str]:
        url_without_key = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom={zoom}&scale=3&size={self.map_width}x{self.map_height}&maptype=satellite&key="
        url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom={zoom}&scale=3&size={self.map_width}x{self.map_height}&maptype=satellite&key={settings.MAP_API_KEY}"
        return url, url_without_key

    def get_lat_long(self, center, zoom, x, y):
        scale = 2**zoom
        proj = MercatorProjection()
        # Find z=0 pixel coordinates of the center
        centerPx = proj.fromLatLngToPoint(center)
        # Find z=0 pixel coordinates of the corners of the Google Static Map image
        # desired_x = (center_x + (image_x - width / 2))
        # e.g.
        # width of an image is 640x640
        # center of the image is 320x320 (width/2, height/2)
        # and we want to point it to (1, 1) image coordinates
        # (1 , 1) => (320-319, 320-319)
        # from above example we can get this formula
        # desired_x = center_x - alpha
        # alpha = center_x - desired_x
        # 319 = 320 - 1
        point = G_Point(
            centerPx.x + (x - self.map_width / 2) / scale,
            centerPx.y + (y - self.map_height / 2) / scale,
        )
        tree_latlng = proj.fromPointToLatLng(point)

        latlng = LatLng(lat=tree_latlng.lat, lng=tree_latlng.lng)

        return latlng

    def get_bounds_lat_long(self, center, zoom, x, y, w, h):
        scale = 2**zoom
        proj = MercatorProjection()
        x2 = x + w
        y2 = y + h
        # Find z=0 pixel coordinates of the center
        centerPx = proj.fromLatLngToPoint(center)
        # Find z=0 pixel coordinates of the corners of the Google Static Map image
        nw_point = G_Point(
            centerPx.x + (x - self.map_width / 2) / scale,
            centerPx.y + (y - self.map_height / 2) / scale,
        )

        se_point = G_Point(
            centerPx.x + (x2 - self.map_width / 2) / scale,
            centerPx.y + (y2 - self.map_height / 2) / scale,
        )

        nw_latlong = proj.fromPointToLatLng(nw_point)
        se_latlong = proj.fromPointToLatLng(se_point)

        bounds = BoundsLatLng()
        bounds.nw = LatLng(lat=nw_latlong.lat, lng=nw_latlong.lng)
        bounds.se = LatLng(lat=se_latlong.lat, lng=se_latlong.lng)

        return bounds

    # Create a method to get z=0 pixel/geo edges of returned Google Static Map image of specified zoom and center and width, height
    def get_corners(self, center, zoom):
        scale = 2**zoom
        proj = MercatorProjection()
        # Find z=0 pixel coordinates of the center
        centerPx = proj.fromLatLngToPoint(center)
        # Find z=0 pixel coordinates of the corners of the Google Static Map image
        SWPoint = G_Point(
            centerPx.x - (self.map_width / 2) / scale,
            centerPx.y + (self.map_height / 2) / scale,
        )
        SEPoint = G_Point(
            centerPx.x + (self.map_width / 2) / scale,
            centerPx.y + (self.map_width / 2) / scale,
        )
        NEPoint = G_Point(
            centerPx.x + (self.map_width / 2) / scale,
            centerPx.y - (self.map_height / 2) / scale,
        )
        NWPoint = G_Point(
            centerPx.x - (self.map_width / 2) / scale,
            centerPx.y - (self.map_height / 2) / scale,
        )
        # Find geographical coordinates of the corners of the Google Static Map image
        SWLatLon = proj.fromPointToLatLng(SWPoint)
        SELatLon = proj.fromPointToLatLng(SEPoint)
        NELatLon = proj.fromPointToLatLng(NEPoint)
        NWLatLon = proj.fromPointToLatLng(NWPoint)
        # Return both z=0 pixel bounds and geographical bounds of the corners of the Google Static Map image
        return {
            "Ngeo": NELatLon.lat,
            "Egeo": NELatLon.lng,
            "NE": (NELatLon.lat, NELatLon.lng),
            "NW": (NWLatLon.lat, NWLatLon.lng),
            "SE": (SELatLon.lat, SELatLon.lng),
            "SW": (SWLatLon.lat, SWLatLon.lng),
            "Sgeo": SWLatLon.lat,
            "Wgeo": SWLatLon.lng,
            "Npix": NEPoint.y,
            "Epix": NEPoint.x,
            "Spix": SWPoint.y,
            "Wpix": SWPoint.x,
        }
