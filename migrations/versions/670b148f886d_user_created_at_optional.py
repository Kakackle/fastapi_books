"""user_created_at_optional

Revision ID: 670b148f886d
Revises: 6cc0cd5313f0
Create Date: 2023-10-16 15:04:46.202732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '670b148f886d'
down_revision: Union[str, None] = '6cc0cd5313f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###