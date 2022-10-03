"""add name to table users

Revision ID: dc7acb5b2a24
Revises: 9906aed008a9
Create Date: 2022-10-03 20:56:08.409082

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dc7acb5b2a24"
down_revision = "9906aed008a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("name", sa.String(length=256), nullable=True))

    pass


def downgrade() -> None:
    pass
