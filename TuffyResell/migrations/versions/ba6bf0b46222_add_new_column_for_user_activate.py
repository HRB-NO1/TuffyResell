"""add new column for user activate”

Revision ID: ba6bf0b46222
Revises: 8604eec64fd3
Create Date: 2022-11-14 12:28:35.417238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba6bf0b46222'
down_revision = '8604eec64fd3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_activated', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_activated')
    # ### end Alembic commands ###
