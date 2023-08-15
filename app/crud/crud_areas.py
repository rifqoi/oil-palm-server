from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy.orm import Session
from app.models.area import Area

from app.models.tree import Tree
from app.schemas.area import AreaInsert
from app.schemas.prediction import TreeUpdateRequest


class CRUDArea:
    def add_area(self, db: Session, *, user_id: int, obj_in: AreaInsert) -> Area:
        print(obj_in)
        area_obj = Area(
            user_id=user_id,
            center_lat=obj_in.center_lat,
            center_long=obj_in.center_long,
            geojson=obj_in.geojson,
        )
        db.add(area_obj)
        db.commit()

        return area_obj

    def get_areas(self, db: Session, *, user_id: int) -> List[Area]:
        areas = db.query(Area).filter(Area.user_id == user_id).all()

        return areas


area = CRUDArea()
