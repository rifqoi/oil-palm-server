from typing import Optional

from sqlalchemy.orm import Session

from app.models.tree import Tree


class CRUDTree:
    def get_all_trees(self, db: Session, *, user_id: int):
        trees = db.query(Tree).filter(Tree.user_id == user_id).all()
        return trees

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


tree = CRUDTree()
