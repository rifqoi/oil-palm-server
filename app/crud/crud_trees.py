from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy.orm import Session

from app.models.tree import Tree
from app.schemas.prediction import TreeUpdateRequest


class CRUDTree:
    def get_all_trees(self, db: Session, *, user_id: int):
        trees = (
            db.query(Tree).filter(Tree.user_id == user_id).order_by(Tree.tree_id).all()
        )
        return trees

    def update_tree_status(
        self,
        db: Session,
        *,
        user_id: int,
        tree_id: int,
        obj_in: Union[TreeUpdateRequest, Dict[str, Any]],
    ):
        db_obj = (
            db.query(Tree)
            .filter(Tree.tree_id == tree_id and Tree.user_id == user_id)
            .first()
        )
        if db_obj is None:
            raise Exception(f"Tree with id {tree_id} not found")

        update_data: Dict[str, Any]
        if isinstance(db_obj, TreeUpdateRequest):
            update_data = db_obj.dict(exclude_none=True)
        else:
            update_data = dict(obj_in)

        obj_data = db_obj.dict()
        for field in obj_data:
            if field in update_data:
                if update_data[field] is not None:
                    setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_tree(self, db: Session, *, user_id: int, tree_id: int):
        rows_affected = (
            db.query(Tree)
            .filter(Tree.tree_id == tree_id and Tree.user_id == user_id)
            .delete()
        )
        if rows_affected == 0:
            raise Exception(f"Tree with id {tree_id} not found")

        db.commit()

    def get_total_counted_trees(self, db: Session, *, user_id: int) -> Optional[int]:
        return db.query(Tree).filter(Tree.user_id == user_id).count()

    def get_all_trees_center(self, db: Session, *, user_id: int) -> Tuple[float, float]:
        center = db.query(Tree.long, Tree.lat).filter(Tree.user_id == user_id).all()
        return center


tree = CRUDTree()
