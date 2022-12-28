"""remove healthiness, add coco bbox, rename bounding_box to yolo_bbox

Revision ID: 659df5b0e9dc
Revises: dc7acb5b2a24
Create Date: 2022-12-28 13:27:13.917990

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision = '659df5b0e9dc'
down_revision = 'dc7acb5b2a24'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("predictions", sa.Column("coco_bbox", ARRAY(sa.Float, dimensions=2)))
    op.alter_column("predictions", "bounding_box", new_column_name="yolo_bbox")
    op.drop_column("predictions", "healthiness")
    pass


def downgrade() -> None:
    op.drop_column("predictions", "coco_bbox")
    op.alter_column("predictions", "yolo_bbox", new_column_name="bounding_box")
    op.add_column("predictions",  sa.Column("healthiness",ARRAY(sa.Float, dimensions=2)))
    pass
