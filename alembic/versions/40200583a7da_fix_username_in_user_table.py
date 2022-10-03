"""fix: username in user table

Revision ID: 40200583a7da
Revises: 9f1ad3765c57
Create Date: 2022-09-28 13:58:00.150206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "40200583a7da"
down_revision = "9f1ad3765c57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=256), nullable=True))
    pass


def downgrade() -> None:
    pass
