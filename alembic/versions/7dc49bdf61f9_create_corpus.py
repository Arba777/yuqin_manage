"""create_corpus

Revision ID: 7dc49bdf61f9
Revises: 5ab07093a1ac
Create Date: 2024-12-23 16:10:47.323376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '7dc49bdf61f9'
down_revision: Union[str, None] = '5ab07093a1ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('corpus', 'deduction')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('corpus', sa.Column('deduction', mysql.INTEGER(), autoincrement=False, nullable=True, comment='扣分'))
    # ### end Alembic commands ###
