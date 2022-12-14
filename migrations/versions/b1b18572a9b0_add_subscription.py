"""add subscription

Revision ID: b1b18572a9b0
Revises: 17485872fff7
Create Date: 2020-09-08 21:48:43.985898

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1b18572a9b0'
down_revision = '17485872fff7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('subscription', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'subscription')
    # ### end Alembic commands ###
