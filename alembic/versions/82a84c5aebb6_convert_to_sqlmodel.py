"""convert to sqlmodel

Revision ID: 82a84c5aebb6
Revises: 
Create Date: 2023-03-01 17:56:35.751483

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "82a84c5aebb6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=256), nullable=False),
        sa.Column(
            "username", sqlmodel.sql.sqltypes.AutoString(length=256), nullable=False
        ),
        sa.Column(
            "password", sqlmodel.sql.sqltypes.AutoString(length=256), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_table(
        "predictions",
        sa.Column("center_coords", sa.ARRAY(sa.Float(), dimensions=1), nullable=True),
        sa.Column("nw_bounds", sa.ARRAY(sa.Float(), dimensions=1), nullable=True),
        sa.Column("se_bounds", sa.ARRAY(sa.Float(), dimensions=1), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prediction_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "trees",
        sa.Column("yolo_bbox", sa.ARRAY(sa.Float(), dimensions=1), nullable=True),
        sa.Column("coco_bbox", sa.ARRAY(sa.Float(), dimensions=1), nullable=True),
        sa.Column("nw_bounds", sa.ARRAY(sa.Float(), dimensions=1), nullable=True),
        sa.Column("se_bounds", sa.ARRAY(sa.Float(), dimensions=1), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("prediction_id", sa.Integer(), nullable=False),
        sa.Column("tree_id", sa.Integer(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("long", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["prediction_id"],
            ["predictions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("trees")
    op.drop_table("predictions")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###
