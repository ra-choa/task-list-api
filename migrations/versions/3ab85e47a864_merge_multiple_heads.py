"""Merge multiple heads

Revision ID: 3ab85e47a864
Revises: 92e6e80e60f3, 04f16c3c7d4d, 9f198a8fe64e
Create Date: 2025-05-19 08:54:02.597699

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ab85e47a864'
down_revision = ('92e6e80e60f3', '04f16c3c7d4d', '9f198a8fe64e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
