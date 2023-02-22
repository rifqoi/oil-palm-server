"""add created_at and updated_at for all tables

Revision ID: 3097e50fd0ff
Revises: c572f4217894
Create Date: 2023-01-18 11:55:00.823802

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3097e50fd0ff'
down_revision = 'c572f4217894'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('predictions', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('predictions', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('trees', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('trees', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('trees', 'updated_at')
    op.drop_column('trees', 'created_at')
    op.drop_column('predictions', 'updated_at')
    op.drop_column('predictions', 'created_at')
    # ### end Alembic commands ###