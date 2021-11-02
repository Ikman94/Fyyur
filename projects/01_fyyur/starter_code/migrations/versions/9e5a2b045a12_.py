"""empty message

Revision ID: 9e5a2b045a12
Revises: 16fc6af441ab
Create Date: 2021-11-01 22:42:15.515993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e5a2b045a12'
down_revision = '16fc6af441ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Shows', sa.Column('start_time', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Shows', 'start_time')
    # ### end Alembic commands ###
